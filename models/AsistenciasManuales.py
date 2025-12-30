from dataclasses import dataclass
from typing import Optional
from datetime import datetime, date, time


@dataclass
class AsistenciaManualDTO:
    IdAsistenciaManual: str
    IdTipoLector: Optional[str] = None
    IdLector: Optional[str] = None
    IdEmpleado: Optional[str] = None
    IdiButton: Optional[str] = None
    Fecha: Optional[datetime] = None
    HoraEntrada: Optional[str] = None
    HoraSalidaComida: Optional[str] = None
    HoraEntradaComida: Optional[str] = None
    HoraSalida: Optional[str] = None
    Observaciones: Optional[str] = None
    TipoEstado: Optional[int] = None
    FechaCreacion: Optional[datetime] = None
    IdUsuarioCreacion: Optional[str] = None
    FechaModificacion: Optional[datetime] = None
    IdUsuarioModificacion: Optional[str] = None

    def to_dict(self):
        def _time_value(v):
            if v is None:
                return None
            if isinstance(v, str):
                s = v.strip()
                if not s:
                    return None
                for fmt in ("%H:%M:%S", "%H:%M"):
                    try:
                        return datetime.strptime(s, fmt).time()
                    except Exception:
                        continue
                return s
            if isinstance(v, time):
                return v
            return v

        def _date_value(v):
            if v is None:
                return None
            if isinstance(v, datetime):
                return v.date()
            if isinstance(v, date):
                return v
            if isinstance(v, str):
                s = v.strip()
                if not s:
                    return None
                for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S"):
                    try:
                        return datetime.strptime(s, fmt).date()
                    except Exception:
                        continue
                return s
            return v

        return {
            "IdAsistenciaManual": self.IdAsistenciaManual,
            "IdTipoLector": self.IdTipoLector,
            "IdLector": self.IdLector,
            "IdEmpleado": self.IdEmpleado,
            "IdiButton": self.IdiButton,
            "Fecha": _date_value(self.Fecha),
            "HoraEntrada": _time_value(self.HoraEntrada),
            "HoraSalidaComida": _time_value(self.HoraSalidaComida),
            "HoraEntradaComida": _time_value(self.HoraEntradaComida),
            "HoraSalida": _time_value(self.HoraSalida),
            "Observaciones": self.Observaciones,
            "TipoEstado": self.TipoEstado,
            "FechaCreacion": self.FechaCreacion if not isinstance(self.FechaCreacion, str) else self.FechaCreacion,
            "IdUsuarioCreacion": self.IdUsuarioCreacion,
            "FechaModificacion": self.FechaModificacion if not isinstance(self.FechaModificacion, str) else self.FechaModificacion,
            "IdUsuarioModificacion": self.IdUsuarioModificacion,
        }
