from models import Division

DIVISIONS = [
    Division("Moon", "2Y8QL0YVG", 105000),
    Division("Emerald", None, 90000),
    Division("Sapphire", None, 80000),
    Division("Diamond", "J002Q000", 70000),
    Division("Black", "2R2R9902Q", 60000),
    Division("White", "2UGJUU8LC", 50000),
    Division("Violet", "28L0PP98V", 40000),
    Division("Scarlet", "QUYVV2YL", 30000),
    Division("Pearl", "RJVVQ280", 20000),
    Division("Sun", "80JPYUV80", 0),
]

class ClubsService:
    def __init__(self, brawl):
        """
        Parameters
        ----------
        brawl : BrawlStarsService
        """
        self.brawl = brawl

    def division_by_name(self, division_name: str) -> Division | None:
        """
        Encontra a instância da divisão correspondente ao nome.

        Parameters
        ----------
        division_name : str
            O nome da divisão que será procurada.

        Returns
        -------
        Division | None
            A instância da divisão, se for encontrada, ou None, caso contrário. 
        """
        return next((d for d in DIVISIONS if d.name == division_name), None)

    async def get_division(self, trophies: int) -> Division | None:
        """
        Encontra a divisão mais adequada baseado no número de troféus do jogador.

        Parameters
        ----------
        trophies : int
            Número de troféus do jogador.

        Returns
        -------
        Division | None
            A divisão adequada ou None, se não encontrar.
        """
        for division in DIVISIONS:
            if division.club_tag is None:
                continue

            if trophies >= division.min_trophies and await self.has_vacancy(division):
                return division

        return None

    async def has_vacancy(self, division: Division) -> bool:
        """
        Verifica se há vagas na divisão.

        Parameters
        ----------
        division : Division
            A divisão que será verificada.
        
        Returns
        -------
        bool
            True, se houver vagas, e False, caso contrário.
        """
        if division.club_tag is None:
            return False

        data = await self.brawl.get_club_data(division.club_tag)
        if data is None:
            return False

        return len(data["members"]) < 30
