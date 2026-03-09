from enum import IntEnum

class Weekday(IntEnum):
    SEGUNDA   = 0
    TERCA     = 1
    QUARTA    = 2
    QUINTA    = 3
    SEXTA     = 4
    SABADO    = 5
    DOMINGO   = 6

    def __str__(self) -> str:
        # FastAPI/Swagger mostra o nome do membro
        return self.name