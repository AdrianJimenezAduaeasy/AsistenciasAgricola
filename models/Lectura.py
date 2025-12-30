from dataclasses import dataclass
from typing import Optional, Any, Dict
from datetime import datetime


@dataclass
class LecturaDTO:
    IdLectura: str
    IdLector: Optional[str] = None
    IdiButton: Optional[str] = None
    FechaLectura : Optional[datetime] = None
    Precio: Optional[float] = None
    Destajo: Optional[float] = None
    PrecioBono: Optional[float] = None
    TipoLectura: Optional[int] = None
    Observaciones: Optional[str] = None
    TipoEstado: Optional[int] = None
    IdAsistenciaManual: Optional[str] = None
    IdCosechaManual: Optional[str] = None
    IdTipoLector: Optional[str] = None
    IdTipoChecada: Optional[str] = None
    FechaCreacion: Optional[datetime] = None
    IdUsuarioCreacion: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "IdLectura": self.IdLectura,
            "IdLector": self.IdLector,
            "IdiButton": self.IdiButton,
            "FechaLectura": self.FechaLectura.isoformat() if self.FechaLectura else None,
            "Precio": self.Precio,
            "Destajo": self.Destajo,
            "PrecioBono": self.PrecioBono,
            "TipoLectura": self.TipoLectura,
            "Observaciones": self.Observaciones,
            "TipoEstado": self.TipoEstado,
            "IdAsistenciaManual": self.IdAsistenciaManual,
            "IdCosechaManual": self.IdCosechaManual,
            "IdTipoLector": self.IdTipoLector,
            "IdTipoChecada": self.IdTipoChecada,
            "FechaCreacion": self.FechaCreacion.isoformat() if self.FechaCreacion else None,
            "IdUsuarioCreacion": self.IdUsuarioCreacion,
        }