from pydantic import BaseModel, validator
from typing import Optional, Any, Dict
from datetime import datetime, time


def _parse_datetime(val: Any) -> Optional[datetime]:
    if val is None:
        return None
    if isinstance(val, datetime):
        return val
    s = str(val).strip()
    if not s:
        return None
    # Try several common formats
    fmts = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
        "%d/%m/%Y %H:%M:%S",
    ]
    for f in fmts:
        try:
            return datetime.strptime(s, f)
        except Exception:
            pass
    # Fallback: try fromisoformat
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


def _parse_time(val: Any) -> Optional[time]:
    if val is None:
        return None
    if isinstance(val, time):
        return val
    s = str(val).strip()
    if not s:
        return None
    fmts = ["%H:%M:%S", "%H:%M"]
    for f in fmts:
        try:
            return datetime.strptime(s, f).time()
        except Exception:
            pass
    return None


class AsistenciaManualSchema(BaseModel):
    IdAsistenciaManual: str
    IdTipoLector: Optional[str] = None
    IdLector: Optional[str] = None
    IdEmpleado: Optional[str] = None
    IdiButton: Optional[str] = None
    Fecha: Optional[datetime] = None
    HoraEntrada: Optional[time] = None
    HoraSalidaComida: Optional[time] = None
    HoraEntradaComida: Optional[time] = None
    HoraSalida: Optional[time] = None
    Observaciones: Optional[str] = None
    TipoEstado: Optional[int] = None
    FechaCreacion: Optional[datetime] = None
    IdUsuarioCreacion: Optional[str] = None
    FechaModificacion: Optional[datetime] = None
    IdUsuarioModificacion: Optional[str] = None

    class Config:
        orm_mode = True

    @validator("TipoEstado", pre=True)
    def _cast_tipo_estado(cls, v):
        if v is None or v == "":
            return None
        try:
            return int(v)
        except Exception:
            return None

    @validator("Fecha", "FechaCreacion", "FechaModificacion", pre=True)
    def _validate_datetime(cls, v):
        return _parse_datetime(v)

    @validator("HoraEntrada", "HoraSalidaComida", "HoraEntradaComida", "HoraSalida", pre=True)
    def _validate_time(cls, v):
        return _parse_time(v)


def parse_db_row(row: Dict[str, Any]) -> AsistenciaManualSchema:
    """Recibe un diccionario (por ejemplo row de cursor o __dict__ de SQLAlchemy) y devuelve una instancia de AsistenciaManualSchema.

    Normaliza strings a datetimes/tiempos y convierte campos numéricos cuando procede.
    """
    if row is None:
        raise ValueError("row is None")

    # Normalizar claves: algunas fuentes devuelven claves en mayúsculas o minúsculas
    normalized = {}
    for k, v in row.items():
        normalized[k] = v

    # Pydantic se encargará del parsing por los validators
    return AsistenciaManualSchema.parse_obj(normalized)


def from_orm_instance(instance: Any) -> AsistenciaManualSchema:
    """Convierte una instancia ORM (SQLAlchemy) a esquema Pydantic.

    Uso: from_orm_instance(sqlalchemy_obj)
    """
    # SQLAlchemy instances may have attributes instead of dict keys
    data = {}
    for field in AsistenciaManualSchema.__fields__:
        data[field] = getattr(instance, field, None)
    return AsistenciaManualSchema.parse_obj(data)
