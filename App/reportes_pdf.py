from datetime import date, datetime
from typing import List
from io import BytesIO
from decimal import Decimal

from borb.pdf import Document, Page, PageLayout, SingleColumnLayout, Paragraph, PDF, FixedColumnWidthTable, LayoutElement, HexColor
from fastapi.responses import StreamingResponse

from .utils import calcular_edad

from .models import Persona, Turno
from .config import (
    ESTADO_ASISTIDO, ESTADO_CANCELADO, ESTADO_CONFIRMADO,
    FORMATO_FECHA_GENERACION, HEADER_DNI, HEADER_EDAD, HEADER_EMAIL, HEADER_ESTADO, 
    HEADER_FECHA, HEADER_HORA, HEADER_ID, HEADER_ID_PERSONA, HEADER_NOMBRE, HEADER_PACIENTE,
    HEADER_TELEFONO, MSG_SIN_TURNOS_CANCELADOS, MSG_SIN_TURNOS_CONFIRMADOS,
    MSG_SIN_TURNOS_FECHA, MSG_SIN_TURNOS_PERSONA, TITULO_SISTEMA,
    PDF_BORDER_DELGADO, PDF_BORDER_GRUESO, PDF_BORDER_MEDIO,
    PDF_COLOR_ALERTA, PDF_COLOR_ASISTIDO, PDF_COLOR_CANCELADO, PDF_COLOR_CONFIRMADO,
    PDF_COLOR_DESHABILITADO, PDF_COLOR_HABILITADO, PDF_COLOR_PENDIENTE, PDF_COLOR_PRIMARIO,
    PDF_COLOR_SECUNDARIO, PDF_COLOR_TEXTO_GRIS, PDF_COLOR_TEXTO_GRIS_CLARO,
    PDF_FONT_BOLD, PDF_FONTSIZE_DATO, PDF_FONTSIZE_NORMAL, PDF_FONTSIZE_PEQUENO,
    PDF_FONTSIZE_SUBTITULO, PDF_FONTSIZE_TITULO, PDF_PADDING_GRANDE, PDF_PADDING_MEDIO,
    PDF_PADDING_MUY_GRANDE, PDF_PADDING_NORMAL, PDF_PADDING_PEQUENO
)


# ==================== Utilidades ====================

def obtener_color_estado(estado: str) -> HexColor:
    colores = {
        'pendiente': HexColor(PDF_COLOR_PENDIENTE),
        'confirmado': HexColor(PDF_COLOR_CONFIRMADO),
        'cancelado': HexColor(PDF_COLOR_CANCELADO),
        'asistido': HexColor(PDF_COLOR_ASISTIDO)
    }
    return colores.get(estado.lower(), HexColor(PDF_COLOR_TEXTO_GRIS_CLARO))


def crear_paragraph(texto: str, **propiedades) -> Paragraph:
    defaults = {
        'font_size': PDF_FONTSIZE_DATO,
        'padding_top': Decimal(PDF_PADDING_PEQUENO),
        'padding_bottom': Decimal(PDF_PADDING_PEQUENO),
        'padding_left': Decimal(PDF_PADDING_PEQUENO),
        'padding_right': Decimal(PDF_PADDING_PEQUENO)
    }
    defaults.update(propiedades)
    return Paragraph(texto, **defaults)


def crear_celda_header(texto: str) -> Paragraph:
    return crear_paragraph(
        texto, 
        font=PDF_FONT_BOLD, 
        font_color=HexColor(PDF_COLOR_PRIMARIO),
        padding_top=Decimal(PDF_PADDING_NORMAL), 
        padding_bottom=Decimal(PDF_PADDING_NORMAL)
    )


def crear_celda_dato(texto: str, font_size=None, padding_extra=False) -> Paragraph:
    propiedades = {'font_size': font_size or PDF_FONTSIZE_DATO}
    if padding_extra:
        propiedades.update({
            'padding_top': Decimal(PDF_PADDING_GRANDE), 
            'padding_bottom': Decimal(PDF_PADDING_GRANDE),
            'vertical_alignment': LayoutElement.VerticalAlignment.MIDDLE
        })
    return crear_paragraph(texto, **propiedades)


def crear_celda_estado(estado: str, padding_extra=False) -> Paragraph:
    propiedades = {'font': PDF_FONT_BOLD, 'font_color': obtener_color_estado(estado)}
    if padding_extra:
        propiedades.update({
            'padding_top': Decimal(PDF_PADDING_GRANDE), 
            'padding_bottom': Decimal(PDF_PADDING_GRANDE),
            'vertical_alignment': LayoutElement.VerticalAlignment.MIDDLE
        })
    return crear_paragraph(estado.upper(), **propiedades)


def finalizar_pdf(doc: Document, filename: str) -> StreamingResponse:
    buffer = BytesIO()
    PDF.write(doc, buffer)
    buffer.seek(0)
    return StreamingResponse(
        buffer, 
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


def agregar_turnos_agrupados_por_persona(layout: PageLayout, turnos: List[Turno], incluir_fecha: bool = True) -> None:
    diccionario_personas = {}
    for turno in turnos:
        if turno.persona_id not in diccionario_personas:
            diccionario_personas[turno.persona_id] = {'persona': turno.persona, 'turnos': []}
        diccionario_personas[turno.persona_id]['turnos'].append(turno)
    
    for persona_data in diccionario_personas.values():
        persona = persona_data['persona']
        turnos_persona = persona_data['turnos']
        layout.append_layout_element(crear_paragraph(
            f"{persona.nombre} | ID: {persona.id} | DNI: {persona.dni} | {len(turnos_persona)} turno(s)",
            font=PDF_FONT_BOLD, 
            font_size=PDF_FONTSIZE_NORMAL
        ))
        layout.append_layout_element(crear_tabla_turnos(turnos_persona, incluir_persona=False, incluir_fecha=incluir_fecha))
        layout.append_layout_element(Paragraph(" "))



# ==================== Creación de PDF Base ====================

def crear_pdf_base(titulo: str, subtitulo: str = None) -> tuple[Document, PageLayout]:
    doc = Document()
    page = Page()
    doc.append_page(page)
    layout = SingleColumnLayout(page)
    
    # Título del sistema
    layout.append_layout_element(crear_paragraph(
        TITULO_SISTEMA,
        font=PDF_FONT_BOLD, 
        font_color=HexColor(PDF_COLOR_PRIMARIO), 
        padding_top=Decimal(PDF_PADDING_PEQUENO),
        padding_left=Decimal(PDF_PADDING_MEDIO), 
        padding_right=Decimal(PDF_PADDING_MEDIO),
        horizontal_alignment=LayoutElement.HorizontalAlignment.MIDDLE
    ))
    
    # Título del reporte
    layout.append_layout_element(crear_paragraph(
        titulo, 
        font=PDF_FONT_BOLD, 
        font_size=PDF_FONTSIZE_TITULO, 
        font_color=HexColor(PDF_COLOR_PRIMARIO),
        horizontal_alignment=LayoutElement.HorizontalAlignment.MIDDLE,
        padding_top=Decimal(PDF_PADDING_MUY_GRANDE), 
        padding_bottom=Decimal(PDF_PADDING_MEDIO)
    ))
    
    # Subtítulo opcional
    if subtitulo:
        layout.append_layout_element(crear_paragraph(
            subtitulo, 
            font_size=PDF_FONTSIZE_NORMAL, 
            font_color=HexColor(PDF_COLOR_TEXTO_GRIS),
            horizontal_alignment=LayoutElement.HorizontalAlignment.MIDDLE
        ))
    
    # Fecha de generación
    layout.append_layout_element(crear_paragraph(
        datetime.now().strftime(FORMATO_FECHA_GENERACION),
        font_size=PDF_FONTSIZE_PEQUENO, 
        font_color=HexColor(PDF_COLOR_TEXTO_GRIS_CLARO),
        horizontal_alignment=LayoutElement.HorizontalAlignment.MIDDLE, 
        padding_bottom=Decimal(PDF_PADDING_GRANDE)
    ))
    
    # Línea separadora
    layout.append_layout_element(Paragraph(
        " ", 
        border_width_bottom=Decimal(PDF_BORDER_DELGADO),
        border_color=HexColor(PDF_COLOR_SECUNDARIO), 
        padding_bottom=Decimal(PDF_PADDING_MEDIO)
    ))
    layout.append_layout_element(Paragraph(" "))
    
    return doc, layout


# ==================== Creación de Tablas ====================

def crear_tabla_turnos(turnos: List[Turno], incluir_persona: bool = False, incluir_fecha: bool = True) -> FixedColumnWidthTable:
    if incluir_persona:
        headers = [
            HEADER_ID, HEADER_ID_PERSONA, HEADER_PACIENTE, 
            HEADER_DNI, HEADER_FECHA, HEADER_HORA, HEADER_ESTADO
        ]
        column_widths = [Decimal(0.06), Decimal(0.08), Decimal(0.26), Decimal(0.10), Decimal(0.14), Decimal(0.14), Decimal(0.22)]
    elif incluir_fecha:
        headers = [HEADER_ID, HEADER_FECHA, HEADER_HORA, HEADER_ESTADO]
        column_widths = [Decimal(0.10), Decimal(0.30), Decimal(0.30), Decimal(0.30)]
    else:
        headers = [HEADER_ID, HEADER_HORA, HEADER_ESTADO]
        column_widths = [Decimal(0.15), Decimal(0.40), Decimal(0.45)]
    
    tabla = FixedColumnWidthTable(number_of_rows=len(turnos) + 1, number_of_columns=len(headers), column_widths=column_widths)
    
    for header in headers:
        tabla.append_layout_element(crear_celda_header(header))
    
    for turno in turnos:
        tabla.append_layout_element(crear_celda_dato(str(turno.id), padding_extra=incluir_persona))
        
        if incluir_persona:
            tabla.append_layout_element(crear_celda_dato(str(turno.persona_id), padding_extra=True))
            tabla.append_layout_element(crear_celda_dato(turno.persona.nombre, padding_extra=True))
            tabla.append_layout_element(crear_celda_dato(turno.persona.dni, padding_extra=True))
        
        if incluir_fecha:
            tabla.append_layout_element(crear_celda_dato(str(turno.fecha), padding_extra=incluir_persona))
        
        tabla.append_layout_element(crear_celda_dato(str(turno.hora), padding_extra=incluir_persona))
        tabla.append_layout_element(crear_celda_estado(turno.estado, padding_extra=incluir_persona))
    
    return tabla


def crear_tabla_personas(personas: List[Persona], incluir_completo: bool = False) -> FixedColumnWidthTable:    
    if incluir_completo:
        headers = [
            HEADER_ID, HEADER_NOMBRE, HEADER_DNI, 
            HEADER_EMAIL, HEADER_TELEFONO, HEADER_EDAD, HEADER_ESTADO
        ]
        column_widths = [Decimal(0.06), Decimal(0.22), Decimal(0.10), Decimal(0.26), Decimal(0.12), Decimal(0.06), Decimal(0.18)]
    else:
        headers = [HEADER_ID, HEADER_NOMBRE, HEADER_DNI]
        column_widths = [Decimal(0.10), Decimal(0.65), Decimal(0.25)]
    
    tabla = FixedColumnWidthTable(number_of_rows=len(personas) + 1, number_of_columns=len(headers), column_widths=column_widths)
    
    for header in headers:
        tabla.append_layout_element(crear_celda_header(header))
    
    for persona in personas:
        tabla.append_layout_element(crear_celda_dato(str(persona.id), padding_extra=True))
        tabla.append_layout_element(crear_celda_dato(persona.nombre, padding_extra=True))
        tabla.append_layout_element(crear_celda_dato(persona.dni, padding_extra=True))
        
        if incluir_completo:
            tabla.append_layout_element(crear_celda_dato(persona.email, font_size=8, padding_extra=True))
            tabla.append_layout_element(crear_celda_dato(persona.telefono, padding_extra=True))
            tabla.append_layout_element(crear_celda_dato(str(calcular_edad(persona.fecha_nacimiento)), padding_extra=True))
            
            estado_color = HexColor(PDF_COLOR_HABILITADO if persona.habilitado else PDF_COLOR_DESHABILITADO)
            tabla.append_layout_element(crear_paragraph(
                "HABILITADO" if persona.habilitado else "DESHABILITADO",
                font=PDF_FONT_BOLD, 
                font_color=estado_color,
                padding_top=Decimal(PDF_PADDING_GRANDE), 
                padding_bottom=Decimal(PDF_PADDING_GRANDE),
                vertical_alignment=LayoutElement.VerticalAlignment.MIDDLE
            ))
    
    return tabla


# ==================== Generadores de PDF ====================




def generar_pdf_turnos_por_fecha(fecha: date, turnos: List[Turno]) -> StreamingResponse:
    doc, layout = crear_pdf_base(f"Turnos - {fecha}", f"Total: {len(turnos)} turnos")
    
    if turnos:
        agregar_turnos_agrupados_por_persona(layout, turnos, incluir_fecha=False)
    else:
        layout.append_layout_element(crear_paragraph(MSG_SIN_TURNOS_FECHA))
    
    return finalizar_pdf(doc, f"turnos_{fecha}.pdf")



def generar_pdf_turnos_cancelados_mes(mes: str, anio: int, turnos: List[Turno]) -> StreamingResponse:
    doc, layout = crear_pdf_base(f"Turnos Cancelados - {mes} {anio}", f"Total: {len(turnos)}")
    
    if turnos:
        agregar_turnos_agrupados_por_persona(layout, turnos, incluir_fecha=True)
    else:
        layout.append_layout_element(crear_paragraph(MSG_SIN_TURNOS_CANCELADOS))
    
    return finalizar_pdf(doc, f"cancelados_{mes}_{anio}.pdf")


def generar_pdf_turnos_por_persona(persona: Persona, turnos: List[Turno]) -> StreamingResponse:    
    doc, layout = crear_pdf_base("HISTORIAL DE TURNOS DEL PACIENTE", "Reporte completo")
    
    # Info del paciente
    info = FixedColumnWidthTable(number_of_rows=5, number_of_columns=2, column_widths=[Decimal(0.20), Decimal(0.80)])
    for label, valor in [("Nombre:", persona.nombre), ("DNI:", persona.dni), ("Email:", persona.email), ("Teléfono:", persona.telefono), ("Edad:", f"{calcular_edad(persona.fecha_nacimiento)} años")]:
        info.append_layout_element(crear_paragraph(
            label, 
            font=PDF_FONT_BOLD, 
            font_color=HexColor(PDF_COLOR_SECUNDARIO),
            padding_left=Decimal(PDF_PADDING_MUY_GRANDE), 
            padding_top=Decimal(2), 
            padding_bottom=Decimal(2)
        ))
        info.append_layout_element(crear_paragraph(
            valor, 
            padding_left=Decimal(PDF_PADDING_MUY_GRANDE),
            padding_top=Decimal(2), 
            padding_bottom=Decimal(2)
        ))
    info.no_borders()
    layout.append_layout_element(info)
    
    # Estado
    estado_color = HexColor(PDF_COLOR_HABILITADO if persona.habilitado else PDF_COLOR_DESHABILITADO)
    layout.append_layout_element(crear_paragraph(
        "HABILITADO PARA SOLICITAR TURNOS" if persona.habilitado else "DESHABILITADO PARA SOLICITAR TURNOS",
        font=PDF_FONT_BOLD, 
        font_size=PDF_FONTSIZE_NORMAL, 
        font_color=estado_color,
        border_width_left=Decimal(PDF_BORDER_GRUESO), 
        border_color=estado_color,
        padding_top=Decimal(6), 
        padding_bottom=Decimal(6), 
        padding_left=Decimal(PDF_PADDING_MUY_GRANDE), 
        padding_right=Decimal(PDF_PADDING_MUY_GRANDE),
        horizontal_alignment=LayoutElement.HorizontalAlignment.MIDDLE
    ))
    
    layout.append_layout_element(Paragraph(" "))
    layout.append_layout_element(crear_paragraph("RESUMEN DE TURNOS", 
        font=PDF_FONT_BOLD, 
        font_size=PDF_FONTSIZE_SUBTITULO,
        font_color=HexColor(PDF_COLOR_PRIMARIO), 
        padding_top=Decimal(PDF_PADDING_GRANDE)
    ))
    
    if turnos:
        # Estadísticas
        stats_tabla = FixedColumnWidthTable(number_of_rows=1, number_of_columns=4)
        stats = [
            ('Total', len(turnos), HexColor(PDF_COLOR_TEXTO_GRIS_CLARO)),
            ('Confirmados', sum(1 for t in turnos if t.estado.lower() == ESTADO_CONFIRMADO.lower()), HexColor(PDF_COLOR_CONFIRMADO)),
            ('Cancelados', sum(1 for t in turnos if t.estado.lower() == ESTADO_CANCELADO.lower()), HexColor(PDF_COLOR_CANCELADO)),
            ('Asistidos', sum(1 for t in turnos if t.estado.lower() == ESTADO_ASISTIDO.lower()), HexColor(PDF_COLOR_ASISTIDO))
        ]
        
        for label, valor, color in stats:
            stats_tabla.append_layout_element(crear_paragraph(
                f"{label}\n{valor}", 
                font=PDF_FONT_BOLD, 
                font_size=PDF_FONTSIZE_NORMAL, 
                font_color=color,
                border_width_left=Decimal(PDF_BORDER_MEDIO), 
                border_color=color,
                padding_top=Decimal(PDF_PADDING_GRANDE), 
                padding_bottom=Decimal(PDF_PADDING_GRANDE), 
                padding_left=Decimal(PDF_PADDING_GRANDE), 
                padding_right=Decimal(PDF_PADDING_GRANDE),
                horizontal_alignment=LayoutElement.HorizontalAlignment.MIDDLE
            ))
        
        stats_tabla.no_borders()
        layout.append_layout_element(stats_tabla)
        layout.append_layout_element(Paragraph(" "))
        layout.append_layout_element(crear_paragraph(
            "DETALLE DE TURNOS", 
            font=PDF_FONT_BOLD,
            font_size=PDF_FONTSIZE_SUBTITULO, 
            font_color=HexColor(PDF_COLOR_PRIMARIO)
        ))
        layout.append_layout_element(crear_tabla_turnos(turnos, incluir_persona=False, incluir_fecha=True))
    else:
        layout.append_layout_element(crear_paragraph(
            MSG_SIN_TURNOS_PERSONA,
            font_color=HexColor(PDF_COLOR_ALERTA), 
            padding_top=Decimal(PDF_PADDING_MUY_GRANDE)
        ))
    
    return finalizar_pdf(doc, f"historial_{persona.dni}.pdf")



def generar_pdf_personas_con_cancelaciones(min_cancelados: int, turnos: List[Turno]) -> StreamingResponse:
    doc, layout = crear_pdf_base(f"Personas con {min_cancelados}+ Turnos Cancelados", None)
    
    if turnos:
        agregar_turnos_agrupados_por_persona(layout, turnos, incluir_fecha=True)
    else:
        layout.append_layout_element(crear_paragraph(f"No hay personas con {min_cancelados}+ cancelaciones."))
    
    return finalizar_pdf(doc, f"cancelaciones_min_{min_cancelados}.pdf")



def generar_pdf_turnos_confirmados(desde: date, hasta: date, turnos: List[Turno]) -> StreamingResponse:
    doc, layout = crear_pdf_base("Turnos Confirmados", f"{desde} a {hasta} - Total: {len(turnos)}")
    
    if turnos:
        agregar_turnos_agrupados_por_persona(layout, turnos, incluir_fecha=True)
    else:
        layout.append_layout_element(crear_paragraph(MSG_SIN_TURNOS_CONFIRMADOS))
    
    return finalizar_pdf(doc, f"confirmados_{desde}_a_{hasta}.pdf")


def generar_pdf_estado_personas(habilitado: bool, personas: List[Persona]) -> StreamingResponse:
    estado = "Habilitadas" if habilitado else "Deshabilitadas"
    doc, layout = crear_pdf_base(f"Personas {estado}", f"Total: {len(personas)}")
    
    if personas:
        layout.append_layout_element(crear_tabla_personas(personas, incluir_completo=True))
    else:
        layout.append_layout_element(crear_paragraph(f"No hay personas {estado.lower()}."))
    
    return finalizar_pdf(doc, f"personas_{estado.lower()}.pdf")