from datetime import date, time
from pydantic import BaseModel
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


# Schemas para reportes
class TurnoReporte(BaseModel):
    
    id: int
    hora: str
    estado: str
    fecha: Optional[str] = None


class PersonaConTurnos(BaseModel):
    nombre: str
    dni: str
    cantidad_turnos: int
    turnos: List[TurnoReporte]


class ReporteTurnosPorFecha(BaseModel):
    fecha: str
    cantidad_turnos: int
    cantidad_personas: int
    personas: List[PersonaConTurnos]


class ReporteTurnosCancelados(BaseModel):
    mes: str
    año: int
    cantidad_total: int
    cantidad_personas: int
    personas: List[PersonaConTurnos]

