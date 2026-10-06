@echo off
REM Script de instalación para xIA Backend (Windows)

echo 🚀 Instalando dependencias para xIA Backend...

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado. Instálalo primero.
    pause
    exit /b 1
)

REM Eliminar entorno virtual existente si fue creado en Linux
if exist "venv" (
    echo ⚠️  Eliminando entorno virtual existente (puede ser de Linux)...
    rmdir /s /q venv
)

REM Crear entorno virtual nuevo para Windows
echo 📦 Creando entorno virtual para Windows...
python -m venv venv

REM Activar entorno virtual
echo 🔧 Activando entorno virtual...
call venv\Scripts\activate.bat

REM Instalar dependencias
echo 📥 Instalando dependencias...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Verificar instalación
echo ✅ Verificando instalación...
python -c "import flask; print('Flask:', flask.__version__)"
python -c "import flask_cors; print('Flask-CORS instalado')"

echo 🎉 Instalación completada!
echo Para ejecutar el servidor:
echo   venv\Scripts\activate.bat
echo   python main.py

pause
