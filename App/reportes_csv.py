from datetime import date
from typing import List
from io import StringIO

import pandas as pd
from fastapi.responses import StreamingResponse

from .utils import calcular_edad
from .models import Persona, Turno
from .config import (
    HEADER_DNI, HEADER_EDAD, HEADER_EMAIL, HEADER_ESTADO, 
    HEADER_FECHA, HEADER_HORA, HEADER_ID, HEADER_ID_PERSONA, 
    HEADER_NOMBRE, HEADER_TELEFONO,
    TEXTO_DESHABILITADO, TEXTO_HABILITADO
)


# ==================== Utilidades ====================

def crear_fila_turno(turno: Turno, **campos_extra) -> dict:
    fila = {
        HEADER_ID: turno.id,
        HEADER_ID_PERSONA: turno.persona_id,
        HEADER_NOMBRE: turno.persona.nombre,
        HEADER_DNI: turno.persona.dni,
        HEADER_FECHA: str(turno.fecha),
        HEADER_HORA: str(turno.hora),
        HEADER_ESTADO: turno.estado
    }
    fila.update(campos_extra)
    return fila


def crear_fila_persona(persona: Persona, **campos_extra) -> dict:
    fila = {
        HEADER_ID: persona.id,
        HEADER_NOMBRE: persona.nombre,
        HEADER_DNI: persona.dni,
        HEADER_EMAIL: persona.email,
        HEADER_TELEFONO: persona.telefono,
        HEADER_EDAD: calcular_edad(persona.fecha_nacimiento),
        HEADER_ESTADO: TEXTO_HABILITADO if persona.habilitado else TEXTO_DESHABILITADO
    }
    fila.update(campos_extra)
    return fila


def finalizar_csv(df: pd.DataFrame, filename: str) -> StreamingResponse:
    buffer = StringIO()
    df.to_csv(buffer, index=False, encoding='utf-8', sep=',', quotechar='"', quoting=1)
    buffer.seek(0)
    return StreamingResponse(
        [buffer.getvalue()],
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# ==================== Generadores de CSV ====================

def generar_csv_turnos_por_fecha(fecha: date, turnos: List[Turno]) -> StreamingResponse:
    reporte = [crear_fila_turno(turno) for turno in turnos]
    df = pd.DataFrame(reporte)
    return finalizar_csv(df, f"turnos_{fecha}.csv")


def generar_csv_turnos_cancelados_mes(mes: str, anio: int, turnos: List[Turno]) -> StreamingResponse:
    reporte = [crear_fila_turno(turno) for turno in turnos]
    df = pd.DataFrame(reporte)
    return finalizar_csv(df, f"cancelados_{mes}_{anio}.csv")


def generar_csv_turnos_por_persona(persona: Persona, turnos: List[Turno]) -> StreamingResponse:
    reporte = [
        {HEADER_DNI: persona.dni, HEADER_NOMBRE: persona.nombre, HEADER_ID: turno.id,
         HEADER_FECHA: str(turno.fecha), HEADER_HORA: str(turno.hora), HEADER_ESTADO: turno.estado}
        for turno in turnos
    ]
    df = pd.DataFrame(reporte)
    return finalizar_csv(df, f"historial_{persona.dni}.csv")


def generar_csv_personas_con_cancelaciones(min_cancelados: int, turnos: List[Turno]) -> StreamingResponse:
    # Agrupar turnos por persona
    diccionario_personas = {}
    for turno in turnos:
        if turno.persona_id not in diccionario_personas:
            diccionario_personas[turno.persona_id] = {'persona': turno.persona, 'turnos': []}
        diccionario_personas[turno.persona_id]['turnos'].append(turno)
    
    # Crear datos para el DataFrame
    reporte = [
        crear_fila_turno(turno, **{
            HEADER_ID_PERSONA: persona_data['persona'].id,
            'Cantidad Cancelados': len(persona_data['turnos']),
            'ID Turno': turno.id
        })
        for persona_data in diccionario_personas.values()
        for turno in persona_data['turnos']
    ]
    df = pd.DataFrame(reporte)
    return finalizar_csv(df, f"cancelaciones_min_{min_cancelados}.csv")


def generar_csv_turnos_confirmados(desde: date, hasta: date, turnos: List[Turno]) -> StreamingResponse:
    reporte = [crear_fila_turno(turno) for turno in turnos]
    df = pd.DataFrame(reporte)
    return finalizar_csv(df, f"confirmados_{desde}_a_{hasta}.csv")


def generar_csv_estado_personas(habilitado: bool, personas: List[Persona]) -> StreamingResponse:
    estado_texto = "habilitadas" if habilitado else "deshabilitadas"
    reporte = [crear_fila_persona(persona) for persona in personas]
    df = pd.DataFrame(reporte)
    return finalizar_csv(df, f"personas_{estado_texto}.csv")
