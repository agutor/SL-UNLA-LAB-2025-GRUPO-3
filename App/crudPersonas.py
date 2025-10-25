from fastapi import HTTPException
from sqlalchemy.orm import Session
from App.schemas import persona_base, actualizar_persona_base

from .utils import validar_email, validar_fecha_nacimiento
from .models import Persona, Turno
from .config import ESTADO_CANCELADO


def crear_persona(db: Session, persona_data: persona_base):
    # Validar email
    email_normalizado = validar_email(persona_data.email)
    
    # Verificar que no exista otra persona con los mismos datos
    verificar_persona_existente(db, email_normalizado, persona_data.dni, persona_data.telefono)

    # Validar fecha de nacimiento
    validar_fecha_nacimiento(persona_data.fecha_nacimiento)

    # Crear persona
    nueva_persona = Persona(
        nombre=persona_data.nombre,
        email=email_normalizado,
        dni=persona_data.dni,
        telefono=persona_data.telefono,
        fecha_nacimiento=persona_data.fecha_nacimiento,
        habilitado=True
    )
    
    db.add(nueva_persona)
    db.commit()
    db.refresh(nueva_persona)
    
    return nueva_persona

def obtener_todas_personas(db: Session):
    return db.query(Persona).all()


def actualizar_persona(db: Session, persona_id: int, persona_data: actualizar_persona_base):
    persona = buscar_persona(db, persona_id)
    
    # Validar y actualizar email
    if persona_data.email is not None:
        email_normalizado = validar_email(persona_data.email)
        verificar_email_duplicado(db, email_normalizado, persona_id)
        persona.email = email_normalizado
    
    # Validar y actualizar DNI
    if persona_data.dni is not None:
        verificar_dni_duplicado(db, persona_data.dni, persona_id)
        persona.dni = persona_data.dni
    
    # Validar y actualizar teléfono
    if persona_data.telefono is not None:
        verificar_telefono_duplicado(db, persona_data.telefono, persona_id)
        persona.telefono = persona_data.telefono
    
    # Validar y actualizar fecha de nacimiento
    if persona_data.fecha_nacimiento is not None:
        validar_fecha_nacimiento(persona_data.fecha_nacimiento)
        persona.fecha_nacimiento = persona_data.fecha_nacimiento
    
    # Actualizar nombre
    if persona_data.nombre is not None:
        persona.nombre = persona_data.nombre
    
    db.commit()
    db.refresh(persona)
    return persona


def buscar_persona(db: Session, persona_id: int):

    persona = db.query(Persona).filter(Persona.id == persona_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

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


def verificar_persona_existente(db: Session, email: str, dni: str, telefono: str):
    persona_existente = db.query(Persona).filter(
        (Persona.email == email) | 
        (Persona.dni == dni) | 
        (Persona.telefono == telefono)
    ).first()
    
    if persona_existente:
        raise HTTPException(status_code=400, detail="Ya existe una persona con este email, DNI o telefono")


def verificar_email_duplicado(db: Session, email: str, persona_id: int):
    persona_existente = db.query(Persona).filter(
        Persona.id != persona_id,
        Persona.email == email
    ).first()
    
    if persona_existente:
        raise HTTPException(status_code=400, detail="Ya existe otra persona con este email")


def verificar_dni_duplicado(db: Session, dni: str, persona_id: int):
    persona_existente = db.query(Persona).filter(
        Persona.id != persona_id,
        Persona.dni == dni
    ).first()
    
    if persona_existente:
        raise HTTPException(status_code=400, detail="Ya existe otra persona con este DNI")


def verificar_telefono_duplicado(db: Session, telefono: str, persona_id: int):
    persona_existente = db.query(Persona).filter(
        Persona.id != persona_id,
        Persona.telefono == telefono
    ).first()
    
    if persona_existente:
        raise HTTPException(status_code=400, detail="Ya existe otra persona con este teléfono")


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
