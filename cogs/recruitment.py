import discord as dc
from discord.ext import commands
from views.recruitment_buttons import FormButton
from views.recruitment_panel import RecruitmentPanel
from repositories.csv_candidates import CandidatesRepository
from repositories.csv_members import MembersRepository
from services.form_validator import FormValidator
from services.recruitment_service import RecruitmentService
from services.brawlstars import BrawlStarsService
from services.clubs_service import ClubsService

class Recruitment(commands.Cog):
    """
    Cog responsável pelos comandos de recrutamento.
    Registra as views e cria o comando de setup do painel de recrutamento.
    """
    def __init__(self, bot, service):
        self.bot = bot
        self.service = service

    async def cog_load(self):
        self.bot.add_view(FormButton(self.service))
        self.bot.add_view(RecruitmentPanel(self.service))

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup_recrutamento(self, ctx):
        embed = dc.Embed(
            title="😝 Recrutamento",
            description="etc etc etc"
        )
        await ctx.send(embed=embed, view=RecruitmentPanel(self.service))
        await ctx.message.delete()

async def setup(bot):
    brawl = BrawlStarsService()
    service = RecruitmentService(
        validator=FormValidator(),
        brawl=brawl,
        candidates=CandidatesRepository(),
        members=MembersRepository(),
        clubs=ClubsService(brawl)
    )
    await bot.add_cog(Recruitment(bot, service))