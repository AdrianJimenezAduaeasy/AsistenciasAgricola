from dataclasses import dataclass
from typing import Optional, Any, Dict
from datetime import datetime


@dataclass
class MarcacionDTO:
    id: int
    emp: Optional[int] = None
    emp_code: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    punch_time: Optional[datetime] = None
    punch_state: Optional[str] = None
    punch_state_display: Optional[str] = None
    verify_type: Optional[int] = None
    verify_type_display: Optional[str] = None
    work_code: Optional[str] = None
    gps_location: Optional[str] = None
    area_alias: Optional[str] = None
    terminal_sn: Optional[str] = None
    temperature: Optional[float] = None
    is_mask: Optional[str] = None
    terminal_alias: Optional[str] = None
    upload_time: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "emp": self.emp,
            "emp_code": self.emp_code,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "department": self.department,
            "position": self.position,
            "punch_time": self.punch_time.isoformat() if self.punch_time else None,
            "punch_state": self.punch_state,
            "punch_state_display": self.punch_state_display,
            "verify_type": self.verify_type,
            "verify_type_display": self.verify_type_display,
            "work_code": self.work_code,
            "gps_location": self.gps_location,
            "area_alias": self.area_alias,
            "terminal_sn": self.terminal_sn,
            "temperature": self.temperature,
            "is_mask": self.is_mask,
            "terminal_alias": self.terminal_alias,
            "upload_time": self.upload_time.isoformat() if self.upload_time else None,
        }

    @classmethod
    def _parse_datetime(cls, val: Any) -> Optional[datetime]:
        if val is None:
            return None
        if isinstance(val, datetime):
            return val
        s = str(val).strip()
        if not s:
            return None
        # Try common formats, fallback to fromisoformat
        fmts = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M",
        ]
        for f in fmts:
            try:
                return datetime.strptime(s, f)
            except Exception:
                pass
        try:
            return datetime.fromisoformat(s)
        except Exception:
            return None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MarcacionDTO":
        """Crea un MarcacionDTO a partir de un dict (por ejemplo JSON o fila de API).

        No modifica la base de datos; solo normaliza tipos.
        """
        return cls(
            id=int(data.get("id") or data.get("Id") or 0),
            emp=_safe_int(data.get("emp") or data.get("IdEmpleado") or data.get("emp_id")),
            emp_code=data.get("emp_code"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            department=data.get("department"),
            position=data.get("position"),
            punch_time=cls._parse_datetime(data.get("punch_time") or data.get("punchTime") or data.get("Fecha")),
            punch_state=str(data.get("punch_state")) if data.get("punch_state") is not None else None,
            punch_state_display=data.get("punch_state_display"),
            verify_type=_safe_int(data.get("verify_type")),
            verify_type_display=data.get("verify_type_display"),
            work_code=data.get("work_code"),
            gps_location=data.get("gps_location"),
            area_alias=data.get("area_alias"),
            terminal_sn=data.get("terminal_sn"),
            temperature=_safe_float(data.get("temperature")),
            is_mask=data.get("is_mask"),
            terminal_alias=data.get("terminal_alias"),
            upload_time=cls._parse_datetime(data.get("upload_time") or data.get("uploadTime")),
        )


def _safe_int(v: Any) -> Optional[int]:
    if v is None or v == "":
        return None
    try:
        return int(v)
    except Exception:
        return None


def _safe_float(v: Any) -> Optional[float]:
    if v is None or v == "":
        return None
    try:
        return float(v)
    except Exception:
        return None
