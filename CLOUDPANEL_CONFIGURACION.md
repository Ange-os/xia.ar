# 🔧 Configuración de CloudPanel para xia.ar (Flask/Python)

## Problema Identificado

CloudPanel está configurado para PHP, pero la aplicación usa **Flask (Python)**. Necesitamos configurar Nginx para hacer proxy reverso a Flask/Gunicorn.

---

## 📋 Pasos de Configuración

### Paso 1: Cambiar Root Directory en CloudPanel

1. Ir a **CloudPanel** → **Sites** → **xia.ar**
2. En **Domain Settings**, cambiar:
   - **Root Directory**: De `xia.ar/public` a `xia.ar` (directorio raíz del proyecto)
   - Esto permite que Nginx maneje tanto el frontend como el proxy al backend

### Paso 2: Agregar Configuración Nginx Personalizada

1. En CloudPanel, ir a **xia.ar** → **Settings** → **Nginx Configuration**
2. En la sección **Additional Nginx Directives**, agregar el contenido de `nginx-cloudpanel.conf`:

```nginx
# Proxy para API del backend Flask (DEBE estar ANTES de location /)
location /api {
    proxy_pass http://127.0.0.1:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-Port $server_port;
    
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
}

# Servir archivos estáticos del frontend
location / {
    try_files $uri $uri/ @flask;
}

# Proxy para Flask (sirve el index.html y otros archivos)
location @flask {
    proxy_pass http://127.0.0.1:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# Servir archivos estáticos directamente
location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
    root /home/xia/htdocs/xia.ar/public;
    expires 30d;
    add_header Cache-Control "public, immutable";
    access_log off;
}
```

3. **Guardar** la configuración

### Paso 3: Instalar Python y Dependencias

Conectarse por SSH al VPS y ejecutar:

```bash
# Ir al directorio del backend
cd /home/xia/htdocs/xia.ar/backend

# Crear entorno virtual (si no existe)
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Instalar Gunicorn si no está en requirements.txt
pip install gunicorn
```

### Paso 4: Crear Servicio Systemd para Flask

Crear el servicio para que Flask se inicie automáticamente:

```bash
sudo nano /etc/systemd/system/xia-backend.service
```

Contenido del archivo:

```ini
[Unit]
Description=xIA Backend API (Flask/Gunicorn)
After=network.target

[Service]
Type=notify
User=xia
Group=xia
WorkingDirectory=/home/xia/htdocs/xia.ar/backend
Environment="PATH=/home/xia/htdocs/xia.ar/backend/venv/bin"
ExecStart=/home/xia/htdocs/xia.ar/backend/venv/bin/gunicorn -c gunicorn_config.py wsgi:application
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Habilitar y iniciar el servicio:

```bash
# Recargar systemd
sudo systemctl daemon-reload

# Habilitar para que inicie al arrancar
sudo systemctl enable xia-backend

# Iniciar el servicio
sudo systemctl start xia-backend

# Verificar estado
sudo systemctl status xia-backend
```

### Paso 5: Verificar Funcionamiento

```bash
# Verificar que el backend está corriendo
curl http://localhost:5000/api/health

# Ver logs del servicio
sudo journalctl -u xia-backend -f

# Ver logs de Gunicorn
tail -f /home/xia/htdocs/xia.ar/backend/logs/gunicorn_error.log
```

### Paso 6: Probar desde el Navegador

1. Abrir `https://xia.ar` en el navegador
2. Verificar que el frontend carga correctamente
3. Probar el chat para verificar que se conecta al backend
4. Verificar la consola del navegador (F12) para ver si hay errores

---

## 🔍 Solución de Problemas

### Error: 502 Bad Gateway

**Causa**: El backend no está corriendo o Nginx no puede conectarse.

**Solución**:
```bash
# Verificar que el servicio está corriendo
sudo systemctl status xia-backend

# Verificar que Gunicorn está escuchando en el puerto 5000
sudo netstat -tlnp | grep 5000

# Reiniciar el servicio
sudo systemctl restart xia-backend
```

### Error: 404 Not Found en /api/chat

**Causa**: La configuración de Nginx no está correcta o el proxy no está funcionando.

**Solución**:
1. Verificar que la configuración de Nginx se guardó correctamente
2. Verificar sintaxis de Nginx: `sudo nginx -t`
3. Recargar Nginx: `sudo systemctl reload nginx`

### Error: Frontend carga pero el chat no funciona

**Causa**: El frontend está intentando conectarse a `localhost:5000` en lugar de usar rutas relativas.

**Solución**: El frontend ya tiene la lógica correcta en `getAPIBaseURL()`. Verificar que está funcionando correctamente.

### Ver Logs

```bash
# Logs del servicio systemd
sudo journalctl -u xia-backend -n 50

# Logs de Gunicorn
tail -f /home/xia/htdocs/xia.ar/backend/logs/gunicorn_error.log
tail -f /home/xia/htdocs/xia.ar/backend/logs/gunicorn_access.log

# Logs de la aplicación Flask
tail -f /home/xia/htdocs/xia.ar/backend/logs/app_*.log

# Logs de Nginx
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

---

## 📝 Notas Importantes

1. **PHP Settings en CloudPanel**: Aunque CloudPanel muestre configuración PHP, no afectará a Flask. La configuración de Nginx personalizada tiene prioridad.

2. **PageSpeed**: Las configuraciones de PageSpeed en CloudPanel seguirán funcionando para archivos estáticos.

3. **SSL/HTTPS**: CloudPanel maneja automáticamente los certificados SSL. No es necesario configurar nada adicional.

4. **Permisos**: Asegurarse de que el usuario `xia` tenga permisos para:
   - Leer archivos en `/home/xia/htdocs/xia.ar/`
   - Escribir en `/home/xia/htdocs/xia.ar/backend/logs/`

---

## ✅ Checklist de Verificación

- [ ] Root Directory cambiado a `xia.ar` en CloudPanel
- [ ] Configuración Nginx personalizada agregada
- [ ] Python 3 y dependencias instaladas
- [ ] Entorno virtual creado y activado
- [ ] Gunicorn instalado
- [ ] Servicio systemd creado y habilitado
- [ ] Backend corriendo (verificar con `systemctl status`)
- [ ] Health check funciona (`curl http://localhost:5000/api/health`)
- [ ] Frontend carga correctamente
- [ ] Chat funciona y se conecta al backend
- [ ] Logs sin errores críticos

---

**Última actualización**: 2025-01-XX

