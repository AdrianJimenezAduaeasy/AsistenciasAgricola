from typing import List
from fastapi import Depends
from sqlalchemy.orm import Session
from .AsistenciaDB import get_asistencias_manuales_CZPicho, getIdEmpleadoByClave
from models.AsistenciasManuales import AsistenciaManualDTO
from models.Marcacion import MarcacionDTO
from .ZKBiotime import get_biotime_data
from datetime import datetime, timedelta
from datetime import time as dtime
import random
import uuid
from starlette.concurrency import run_in_threadpool
from database import get_db
from .AsistenciaDB import crearAsistenciaManual, crearLectura, crearLecturaRancho, updateAsistenciaManual
from models.Lectura import LecturaDTO
from models.LecturaRancho import LecturaRanchoDTO

def generateUUID():
    # Usar uuid4 es más seguro para evitar colisiones
    return str(uuid.uuid4()).replace('-', '')[:19]

async def validarAsistenciasExistentes(db: Session = Depends(get_db)):
    def is_empty_time(val):
        if val is None:
            return True
        if isinstance(val, str):
            return val in ("", "00:00", "00:00:00")
        if hasattr(val, "hour"):
            return val.hour == 0 and val.minute == 0 and getattr(val, "second", 0) == 0
        return False

    # 1. Obtener datos iniciales
    asistenciasManuales: List[AsistenciaManualDTO] = await get_asistencias_manuales_CZPicho(db)
    # Ejecutar la llamada bloqueante de BioTime en un threadpool
    marcaciones_raw: List[MarcacionDTO] = await run_in_threadpool(get_biotime_data)

    # 2. Filtrado de Marcaciones (Tiempo y Duplicados)
    now = datetime.now()
    limite_tiempo = now - timedelta(minutes=10)
    
    vistos = set()
    marcaciones_filtradas = []

    for m in marcaciones_raw:
        # Filtro 1: Solo marcaciones de los últimos 10 minutos
        if m.punch_time and m.punch_time >= limite_tiempo:
            # Filtro 2: Evitar duplicados exactos (Mismo empleado y misma hora)
            identificador = (m.emp_code, m.punch_time)
            if identificador not in vistos:
                marcaciones_filtradas.append(m)
                vistos.add(identificador)

    # 3. Validación de Existencia de Empleados (Cache para optimizar DB)
    cache_empleados = {}
    marcaciones_validas_con_id = []

    for marcacion in marcaciones_filtradas:
        clave = marcacion.emp_code
        if clave in cache_empleados:
            id_emp = cache_empleados[clave]
        else:
            id_emp = await getIdEmpleadoByClave(clave, db)
            cache_empleados[clave] = id_emp
        
        if id_emp:
            marcaciones_validas_con_id.append({"marcacion": marcacion, "idEmpleado": id_emp})
        else:
            print(f"Empleado con clave {clave} no encontrado en DB.")

    # 4. Procesamiento de Asistencias (Actualizar existentes vs Nuevas)
    asistenciasActualizables: List[AsistenciaManualDTO] = []
    asistenciasNuevas: List[AsistenciaManualDTO] = []
    
    # Marcaciones que no coincidan con ninguna asistencia existente se volverán "Nuevas"
    indices_procesados = set()

    for i, item in enumerate(marcaciones_validas_con_id):
        m = item["marcacion"]
        id_emp = item["idEmpleado"]
        procesada = False

        for asistencia in asistenciasManuales:
            # Si el empleado coincide
            
            if str(id_emp) == str(asistencia.IdEmpleado):
                hora_val = m.punch_time.time() if m.punch_time else None
                
                # Lógica de cascada para llenar campos vacíos
                if is_empty_time(asistencia.HoraSalidaComida):
                    asistencia.HoraSalidaComida = hora_val or dtime(0, 0)
                    asistenciasActualizables.append(asistencia)
                    res_update = await updateAsistenciaManual(asistencia, db)
                    if isinstance(res_update, dict) and res_update.get("error"):
                        print("Error updateAsistenciaManual:", res_update)
                        return res_update
                    nuevaLectura = LecturaDTO(
                        IdLectura=generateUUID(),
                        IdLector="0",
                        IdiButton=id_emp,
                        FechaLectura=m.punch_time,
                        Precio=0.0,
                        Destajo=0.0,
                        PrecioBono=0.0,
                        TipoLectura=1,
                        Observaciones="Generada automáticamente desde ZKBiotime",
                        TipoEstado=1,
                        IdAsistenciaManual=asistencia.IdAsistenciaManual,
                        IdCosechaManual=None,
                        IdTipoLector=1,
                        IdTipoChecada=2,
                        FechaCreacion=datetime.now(),
                        IdUsuarioCreacion="Admin"
                    )
                    res_lectura = await crearLectura(nuevaLectura, db)
                    if isinstance(res_lectura, dict) and res_lectura.get("error"):
                        print("Error crearLectura:", res_lectura)
                        return res_lectura

                    res_rancho = await crearLecturaRancho(LecturaRanchoDTO(
                        IdLectura=nuevaLectura.IdLectura,
                        IdRancho="4SIPLI9BQ4JUFM5",
                        FechaCreacion=nuevaLectura.FechaCreacion,
                        IdUsuarioCreacion="Admin"
                    ), db)
                    if isinstance(res_rancho, dict) and res_rancho.get("error"):
                        print("Error crearLecturaRancho:", res_rancho)
                        return res_rancho
                    procesada = True
                    break
                elif is_empty_time(asistencia.HoraEntradaComida):
                    asistencia.HoraEntradaComida = hora_val or dtime(0, 0)
                    asistenciasActualizables.append(asistencia)
                    res_update = await updateAsistenciaManual(asistencia, db)
                    if isinstance(res_update, dict) and res_update.get("error"):
                        print("Error updateAsistenciaManual:", res_update)
                        return res_update
                    nuevaLectura = LecturaDTO(
                        IdLectura=generateUUID(),
                        IdLector="0",
                        IdiButton=id_emp,
                        FechaLectura=m.punch_time,
                        Precio=0.0,
                        Destajo=0.0,
                        PrecioBono=0.0,
                        TipoLectura=1,
                        Observaciones="Generada automáticamente desde ZKBiotime",
                        TipoEstado=1,
                        IdAsistenciaManual=asistencia.IdAsistenciaManual,
                        IdCosechaManual=None,
                        IdTipoLector=1,
                        IdTipoChecada=3,
                        FechaCreacion=datetime.now(),
                        IdUsuarioCreacion="Admin"
                    )
                    res_lectura = await crearLectura(nuevaLectura, db)
                    if isinstance(res_lectura, dict) and res_lectura.get("error"):
                        print("Error crearLectura:", res_lectura)
                        return res_lectura
                    res_rancho = await crearLecturaRancho(LecturaRanchoDTO(
                        IdLectura=nuevaLectura.IdLectura,
                        IdRancho="4SIPLI9BQ4JUFM5",
                        FechaCreacion=nuevaLectura.FechaCreacion,
                        IdUsuarioCreacion="Admin"
                    ), db)
                    if isinstance(res_rancho, dict) and res_rancho.get("error"):
                        print("Error crearLecturaRancho:", res_rancho)
                        return res_rancho
                    procesada = True
                    break
                elif is_empty_time(asistencia.HoraSalida):
                    asistencia.HoraSalida = hora_val or dtime(0, 0)
                    asistenciasActualizables.append(asistencia)
                    res_update = await updateAsistenciaManual(asistencia, db)
                    if isinstance(res_update, dict) and res_update.get("error"):
                        print("Error updateAsistenciaManual:", res_update)
                        return res_update
                    nuevaLectura = LecturaDTO(
                        IdLectura=generateUUID(),
                        IdLector="0",
                        IdiButton=id_emp,
                        FechaLectura=m.punch_time,
                        Precio=0.0,
                        Destajo=0.0,
                        PrecioBono=0.0,
                        TipoLectura=1,
                        Observaciones="Generada automáticamente desde ZKBiotime",
                        TipoEstado=1,
                        IdAsistenciaManual=asistencia.IdAsistenciaManual,
                        IdCosechaManual=None,
                        IdTipoLector=1,
                        IdTipoChecada=4,
                        FechaCreacion=datetime.now(),
                        IdUsuarioCreacion="Admin"
                    )
                    res_lectura = await crearLectura(nuevaLectura, db)
                    if isinstance(res_lectura, dict) and res_lectura.get("error"):
                        print("Error crearLectura:", res_lectura)
                        return res_lectura
                    res_rancho = await crearLecturaRancho(LecturaRanchoDTO(
                        IdLectura=nuevaLectura.IdLectura,
                        IdRancho="4SIPLI9BQ4JUFM5",
                        FechaCreacion=nuevaLectura.FechaCreacion,
                        IdUsuarioCreacion="Admin"
                    ), db)
                    if isinstance(res_rancho, dict) and res_rancho.get("error"):
                        print("Error crearLecturaRancho:", res_rancho)
                        return res_rancho
                    procesada = True
                    break
        
        if not procesada:
            # 5. Crear Nueva Asistencia si no se pudo actualizar ninguna existente
            nuevaAsistencia = AsistenciaManualDTO(
                IdAsistenciaManual=generateUUID(),
                IdTipoLector="1",
                IdLector="0",
                IdEmpleado=id_emp,
                IdiButton=id_emp,
                Fecha=m.punch_time.date(),
                HoraEntrada=m.punch_time.time() if m.punch_time else dtime(0, 0),
                HoraSalidaComida=dtime(0, 0),
                HoraEntradaComida=dtime(0, 0),
                HoraSalida=dtime(0, 0),
                Observaciones="Generada automáticamente desde ZKBiotime",
                TipoEstado=1,
                FechaCreacion=datetime.now(),
                IdUsuarioCreacion="Admin"
            )
            asistenciasNuevas.append(nuevaAsistencia)
            res_asistencia = await crearAsistenciaManual(nuevaAsistencia, db)
            if isinstance(res_asistencia, dict) and res_asistencia.get("error"):
                print("Error crearAsistenciaManual:", res_asistencia)
                return res_asistencia
            #Crear Lectura asociada

            nuevaLectura = LecturaDTO(
                IdLectura=generateUUID(),
                IdLector="0",
                IdiButton=id_emp,
                FechaLectura=m.punch_time,
                Precio=0.0,
                Destajo=0.0,
                PrecioBono=0.0,
                TipoLectura=1,
                Observaciones="Generada automáticamente desde ZKBiotime",
                TipoEstado=1,
                IdAsistenciaManual=nuevaAsistencia.IdAsistenciaManual,
                IdCosechaManual=None,
                IdTipoLector=1,
                IdTipoChecada=1,
                FechaCreacion=nuevaAsistencia.FechaCreacion,
                IdUsuarioCreacion="Admin"
            )
            res_lectura = await crearLectura(nuevaLectura, db)
            if isinstance(res_lectura, dict) and res_lectura.get("error"):
                print("Error crearLectura:", res_lectura)
                return res_lectura
            res_rancho = await crearLecturaRancho(LecturaRanchoDTO(
                IdLectura=nuevaLectura.IdLectura,
                IdRancho="4SIPLI9BQ4JUFM5",
                FechaCreacion=nuevaAsistencia.FechaCreacion,
                IdUsuarioCreacion="Admin"
            ), db)
            if isinstance(res_rancho, dict) and res_rancho.get("error"):
                print("Error crearLecturaRancho:", res_rancho)
                return res_rancho

    return {
        "asistenciasActualizables": asistenciasActualizables, 
        "asistenciasNuevas": asistenciasNuevas
    }