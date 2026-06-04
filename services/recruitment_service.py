import discord as dc
from dataclasses import dataclass
from views.form_button import FormButton
from services.form_validator import FormValidator
from services.brawlstars import BrawlStarsService
from services.clubs_service import ClubsService, Division
from repositories.csv_candidates import CandidatesRepository
from repositories.csv_members import MembersRepository
from utils.constants import FORMS_CHANNEL_ID

@dataclass
class SubmitResult:
    """Resultado do envio de um formulário."""
    ok: bool
    error: str = ""

class RecruitmentService:
    """
    Serviço responsável por organizar o fluxo do recrutamento.
    Valida dados, checa duplicatas, busca troféus e organiza o envio e avaliação de formulários.
    """
    def __init__(self, validator, brawl, members, candidates, clubs):
        """
        Parameters
        ----------
        validator : FormValidator
        brawl : BrawlStarsService
        members : MembersRepository
        candidates : CandidatesRepository
        clubs : ClubsService
        """
        self.validator = validator
        self.brawl = brawl
        self.members = members
        self.candidates = candidates
        self.clubs = clubs

    async def submit(self, interaction: dc.Interaction, name: str, player_id: str, phone: str, reason: str):
        """
        Realiza o envio um formulário de recrutamento no canal de recrutamento e aguarda aprovação.

        Parameters
        ----------
        interaction : discord.Interaction
            Interação do discord que originou o envio do formulário.
        name : str
            Nome do candidato.
        player_id : str
            ID do jogador.
        phone : str
            Telefone do candidato.
        reason : str
            Motivo para entrar na comunidade.

        Returns
        -------
        SubmitResult
            Resultado com ok=True, ou ok=False e mensagem de erro.
        """
        player_id, phone = self.validator.clean(player_id, phone)

        error = self.validator.validate(phone)
        if error:
            return SubmitResult(ok=False, error=error)

        if self.members.exists(player_id=player_id):
            return SubmitResult(ok=False, error="ID já cadastrado.")

        if self.members.exists(phone=phone):
            return SubmitResult(ok=False, error="Telefone já cadastrado.")

        if self.candidates.exists(player_id=player_id, phone=phone):
            return SubmitResult(ok=False, error="Você já enviou o formulário, aguarde.")

        player = await self.brawl.get_player_data(player_id)
        if player is None:
            return SubmitResult(ok=False, error="Jogador não encontrado.")

        trophies = int(player.get("trophies", 0))
        
        division = await self.clubs.get_division(trophies)
        if division is None:
            return SubmitResult(ok=False, error="Não temos uma divisão adequada para você no momento :()")

        embed = self._build_embed(interaction, name, player_id, phone, reason, trophies, division)

        channel = await self._get_channel(interaction)

        if channel is None:
            return SubmitResult(ok=False, error="Canal de formulários não encontrado.")

        message = await channel.send(embed=embed, view=FormButton(self))

        self.candidates.save(str(message.id), str(interaction.user.id), name, player_id, phone, str(trophies), division.name)

        return SubmitResult(ok=True)

    async def approve(self, interaction: dc.Interaction):
        """Aprova o formulário."""
        await self._resolve(interaction, approved=True)

    async def decline(self, interaction: dc.Interaction):
        """Recusa o formulário."""
        await self._resolve(interaction, approved=False)

    async def _resolve(self, interaction: dc.Interaction, approved: bool):
        """
        Resolve um formulário como aprovado ou recusado.

        Edita o embed com o status final, desativa os botões, tenta enviar o resultado 
        na dm e, se aprovado, move o candidato para o repositório de membros.

        Parameters
        ----------
        interaction : discord.Interaction
            Interação do discord que avaliou o formulário.
        approved : bool
            True para aprovar, False para recusar.
        """
        embed = interaction.message.embeds[0]
        label = f"Aprovado por {interaction.user.mention}" if approved else f"Recusado por {interaction.user.mention}!"
        embed.description = embed.description.replace("Aguardando análise...", label)
        embed.color = dc.Color.green() if approved else dc.Color.red()

        if approved:
            candidate = self.candidates.pop(str(interaction.message.id))
            if candidate:
                user = await interaction.client.fetch_user(int(candidate.user_id))
                try:
                    await user.send("oier voce foi aceito")
                    self.members.save(candidate)
                except dc.Forbidden:
                    print(f"DM fechada para {user_id}")

        disabled_view = FormButton(self)
        for item in disabled_view.children:
            item.disabled = True

        await interaction.response.edit_message(embed=embed, view=disabled_view)

    def _build_embed(self, interaction: dc.Interaction, name: str, player_id: str, phone: str, reason: str, trophies: int, division: Division):
        """
        Monta o embed do formulário.
        
        Parameters
        ----------
        interaction: discord.Interaction
            Interação do discord que originou o envio do formulário.
        name : str
            Nome do candidato.
        player_id : str
            ID do jogador.
        phone : str
            Telefone do candidato.
        reason : str
            Motivo para entrar na comunidade.
        trophies : int
            Número de troféus do jogador.
        division : Division
            A divisão mais adequada para o jogador.

        Returns
        -------
        discord.Embed
            Embed formatado com os dados do candidato para envio.
        """
        trophies_str = f"{trophies:,}".replace(",", ".") if trophies > 0 else "Não sei"

        return dc.Embed(
            title="📝 Formulário de Recrutamento", 
            color=dc.Color.default(), 
            timestamp=interaction.created_at,
            description=(
                f"**Usuário:** {interaction.user.mention}\n"
                f"**Status:** Aguardando análise...\n"
                f"--------------------------\n"
                f"```yaml\n"
                f"Nickname: {name}\n"
                f"ID: #{player_id}\n"
                f"Troféus: {trophies_str}\n"
                f"Divisão adequada: {division.name}\n"
                f"Telefone: ({phone[:2]}) {phone[2]} {phone[3:7]}-{phone[7:]}\n"
                f"```\n"
                f"**Motivo:**\n"
                f"> {reason}\n"
                f"--------------------------\n"
            )
        ).set_thumbnail(url=interaction.user.display_avatar.url)

    async def _get_channel(self, interaction: dc.Interaction):
        """
        Busca o canal de formulário.
        
        Parameters
        ----------
        interaction : discord.Interaction
            Interação do discord que originou o envio do formulário.
        
        Returns
        -------
        discord.TextChannel | None
            Canal de texto ou None, se não encontrar.
        """
        channel = interaction.client.get_channel(FORMS_CHANNEL_ID)
        if channel is None:
            try:
                channel = await interaction.client.fetch_channel(FORMS_CHANNEL_ID)
            except Exception as err:
                print(f"Erro ao buscar canal de logs do formulário: {err}")
        return channel
