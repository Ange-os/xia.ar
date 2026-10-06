# Configuración de Gunicorn para producción
import multiprocessing
import os

# Directorio de trabajo
bind = "127.0.0.1:5000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 60
keepalive = 5

# Logging
accesslog = os.path.join(os.path.dirname(__file__), "logs", "gunicorn_access.log")
errorlog = os.path.join(os.path.dirname(__file__), "logs", "gunicorn_error.log")
loglevel = "info"

# Proceso
daemon = False
pidfile = os.path.join(os.path.dirname(__file__), "gunicorn.pid")

# Usuario y grupo (ajustar según tu configuración)
# user = "xia"
# group = "xia"

# Preload app para mejor rendimiento
preload_app = True

# Máximo de requests por worker antes de reiniciar (previene memory leaks)
max_requests = 1000
max_requests_jitter = 50

