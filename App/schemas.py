from datetime import date, time
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List

from .config import ESTADO_PENDIENTE


# Validación de Turnos (Ingreso de datos)
class turno_base(BaseModel):
    persona_id: int
    fecha: date
    hora: time
    estado: Optional[str] = ESTADO_PENDIENTE


class actualizar_turno_base(BaseModel):
    fecha: Optional[date] = None
    hora: Optional[time] = None
    estado: Optional[str] = None


# Validación de Personas (Ingreso de datos)
class persona_base(BaseModel):
    nombre: str
    dni: str
    email: EmailStr
    telefono: str
    fecha_nacimiento: date
    
    @field_validator('dni')
    @classmethod
    def validar_dni(cls, valor):
        if not valor:
            raise ValueError('El DNI no puede estar vacío')
        if not valor.isdigit():
            raise ValueError('El DNI debe contener solo números')
        if len(valor) < 7 or len(valor) > 8:
            raise ValueError('El DNI debe tener entre 7 y 8 dígitos')
        return valor
    
    @field_validator('telefono')
    @classmethod
    def validar_telefono(cls, valor):
        if not valor:
            raise ValueError('El teléfono no puede estar vacío')
        if not valor.isdigit():
            raise ValueError('El teléfono debe contener solo números')
        if len(valor) < 10:
            raise ValueError('El teléfono debe tener al menos 10 dígitos')
        return valor


class actualizar_persona_base(BaseModel):
    nombre: Optional[str] = None
    dni: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    
    @field_validator('dni')
    @classmethod
    def validar_dni(cls, valor):
        if valor is not None:
            if not valor:
                raise ValueError('El DNI no puede estar vacío')
            if not valor.isdigit():
                raise ValueError('El DNI debe contener solo números')
            if len(valor) < 7 or len(valor) > 8:
                raise ValueError('El DNI debe tener entre 7 y 8 dígitos')
        return valor
    
    @field_validator('telefono')
    @classmethod
    def validar_telefono(cls, valor):
        if valor is not None:
            if not valor:
                raise ValueError('El teléfono no puede estar vacío')
            if not valor.isdigit():
                raise ValueError('El teléfono debe contener solo números')
            if len(valor) < 10:
                raise ValueError('El teléfono debe tener al menos 10 dígitos')
        return valor


# Schemas de respuesta para turnos
class TurnoRespuesta(BaseModel):
    id: int
    persona_id: int
    fecha: date
    hora: time
    estado: str


class TurnosDisponiblesRespuesta(BaseModel):
    fecha: date
    horarios_disponibles: List[time]


# Schemas de respuesta para personas
class PersonaRespuesta(BaseModel):
    id: int
    nombre: str
    dni: str
    email: str
    telefono: str
    fecha_nacimiento: date
    edad: int
    habilitado: bool


# Schemas para reportes
class PersonaSimple(BaseModel):
    id: int
    nombre: str
    dni: str


class TurnoReporte(BaseModel):
    id: int
    hora: time
    estado: str
    fecha: Optional[date] = None
    persona: Optional[PersonaSimple] = None


class PersonaConTurnos(BaseModel):
    id: int
    nombre: str
    dni: str
    cantidad_turnos: int
    turnos: List[TurnoReporte]


class ReporteTurnosPorFecha(BaseModel):
    fecha: date
    cantidad_turnos: int
    cantidad_personas: int
    personas: List[PersonaConTurnos]


class ReporteTurnosCancelados(BaseModel):
    mes: str
    año: int
    cantidad_total: int
    cantidad_personas: int
    personas: List[PersonaConTurnos]


class ReportePersonasConCancelaciones(BaseModel):
    min_cancelados: int
    cantidad_personas: int
    personas: List[PersonaConTurnos]


class ReporteTurnosConfirmadosPaginado(BaseModel):
    desde: date
    hasta: date
    pagina: int
    total_turnos: int
    total_paginas: int
    turnos: List[TurnoReporte]


class PersonaCompleta(BaseModel):
    id: int
    nombre: str
    dni: str
    email: str
    telefono: str
    fecha_nacimiento: date
    edad: int
    habilitado: bool


class ReporteEstadoPersonas(BaseModel):
    habilitado: bool
    cantidad_personas: int
    personas: List[PersonaCompleta]
