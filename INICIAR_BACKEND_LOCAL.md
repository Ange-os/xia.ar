# 🚀 Iniciar Backend Localmente (Desarrollo)

> **Problema**: El frontend muestra "Error de conexión. Verifica que el servidor esté funcionando."

---

## 🔍 Diagnóstico

El frontend está intentando conectarse a `http://localhost:5000/api/chat`, pero el backend no está corriendo.

---

## ✅ Solución: Iniciar el Backend

### Paso 1: Abrir Terminal en el Directorio Backend

```powershell
# Desde PowerShell o CMD
cd D:\root\xIA\htdocs\xia.ar\backend
```

### Paso 2: Activar Entorno Virtual

```powershell
# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Si tienes problemas con PowerShell, usar:
.\venv\Scripts\activate.bat
```

**Si aparece error de ejecución de scripts en PowerShell:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Paso 3: Verificar que las Dependencias Están Instaladas

```powershell
# Verificar Flask
python -c "import flask; print('Flask:', flask.__version__)"

# Si falta algo, instalar:
pip install -r requirements.txt
```

### Paso 4: Iniciar el Servidor

```powershell
# Iniciar servidor Flask
python main.py
```

**Deberías ver algo como:**
```
💻 Modo DESARROLLO detectado
📁 Buscando archivo .env en: D:\root\xIA\htdocs\xia.ar\backend\.env
🚀 Iniciando xIA Backend API en puerto 5000
📁 Frontend: ../public/
🤖 Agente: SimpleAgent
📧 Email: EmailService
 * Running on http://0.0.0.0:5000
```

### Paso 5: Verificar que Funciona

Abrir en el navegador:
- `http://localhost:5000/api/health`

Debería responder con:
```json
{
  "status": "healthy",
  "timestamp": "...",
  "version": "1.0.0"
}
```

---

## 🌐 Probar el Frontend

Una vez que el backend esté corriendo:

1. **Abrir el frontend**: `http://localhost/xIA/htdocs/xia.ar/public/index.html`
2. **Hacer una consulta** en el chat
3. **Debería funcionar** ✅

---

## 🔧 Configuración Opcional

### Crear Archivo .env (Opcional)

Si quieres configurar variables de entorno:

```powershell
# Crear archivo .env
New-Item -Path .env -ItemType File
```

Editar `.env`:
```env
FLASK_ENV=development
PORT=5000
SECRET_KEY=clave-secreta-desarrollo
```

---

## 🐛 Solución de Problemas

### Error: "No module named 'flask'"

**Solución**: Instalar dependencias
```powershell
pip install -r requirements.txt
```

### Error: "Port 5000 is already in use"

**Solución**: Cambiar puerto o cerrar el proceso
```powershell
# Ver qué está usando el puerto 5000
netstat -ano | findstr :5000

# Cambiar puerto en .env o directamente:
$env:PORT=5001
python main.py
```

### Error: "Execution Policy"

**Solución**: Permitir ejecución de scripts
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### El backend inicia pero el frontend no se conecta

**Verificar**:
1. El backend está corriendo en `http://localhost:5000`
2. Abrir `http://localhost:5000/api/health` en el navegador
3. Verificar la consola del navegador (F12) para ver errores

---

## 📋 Comandos Rápidos

### Todo en uno (PowerShell):

```powershell
cd D:\root\xIA\htdocs\xia.ar\backend
.\venv\Scripts\Activate.ps1
python main.py
```

### Script de Inicio Rápido (crear `start_local.bat`):

```batch
@echo off
cd /d D:\root\xIA\htdocs\xia.ar\backend
call venv\Scripts\activate.bat
python main.py
pause
```

---

## ✅ Checklist

- [ ] Terminal abierta en `D:\root\xIA\htdocs\xia.ar\backend`
- [ ] Entorno virtual activado (`venv\Scripts\activate`)
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Backend corriendo (`python main.py`)
- [ ] Verificar en navegador: `http://localhost:5000/api/health`
- [ ] Probar frontend: `http://localhost/xIA/htdocs/xia.ar/public/index.html`

---

> **Nota**: Mantén la terminal abierta mientras trabajas. Para detener el servidor, presiona `Ctrl+C`.

