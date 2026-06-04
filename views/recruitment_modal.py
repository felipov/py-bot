import discord as dc
from models import Candidate

class RecruitmentModal(dc.ui.Modal, title="Clubs Recruitment Form"):
    input_name = dc.ui.Label(
        text="Qual é o seu nome?",
        component=dc.ui.TextInput(
            custom_id="name_form_modal",
            placeholder="Escreva seu nome completo...", 
            style=dc.TextStyle.short,
            min_length=8, max_length=50
        )
    )

    input_tag = dc.ui.Label(
        text="Qual é a sua TAG no jogo? (ex.: #9JPJJPUUY)",
        component=dc.ui.TextInput(
            custom_id="id_form_modal",
            placeholder="Digite sua TAG do Brawl Stars...", 
            style=dc.TextStyle.short,
            min_length=5, max_length=10
        )
    )

    input_phone = dc.ui.Label(
        text="Qual é o seu número de telefone?",
        component=dc.ui.TextInput(
            custom_id="num_form_modal",
            placeholder="Digite seu número de telefone com DDD...",
            style=dc.TextStyle.short,
            min_length=11, max_length=15
        )
    )

    input_reason = dc.ui.Label(
        text="Um motivo para ser aceito (ex.: sei la)",
        component=dc.ui.TextInput(
            custom_id="reason_form_modal",
            placeholder="Escreva um bom motivo...",
            style=dc.TextStyle.long,
            min_length=5, max_length=150
        )
    )

    def __init__(self, service):
        super().__init__()
        self.service = service

    async def on_submit(self, interaction: dc.Interaction):
        await interaction.response.defer(ephemeral=True)

        result = await self.service.submit(
            interaction,
            Candidate( 
                user_id = interaction.user.id,
                name = self.input_name.component.value,
                phone = self.input_phone.component.value,
                player_tag = self.input_tag.component.value,
                reason = self.input_reason.component.value
            ),
        )
        
        if not result.ok:
            await interaction.followup.send(result.error, ephemeral=True)
            return

        await interaction.followup.send("enviado!", ephemeral=True)