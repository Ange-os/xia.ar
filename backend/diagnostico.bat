@echo off
REM Script de diagnóstico para identificar el error

echo ========================================
echo DIAGNOSTICO DEL BACKEND
echo ========================================
echo.

cd /d "%~dp0"

echo [1] Verificando Python del sistema...
where python >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python no encontrado en PATH
    echo    Verifica que Python esté instalado y en el PATH
    pause
    exit /b 1
)
python --version
echo ✅ Python encontrado
echo.

echo [2] Verificando entorno virtual...
if exist "venv\Scripts\python.exe" (
    echo ✅ venv\Scripts\python.exe existe
) else (
    echo ❌ ERROR: venv\Scripts\python.exe NO existe
)
echo.

echo [3] Intentando activar entorno virtual...
call venv\Scripts\activate.bat 2>&1
if errorlevel 1 (
    echo ❌ ERROR al activar entorno virtual
) else (
    echo ✅ Entorno virtual activado
)
echo.

echo [4] Verificando Flask...
python -c "import flask; print('Flask:', flask.__version__)" 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Flask no se puede importar
) else (
    echo ✅ Flask encontrado
)
echo.

echo [5] Verificando flask_cors...
python -c "import flask_cors; print('Flask-CORS OK')" 2>&1
if errorlevel 1 (
    echo ❌ ERROR: flask_cors no se puede importar
) else (
    echo ✅ Flask-CORS encontrado
)
echo.

echo [6] Verificando agentes...
python -c "import sys; sys.path.insert(0, 'agents'); from agents.agent_simple import SimpleAgent; print('✅ Agente OK')" 2>&1
if errorlevel 1 (
    echo ❌ ERROR: No se puede importar agent_simple
) else (
    echo ✅ Agente encontrado
)
echo.

echo [7] Intentando ejecutar main.py...
echo.
python main.py 2>&1
echo.
echo Exit code: %ERRORLEVEL%

echo.
echo ========================================
echo DIAGNOSTICO COMPLETADO
echo ========================================
pause

