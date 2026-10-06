#!/bin/bash
echo Probando sistema de notificaciones...
curl -X POST http://localhost:5000/api/chat -H Content-Type: application/json -d \ -encodedCommand XABcAFwAIgBtAGUAcwBzAGEAZwBlAFwAXABcACIAOgAgAFwAXABcACIAdABlAHMAdAAgAGUAcgByAG8AcgBcAFwAXAAiAA== \
echo Prueba enviada. Revisa tu email.
