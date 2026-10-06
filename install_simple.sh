#!/bin/bash
echo Instalando xIA Backend...
python3 --version
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo Instalacion completada!
