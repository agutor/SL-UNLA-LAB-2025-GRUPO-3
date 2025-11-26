from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from App.schemas import persona_base, actualizar_persona_base

from .utils import validar_fecha_nacimiento
from .models import Persona, Turno
from .config import ESTADO_CANCELADO


def crear_persona(db: Session, persona_data: persona_base):
    # Validar fecha de nacimiento
    validar_fecha_nacimiento(persona_data.fecha_nacimiento)

    # Crear persona
    nueva_persona = Persona(
        nombre=persona_data.nombre,
        email=persona_data.email,
        dni=persona_data.dni,
        telefono=persona_data.telefono,
        fecha_nacimiento=persona_data.fecha_nacimiento,
        habilitado=True
    )
    
    try:
        db.add(nueva_persona)
        db.commit()
        db.refresh(nueva_persona)
    except IntegrityError as error:
        db.rollback()
        # Determinar qué campo causó el error
        error_msg = str(error.orig).lower()
        if 'email' in error_msg:
            raise HTTPException(status_code=400, detail="Ya existe una persona con este email")
        elif 'dni' in error_msg:
            raise HTTPException(status_code=400, detail="Ya existe una persona con este DNI")
        elif 'telefono' in error_msg or 'teléfono' in error_msg:
            raise HTTPException(status_code=400, detail="Ya existe una persona con este teléfono")
        else:
            raise HTTPException(status_code=400, detail="Ya existe una persona con este email, DNI o teléfono")
    
    return nueva_persona

def obtener_todas_personas(db: Session):
    return db.query(Persona).all()


def actualizar_persona(db: Session, persona_id: int, persona_data: actualizar_persona_base):
    persona = buscar_persona(db, persona_id)
    
    # Validar y actualizar email
    if persona_data.email is not None:
        persona.email = persona_data.email
    
    # Actualizar DNI
    if persona_data.dni is not None:
        persona.dni = persona_data.dni
    
    # Actualizar teléfono
    if persona_data.telefono is not None:
        persona.telefono = persona_data.telefono
    
    # Validar y actualizar fecha de nacimiento
    if persona_data.fecha_nacimiento is not None:
        validar_fecha_nacimiento(persona_data.fecha_nacimiento)
        persona.fecha_nacimiento = persona_data.fecha_nacimiento
    
    # Actualizar nombre
    if persona_data.nombre is not None:
        persona.nombre = persona_data.nombre
    
    try:
        db.commit()
        db.refresh(persona)
    except IntegrityError as error:
        db.rollback()
        # Determinar qué campo causó el error
        error_msg = str(error.orig).lower()
        if 'email' in error_msg:
            raise HTTPException(status_code=400, detail="Ya existe otra persona con este email")
        elif 'dni' in error_msg:
            raise HTTPException(status_code=400, detail="Ya existe otra persona con este DNI")
        elif 'telefono' in error_msg or 'teléfono' in error_msg:
            raise HTTPException(status_code=400, detail="Ya existe otra persona con este teléfono")
        else:
            raise HTTPException(status_code=400, detail="Ya existe otra persona con estos datos")
    
    return persona


def buscar_persona(db: Session, persona_id: int):

    persona = db.query(Persona).filter(Persona.id == persona_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    return persona


def buscar_persona_por_dni(db: Session, dni: str):

    persona = db.query(Persona).filter(Persona.dni == dni).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada con ese DNI")

    return persona


def validar_persona_habilitada(db: Session, persona_id: int):

    persona = buscar_persona(db, persona_id)   
    if not persona.habilitado:
        raise HTTPException(status_code=400, detail="La persona está deshabilitada")

def cambiar_estado_persona(db: Session, persona_id: int):

    persona = buscar_persona(db, persona_id)
    
    # si esta habilitada la deshabilita, y viceversa
    persona.habilitado = not persona.habilitado
    
    db.commit()
    db.refresh(persona)


def obtener_personas_con_turnos_cancelados(db: Session, min_cancelados: int):
    
    personas = db.query(Persona).all()
    
    todos_turnos_cancelados = []
    
    for persona in personas:
        turnos_cancelados = db.query(Turno).filter(
            Turno.persona_id == persona.id,
            Turno.estado == ESTADO_CANCELADO
        ).all()
        
        #Si la persona tiene al menos min_cancelados se agregan a la lista
        if len(turnos_cancelados) >= min_cancelados:
            todos_turnos_cancelados.extend(turnos_cancelados)
    
    return todos_turnos_cancelados


def obtener_personas_por_estado(db: Session, habilitado: bool):
    return db.query(Persona).filter(Persona.habilitado == habilitado).all()