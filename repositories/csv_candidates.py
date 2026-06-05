from models import Candidate
from repositories.mappers import CSVMapper
import csv

class CandidatesRepository:
    """
    Repositório de candidatos pendentes de avaliação.
    Lê e escreve no CSV correspondente.
    """
    def __init__(self, path: str = "database/candidates.csv"):
        self.path = path
        self.mapper = CSVMapper()
        self.headers = ["user_id", "name", "phone", "nickname", "player_tag", "trophies", "division"]

    def exists(self, user_id: int = None, player_tag: str = None, phone: str = None) -> bool:
        with open(self.path, mode="r", encoding="utf-8") as arq:  
            rows = csv.DictReader(arq)  
            for row in rows:
                if user_id and row["user_id"] == str(user_id):
                    return True
                if player_tag and row["player_tag"] == player_tag:
                    return True
                if phone and row["phone"] == phone:
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

    def pop(self, user_id: int, only_get: bool = False) -> Candidate | None:
        with open(self.path, mode="r", encoding="utf-8") as arq:
            reader = csv.DictReader(arq)
            rows = list(reader)

        found = None
        for index, row in enumerate(rows):
            if row["user_id"] == str(user_id):
                found = row
                if not only_get:
                    rows.pop(index)
                break
        
        if not only_get and found:
            with open(self.path, mode="w", encoding="utf-8") as arq:
                writer = csv.DictWriter(arq, fieldnames=self.headers)
                writer.writeheader()
                writer.writerows(rows)
            
        if found is None:
            return None
        
        return self.mapper.transform(found)

    def list_candidates(self) -> list[Candidate]:
        with open(self.path, mode="r", encoding="utf-8") as arq:
            reader = csv.DictReader(arq)
            return [self.mapper.transform(row) for row in reader]