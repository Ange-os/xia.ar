#!/bin/bash
echo \ 🚀 Instalando xIA Backend en VPS...\
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev python3-pip
sudo apt install -y build-essential libssl-dev libffi-dev python3-dev
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo \✅ Instalación completada!\
