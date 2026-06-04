from dataclasses import dataclass

@dataclass
class Candidate:
    user_id: str
    name: str
    player_id: str
    phone: str
    trophies: str
    division_name: str

class CandidatesRepository:
    """
    Repositório de candidatos pendentes de avaliação.
    Lê e escreve no CSV correspondente.
    """
    def __init__(self, path: str = "database/candidates.csv"):
        self.path = path

    def exists(self, player_id: str = None, phone: str = None) -> bool:
        with open(self.path, mode="r", encoding="utf-8") as arq:    
            for linha in arq:
                col = linha.strip().split(",")
                if col[2] == player_id or col[3] == phone:
                    return True
        return False

    def save(self, message_id: str, user_id: str, name: str, player_id: str, phone: str, trophies: str, division_name: str):
        with open(self.path, mode="a", encoding="utf-8") as arq:
            arq.write(",".join([message_id, user_id, name, player_id, phone, trophies, division_name]) + "\n")

    def pop(self, message_id: str) -> tuple | None:
        found = None
        with open(self.path, mode="r", encoding="utf-8") as arq:
            linhas = arq.readlines()
            for index, linha in enumerate(linhas):
                col = linha.strip().split(",")
                if col[0] == message_id:
                    found = tuple(col[1:])
                    linhas.pop(index)
                    break
        
        with open(self.path, mode="w", encoding="utf-8") as arq:
            arq.writelines(linhas)
        
        return Candidate(*col[1:])