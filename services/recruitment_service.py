import discord as dc
from dataclasses import dataclass
from views.form_button import FormButton
from views.form_button import ConfirmDivisionView
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

    async def submit(self, interaction: dc.Interaction, c: Candidate):
        """
        Realiza o envio um formulário de recrutamento no canal de recrutamento e aguarda aprovação.

        Parameters
        ----------
        interaction : discord.Interaction
            Interação do discord que originou o envio do formulário.
        c : Candidate
            O candidato a novo membro da comunidade.

        Returns
        -------
        SubmitResult
            Resultado com ok=True, ou ok=False e mensagem de erro.
        """
        c.player_tag, c.phone = self.validator.clean(c.player_tag, c.phone)

        error = self.validator.validate(c.phone)
        if error:
            return SubmitResult(ok=False, error=error)

        if self.members.exists(player_tag=c.player_tag):
            return SubmitResult(ok=False, error="ID já cadastrado.")

        if self.members.exists(phone=c.phone):
            return SubmitResult(ok=False, error="Telefone já cadastrado.")

        if self.candidates.exists(player_tag=c.player_tag, phone=c.phone):
            return SubmitResult(ok=False, error="Você já enviou o formulário, aguarde.")

        player = await self.brawl.get_player_data(c.player_tag)
        if player is None:
            return SubmitResult(ok=False, error="Jogador não encontrado.")

        trophies = player.get("trophies", 0)
        nickname = player.get("name", "Não encontrado")
        
        division = await self.clubs.get_division(trophies)
        if division is None:
            return SubmitResult(ok=False, error="Não temos uma divisão adequada para você no momento :(")

        c.trophies = trophies
        c.nickname = nickname
        c.division = division

        channel = await self._get_channel(interaction)
        if channel is None:
            return SubmitResult(ok=False, error="Canal de formulários não encontrado.")

        embed = self._build_embed(interaction, c)
        await channel.send(embed=embed, view=FormButton(self))

        self.candidates.save(c)

        return SubmitResult(ok=True)

    async def approve(self, interaction: dc.Interaction):
        """Aprova o formulário."""
        await self._resolve(interaction, approved=True)

    async def decline(self, interaction: dc.Interaction):
        """Recusa o formulário."""
        await self._resolve(interaction, approved=False)

    async def change_division(self, interaction: dc.Interaction, division_name: str):
        embed = interaction.message.embeds[0]
        candidate_id = "".join(c for c in embed.footer.text if c.isdigit())
        candidate = self.candidates.pop(candidate_id, only_get = True)

        division = self.clubs.division_by_name(division_name)
        if division is None:
            await interaction.response.send_message("Divisão não encontrada.", ephemeral=True)
            return

        if not await self.clubs.has_vacancy(division):
            embed = dc.Embed(
                title = "Clube cheio! 😦",
                description = f"Não há vagas na **{division_name} Division**. Deseja forçar a entrada?",
                color = dc.Color.orange()
            )
            await interaction.response.send_message(
                embed = embed,
                view = ConfirmDivisionView(self, division, candidate),
                ephemeral = True
            )
            return
        
        await self._approve_with_division(interaction, candidate, division)

    async def force_approve(self, interaction: dc.Interaction, division: Division, candidate: Candidate):
        self.candidates.pop(candidate.user_id)
        await self._approve_with_division(interaction, candidate, division)

    async def _approve_with_division(self, interaction: dc.Interaction, candidate: Candidate, division: Division):
        candidate.division = division
        self.members.save(candidate)
        user = await interaction.client.fetch_user(int(candidate.user_id))
        try:
            await user.send("oier voce foi aceitor")
        except dc.Forbidden:
            print(f"DM fechada para {user_id}")
        except Exception as err:
            print(f"Erro ao enviar DM: {err}")

        embed = interaction.message.embeds[0]
        embed.description = embed.description.replace("Aguardando análise...", f"Aprovado por {interaction.user.mention}")
        embed.color = dc.Color.green()

        disabled_view = dc.ui.View.from_message(interaction.message)
        for item in disabled_view.children:
            item.disabled = True

        await interaction.response.edit_message(embed=embed, view=disabled_view)

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
        await interaction.response.defer()

        embed = interaction.message.embeds[0]
        label = f"Aprovado por {interaction.user.mention}" if approved else f"Recusado por {interaction.user.mention}!"
        embed.description = embed.description.replace("Aguardando análise...", label)
        embed.color = dc.Color.green() if approved else dc.Color.red()

        user_id = "".join(c for c in embed.footer.text if c.isdigit())
        candidate = self.candidates.pop(user_id)

        if candidate:
            try:
                user = await interaction.client.fetch_user(int(user_id))
                if approved:
                    await user.send("oier voce foi aceitor")
                    self.members.save(candidate)
                else:
                    await user.send("oier voce nao foi aceitor")
            except dc.Forbidden:
                print(f"DM fechada para {user_id}")
            except Exception as err:
                print(f"Erro ao enviar DM: {err}")

        disabled_view = dc.ui.View.from_message(interaction.message)
        for item in disabled_view.children:
            item.disabled = True

        await interaction.message.edit(embed=embed, view=disabled_view)

    def _build_embed(self, interaction: dc.Interaction, c: Candidate):
        """
        Monta o embed do formulário.
        
        Parameters
        ----------
        interaction: discord.Interaction
            Interação do discord que originou o envio do formulário.
        c : Candidate
            O candidato a novo membro da comunidade.

        Returns
        -------
        discord.Embed
            Embed formatado com os dados do candidato para envio.
        """
        trophies_str = f"{c.trophies:,}".replace(",", ".") if c.trophies > 0 else "Não sei"

        embed = dc.Embed(
            title="📝 Formulário de Recrutamento", 
            color=dc.Color.default(), 
            timestamp=interaction.created_at,
            description=(
                f"**Usuário:** {interaction.user.mention}\n"
                f"**Status:** Aguardando análise...\n"
                f"------------------------------------------\n"
                f"**Informações Pessoais:**\n"
                f"```yaml\n"
                f"Nome completo: {c.name}\n"
                f"Telefone: ({c.phone[:2]}) {c.phone[2]}{c.phone[3:7]}-{c.phone[7:]}\n"
                f"```\n"
                f"**Informações no Brawl Stars**\n"
                f"```yaml\n"
                f"Nickname: {c.nickname} #{c.player_tag}\n"
                f"Troféus: {trophies_str}\n"
                f"Divisão indicada: {c.division.name}\n"
                f"```\n"
                f"**Motivo:**\n"
                f"> {c.reason}\n"
                f"------------------------------------------\n"
            )
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_footer(text=f"ID do Usuário: {interaction.user.id}")
        return embed

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
