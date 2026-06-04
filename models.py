from dataclasses import dataclass

@dataclass
class Candidate:
    """Informações do candidato."""
    user_id: int = ""
    name: str = ""
    phone: str = ""
    nickname: str = ""
    player_tag: str = ""
    trophies: int = ""
    division: Division = None
    reason: str = ""

@dataclass
class Division:
    """Informações da divisão"""
    name: str
    club_tag: str
    min_trophies: int