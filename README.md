# 🚀 xIA Backend API

Backend para el sistema de consultoría xIA.ar con agente de IA y servicio de email.

## 📋 Requisitos

- Python 3.8+
- pip (gestor de paquetes de Python)

## 🔧 Instalación

### Windows:
```bash
# Ejecutar el script de instalación
install.bat
```

### Linux/Mac:
```bash
# Ejecutar el script de instalación
chmod +x install.sh
./install.sh
```

### Instalación manual:
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## 🚀 Ejecución

```bash
# Activar entorno virtual
# Windows:
venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# Ejecutar servidor
python main.py
```

El servidor se ejecutará en `http://localhost:5000`

## 📡 Endpoints

### `GET /api/health`
Health check del servidor.

### `POST /api/chat`
Chat con el agente de IA.
```json
{
  "message": "Tu consulta aquí"
}
```

### `POST /api/send-email`
Enviar consulta por email.
```json
{
  "name": "Nombre",
  "email": "email@ejemplo.com",
  "phone": "+54 9 11 1234-5678",
  "summary": "Resumen de la consulta"
}
```

## 🔧 Configuración

### Variables de entorno:
- `FLASK_ENV`: `development` para modo debug
- `PORT`: Puerto del servidor (default: 5000)
- `SECRET_KEY`: Clave secreta para Flask

### Archivos de configuración:
- `agents/agent_simple.py`: Agente de IA
- `agents/email_service.py`: Servicio de email

## 🐛 Troubleshooting

### Error: "flask_cors could not be resolved"
```bash
pip install flask-cors
```

### Error: "agent_simple could not be resolved"
Verificar que el archivo `agents/agent_simple.py` existe.

### Error: "email_service could not be resolved"
Verificar que el archivo `agents/email_service.py` existe.

## 📁 Estructura

```
backend/
├── main.py              # Servidor principal
├── requirements.txt     # Dependencias
├── install.sh          # Script de instalación (Linux/Mac)
├── install.bat         # Script de instalación (Windows)
├── agents/
│   ├── agent_simple.py  # Agente de IA
│   └── email_service.py # Servicio de email
└── venv/               # Entorno virtual (se crea al instalar)
```

## 🔄 Desarrollo

Para desarrollo, activa el modo debug:
```bash
export FLASK_ENV=development  # Linux/Mac
set FLASK_ENV=development      # Windows
python main.py
```

## 📦 Despliegue

Ver `../deploy.md` para instrucciones de despliegue en producción.
