from models import Candidate, Division
from services.brawlstars import BrawlStarsService
from services.clubs_service import ClubsService

class CSVMapper: 
    def __init__(self):
        brawl = BrawlStarsService()
        self.clubs_service = ClubsService(brawl)

    def transform(self, raw_data: dict) -> Candidate:
        return Candidate(
            user_id = int(raw_data["user_id"]),
            name = raw_data["name"],
            phone = raw_data["phone"],
            nickname = raw_data["nickname"],
            player_tag = raw_data["player_tag"],
            trophies = int(raw_data["trophies"]),
            division = self.clubs_service.division_by_name(raw_data["division"])
        )