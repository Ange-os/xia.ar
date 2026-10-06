@echo off
REM Script para iniciar el backend localmente en Windows

echo 🚀 Iniciando xIA Backend Local...
echo.

REM Cambiar al directorio del backend
cd /d "%~dp0"

REM Verificar que existe el entorno virtual y que es de Windows
if not exist "venv\Scripts\python.exe" (
    echo ⚠️  Entorno virtual no encontrado o incompatible (puede ser de Linux).
    echo 📦 Recreando entorno virtual para Windows...
    if exist "venv" (
        echo    Eliminando venv existente...
        rmdir /s /q venv
    )
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Error al crear entorno virtual
        pause
        exit /b 1
    )
    echo 📥 Instalando dependencias...
    call venv\Scripts\activate.bat
    pip install --upgrade pip
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Error al instalar dependencias
        pause
        exit /b 1
    )
)

REM Activar entorno virtual
echo 🔧 Activando entorno virtual...
call venv\Scripts\activate.bat

REM Verificar Flask
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Flask no encontrado. Instalando dependencias...
    pip install -r requirements.txt
)

REM Iniciar servidor
echo.
echo ✅ Iniciando servidor Flask...
echo 📡 El servidor estará disponible en: http://localhost:5000
echo 🌐 Frontend: http://localhost/xIA/htdocs/xia.ar/public/index.html
echo.
echo ⚠️  Mantén esta ventana abierta mientras trabajas.
echo ⚠️  Presiona Ctrl+C para detener el servidor.
echo.

python main.py

pause

