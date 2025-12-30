from fastapi import APIRouter
from services.ZKBiotime import get_biotime_data
from starlette.concurrency import run_in_threadpool

router = APIRouter()


@router.get("/prueba")
async def prueba():
    return {"mensaje": "Este es un endpoint de prueba"}


@router.get("/checadas")
async def checadas():
    result = await run_in_threadpool(get_biotime_data)
    # `get_biotime_data` ahora devuelve instancias `MarcacionDTO`; convertir a dicts para JSON
    try:
        return [r.to_dict() for r in result]
    except Exception:
        return result

