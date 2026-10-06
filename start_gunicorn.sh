#!/bin/bash
# Script para iniciar Flask con Gunicorn en producción

# Cambiar al directorio del backend
cd "$(dirname "$0")"

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Crear directorio de logs si no existe
mkdir -p logs

# Verificar que Gunicorn está instalado
if ! command -v gunicorn &> /dev/null; then
    echo "❌ Gunicorn no está instalado. Instalando..."
    pip install gunicorn
fi

# Iniciar Gunicorn
echo "🚀 Iniciando xIA Backend con Gunicorn..."
gunicorn -c gunicorn_config.py wsgi:application

