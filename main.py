#!/usr/bin/env python3
"""
xIA Backend API
Servidor Flask para consultoría en sistemas
"""

from flask import Flask, request, jsonify, send_from_directory
import os
import sys
import logging
from datetime import datetime

# Detectar entorno y cargar variables de entorno
def load_environment_config():
    """Cargar configuración según el entorno (desarrollo o producción)"""
    
    # Detectar si estamos en desarrollo o producción
    is_production = os.path.exists('/home/xia')  # VPS tiene usuario xia
    
    if is_production:
        # Modo PRODUCCIÓN (VPS)
        env_path = os.path.expanduser('~/.config/xia/.env')
        print(f"🏭 Modo PRODUCCIÓN detectado")
    else:
        # Modo DESARROLLO (máquina local)
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        print(f"💻 Modo DESARROLLO detectado")
    
    print(f"📁 Buscando archivo .env en: {env_path}")
    
    if os.path.exists(env_path):
        try:
            from dotenv import load_dotenv
            load_dotenv(env_path)
            print(f"✅ Variables de entorno cargadas desde: {env_path}")
            return True
        except ImportError:
            print("⚠️ python-dotenv no instalado. Usando variables del sistema.")
            return False
    else:
        print(f"⚠️ Archivo .env no encontrado en: {env_path}")
        print("📋 Crear archivo .env con las variables necesarias")
        return False

# Cargar configuración
load_environment_config()

# Configurar logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/app_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()  # También mostrar en consola
    ]
)

# Intentar importar flask_cors
try:
    from flask_cors import CORS
    cors_available = True
except ImportError:
    print("⚠️ Flask-CORS no está instalado. Instálalo con: pip install flask-cors")
    cors_available = False

# Agregar el directorio padre al path para importar agents como paquete
backend_dir = os.path.dirname(__file__)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Importar agentes
try:
    from agents.agent_simple import SimpleAgent
    from agents.email_service import EmailService
    from agents.notification_service import NotificationService
    agents_available = True
except ImportError as e:
    print(f"⚠️ Error importando agentes: {e}")
    import traceback
    traceback.print_exc()
    agents_available = False

app = Flask(__name__)

# Configurar CORS si está disponible
if cors_available:
    CORS(app)  # Permitir CORS para el frontend
else:
    print("⚠️ CORS deshabilitado - puede causar problemas con el frontend")

# Configuración
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Inicializar servicios
if agents_available:
    agent = SimpleAgent()
    email_service = EmailService()
    notification_service = NotificationService()
    print("✅ Agentes inicializados correctamente")
else:
    print("⚠️ Agentes no disponibles - usando modo de prueba")
    agent = None
    email_service = None
    notification_service = None

# Configurar ruta para archivos estáticos
PUBLIC_DIR = os.path.join(os.path.dirname(__file__), '..', 'public')
PUBLIC_DIR = os.path.abspath(PUBLIC_DIR)

@app.route('/')
def serve_frontend():
    """Servir el frontend estático"""
    return send_from_directory(PUBLIC_DIR, 'index.html')

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """Servir archivos estáticos (imágenes, CSS, JS, etc.)"""
    return send_from_directory(os.path.join(PUBLIC_DIR, 'assets'), filename)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint para consultas del chat"""
    try:
        data = request.get_json()
        
        # Log de la petición
        app.logger.info(f"📨 Chat request recibida: {data}")
        
        if not data or 'message' not in data:
            app.logger.warning("❌ Mensaje requerido faltante")
            return jsonify({'error': 'Mensaje requerido'}), 400
        
        message = data['message'].strip()
        if not message:
            app.logger.warning("❌ Mensaje vacío")
            return jsonify({'error': 'Mensaje no puede estar vacío'}), 400
        
        app.logger.info(f"🤖 Procesando mensaje: '{message}'")
        
        # Procesar con el agente
        if agent:
            app.logger.info("✅ Usando SimpleAgent")
            response = agent.process_message(message)
            app.logger.info(f"📝 Respuesta del agente: '{response[:100]}...'")
        else:
            app.logger.warning("⚠️ Agente no disponible, usando fallback")
            # Modo de prueba cuando el agente no está disponible
            responses = [
                "Entiendo tu consulta. Para sistemas web, te recomiendo usar tecnologías modernas como React o Vue.js para el frontend.",
                "Excelente pregunta. Para bases de datos, considera PostgreSQL para aplicaciones complejas o MongoDB para datos no estructurados.",
                "Para APIs, te sugiero usar Node.js con Express o Python con FastAPI. Ambos son excelentes opciones.",
                "En cuanto a deployment, Docker y Kubernetes son las mejores prácticas para escalabilidad.",
                "Para seguridad, implementa autenticación JWT y siempre valida datos del lado del servidor."
            ]
            import random
            response = random.choice(responses)
            app.logger.info(f"📝 Respuesta fallback: '{response[:100]}...'")
        
        result = {
            'response': response,
            'timestamp': datetime.now().isoformat()
        }
        
        app.logger.info(f"✅ Chat response enviada exitosamente")
        return jsonify(result)
        
    except Exception as e:
        error_msg = str(e)
        app.logger.error(f'❌ Error en chat: {error_msg}')
        app.logger.error(f'❌ Stack trace: {str(e.__traceback__)}')
        
        # Enviar notificación de error por email
        if notification_service:
            try:
                notification_service.send_error_notification(
                    error_type="Chat API Error",
                    error_message=error_msg,
                    error_details=str(e.__traceback__),
                    user_message=data.get('message', 'N/A') if 'data' in locals() else 'N/A'
                )
            except Exception as notify_error:
                app.logger.error(f'❌ Error enviando notificación: {notify_error}')
        
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/email', methods=['POST'])
def send_email():
    """Endpoint para enviar emails de consulta"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'email', 'summary']
        for field in required_fields:
            if not data or field not in data:
                return jsonify({'error': f'Campo {field} requerido'}), 400
        
        # Validar email
        email = data['email'].strip()
        if '@' not in email or '.' not in email.split('@')[1]:
            return jsonify({'error': 'Email inválido'}), 400
        
        # Enviar email
        if email_service:
            result = email_service.send_consultation_email(
                name=data['name'].strip(),
                email=email,
                phone=data.get('phone', '').strip(),
                summary=data['summary'].strip()
            )
        else:
            # Modo de prueba cuando el servicio de email no está disponible
            result = {'success': True, 'message': 'Email simulado enviado'}
        
        if result['success']:
            return jsonify({
                'message': 'Consulta enviada exitosamente',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': result['error']}), 500
            
    except Exception as e:
        error_msg = str(e)
        app.logger.error(f'❌ Error en email: {error_msg}')
        app.logger.error(f'❌ Stack trace: {str(e.__traceback__)}')
        
        # Enviar notificación de error por email
        if notification_service:
            try:
                notification_service.send_error_notification(
                    error_type="Email API Error",
                    error_message=error_msg,
                    error_details=str(e.__traceback__),
                    user_message=data.get('summary', 'N/A') if 'data' in locals() else 'N/A'
                )
            except Exception as notify_error:
                app.logger.error(f'❌ Error enviando notificación: {notify_error}')
        
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint no encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    # Configuración para desarrollo
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    port = int(os.environ.get('PORT', 5000))
    
    print(f"🚀 Iniciando xIA Backend API en puerto {port}")
    print(f"📁 Frontend: ../public/")
    print(f"🤖 Agente: {agent.__class__.__name__ if agent else 'No disponible'}")
    print(f"📧 Email: {email_service.__class__.__name__ if email_service else 'No disponible'}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode,
        threaded=True
    )