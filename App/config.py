import os
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

# Variables de base de datos
URL_BASE_DATOS = os.getenv("URL_BASE_DATOS")

# Variables de turnos
HORARIO_INICIO = os.getenv("HORARIO_INICIO")
HORARIO_FIN = os.getenv("HORARIO_FIN")
HORARIOS_DISPONIBLES = []
INTERVALO_TURNOS_MINUTOS = int(os.getenv("INTERVALO_TURNOS_MINUTOS"))
MAX_TURNOS_CANCELADOS = int(os.getenv("MAX_TURNOS_CANCELADOS"))
DIAS_LIMITE_CANCELACIONES = int(os.getenv("DIAS_LIMITE_CANCELACIONES"))

# Variables de personas
MAX_EDAD_PERMITIDA = int(os.getenv("MAX_EDAD_PERMITIDA"))

# Estados de turnos
ESTADO_PENDIENTE = os.getenv("ESTADO_PENDIENTE")
ESTADO_CONFIRMADO = os.getenv("ESTADO_CONFIRMADO")
ESTADO_CANCELADO = os.getenv("ESTADO_CANCELADO")
ESTADO_ASISTIDO = os.getenv("ESTADO_ASISTIDO")

# Variables para reportes
MIN_CANCELADOS_DEFAULT = int(os.getenv("MIN_CANCELADOS_DEFAULT", "5"))
LIMIT_PAGINACION_DEFAULT = int(os.getenv("LIMIT_PAGINACION_DEFAULT", "5"))

# ==================== Configuración de PDFs ====================

# Colores del sistema para PDFs
PDF_COLOR_PRIMARIO = os.getenv("PDF_COLOR_PRIMARIO", "#2C3E50")
PDF_COLOR_SECUNDARIO = os.getenv("PDF_COLOR_SECUNDARIO", "#3498DB")
PDF_COLOR_TEXTO_GRIS = os.getenv("PDF_COLOR_TEXTO_GRIS", "#7F8C8D")
PDF_COLOR_TEXTO_GRIS_CLARO = os.getenv("PDF_COLOR_TEXTO_GRIS_CLARO", "#95A5A6")

# Colores por estado de turno
PDF_COLOR_PENDIENTE = os.getenv("PDF_COLOR_PENDIENTE", "#F39C12")
PDF_COLOR_CONFIRMADO = os.getenv("PDF_COLOR_CONFIRMADO", "#27AE60")
PDF_COLOR_CANCELADO = os.getenv("PDF_COLOR_CANCELADO", "#E74C3C")
PDF_COLOR_ASISTIDO = os.getenv("PDF_COLOR_ASISTIDO", "#3498DB")

# Colores para personas
PDF_COLOR_HABILITADO = os.getenv("PDF_COLOR_HABILITADO", "#27AE60")
PDF_COLOR_DESHABILITADO = os.getenv("PDF_COLOR_DESHABILITADO", "#E74C3C")

# Colores adicionales
PDF_COLOR_ALERTA = os.getenv("PDF_COLOR_ALERTA", "#E67E22")

# Fuentes
PDF_FONT_NORMAL = os.getenv("PDF_FONT_NORMAL", "Helvetica")
PDF_FONT_BOLD = os.getenv("PDF_FONT_BOLD", "Helvetica-Bold")

# Tamaños de fuente
PDF_FONTSIZE_TITULO = int(os.getenv("PDF_FONTSIZE_TITULO", "14"))
PDF_FONTSIZE_SUBTITULO = int(os.getenv("PDF_FONTSIZE_SUBTITULO", "11"))
PDF_FONTSIZE_NORMAL = int(os.getenv("PDF_FONTSIZE_NORMAL", "10"))
PDF_FONTSIZE_DATO = int(os.getenv("PDF_FONTSIZE_DATO", "9"))
PDF_FONTSIZE_PEQUENO = int(os.getenv("PDF_FONTSIZE_PEQUENO", "8"))

# Espaciado
PDF_PADDING_PEQUENO = int(os.getenv("PDF_PADDING_PEQUENO", "3"))
PDF_PADDING_NORMAL = int(os.getenv("PDF_PADDING_NORMAL", "4"))
PDF_PADDING_MEDIO = int(os.getenv("PDF_PADDING_MEDIO", "5"))
PDF_PADDING_GRANDE = int(os.getenv("PDF_PADDING_GRANDE", "8"))
PDF_PADDING_MUY_GRANDE = int(os.getenv("PDF_PADDING_MUY_GRANDE", "10"))

# Bordes
PDF_BORDER_DELGADO = int(os.getenv("PDF_BORDER_DELGADO", "1"))
PDF_BORDER_MEDIO = int(os.getenv("PDF_BORDER_MEDIO", "3"))
PDF_BORDER_GRUESO = int(os.getenv("PDF_BORDER_GRUESO", "4"))

# Textos del sistema
PDF_TITULO_SISTEMA = os.getenv("PDF_TITULO_SISTEMA", "SISTEMA DE GESTIÓN DE TURNOS MÉDICOS")
PDF_FORMATO_FECHA_GENERACION = os.getenv("PDF_FORMATO_FECHA", "Generado el: %d/%m/%Y %H:%M")

# Mensajes comunes
PDF_MSG_SIN_DATOS = os.getenv("PDF_MSG_SIN_DATOS", "No hay datos.")
PDF_MSG_SIN_TURNOS_FECHA = os.getenv("PDF_MSG_SIN_TURNOS_FECHA", "No hay turnos para esta fecha.")
PDF_MSG_SIN_TURNOS_CANCELADOS = os.getenv("PDF_MSG_SIN_TURNOS_CANCELADOS", "No hay turnos cancelados este mes.")
PDF_MSG_SIN_TURNOS_CONFIRMADOS = os.getenv("PDF_MSG_SIN_TURNOS_CONFIRMADOS", "No hay turnos confirmados.")
PDF_MSG_SIN_TURNOS_PERSONA = os.getenv("PDF_MSG_SIN_TURNOS_PERSONA", "ATENCION: Este paciente no tiene turnos registrados.")

# Encabezados de tablas
PDF_HEADER_ID = os.getenv("PDF_HEADER_ID", "ID")
PDF_HEADER_ID_PERSONA = os.getenv("PDF_HEADER_ID_PERSONA", "ID Persona")
PDF_HEADER_PACIENTE = os.getenv("PDF_HEADER_PACIENTE", "Paciente")
PDF_HEADER_NOMBRE = os.getenv("PDF_HEADER_NOMBRE", "Nombre")
PDF_HEADER_DNI = os.getenv("PDF_HEADER_DNI", "DNI")
PDF_HEADER_EMAIL = os.getenv("PDF_HEADER_EMAIL", "Email")
PDF_HEADER_TELEFONO = os.getenv("PDF_HEADER_TELEFONO", "Teléfono")
PDF_HEADER_EDAD = os.getenv("PDF_HEADER_EDAD", "Edad")
PDF_HEADER_FECHA = os.getenv("PDF_HEADER_FECHA", "Fecha")
PDF_HEADER_HORA = os.getenv("PDF_HEADER_HORA", "Hora")
PDF_HEADER_ESTADO = os.getenv("PDF_HEADER_ESTADO", "Estado")