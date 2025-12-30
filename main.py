from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from routers import asistencias
from database import get_db
from services.AsistenciaDB import get_asistencias_manuales_CZPicho
from starlette.concurrency import run_in_threadpool
from services.validaciones import validarAsistenciasExistentes

app = FastAPI()

app.include_router(asistencias.router)

@app.get("/")
async def root():
    return {"mensaje": "Hola Mundo desde FastAPI"}

@app.get("/test-db")
async def test_db(db: Session = Depends(get_db)):
    try:
        # Intenta hacer una consulta simple
        result = db.execute(text("SELECT 1"))
        return {"mensaje": "Conexión a base de datos exitosa", "resultado": result.scalar()}
    except Exception as e:
        return {"error": str(e)}
    
@app.get("/asistencias-manuales")
async def asistencias_manuales(db: Session = Depends(get_db)):
    # la función devuelve una lista de dataclass; FastAPI no serializa dataclass automáticamente
    result = await get_asistencias_manuales_CZPicho(db)
    # Si result es un dict con 'error', devolverlo tal cual
    if isinstance(result, dict) and result.get("error"):
        return result
    # Convertir dataclasses a dicts para JSON
    return [r.to_dict() for r in result]

@app.get("/validar-asistencias")
async def validar_asistencias(db: Session = Depends(get_db)):
    from services.validaciones import validarAsistenciasExistentes
    # validarAsistenciasExistentes es async y acepta la sesión db
    result = await validarAsistenciasExistentes(db)
    return result

#uvicorn main:app --reload