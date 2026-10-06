# 🔧 Recrear Entorno Virtual Manualmente (Windows)

> **Problema**: El venv tiene rutas de Linux (`/usr/bin`) y no funciona en Windows

---

## 📋 Pasos Manuales

### Paso 1: Eliminar el venv Existente

```powershell
# Ir al directorio backend
cd D:\root\xIA\htdocs\xia.ar\backend

# Eliminar carpeta venv (si existe)
# Puedes hacerlo desde el explorador de archivos o:
Remove-Item -Recurse -Force venv
# O desde CMD:
# rmdir /s /q venv
```

### Paso 2: Verificar Python de Windows

```powershell
# Verificar que Python está instalado y en el PATH
python --version

# Ver dónde está Python
where python

# Debería mostrar algo como:
# C:\Users\TuUsuario\AppData\Local\Programs\Python\Python3XX\python.exe
# O
# C:\Python3XX\python.exe
```

**Si no encuentra Python:**
- Instalar Python desde https://www.python.org/
- Asegurarse de marcar "Add Python to PATH" durante la instalación

### Paso 3: Crear Nuevo Entorno Virtual

```powershell
# Asegurarse de estar en el directorio backend
cd D:\root\xIA\htdocs\xia.ar\backend

# Crear nuevo entorno virtual
python -m venv venv

# Verificar que se creó correctamente
dir venv\Scripts\python.exe
```

**Deberías ver:**
- `venv\Scripts\python.exe` existe
- `venv\pyvenv.cfg` tiene rutas de Windows (no `/usr/bin`)

### Paso 4: Activar el Entorno Virtual

```powershell
# Activar venv
.\venv\Scripts\Activate.ps1

# Si da error de ejecución de scripts:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# O usar el .bat:
.\venv\Scripts\activate.bat
```

**Deberías ver:**
```
(venv) PS D:\root\xIA\htdocs\xia.ar\backend>
```

### Paso 5: Verificar Python del Venv

```powershell
# Verificar que usa Python de Windows
python --version
where python

# Debería mostrar:
# D:\root\xIA\htdocs\xia.ar\backend\venv\Scripts\python.exe
```

### Paso 6: Actualizar pip

```powershell
python -m pip install --upgrade pip
```

### Paso 7: Instalar Dependencias

```powershell
# Instalar todas las dependencias
pip install -r requirements.txt
```

**Deberías ver:**
```
Collecting Flask==2.3.3
Collecting Flask-CORS==4.0.0
...
Successfully installed Flask-2.3.3 Flask-CORS-4.0.0 ...
```

### Paso 8: Verificar Instalación

```powershell
# Verificar Flask
python -c "import flask; print('Flask:', flask.__version__)"

# Verificar Flask-CORS
python -c "import flask_cors; print('Flask-CORS OK')"

# Verificar python-dotenv
python -c "import dotenv; print('python-dotenv OK')"
```

### Paso 9: Verificar pyvenv.cfg

```powershell
# Ver el contenido de pyvenv.cfg
type venv\pyvenv.cfg

# Debería mostrar algo como:
# home = C:\Users\TuUsuario\AppData\Local\Programs\Python\Python312
# include-system-site-packages = false
# version = 3.12.x
```

**NO debe tener `/usr/bin`** ✅

### Paso 10: Probar el Backend

```powershell
# Asegurarse de que el venv está activado
# (deberías ver (venv) en el prompt)

# Ejecutar el servidor
python main.py
```

**Deberías ver:**
```
💻 Modo DESARROLLO detectado
📁 Buscando archivo .env en: D:\root\xIA\htdocs\xia.ar\backend\.env
🚀 Iniciando xIA Backend API en puerto 5000
 * Running on http://0.0.0.0:5000
```

---

## ✅ Verificación Final

### Comandos de Verificación:

```powershell
# 1. Verificar que venv existe
Test-Path venv\Scripts\python.exe
# Debería devolver: True

# 2. Verificar pyvenv.cfg
Get-Content venv\pyvenv.cfg
# NO debe tener /usr/bin

# 3. Activar y verificar Python
.\venv\Scripts\activate.bat
python --version
where python
# Debe apuntar a venv\Scripts\python.exe

# 4. Verificar Flask
python -c "import flask; print(flask.__version__)"
```

---

## 🐛 Solución de Problemas

### Error: "python no se reconoce como comando"

**Solución**: Python no está en el PATH
```powershell
# Agregar Python al PATH manualmente o reinstalar Python
# marcando "Add Python to PATH"
```

### Error: "No module named 'venv'"

**Solución**: Python está instalado pero sin módulo venv
```powershell
# Reinstalar Python con todas las opciones marcadas
# O instalar python-venv
```

### Error: "Execution Policy"

**Solución**: Permitir ejecución de scripts
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### El venv se crea pero sigue buscando /usr/bin

**Solución**: Verificar que estás usando Python de Windows
```powershell
# Ver qué Python estás usando
where python
python --version

# Si muestra rutas de Linux, hay un problema con el PATH
```

---

## 📝 Comandos Completos en Orden

```powershell
# 1. Ir al directorio
cd D:\root\xIA\htdocs\xia.ar\backend

# 2. Eliminar venv (si existe)
Remove-Item -Recurse -Force venv -ErrorAction SilentlyContinue

# 3. Verificar Python
python --version
where python

# 4. Crear venv
python -m venv venv

# 5. Activar venv
.\venv\Scripts\activate.bat

# 6. Actualizar pip
python -m pip install --upgrade pip

# 7. Instalar dependencias
pip install -r requirements.txt

# 8. Verificar
python -c "import flask; print('OK')"

# 9. Ejecutar
python main.py
```

---

> **Nota**: Si después de estos pasos sigue buscando `/usr/bin`, puede haber un problema con el PATH del sistema o con cómo se instaló Python.

