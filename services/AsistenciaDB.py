from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from starlette.concurrency import run_in_threadpool
from models.AsistenciasManuales import AsistenciaManualDTO
from models.schemas import from_orm_instance
from models.schemas import parse_db_row
from models.Lectura import LecturaDTO
from models.LecturaRancho import LecturaRanchoDTO


async def get_asistencias_manuales_CZPicho(db: Session = Depends(get_db)):
    try:
        # Ejecutar el select en el threadpool
        result = await run_in_threadpool(db.execute, text("select * from [AsistenciasManuales]"))
        rows = await run_in_threadpool(result.fetchall)

        parsed = []
        for row in rows:
            # row puede ser Row; usar _mapping para dict
            try:
                data = dict(row._mapping) if hasattr(row, "_mapping") else dict(row)
            except Exception:
                # Fallback
                data = {col: getattr(row, col, None) for col in getattr(row, 'keys', lambda: [])()}

            # Normalizar/parsear usando el schema existente (convierte fechas/horas/tipos)
            pyd = parse_db_row(data)

            # Crear DTO (dataclass) desde el dict del Pydantic model
            dto = AsistenciaManualDTO(**pyd.dict())
            parsed.append(dto)

        return parsed
    except Exception as e:
        return {"error": str(e)}
    
async def validarExistenciaEmpleado(IDEmpleado: str, db: Session = Depends(get_db)):
    try:
        clave = IDEmpleado.upper()
        if not clave.startswith("E"):
            clave = f"E{clave}"

        query = text("SELECT COUNT(1) FROM iButtons WHERE Clave = :clave")
        result = await run_in_threadpool(db.execute, query, {"clave": clave})
        count = result.scalar()

        print("validarExistenciaEmpleado:", clave, "count:", count)

        return count > 0
    except Exception as e:
        print(f"Error validarExistenciaEmpleado: {e}")
        return False

    
async def getIdEmpleadoByClave(Clave: str, db: Session = Depends(get_db)):
    try:
        clave = Clave.upper()
        if not clave.startswith("E"):
            clave = f"E{clave}"

        query = text("""
            SELECT IdiButton 
            FROM iButtons 
            WHERE Clave = :clave
        """)

        result = await run_in_threadpool(db.execute, query, {"clave": clave})
        return result.scalar()
    except Exception as e:
        print(f"Error getIdEmpleadoByClave: {e}")
        return None

    
async def validarUUIDExistente(UUID: str, db: Session = Depends(get_db)):
    try:
        query = text("SELECT COUNT(1) FROM AsistenciasManuales WHERE IdAsistenciaManual = :uuid")
        result = await run_in_threadpool(db.execute, query, {"uuid": UUID})
        count = await run_in_threadpool(result.scalar)
    except Exception as e:
        # Log and return False on error
        print(f"Error validarUUIDExistente: {e}")
        return False
    
async def crearAsistenciaManual(asistencia: AsistenciaManualDTO, db: Session = Depends(get_db)):
    try:
        query = text("""
            INSERT INTO AsistenciasManuales 
            (IdAsistenciaManual,IdTipoLector,IdLector,IdEmpleado,IdiButton,Fecha,HoraEntrada,HoraSalidaComida,HoraEntradaComida,HoraSalida,Observaciones,TipoEstado,FechaCreacion,IdUsuarioCreacion,FechaModificacion,IdUsuarioModificacion)
            VALUES 
            (:IdAsistenciaManual, :IdTipoLector, :IdLector, :IdEmpleado, :IdiButton, :Fecha, :HoraEntrada, :HoraSalidaComida, :HoraEntradaComida, :HoraSalida, :Observaciones, :TipoEstado, :FechaCreacion, :IdUsuarioCreacion, :FechaModificacion, :IdUsuarioModificacion)
        """)
        await run_in_threadpool(db.execute, query, asistencia.to_dict())
        await run_in_threadpool(db.commit)
        return {"mensaje": "Asistencia manual creada exitosamente"}
    except Exception as e:
        await run_in_threadpool(db.rollback)
        return {"error": str(e)}
    
async def updateAsistenciaManual(asistencia: AsistenciaManualDTO, db: Session = Depends(get_db)):
    try:
        query = text("""
            UPDATE AsistenciasManuales
            SET 
                IdTipoLector = :IdTipoLector,
                IdLector = :IdLector,
                IdEmpleado = :IdEmpleado,
                IdiButton = :IdiButton,
                Fecha = :Fecha,
                HoraEntrada = :HoraEntrada,
                HoraSalidaComida = :HoraSalidaComida,
                HoraEntradaComida = :HoraEntradaComida,
                HoraSalida = :HoraSalida,
                Observaciones = :Observaciones,
                TipoEstado = :TipoEstado,
                FechaModificacion = :FechaModificacion,
                IdUsuarioModificacion = :IdUsuarioModificacion
            WHERE IdAsistenciaManual = :IdAsistenciaManual
        """)
        await run_in_threadpool(db.execute, query, asistencia.to_dict())
        await run_in_threadpool(db.commit)
        return {"mensaje": "Asistencia manual actualizada exitosamente"}
    except Exception as e:
        await run_in_threadpool(db.rollback)
        return {"error": str(e)}
    
async def crearLectura(lectura: LecturaDTO, db: Session = Depends(get_db)):
    try:
        query = text("""
            INSERT INTO Lecturas 
            (IdLectura,IdLector,IdiButton,FechaLectura,Precio,Destajo,PrecioBono,TipoLectura,Observaciones,TipoEstado,IdAsistenciaManual,IdCosechaManual,IdTipoLector,IdTipoChecada,FechaCreacion,IdUsuarioCreacion)
            VALUES (:IdLectura, :IdLector, :IdiButton, :FechaLectura, :Precio, :Destajo, :PrecioBono, :TipoLectura, :Observaciones, :TipoEstado, :IdAsistenciaManual, :IdCosechaManual, :IdTipoLector, :IdTipoChecada, :FechaCreacion, :IdUsuarioCreacion)
        """)
        await run_in_threadpool(db.execute, query, lectura.__dict__)
        await run_in_threadpool(db.commit)
        return {"mensaje": "Lectura creada exitosamente"}
    except Exception as e:
        await run_in_threadpool(db.rollback)
        return {"error": str(e)}

async def crearLecturaRancho(lectura: LecturaRanchoDTO, db: Session = Depends(get_db)):
    try:
        query = text("""
            INSERT INTO LecturasRancho 
            (IdLectura
           ,IdRancho
           ,FechaCreacion
           ,IdUsuarioCreacion)
            VALUES (:IdLectura, :IdRancho, :FechaCreacion, :IdUsuarioCreacion)
        """)
        await run_in_threadpool(db.execute, query, lectura.to_dict())
        await run_in_threadpool(db.commit)
        return {"mensaje": "Lectura Rancho creada exitosamente"}
    except Exception as e:
        await run_in_threadpool(db.rollback)
        return {"error": str(e)}