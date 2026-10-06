@echo off
REM Script para recrear el entorno virtual en Windows
REM Útil cuando el venv fue creado en Linux

echo ========================================
echo RECREANDO ENTORNO VIRTUAL PARA WINDOWS
echo ========================================
echo.

cd /d "%~dp0"

echo [1] Verificando Python...
python --version
if errorlevel 1 (
    echo ❌ ERROR: Python no encontrado
    echo    Instala Python desde https://www.python.org/
    pause
    exit /b 1
)
echo ✅ Python encontrado
echo.

echo [2] Eliminando entorno virtual existente...
if exist "venv" (
    echo    Eliminando venv...
    rmdir /s /q venv
    echo ✅ Venv eliminado
) else (
    echo ✅ No hay venv existente
)
echo.

echo [3] Creando nuevo entorno virtual para Windows...
python -m venv venv
if errorlevel 1 (
    echo ❌ ERROR al crear entorno virtual
    pause
    exit /b 1
)
echo ✅ Entorno virtual creado
echo.

echo [4] Activando entorno virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ ERROR al activar entorno virtual
    pause
    exit /b 1
)
echo ✅ Entorno virtual activado
echo.

echo [5] Actualizando pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ⚠️  Advertencia: Error al actualizar pip (continuando...)
)
echo.

echo [6] Instalando dependencias...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ ERROR al instalar dependencias
    pause
    exit /b 1
)
echo ✅ Dependencias instaladas
echo.

echo [7] Verificando instalación...
python -c "import flask; print('✅ Flask:', flask.__version__)"
python -c "import flask_cors; print('✅ Flask-CORS OK')"
python -c "import dotenv; print('✅ python-dotenv OK')"
echo.

echo ========================================
echo ✅ ENTORNO VIRTUAL RECREADO EXITOSAMENTE
echo ========================================
echo.
echo Ahora puedes ejecutar:
echo   start_local.bat
echo   o
echo   venv\Scripts\activate.bat
echo   python main.py
echo.
pause

