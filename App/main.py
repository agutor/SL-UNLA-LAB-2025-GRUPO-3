from datetime import date
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends

from .config import LIMIT_PAGINACION_DEFAULT
from .crudPersonas import obtener_todas_personas, crear_persona, actualizar_persona, buscar_persona
from .crudTurnos import (cancelar_turno, confirmar_turno, crear_turno, eliminar_turno, listar_turnos, 
                        actualizar_turno, buscar_turno, obtener_turnos_disponibles, obtener_turnos_por_fecha,
                        agrupar_turnos_por_persona, obtener_turnos_cancelados_mes_actual, obtener_turnos_por_dni)
from .database import Base, engine
from .models import Turno
from .schemas import actualizar_turno_base, turno_base, ReporteTurnosPorFecha, ReporteTurnosCancelados
from .utils import get_db, calcular_edad, validar_formato_fecha, obtener_nombre_mes


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="SL-UNLA-LAB-2025-GRUPO-03-API", lifespan=lifespan)


@app.get("/")
def inicio():
    return {"ok": True, "mensaje": "API funcionando"}


# Endpoints Turnos
@app.post("/turnos")
def crear_turno_endpoint(turno_data: turno_base, db = Depends(get_db)):

    nuevo_turno = crear_turno(db, turno_data)

    return {
        "id": nuevo_turno.id,
        "persona_id": nuevo_turno.persona_id,
        "fecha": str(nuevo_turno.fecha),
        "hora": str(nuevo_turno.hora),
        "estado": nuevo_turno.estado
    }

@app.get("/turnos")
def listar_turnos_endpoint(db = Depends(get_db)):

    turnos = listar_turnos(db)

    return [
        {
            "id": t.id,
            "persona_id": t.persona_id,
            "fecha": str(t.fecha),
            "hora": str(t.hora),
            "estado": t.estado
        }
        for t in turnos
    ]

@app.get("/turnos/{id}")
def obtener_turno(id: int, db = Depends(get_db)):
    turno = buscar_turno(db, id)
    return {
        "id": turno.id,
        "persona_id": turno.persona_id,
        "fecha": str(turno.fecha),
        "hora": str(turno.hora),
        "estado": turno.estado
    }

@app.put("/turnos/{id}")
def actualizar_turno_endpoint(id: int, turno_data: actualizar_turno_base, db = Depends(get_db)):
    
    turno = actualizar_turno(db, id, turno_data)
    
    return {
        "id": turno.id,
        "persona_id": turno.persona_id,
        "fecha": str(turno.fecha),
        "hora": str(turno.hora),
        "estado": turno.estado
    }

@app.delete("/turnos/{id}")

def eliminar_turno_endpoint(id: int, db = Depends(get_db)):

    eliminar_turno(db, id)

    return {"ok": True, "mensaje": "Turno eliminado"}



# Endpoint - Cálculo de turnos disponibles
@app.get("/turnos-disponibles")
def obtener_turnos_disponibles_endpoint(fecha: str):
    db = next(get_db())

    validar_formato_fecha(fecha)    
    turnos_disponibles = obtener_turnos_disponibles(db, date.fromisoformat(fecha))

    #respuesta del Endpoint
    return {
        "fecha": fecha,
        "horarios_disponibles": turnos_disponibles
    } 

@app.put("/turnos/{turno_id}/cancelar")
def cancelar_turno_endpoint(turno_id: int, db = Depends(get_db)):
    
    turno_cancelado = cancelar_turno(db, turno_id)
        
    return {
        "id": turno_cancelado.id,
        "fecha": turno_cancelado.fecha.strftime("%Y-%m-%d"),
        "hora": turno_cancelado.hora.strftime("%H:%M"),
        "estado": turno_cancelado.estado
    }
    

@app.put("/turnos/{turno_id}/confirmar")
def confirmar_turno_endpoint(turno_id: int, db = Depends(get_db)):
        
    turno_confirmado = confirmar_turno(db, turno_id)
    
    return {
        "id": turno_confirmado.id,
        "fecha": turno_confirmado.fecha.strftime("%Y-%m-%d"),
        "hora": turno_confirmado.hora.strftime("%H:%M"),
        "estado": turno_confirmado.estado
    }


# Endpoints Reportes

@app.get("/reportes/turnos-por-fecha", response_model=ReporteTurnosPorFecha, response_model_exclude_none=True)
def obtener_turnos_por_fecha_endpoint(fecha: str, db = Depends(get_db)):
    
    validar_formato_fecha(fecha)
    fecha_date = date.fromisoformat(fecha)
    
    turnos = obtener_turnos_por_fecha(db, fecha_date)
    personas_turnos = agrupar_turnos_por_persona(turnos, incluir_fecha=False)
    
    return ReporteTurnosPorFecha(
        fecha=fecha,
        cantidad_turnos=len(turnos),
        cantidad_personas=len(personas_turnos),
        personas=personas_turnos
    )


@app.get("/reportes/turnos-cancelados-por-mes", response_model=ReporteTurnosCancelados)
def obtener_turnos_cancelados_mes_endpoint(db = Depends(get_db)):
    
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


@app.get("/reportes/turnos-por-persona")
def obtener_turnos_por_persona_endpoint(dni: str, db = Depends(get_db)):
    
    turnos = obtener_turnos_por_dni(db, dni)
    personas_turnos = agrupar_turnos_por_persona(turnos, incluir_fecha=True)
    
    return personas_turnos[0]


# Endpoints Personas

@app.post("/personas")
#el async def es necesario por que uso el await mas abajo
async def crear_persona_endpoint(request: Request):
    datos = await request.json()
    db = next(get_db())

    nueva_persona = crear_persona(db, datos)
    
    edad = calcular_edad(nueva_persona.fecha_nacimiento)
    
    return {
        "id": nueva_persona.id,
        "nombre": nueva_persona.nombre,
        "email": nueva_persona.email,
        "dni": nueva_persona.dni,
        "telefono": nueva_persona.telefono,
        "fecha_nacimiento": str(nueva_persona.fecha_nacimiento),
        "edad": edad,
        "habilitado": nueva_persona.habilitado
    }


@app.get("/personas")
def listar_personas():
    db = next(get_db())
    personas = obtener_todas_personas(db)
    return [
        {
            "id": p.id,
            "nombre": p.nombre,
            "email": p.email,
            "dni": p.dni,
            "telefono": p.telefono,
            "fecha_nacimiento": str(p.fecha_nacimiento),
            "edad": calcular_edad(p.fecha_nacimiento),
            "habilitado": p.habilitado
        }
        for p in personas
    ]


@app.get("/personas/{id}")
def obtener_persona(id: int):
    db = next(get_db())
    persona = buscar_persona(db, id)
    
    edad = calcular_edad(persona.fecha_nacimiento)
    
    return {
        "id": persona.id,
        "nombre": persona.nombre,
        "email": persona.email,
        "dni": persona.dni,
        "telefono": persona.telefono,
        "fecha_nacimiento": str(persona.fecha_nacimiento),
        "edad": edad,
        "habilitado": persona.habilitado
    }


@app.put("/personas/{id}")
async def actualizar_persona_endpoint(id: int, request: Request):
    datos = await request.json()
    db = next(get_db())
    persona = actualizar_persona(db, id, datos)
    edad = calcular_edad(persona.fecha_nacimiento)
    
    return {
        "id": persona.id,
        "nombre": persona.nombre,
        "email": persona.email,
        "dni": persona.dni,
        "telefono": persona.telefono,
        "fecha_nacimiento": str(persona.fecha_nacimiento),
        "edad": edad,
        "habilitado": persona.habilitado
    }


@app.delete("/personas/{id}")
def eliminar_persona(id: int):
    db = next(get_db())
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

