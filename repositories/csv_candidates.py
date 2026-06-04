from services.clubs_service import ClubsService
from services.brawlstars import BrawlStarsService
from models import Candidate

class CandidatesRepository:
    """
    Repositório de candidatos pendentes de avaliação.
    Lê e escreve no CSV correspondente.
    """
    def __init__(self, path: str = "database/candidates.csv"):
        self.path = path

    def exists(self, player_tag: str = None, phone: str = None) -> bool:
        with open(self.path, mode="r", encoding="utf-8") as arq:    
            for linha in arq:
                col = linha.strip().split(",")
                if col[4] == player_tag or col[2] == phone:
                    return True
        return False

    def save(self, c: Candidate):
        data = [
            str(c.user_id), 
            c.name, 
            c.phone, 
            c.nickname,
            c.player_tag, 
            str(c.trophies), 
            c.division.name
        ]
        with open(self.path, mode="a", encoding="utf-8") as arq:
            arq.write(",".join(data) + "\n")

    def pop(self, user_id: str, only_get: bool = False) -> Candidate | None:
        with open(self.path, mode="r", encoding="utf-8") as arq:
            linhas = arq.readlines()
            for index, linha in enumerate(linhas):
                col = linha.strip().split(",")
                if col[0] == user_id:
                    linhas.pop(index)
                    break
        
        if only_get == False:
            with open(self.path, mode="w", encoding="utf-8") as arq:
                arq.writelines(linhas)
        
        brawl = BrawlStarsService()
        clubs_service = ClubsService(brawl)
        return Candidate(
            user_id = int(col[0]),
            name = col[1],
            phone = col[2],
            nickname = col[3],
            player_tag = col[4],
            trophies = int(col[5]),
            division = clubs_service.division_by_name(col[6])
        )