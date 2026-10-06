#!/bin/bash
echo Instalando pip...
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py --user
echo Pip instalado!
