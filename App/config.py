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

# ==================== Configuración de Reportes ====================

# Encabezados de tablas (usados en PDF y CSV)
HEADER_ID = os.getenv("HEADER_ID", "ID")
HEADER_ID_PERSONA = os.getenv("HEADER_ID_PERSONA", "ID Persona")
HEADER_PACIENTE = os.getenv("HEADER_PACIENTE", "Paciente")
HEADER_NOMBRE = os.getenv("HEADER_NOMBRE", "Nombre")
HEADER_DNI = os.getenv("HEADER_DNI", "DNI")
HEADER_EMAIL = os.getenv("HEADER_EMAIL", "Email")
HEADER_TELEFONO = os.getenv("HEADER_TELEFONO", "Teléfono")
HEADER_EDAD = os.getenv("HEADER_EDAD", "Edad")
HEADER_FECHA = os.getenv("HEADER_FECHA", "Fecha")
HEADER_HORA = os.getenv("HEADER_HORA", "Hora")
HEADER_ESTADO = os.getenv("HEADER_ESTADO", "Estado")

# Textos del sistema
TITULO_SISTEMA = os.getenv("TITULO_SISTEMA", "SISTEMA DE GESTIÓN DE TURNOS MÉDICOS")
FORMATO_FECHA_GENERACION = os.getenv("FORMATO_FECHA", "Generado el: %d/%m/%Y %H:%M")

# Mensajes comunes
MSG_SIN_DATOS = os.getenv("MSG_SIN_DATOS", "No hay datos.")
MSG_SIN_TURNOS_FECHA = os.getenv("MSG_SIN_TURNOS_FECHA", "No hay turnos para esta fecha.")
MSG_SIN_TURNOS_CANCELADOS = os.getenv("MSG_SIN_TURNOS_CANCELADOS", "No hay turnos cancelados este mes.")
MSG_SIN_TURNOS_CONFIRMADOS = os.getenv("MSG_SIN_TURNOS_CONFIRMADOS", "No hay turnos confirmados.")
MSG_SIN_TURNOS_PERSONA = os.getenv("MSG_SIN_TURNOS_PERSONA", "ATENCION: Este paciente no tiene turnos registrados.")

# Textos adicionales para reportes
TEXTO_HABILITADO = os.getenv("TEXTO_HABILITADO", "HABILITADO")
TEXTO_DESHABILITADO = os.getenv("TEXTO_DESHABILITADO", "DESHABILITADO")
TEXTO_INFO_PACIENTE = os.getenv("TEXTO_INFO_PACIENTE", "Información del Paciente")
TEXTO_ANOS = os.getenv("TEXTO_ANOS", "años")

# ==================== Configuración específica de PDFs ====================

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