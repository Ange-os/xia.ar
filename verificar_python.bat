@echo off
REM Script para verificar qué Python se está usando

echo ========================================
echo VERIFICACION DE PYTHON
echo ========================================
echo.

echo [1] Python en PATH del sistema:
where python
echo.

echo [2] Version de Python:
python --version
echo.

echo [3] Ruta completa de Python:
for /f "delims=" %%i in ('where python') do (
    echo    %%i
    dir "%%i" 2>nul
)
echo.

echo [4] Verificando si hay Python de Linux en PATH:
echo    Buscando /usr/bin en PATH...
echo %PATH% | findstr /i "usr" >nul
if errorlevel 1 (
    echo    ✅ No se encontró /usr en PATH
) else (
    echo    ⚠️  Se encontró 'usr' en PATH - puede ser problema
    echo    PATH contiene:
    echo    %PATH%
)
echo.

echo [5] Si existe venv, verificar pyvenv.cfg:
if exist "venv\pyvenv.cfg" (
    echo    Contenido de pyvenv.cfg:
    type venv\pyvenv.cfg
    echo.
    findstr /i "usr" venv\pyvenv.cfg >nul
    if errorlevel 1 (
        echo    ✅ pyvenv.cfg NO tiene rutas de Linux
    ) else (
        echo    ❌ pyvenv.cfg tiene rutas de Linux - RECREAR VENV
    )
) else (
    echo    ⚠️  No existe venv\pyvenv.cfg
)
echo.

echo ========================================
pause

