from models import Candidate

class MembersRepository:
    """
    Repositório dos membros do clube.
    Lê e escreve no CSV correspondente.
    """
    def __init__(self, path: str = "database/members.csv"):
        self.path = path

    def exists(self, player_tag: str = None, phone: str = None) -> bool:
        with open(self.path, mode="r", encoding="utf-8") as arq:
            for linha in arq:
                col = linha.strip().split(",")
                if col[1] == player_tag or col[2] == phone:
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