#!/usr/bin/env python3
"""
WSGI entry point para Gunicorn
"""
import os
import sys

# Agregar el directorio del backend al path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Importar la aplicación Flask
from main import app

# Para Gunicorn
application = app

if __name__ == "__main__":
    # Para desarrollo local
    app.run(host='0.0.0.0', port=5000, debug=False)

