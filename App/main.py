from datetime import date
from math import ceil
from typing import List
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException

from .config import LIMIT_PAGINACION_DEFAULT, MIN_CANCELADOS_DEFAULT, HORARIO_INICIO, HORARIO_FIN, INTERVALO_TURNOS_MINUTOS, HORARIOS_DISPONIBLES
from .crudPersonas import obtener_todas_personas, crear_persona, actualizar_persona, buscar_persona, obtener_personas_con_turnos_cancelados, obtener_personas_por_estado, buscar_persona_por_dni
from .crudTurnos import (cancelar_turno, confirmar_turno, crear_turno, eliminar_turno, listar_turnos, 
                        actualizar_turno, buscar_turno, obtener_turnos_disponibles, obtener_turnos_por_fecha,
                        agrupar_turnos_por_persona, obtener_turnos_cancelados_mes_actual, obtener_turnos_por_persona,
                        obtener_turnos_confirmados_por_periodo, obtener_todos_turnos_confirmados_por_periodo)
from .database import Base, engine
from .models import Turno
from .schemas import actualizar_turno_base, turno_base, ReporteTurnosPorFecha, ReporteTurnosCancelados, ReportePersonasConCancelaciones, TurnoReporte, ReporteTurnosConfirmadosPaginado, PersonaSimple, ReporteEstadoPersonas, PersonaCompleta, TurnoRespuesta, TurnosDisponiblesRespuesta, PersonaConTurnos, persona_base, actualizar_persona_base, PersonaRespuesta
from .utils import get_db, calcular_edad, validar_formato_fecha, obtener_nombre_mes, generar_horarios_disponibles
from .reportes_pdf import (generar_pdf_turnos_por_fecha, generar_pdf_turnos_cancelados_mes, 
                       generar_pdf_turnos_por_persona, generar_pdf_personas_con_cancelaciones,
                       generar_pdf_turnos_confirmados, generar_pdf_estado_personas)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    horarios = generar_horarios_disponibles(HORARIO_INICIO, HORARIO_FIN, INTERVALO_TURNOS_MINUTOS)
    HORARIOS_DISPONIBLES.extend(horarios)
    yield

app = FastAPI(title="SL-UNLA-LAB-2025-GRUPO-03-API", lifespan=lifespan)


@app.get("/")
def inicio():
    return {"ok": True, "mensaje": "API funcionando"}

# ========================== Endpoints Personas ==========================

@app.post("/personas", response_model=PersonaRespuesta)
def crear_persona_endpoint(persona_data: persona_base, db = Depends(get_db)):
    try:
        nueva_persona = crear_persona(db, persona_data)
        
        return PersonaRespuesta(
            id=nueva_persona.id,
            nombre=nueva_persona.nombre,
            dni=nueva_persona.dni,
            email=nueva_persona.email,
            telefono=nueva_persona.telefono,
            fecha_nacimiento=nueva_persona.fecha_nacimiento,
            edad=calcular_edad(nueva_persona.fecha_nacimiento),
            habilitado=nueva_persona.habilitado
        )
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear la persona")


@app.get("/personas", response_model=List[PersonaRespuesta])
def listar_personas(db = Depends(get_db)):
    try:
        personas = obtener_todas_personas(db)
        return [
            PersonaRespuesta(
                id=persona.id,
                nombre=persona.nombre,
                dni=persona.dni,
                email=persona.email,
                telefono=persona.telefono,
                fecha_nacimiento=persona.fecha_nacimiento,
                edad=calcular_edad(persona.fecha_nacimiento),
                habilitado=persona.habilitado
            )
            for persona in personas
        ]
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error al obtener las personas")


@app.get("/personas/{id}", response_model=PersonaRespuesta)
def obtener_persona(id: int, db = Depends(get_db)):
    try:
        persona = buscar_persona(db, id)
        
        return PersonaRespuesta(
            id=persona.id,
            nombre=persona.nombre,
            dni=persona.dni,
            email=persona.email,
            telefono=persona.telefono,
            fecha_nacimiento=persona.fecha_nacimiento,
            edad=calcular_edad(persona.fecha_nacimiento),
            habilitado=persona.habilitado
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error al obtener la persona")


@app.put("/personas/{id}", response_model=PersonaRespuesta)
def actualizar_persona_endpoint(id: int, persona_data: actualizar_persona_base, db = Depends(get_db)):
    try:
        persona = actualizar_persona(db, id, persona_data)
        
        return PersonaRespuesta(
            id=persona.id,
            nombre=persona.nombre,
            dni=persona.dni,
            email=persona.email,
            telefono=persona.telefono,
            fecha_nacimiento=persona.fecha_nacimiento,
            edad=calcular_edad(persona.fecha_nacimiento),
            habilitado=persona.habilitado
        )
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al actualizar la persona")


@app.delete("/personas/{id}")
def eliminar_persona(id: int, db = Depends(get_db)):
    persona = buscar_persona(db, id)
    
    # Verificar si la persona tiene turnos asociados
    turnos_asociados = db.query(Turno).filter(Turno.persona_id == id).count()
    
    if turnos_asociados > 0:
        return {
            "ok": False, 
            "mensaje": f"No se puede eliminar la persona porque tiene {turnos_asociados} turno(s) asociado(s). Primero elimine o cancele los turnos."
        }

    db.delete(persona)
    db.commit()
    return {"ok": True, "mensaje": "Persona eliminada"}


# ========================== Endpoints Turnos ==========================

@app.post("/turnos", response_model=TurnoRespuesta)
def crear_turno_endpoint(turno_data: turno_base, db = Depends(get_db)):
    try:
        nuevo_turno = crear_turno(db, turno_data)

        return TurnoRespuesta(
            id=nuevo_turno.id,
            persona_id=nuevo_turno.persona_id,
            fecha=nuevo_turno.fecha,
            hora=nuevo_turno.hora,
            estado=nuevo_turno.estado
        )
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear el turno")

@app.get("/turnos", response_model=List[TurnoRespuesta])
def listar_turnos_endpoint(db = Depends(get_db)):
    try:
        turnos = listar_turnos(db)

        return [
            TurnoRespuesta(
                id=turno.id,
                persona_id=turno.persona_id,
                fecha=turno.fecha,
                hora=turno.hora,
                estado=turno.estado
            )
            for turno in turnos
        ]
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error al obtener los turnos")

@app.get("/turnos/{id}", response_model=TurnoRespuesta)
def obtener_turno(id: int, db = Depends(get_db)):
    try:
        turno = buscar_turno(db, id)
        return TurnoRespuesta(
            id=turno.id,
            persona_id=turno.persona_id,
            fecha=turno.fecha,
            hora=turno.hora,
            estado=turno.estado
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error al obtener el turno")

@app.put("/turnos/{id}", response_model=TurnoRespuesta)
def actualizar_turno_endpoint(id: int, turno_data: actualizar_turno_base, db = Depends(get_db)):
    try:
        turno = actualizar_turno(db, id, turno_data)
        
        return TurnoRespuesta(
            id=turno.id,
            persona_id=turno.persona_id,
            fecha=turno.fecha,
            hora=turno.hora,
            estado=turno.estado
        )
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al actualizar el turno")

@app.delete("/turnos/{id}")
def eliminar_turno_endpoint(id: int, db = Depends(get_db)):

    eliminar_turno(db, id)

    return {"ok": True, "mensaje": "Turno eliminado"}


@app.get("/turnos-disponibles", response_model=TurnosDisponiblesRespuesta)
def obtener_turnos_disponibles_endpoint(fecha: str, db = Depends(get_db)):
    try:
        validar_formato_fecha(fecha)    
        fecha_date = date.fromisoformat(fecha)
        turnos_disponibles = obtener_turnos_disponibles(db, fecha_date)

        return TurnosDisponiblesRespuesta(
            fecha=fecha_date,
            horarios_disponibles=turnos_disponibles
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error al obtener turnos disponibles") 

@app.put("/turnos/{turno_id}/cancelar", response_model=TurnoRespuesta)
def cancelar_turno_endpoint(turno_id: int, db = Depends(get_db)):
    try:
        turno_cancelado = cancelar_turno(db, turno_id)
            
        return TurnoRespuesta(
            id=turno_cancelado.id,
            persona_id=turno_cancelado.persona_id,
            fecha=turno_cancelado.fecha,
            hora=turno_cancelado.hora,
            estado=turno_cancelado.estado
        )
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al cancelar el turno")
    

@app.put("/turnos/{turno_id}/confirmar", response_model=TurnoRespuesta)
def confirmar_turno_endpoint(turno_id: int, db = Depends(get_db)):
    try:
        turno_confirmado = confirmar_turno(db, turno_id)
        
        return TurnoRespuesta(
            id=turno_confirmado.id,
            persona_id=turno_confirmado.persona_id,
            fecha=turno_confirmado.fecha,
            hora=turno_confirmado.hora,
            estado=turno_confirmado.estado
        )
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al confirmar el turno")


# ========================== Endpoints Reportes ==========================

@app.get("/reportes/turnos-por-fecha", response_model=ReporteTurnosPorFecha, response_model_exclude_none=True)
def obtener_turnos_por_fecha_endpoint(fecha: str, db = Depends(get_db)):
    try:
        validar_formato_fecha(fecha)
        fecha_date = date.fromisoformat(fecha)
        
        turnos = obtener_turnos_por_fecha(db, fecha_date)
        personas_turnos = agrupar_turnos_por_persona(turnos, incluir_fecha=False)
        
        return ReporteTurnosPorFecha(
            fecha=fecha_date,
            cantidad_turnos=len(turnos),
            cantidad_personas=len(personas_turnos),
            personas=personas_turnos
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error al generar el reporte")


@app.get("/reportes/turnos-cancelados-por-mes", response_model=ReporteTurnosCancelados, response_model_exclude_none=True)
def obtener_turnos_cancelados_mes_endpoint(db = Depends(get_db)):
    try:
        turnos_cancelados = obtener_turnos_cancelados_mes_actual(db)
        personas_turnos = agrupar_turnos_por_persona(turnos_cancelados, incluir_fecha=True)
        fecha_actual = date.today()
        
        return ReporteTurnosCancelados(
            mes=obtener_nombre_mes(fecha_actual),
            año=fecha_actual.year,
            cantidad_total=len(turnos_cancelados),
            cantidad_personas=len(personas_turnos),
            personas=personas_turnos
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error al generar el reporte")


@app.get("/reportes/turnos-por-persona", response_model=PersonaConTurnos, response_model_exclude_none=True)
def obtener_turnos_por_persona_endpoint(dni: str, db = Depends(get_db)):
    try:
        persona = buscar_persona_por_dni(db, dni)
        turnos = obtener_turnos_por_persona(db, persona.id)
        
        turnos_reporte = [
            TurnoReporte(
                id=turno.id,
                fecha=turno.fecha,
                hora=turno.hora,
                estado=turno.estado
            )
            for turno in turnos
        ]
        
        return PersonaConTurnos(
            id=persona.id,
            nombre=persona.nombre,
            dni=persona.dni,
            cantidad_turnos=len(turnos_reporte),
            turnos=turnos_reporte
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error al generar el reporte")


@app.get("/reportes/turnos-cancelados", response_model=ReportePersonasConCancelaciones, response_model_exclude_none=True)
def obtener_personas_con_cancelaciones_endpoint(min: int = MIN_CANCELADOS_DEFAULT, db = Depends(get_db)):
    try:
        if min < 1:
            raise HTTPException(
                status_code=400,
                detail="El número mínimo de turnos cancelados debe ser al menos 1"
            )
        
        turnos_con_minimo_cancelaciones = obtener_personas_con_turnos_cancelados(db, min)
        personas_con_cancelaciones = agrupar_turnos_por_persona(turnos_con_minimo_cancelaciones, incluir_fecha=True)
        
        return ReportePersonasConCancelaciones(
            min_cancelados=min,
            cantidad_personas=len(personas_con_cancelaciones),
            personas=personas_con_cancelaciones
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error al generar el reporte")


@app.get("/reportes/turnos-confirmados", response_model=ReporteTurnosConfirmadosPaginado, response_model_exclude_none=True)
def obtener_turnos_confirmados_endpoint(desde: str, hasta: str, pagina: int = 1, db = Depends(get_db)):
    try:
        validar_formato_fecha(desde)
        validar_formato_fecha(hasta)
        
        fecha_desde = date.fromisoformat(desde)
        fecha_hasta = date.fromisoformat(hasta)
        
        turnos_paginados, total_turnos_confirmados = obtener_turnos_confirmados_por_periodo(
            db, fecha_desde, fecha_hasta, pagina, LIMIT_PAGINACION_DEFAULT
        )
        
        turnos_detalle = [
            TurnoReporte(
                id=turno.id,
                fecha=turno.fecha,
                hora=turno.hora,
                estado=turno.estado,
                persona=PersonaSimple(
                    id=turno.persona.id,
                    nombre=turno.persona.nombre,
                    dni=turno.persona.dni
                )
            )
            for turno in turnos_paginados
        ]
        
        total_paginas = ceil(total_turnos_confirmados / LIMIT_PAGINACION_DEFAULT)
        
        return ReporteTurnosConfirmadosPaginado(
            desde=fecha_desde,
            hasta=fecha_hasta,
            pagina=pagina,
            total_turnos=total_turnos_confirmados,
            total_paginas=total_paginas,
            turnos=turnos_detalle
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error al generar el reporte")


@app.get("/reportes/estado-personas", response_model=ReporteEstadoPersonas)
def obtener_personas_por_estado_endpoint(habilitado: bool, db = Depends(get_db)):
    try:
        personas = obtener_personas_por_estado(db, habilitado)
        
        personas_detalle = [
            PersonaCompleta(
                id=persona.id,
                nombre=persona.nombre,
                dni=persona.dni,
                email=persona.email,
                telefono=persona.telefono,
                fecha_nacimiento=persona.fecha_nacimiento,
                edad=calcular_edad(persona.fecha_nacimiento),
                habilitado=persona.habilitado
            )
            for persona in personas
        ]
        
        return ReporteEstadoPersonas(
            habilitado=habilitado,
            cantidad_personas=len(personas_detalle),
            personas=personas_detalle
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error al generar el reporte")


# ========================== Endpoints Reportes PDF ==========================

@app.get("/reportes/pdf/turnos-por-fecha")
def obtener_pdf_turnos_por_fecha(fecha: str, db = Depends(get_db)):
    try:
        validar_formato_fecha(fecha)
        fecha_date = date.fromisoformat(fecha)
        
        turnos = obtener_turnos_por_fecha(db, fecha_date)
        
        return generar_pdf_turnos_por_fecha(fecha_date, turnos)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error al generar el PDF")


@app.get("/reportes/pdf/turnos-cancelados-por-mes")
def obtener_pdf_turnos_cancelados_mes(db = Depends(get_db)):
    try:
        turnos_cancelados = obtener_turnos_cancelados_mes_actual(db)
        fecha_actual = date.today()
        
        return generar_pdf_turnos_cancelados_mes(
            obtener_nombre_mes(fecha_actual),
            fecha_actual.year,
            turnos_cancelados
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error al generar el PDF")


@app.get("/reportes/pdf/turnos-por-persona")
def obtener_pdf_turnos_por_persona(dni: str, db = Depends(get_db)):
    try:
        persona = buscar_persona_por_dni(db, dni)
        turnos = obtener_turnos_por_persona(db, persona.id)
        
        return generar_pdf_turnos_por_persona(persona, turnos)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al generar el PDF: {str(e)}")


@app.get("/reportes/pdf/turnos-cancelados")
def obtener_pdf_personas_con_cancelaciones(min: int = MIN_CANCELADOS_DEFAULT, db = Depends(get_db)):
    try:
        if min < 1:
            raise HTTPException(
                status_code=400,
                detail="El número mínimo de turnos cancelados debe ser al menos 1"
            )
        
        turnos_con_minimo_cancelaciones = obtener_personas_con_turnos_cancelados(db, min)
        
        return generar_pdf_personas_con_cancelaciones(min, turnos_con_minimo_cancelaciones)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error al generar el PDF")


@app.get("/reportes/pdf/turnos-confirmados")
def obtener_pdf_turnos_confirmados(desde: str, hasta: str, db = Depends(get_db)):
    try:
        validar_formato_fecha(desde)
        validar_formato_fecha(hasta)
        
        fecha_desde = date.fromisoformat(desde)
        fecha_hasta = date.fromisoformat(hasta)
        
        turnos_confirmados = obtener_todos_turnos_confirmados_por_periodo(db, fecha_desde, fecha_hasta)
        
        return generar_pdf_turnos_confirmados(fecha_desde, fecha_hasta, turnos_confirmados)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error al generar el PDF")


@app.get("/reportes/pdf/estado-personas")
def obtener_pdf_estado_personas(habilitado: bool, db = Depends(get_db)):
    try:
        personas = obtener_personas_por_estado(db, habilitado)
        
        return generar_pdf_estado_personas(habilitado, personas)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error al generar el PDF")