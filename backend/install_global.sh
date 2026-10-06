#!/bin/bash
echo Instalando xIA Backend globalmente...
python3 --version
python3 -m pip install --user --upgrade pip
python3 -m pip install --user Flask Flask-CORS python-dotenv gunicorn Werkzeug
echo Instalacion global completada!
