# Sistema de Gestión de Turnos - API REST

### Sistema de gestión de turnos médicos.
  
**Universidad Nacional de Lanús (UNLa)**  
**Asignatura:** Seminario de Lenguajes - Python  
**Docente:** Mg. Lic. María Alejandra VRANIC  
**Docente:** Lic. Nicolás BOREA  
**Docente:** Lic. Gonzalo CERBELLI  
**Año:** 2025  
**Grupo 3:** Agustín Torres Valenzuela  

---

## Descripción del Proyecto

API REST para la gestión de turnos médicos que permite:
- Administrar personas (pacientes)
- Gestionar turnos (crear, modificar, cancelar, confirmar)
- Consultar disponibilidad de horarios
- Generar reportes

---

## Especificaciones para Levantar el Proyecto

### **Requisitos Previos**

- Python 3.12 o superior
- pip (gestor de paquetes de Python)
- Git

### **Instalación**

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/agutor/SL-UNLA-LAB-2025-GRUPO-3.git
   cd SL-UNLA-LAB-2025-GRUPO-3
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Linux/Mac
    ```

   ```
   python -m venv venv
   venv\Scripts\activate  # En Windows
    ```

3. **Instalar dependencias**
   ```bash
   pip install -r Requirements.txt
   ```

4. **Levantar el servidor**
   ```bash
   uvicorn App.main:app --reload
   ```

5. **Acceder a la aplicación**
   - API: http://127.0.0.1:8000
   - Documentación interactiva (Swagger): http://127.0.0.1:8000/docs
   - Documentación alternativa (ReDoc): http://127.0.0.1:8000/redoc
   - Utilizando la [Collection disponible](./SL-UNLA-LAB-GRUPO-3.postman_collection.json) en Postman
   
---

## Colección de Endpoints

### **Verificación**
- `GET /` - Verificar funcionamiento de la API

### **Personas (ABM)**
- `POST /personas` - Crear una persona
- `GET /personas` - Listar todas las personas
- `GET /personas/{id}` - Obtener persona por ID
- `PUT /personas/{id}` - Actualizar persona
- `DELETE /personas/{id}` - Eliminar persona

### **Turnos (ABM)**
- `POST /turnos` - Crear un turno
- `GET /turnos` - Listar todos los turnos
- `GET /turnos/{id}` - Obtener turno por ID
- `PUT /turnos/{id}` - Actualizar turno
- `DELETE /turnos/{id}` - Eliminar turno
- `GET /turnos-disponibles?fecha=YYYY-MM-DD` - Consultar horarios disponibles

### **Estado de Turnos**
- `PUT /turnos/{turno_id}/cancelar` - Cancelar un turno
- `PUT /turnos/{turno_id}/confirmar` - Confirmar un turno

### **Reportes**
- `GET /reportes/turnos-por-fecha?fecha=YYYY-MM-DD` - Turnos por fecha específica
- `GET /reportes/turnos-cancelados-por-mes` - Turnos cancelados del mes actual
- `GET /reportes/turnos-por-persona?dni=12345678` - Turnos de una persona por DNI
- `GET /reportes/turnos-cancelados?min=5` - Personas con mínimo de cancelaciones
- `GET /reportes/turnos-confirmados?desde=YYYY-MM-DD&hasta=YYYY-MM-DD&pagina=1` - Turnos confirmados con paginación
- `GET /reportes/estado-personas?habilitado=true` - Personas por estado (habilitadas/deshabilitadas)

---

**Enlace al video:** [Google Drive](https://drive.google.com/drive/folders/1Pzwx9yPld4Ttu2pUoRtpltgWTY_l6NnJ?usp=sharing)

---

## Estructura del Proyecto

```
SL-UNLA-LAB-2025-GRUPO-3/
│
├── App/
│   ├── main.py              # Punto de entrada de la aplicación
│   ├── config.py            # Configuración y variables de entorno
│   ├── database.py          # Configuración de la base de datos
│   ├── models.py            # Modelos SQLAlchemy
│   ├── schemas.py           # Esquemas Pydantic
│   ├── utils.py             # Funciones utilitarias
│   ├── crudPersonas.py      # Operaciones CRUD de personas
│   └── crudTurnos.py        # Operaciones CRUD de turnos
│
├── .env                    
├── Requirements.txt       
├── readme.md               
```

---

## Tecnologías Utilizadas

- **FastAPI** 
- **SQLAlchemy**
- **Pydantic**
- **SQLite**
- **Uvicorn** 
- **python-dotenv**

