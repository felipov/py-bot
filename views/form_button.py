import discord as dc

class ConfirmDivisionView(dc.ui.View):
    def __init__(self, service, division, candidate: Candidate):
        super().__init__(timeout=180)
        self.service = service
        self.division = division
        self.candidate = candidate

    @dc.ui.button(custom_id="btn_force_division", label="Sim, forçar entrada", emoji="😰")
    async def force_division(self, interaction: dc.Interaction, button: dc.ui.Button):
        await self.service.force_approve(interaction, self.division, self.candidate)

class FormButton(dc.ui.View):
    def __init__(self, service):
        super().__init__(timeout=None)
        self.service = service
    
    @dc.ui.button(custom_id="btn_approve_form", style=dc.ButtonStyle.green, emoji="✅")
    async def approve(self, interaction: dc.Interaction, button: dc.ui.Button):
        await self.service.approve(interaction)

    @dc.ui.button(custom_id="btn_decline_form", style=dc.ButtonStyle.red, emoji="❌")
    async def decline(self, interaction: dc.Interaction, button: dc.ui.Button):
        await self.service.decline(interaction)

    @dc.ui.select(
        custom_id = "select_division_form",
        placeholder = "Escolher outra divisão",
        options = [
            dc.SelectOption(label="Moon Division", description="105000+ Troféus", value="Moon"),
            dc.SelectOption(label="Emerald Division", description="90000+ Troféus", value="Emerald"),
            dc.SelectOption(label="Sapphire Division", description="80000+ Troféus", value="Sapphire"),
            dc.SelectOption(label="Diamond Division", description="70000+ Troféus", value="Diamond"),
            dc.SelectOption(label="Black Division", description="60000+ Troféus", value="Black"),
            dc.SelectOption(label="White Division", description="50000+ Troféus", value="White"),
            dc.SelectOption(label="Violet Division", description="40000+ Troféus", value="Violet"),
            dc.SelectOption(label="Scarlet Division", description="30000+ Troféus", value="Scarlet"),
            dc.SelectOption(label="Pearl Division", description="20000+ Troféus", value="Pearl"),
            dc.SelectOption(label="Sun Division", description="0+ Troféus", value="Sun")
        ]
    )
    async def define_division(self, interaction: dc.Interaction, select: dc.ui.Select):
        division_name = select.values[0]
        await self.service.change_division(interaction, division_name)
    
    async def force_division(self, interaction: dc.Interaction, button: dc.ui.Button):
        await self.service.force_approve(interaction, self.division, self.candidate_id)