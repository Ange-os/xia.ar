"""
Servicio de email para consultas
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Optional

class EmailService:
    """
    Servicio para enviar emails de consultas
    """
    
    def __init__(self):
        # Cargar variables de entorno desde el directorio padre
        from dotenv import load_dotenv
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        load_dotenv(env_path)
        
        self.smtp_host = os.getenv('SMTP_HOST')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_pass = os.getenv('SMTP_PASS')
        self.consultation_email = os.getenv('CONSULTATION_EMAIL', 'alefield@gmail.com')
        
        if not all([self.smtp_host, self.smtp_user, self.smtp_pass]):
            print("⚠️ Advertencia: Las credenciales SMTP no están configuradas.")
            self.is_configured = False
        else:
            self.is_configured = True
            print(f"✅ EmailService configurado para: {self.smtp_user}")
        
        # Configuración de la empresa
        self.company_name = 'xIA'
        self.company_email = 'info@xia.ar'
    
    def send_consultation_email(self, name: str, email: str, phone: str, summary: str) -> Dict[str, any]:
        """
        Envía un email con la consulta del cliente
        """
        try:
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = self.company_email
            msg['To'] = self.consultation_email
            msg['Subject'] = f'[xIA] Nueva consulta de {name}'
            
            # Crear contenido del email
            body = self._create_email_body(name, email, phone, summary)
            msg.attach(MIMEText(body, 'html', 'utf-8'))
            
            # Enviar email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            return {
                'success': True,
                'message': 'Email enviado exitosamente',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al enviar email: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def _create_email_body(self, name: str, email: str, phone: str, summary: str) -> str:
        """
        Crea el contenido HTML del email
        """
        phone_display = f"<strong>Teléfono:</strong> {phone}<br>" if phone else ""
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-inline-size: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #4f8cff; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 8px 8px; }}
                .field {{ margin-block-end: 15px; }}
                .label {{ font-weight: bold; color: #4f8cff; }}
                .summary {{ background: white; padding: 15px; border-inline-start: 4px solid #4f8cff; margin: 15px 0; }}
                .footer {{ text-align: center; margin-block-start: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🔍 Nueva Consulta - xIA</h2>
                </div>
                <div class="content">
                    <div class="field">
                        <span class="label">Cliente:</span> {name}
                    </div>
                    <div class="field">
                        <span class="label">Email:</span> {email}
                    </div>
                    {phone_display}
                    <div class="field">
                        <span class="label">Fecha:</span> {datetime.now().strftime('%d/%m/%Y %H:%M')}
                    </div>
                    
                    <div class="summary">
                        <span class="label">Resumen de la consulta:</span><br>
                        {summary.replace(chr(10), '<br>')}
                    </div>
                    
                    <div class="footer">
                        <p>Este email fue generado automáticamente por el sistema de consultas xIA</p>
                        <p>Responder a: {email}</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_body