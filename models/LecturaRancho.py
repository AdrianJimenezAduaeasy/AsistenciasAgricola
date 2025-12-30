from dataclasses import dataclass
from typing import Optional, Any, Dict
from datetime import datetime


@dataclass
class LecturaRanchoDTO:
    IdLectura: str
    IdRancho: Optional[str] = None
    FechaCreacion: Optional[datetime] = None
    IdUsuarioCreacion: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "IdLectura": self.IdLectura,
            "IdRancho": self.IdRancho,
            "FechaCreacion": self.FechaCreacion,
            "IdUsuarioCreacion": self.IdUsuarioCreacion,
        }