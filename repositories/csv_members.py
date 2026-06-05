from models import Candidate
import csv

class MembersRepository:
    """
    Repositório dos membros do clube.
    Lê e escreve no CSV correspondente.
    """
    def __init__(self, path: str = "database/members.csv"):
        self.path = path
        self.headers = ["user_id", "name", "phone", "nickname", "player_tag", "trophies", "division"]

    def exists(self, player_tag: str = None, phone: str = None) -> bool:
        with open(self.path, mode="r", encoding="utf-8") as arq:
            rows = csv.DictReader(arq)
            for row in rows:
                if row["player_tag"] == player_tag:
                    return True
                if row["phone"] == phone:
                    return True
        return False

    def save(self, c: Candidate):
        with open(self.path, mode="a", encoding="utf-8") as arq:
            writer = csv.DictWriter(arq, fieldnames=self.headers)
            writer.writerow({
                "user_id": str(c.user_id),
                "name": c.name,
                "phone": c.phone,
                "nickname": c.nickname,
                "player_tag": c.player_tag,
                "trophies": str(c.trophies),
                "division": c.division.name
            })