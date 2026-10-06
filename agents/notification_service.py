#!/usr/bin/env python3
"""
Servicio para envío de notificaciones de errores por email
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime

class NotificationService:
    def __init__(self):
        # Cargar variables de entorno desde el directorio padre
        from dotenv import load_dotenv
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        load_dotenv(env_path)
        
        self.smtp_host = os.getenv('SMTP_HOST')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_pass = os.getenv('SMTP_PASS')
        self.admin_email = os.getenv('ADMIN_EMAIL')
        self.app_name = os.getenv('APP_NAME', 'xIA Backend')
        
        if not all([self.smtp_host, self.smtp_user, self.smtp_pass, self.admin_email]):
            print("⚠️ Advertencia: Las credenciales SMTP o el email del administrador no están configurados para notificaciones.")
            self.is_configured = False
        else:
            self.is_configured = True
            print(f"✅ NotificationService configurado para: {self.admin_email}")
    
    def send_error_notification(self, error_type, error_message, error_details, user_message="N/A"):
        """
        Enviar notificación de error por email al administrador
        """
        if not self.is_configured:
            print("❌ Servicio de notificaciones no configurado. No se pudo enviar el email.")
            return False
        
        subject = f"🚨 Error Crítico en {self.app_name}: {error_type}"
        
        # Crear contenido HTML del email
        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 700px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #dc2626; border-bottom: 2px solid #dc2626; padding-bottom: 10px;">
                    🚨 Error Detectado en {self.app_name}
                </h2>
                
                <div style="background-color: #fef2f2; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #dc2626;">
                    <h3 style="color: #dc2626; margin-top: 0;">📋 Información del Error</h3>
                    <p><strong>Tipo de Error:</strong> {error_type}</p>
                    <p><strong>Fecha y Hora:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><strong>Mensaje del Usuario:</strong> {user_message}</p>
                </div>
                
                <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #1e40af; margin-top: 0;">🔍 Detalles del Error</h3>
                    <div style="background-color: white; padding: 15px; border-radius: 4px; border: 1px solid #e5e7eb;">
                        <pre style="white-space: pre-wrap; word-wrap: break-word; margin: 0; font-family: 'Courier New', monospace; font-size: 12px; color: #dc2626;">{error_message}</pre>
                    </div>
                </div>
                
                <div style="background-color: #f0f9ff; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #0369a1; margin-top: 0;">🔧 Stack Trace</h3>
                    <div style="background-color: white; padding: 15px; border-radius: 4px; border: 1px solid #e5e7eb; max-height: 300px; overflow-y: auto;">
                        <pre style="white-space: pre-wrap; word-wrap: break-word; margin: 0; font-family: 'Courier New', monospace; font-size: 11px; color: #374151;">{error_details}</pre>
                    </div>
                </div>
                
                <div style="background-color: #fef3c7; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #92400e; margin-top: 0;">📋 Acciones Recomendadas</h3>
                    <ul style="margin: 0; padding-left: 20px;">
                        <li>Revisar los logs del servidor para más detalles</li>
                        <li>Verificar el estado del servicio de la aplicación</li>
                        <li>Probar la API afectada manualmente</li>
                        <li>Reiniciar el servicio si es necesario</li>
                        <li>Verificar la configuración de la base de datos</li>
                        <li>Revisar el uso de memoria y CPU del servidor</li>
                    </ul>
                </div>
                
                <div style="background-color: #f3f4f6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h4 style="color: #374151; margin-top: 0;">🔗 Enlaces Útiles</h4>
                    <ul style="margin: 0; padding-left: 20px;">
                        <li><strong>Logs del servidor:</strong> /home/xia/htdocs/xia.ar/backend/logs/</li>
                        <li><strong>Estado del servicio:</strong> systemctl status xia-backend</li>
                        <li><strong>Reiniciar servicio:</strong> systemctl restart xia-backend</li>
                        <li><strong>Monitoreo:</strong> htop, df -h, free -m</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
                    <p style="color: #6b7280; font-size: 14px;">
                        Este email fue enviado automáticamente por el sistema de monitoreo de errores de {self.app_name}.<br>
                        <strong>Timestamp:</strong> {datetime.now().isoformat()}
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Crear mensaje
        msg = MIMEMultipart('alternative')
        msg['From'] = self.smtp_user
        msg['To'] = self.admin_email
        msg['Subject'] = subject
        
        # Adjuntar contenido HTML
        html_part = MIMEText(body_html, 'html', 'utf-8')
        msg.attach(html_part)
        
        try:
            # Conectar y enviar
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
            
            print(f"✅ Notificación de error enviada exitosamente a {self.admin_email}")
            return True
            
        except Exception as e:
            print(f"❌ Error al enviar la notificación por email: {e}")
            return False