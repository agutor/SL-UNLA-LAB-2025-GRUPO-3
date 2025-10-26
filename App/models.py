from sqlalchemy import Integer, String, Boolean, Date, Time, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, time

from .database import Base


class Persona(Base):
    __tablename__ = "personas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    dni: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    telefono: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    fecha_nacimiento: Mapped[date] = mapped_column(Date, nullable=False)
    habilitado: Mapped[bool] = mapped_column(Boolean, default=True)
    
    turnos = relationship("Turno", back_populates="persona")

class Turno(Base):
    __tablename__ = "turnos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    persona_id: Mapped[int] = mapped_column(Integer, ForeignKey("personas.id"), nullable=False)
    persona = relationship("Persona", back_populates="turnos")
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    hora: Mapped[time] = mapped_column(Time, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="pendiente")

