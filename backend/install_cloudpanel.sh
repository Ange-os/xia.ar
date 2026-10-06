#!/bin/bash
# Script de instalación para CloudPanel/VPS
# Ejecutar como usuario xia o con sudo

set -e

echo "🚀 Instalando xIA Backend para CloudPanel..."

# Obtener directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado. Instalando..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
fi

# Crear entorno virtual
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
echo "🔌 Activando entorno virtual..."
source venv/bin/activate

# Actualizar pip
echo "⬆️ Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias
echo "📥 Instalando dependencias..."
pip install -r requirements.txt

# Verificar que Gunicorn está instalado
if ! python -c "import gunicorn" 2>/dev/null; then
    echo "📦 Instalando Gunicorn..."
    pip install gunicorn
fi

# Crear directorio de logs
mkdir -p logs

# Hacer ejecutable el script de inicio
chmod +x start_gunicorn.sh

echo "✅ Instalación completada!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Configurar Nginx en CloudPanel (ver CLOUDPANEL_CONFIGURACION.md)"
echo "2. Crear servicio systemd (ver CLOUDPANEL_CONFIGURACION.md)"
echo "3. Iniciar el servicio: sudo systemctl start xia-backend"

