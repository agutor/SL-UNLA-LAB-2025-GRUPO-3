from datetime import date, time, timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session
from App.schemas import turno_base, PersonaConTurnos, TurnoReporte

from .utils import validar_fecha_pasada, validar_turno_modificable, validar_rango_fechas
from .crudPersonas import validar_persona_habilitada, buscar_persona, cambiar_estado_persona
from .models import Turno
from .config import HORARIO_INICIO, HORARIO_FIN, INTERVALO_TURNOS_MINUTOS, MAX_TURNOS_CANCELADOS, DIAS_LIMITE_CANCELACIONES, ESTADO_PENDIENTE, ESTADO_CONFIRMADO, ESTADO_CANCELADO, ESTADO_ASISTIDO, LIMIT_PAGINACION_DEFAULT, HORARIOS_DISPONIBLES


def crear_turno(db: Session, turno_data: turno_base):

    persona_id = turno_data.persona_id
    
    validar_persona_habilitada(db, persona_id)

    turnos_cancelados = validar_turnos_cancelados(db, persona_id)
    if turnos_cancelados:
        raise HTTPException(
            status_code=400, 
            detail=f"No se puede asignar turno: la persona tiene {MAX_TURNOS_CANCELADOS} o más turnos cancelados en los últimos 6 meses."
        )
    
    validar_fecha_pasada(turno_data.fecha)
    
    # Validar que el horario esté dentro del rango de atención
    hora_solicitada = turno_data.hora
    hora_inicio = time.fromisoformat(HORARIO_INICIO)
    hora_fin = time.fromisoformat(HORARIO_FIN)
    
    if hora_solicitada < hora_inicio or hora_solicitada > hora_fin:
        raise HTTPException(
            status_code=400, 
            detail=f"El horario {hora_solicitada.strftime('%H:%M')} está fuera del horario de atención ({HORARIO_INICIO} - {HORARIO_FIN})"
        )
    
    # Validar que el horario sea un múltiplo del intervalo de turnos
    minutos_totales = hora_solicitada.hour * 60 + hora_solicitada.minute
    minutos_inicio = hora_inicio.hour * 60 + hora_inicio.minute
    diferencia_minutos = minutos_totales - minutos_inicio
    
    if diferencia_minutos % INTERVALO_TURNOS_MINUTOS != 0:
        raise HTTPException(
            status_code=400, 
            detail=f"El horario debe ser cada {INTERVALO_TURNOS_MINUTOS} minutos. Horarios válidos: 08:00, 08:30, 09:00, etc."
        )

    # Verificar que el horario esté disponible (no ocupado)
    horarios_disponibles = obtener_turnos_disponibles(db, turno_data.fecha)
    
    if hora_solicitada not in horarios_disponibles:
        raise HTTPException(
            status_code=400, 
            detail=f"El horario {hora_solicitada.strftime('%H:%M')} del día {turno_data.fecha} ya está ocupado"
        )
    
    
    nuevo_turno = Turno(
        persona_id=persona_id,
        fecha=turno_data.fecha,
        hora=turno_data.hora,
        estado=turno_data.estado
    )
    
    db.add(nuevo_turno)
    db.commit()
    db.refresh(nuevo_turno)
    
    return nuevo_turno

def listar_turnos(db: Session):
    return db.query(Turno).all()

def actualizar_turno(db: Session, turno_id: int, turno_data: turno_base):

    turno = buscar_turno(db, turno_id)
    
    validar_turno_modificable(turno)

    if turno_data.fecha is not None:
        validar_fecha_pasada(turno_data.fecha)
        turno.fecha = turno_data.fecha
    
    if turno_data.hora is not None:
        turno.hora = turno_data.hora
    
    if turno_data.estado is not None:
        turno.estado = turno_data.estado
    
    db.commit()
    db.refresh(turno)
    
    return turno

def eliminar_turno(db: Session, turno_id: int):

    turno = buscar_turno(db, turno_id)
    db.delete(turno)
    db.commit()


def buscar_turno(db: Session, turno_id: int):

    turno = db.query(Turno).filter(Turno.id == turno_id).first()
    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")

    return turno


def cancelar_turno(db: Session, turno_id: int):
    turno = buscar_turno(db, turno_id)
    
    validar_turno_modificable(turno)
    
    validar_fecha_pasada(turno.fecha)
    
    turno.estado = ESTADO_CANCELADO
    db.commit()
    db.refresh(turno)

    return turno
    

def contar_turnos_cancelados(db: Session, persona_id: int, dias_limite: int):

    fecha_actual = date.today()
    fecha_limite = fecha_actual - timedelta(days=dias_limite)

    turnos_cancelados = db.query(Turno).filter(
        Turno.persona_id == persona_id,
        Turno.estado == ESTADO_CANCELADO,
        Turno.fecha >= fecha_limite
    ).count()
    
    return turnos_cancelados

def obtener_turnos_por_fecha(db: Session, fecha: date):
    return db.query(Turno).filter(Turno.fecha == fecha).all()


def obtener_turnos_por_persona(db: Session, persona_id: int):
    return db.query(Turno).filter(Turno.persona_id == persona_id).all()


def obtener_turnos_disponibles(db: Session, fecha: date):
    
    validar_fecha_pasada(fecha)
    
    turnos_ocupados = db.query(Turno.hora).filter(
        Turno.fecha == fecha,
        Turno.estado != ESTADO_CANCELADO
    ).all()
    
    horas_ocupadas = {turno_ocupado.hora for turno_ocupado in turnos_ocupados}
    
    return [
        hora 
        for hora in HORARIOS_DISPONIBLES 
        if hora not in horas_ocupadas
    ]


def validar_turnos_cancelados(db: Session, persona_id: int):
    
    turnos_cancelados = contar_turnos_cancelados(db, persona_id, DIAS_LIMITE_CANCELACIONES)

    # Deshabilitar la persona si tiene 5 o más cancelaciones
    if turnos_cancelados >= MAX_TURNOS_CANCELADOS:
        persona = buscar_persona(db, persona_id)
        if persona and persona.habilitado:
            cambiar_estado_persona(db, persona_id)
            return True

    return False


def confirmar_turno(db: Session, turno_id: int):
    
    turno = buscar_turno(db, turno_id)
    
    validar_turno_modificable(turno)
    
    if turno.estado != ESTADO_PENDIENTE:
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden confirmar turnos pendientes"
        )
    
    turno.estado = ESTADO_CONFIRMADO
    db.commit()
    db.refresh(turno)
    
    return turno


def marcar_asistencia_turno(db: Session, turno_id: int):
    
    turno = buscar_turno(db, turno_id)

    if turno.estado != ESTADO_CONFIRMADO:
        raise HTTPException(
            status_code=400,
            detail="Solo se puede marcar asistencia en turnos confirmados"
        )
    
    turno.estado = ESTADO_ASISTIDO
    db.commit()
    db.refresh(turno)
    
    return turno


def agrupar_turnos_por_persona(turnos, incluir_fecha=False):
    
    diccionario_personas = {}
    
    for turno in turnos:
        persona_id = turno.persona_id
        
        if persona_id not in diccionario_personas:
            diccionario_personas[persona_id] = PersonaConTurnos(
                id=turno.persona.id,
                nombre=turno.persona.nombre,
                dni=turno.persona.dni,
                cantidad_turnos=0,
                turnos=[]
            )
        
        turno_reporte = TurnoReporte(
            id=turno.id,
            hora=turno.hora,
            estado=turno.estado
        )
        
        if incluir_fecha:
            turno_reporte.fecha = turno.fecha
        
        diccionario_personas[persona_id].turnos.append(turno_reporte)
    
    for persona in diccionario_personas.values():
        persona.cantidad_turnos = len(persona.turnos)
    
    return list(diccionario_personas.values())


def obtener_turnos_cancelados_mes_actual(db: Session):
    
    fecha_actual = date.today()
    primer_dia_mes = date(fecha_actual.year, fecha_actual.month, 1)
    
    # Calculo ultimo dia de mes, if necesario para diciembre - enero
    if fecha_actual.month == 12:
        ultimo_dia_mes = date(fecha_actual.year + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia_mes = date(fecha_actual.year, fecha_actual.month + 1, 1) - timedelta(days=1)
    
    turnos = db.query(Turno).filter(
        Turno.estado == ESTADO_CANCELADO,
        Turno.fecha >= primer_dia_mes,
        Turno.fecha <= ultimo_dia_mes
    ).all()
    
    return turnos




def obtener_turnos_confirmados_por_periodo(db: Session, fecha_desde: date, fecha_hasta: date, pagina: int = 1, limite: int = LIMIT_PAGINACION_DEFAULT):
    
    validar_rango_fechas(fecha_desde, fecha_hasta)
    
    turnos_confirmados_query = db.query(Turno).filter(
        Turno.estado == ESTADO_CONFIRMADO,
        Turno.fecha >= fecha_desde,
        Turno.fecha <= fecha_hasta
    )
    
    #Se cuenta el total de turnos confirmados para calcular la paginacion
    total_turnos_confirmados = turnos_confirmados_query.count()
    
    offset = (pagina - 1) * limite
    turnos_paginados = turnos_confirmados_query.offset(offset).limit(limite).all()
    
    return turnos_paginados, total_turnos_confirmados


def obtener_todos_turnos_confirmados_por_periodo(db: Session, fecha_desde: date, fecha_hasta: date):
    validar_rango_fechas(fecha_desde, fecha_hasta)
    
    return db.query(Turno).filter(
        Turno.estado == ESTADO_CONFIRMADO,
        Turno.fecha >= fecha_desde,
        Turno.fecha <= fecha_hasta
    ).all()
