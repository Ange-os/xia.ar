#!/bin/bash
echo \ 🚀 Iniciando despliegue de xIA Backend...\
sudo apt update
sudo apt install -y python3.12-venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo \✅ Despliegue completado!\
