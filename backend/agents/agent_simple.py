"""
Agente simplificado para consultoría en sistemas
"""

import re
import random
from typing import Dict, List, Optional

class SimpleAgent:
    """
    Agente especializado en consultoría de sistemas de programación
    """
    
    def __init__(self):
        self.responses = {
            'web': [
                'Para desarrollo web moderno, te recomiendo React o Vue.js para el frontend, con Node.js o Python para el backend.',
                'Considera usar TypeScript para proyectos web grandes, mejora la mantenibilidad del código.',
                'Para SEO y rendimiento, Next.js o Nuxt.js son excelentes opciones con SSR.',
                'Implementa PWA (Progressive Web App) para mejor experiencia móvil.'
            ],
            'database': [
                'PostgreSQL es ideal para aplicaciones complejas con relaciones, MongoDB para datos no estructurados.',
                'Para alta disponibilidad, considera Redis para caché y PostgreSQL con replicación.',
                'Diseña índices apropiados y normaliza correctamente para optimizar consultas.',
                'Usa migraciones de base de datos para control de versiones del esquema.'
            ],
            'api': [
                'REST es estándar, pero GraphQL ofrece más flexibilidad para consultas complejas.',
                'Implementa autenticación JWT y rate limiting para seguridad.',
                'Documenta tu API con Swagger/OpenAPI para mejor mantenimiento.',
                'Usa versionado de API (v1, v2) para compatibilidad hacia atrás.'
            ],
            'deployment': [
                'Docker containeriza tu aplicación para consistencia entre entornos.',
                'Kubernetes maneja el orquestamiento y escalado automático.',
                'CI/CD con GitHub Actions o GitLab CI automatiza el despliegue.',
                'Monitorea con herramientas como Prometheus y Grafana.'
            ],
            'security': [
                'Implementa HTTPS, validación de entrada y sanitización de datos.',
                'Usa OAuth 2.0 para autenticación de terceros.',
                'Aplica el principio de menor privilegio en permisos.',
                'Realiza auditorías de seguridad regulares y pruebas de penetración.'
            ],
            'mobile': [
                'React Native o Flutter para desarrollo multiplataforma eficiente.',
                'Swift para iOS nativo, Kotlin para Android nativo.',
                'Considera PWA como alternativa económica a apps nativas.',
                'Implementa notificaciones push y offline-first architecture.'
            ],
            'ai': [
                'Python con TensorFlow o PyTorch para machine learning.',
                'APIs como OpenAI GPT o Google BERT para NLP.',
                'Considera edge computing para inferencia en tiempo real.',
                'Implementa pipelines de ML con MLOps para producción.'
            ]
        }
        
        self.general_responses = [
            'Excelente pregunta. Para darte la mejor recomendación, ¿podrías contarme más detalles sobre tu proyecto?',
            'Entiendo tu consulta. Te sugiero considerar la escalabilidad y mantenibilidad a largo plazo.',
            'Buena pregunta. ¿Has considerado las alternativas de código abierto vs soluciones comerciales?',
            'Interesante. ¿Cuál es el tamaño de tu equipo de desarrollo y el presupuesto disponible?',
            'Para esta consulta, te recomiendo hacer un prototipo primero para validar la solución.'
        ]
    
    def process_message(self, message: str) -> str:
        """
        Procesa un mensaje y devuelve una respuesta contextual
        """
        message_lower = message.lower()
        
        # Detectar categoría de la consulta
        category = self._detect_category(message_lower)
        
        if category and category in self.responses:
            response = random.choice(self.responses[category])
            return f"{response} ¿Te gustaría que profundice en algún aspecto específico?"
        
        # Respuesta general si no se detecta categoría específica
        return random.choice(self.general_responses)
    
    def _detect_category(self, message: str) -> Optional[str]:
        """
        Detecta la categoría de la consulta basada en palabras clave
        """
        keywords = {
            'web': ['web', 'frontend', 'backend', 'react', 'vue', 'angular', 'html', 'css', 'javascript'],
            'database': ['base de datos', 'database', 'sql', 'postgresql', 'mysql', 'mongodb', 'redis'],
            'api': ['api', 'rest', 'graphql', 'endpoint', 'microservicio'],
            'deployment': ['deploy', 'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'servidor'],
            'security': ['seguridad', 'security', 'autenticación', 'autorización', 'jwt', 'oauth'],
            'mobile': ['móvil', 'mobile', 'app', 'ios', 'android', 'react native', 'flutter'],
            'ai': ['ia', 'ai', 'machine learning', 'ml', 'inteligencia artificial', 'neural']
        }
        
        for category, words in keywords.items():
            if any(word in message for word in words):
                return category
        
        return None