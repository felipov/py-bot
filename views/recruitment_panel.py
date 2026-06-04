import discord as dc
from views.recruitment_modal import RecruitmentModal

class RecruitmentPanel(dc.ui.View):
    def __init__(self, service):
        super().__init__(timeout=None)
        self.service = service

    @dc.ui.button(custom_id="form_button", label="Abrir Formulário")
    async def open_form(self, interaction: dc.Interaction, button: dc.ui.Button):
        await interaction.response.send_modal(RecruitmentModal(self.service))