#!/bin/bash
# Script de instalación para xIA Backend

echo "🚀 Instalando dependencias para xIA Backend..."

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado. Instálalo primero."
    exit 1
fi

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "📥 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

# Verificar instalación
echo "✅ Verificando instalación..."
python -c "import flask; print('Flask:', flask.__version__)"
python -c "import flask_cors; print('Flask-CORS instalado')"

echo "🎉 Instalación completada!"
echo "Para ejecutar el servidor:"
echo "  source venv/bin/activate"
echo "  python main.py"
