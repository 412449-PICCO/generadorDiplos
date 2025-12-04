"""
Servicio de envío de emails con SendGrid
"""
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Servicio para enviar emails a participantes"""

    def __init__(self, api_key: str, from_email: str, from_name: str, app_url: str):
        """
        Inicializa el servicio de email

        Args:
            api_key: API key de SendGrid
            from_email: Email del remitente
            from_name: Nombre del remitente
            app_url: URL base de la aplicación
        """
        self.api_key = api_key
        self.from_email = from_email
        self.from_name = from_name
        self.app_url = app_url.rstrip('/')
        self.configured = bool(api_key and api_key != 'your_sendgrid_api_key')

        if self.configured:
            self.client = SendGridAPIClient(api_key)
            logger.info("SendGrid configurado correctamente")
        else:
            self.client = None
            logger.warning("SendGrid no está configurado")

    def enviar_certificado(
        self,
        email: str,
        nombre: str,
        slug: str,
        asunto: Optional[str] = None
    ) -> bool:
        """
        Envía un email con el link al certificado

        Args:
            email: Email del destinatario
            nombre: Nombre del destinatario
            slug: Slug del certificado
            asunto: Asunto personalizado (opcional)

        Returns:
            True si se envió correctamente, False en caso contrario
        """
        if not self.configured:
            logger.error("No se puede enviar email: SendGrid no configurado")
            return False

        try:
            # URL del certificado
            certificado_url = f"{self.app_url}/certificado/{slug}"

            # Asunto
            if not asunto:
                asunto = "Tu certificado está listo"

            # Contenido HTML
            html_content = self._generar_html_email(nombre, certificado_url)

            # Crear mensaje
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(email),
                subject=asunto,
                html_content=Content("text/html", html_content)
            )

            # Enviar
            response = self.client.send(message)

            if response.status_code in [200, 201, 202]:
                logger.info(f"Email enviado exitosamente a {email}")
                return True
            else:
                logger.error(f"Error al enviar email a {email}: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error al enviar email a {email}: {e}")
            return False

    def enviar_batch(
        self,
        certificados: List[Dict[str, str]],
        asunto: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Envía emails en batch

        Args:
            certificados: Lista de dicts con 'email', 'nombre', 'slug'
            asunto: Asunto personalizado (opcional)

        Returns:
            Dict con resultados del envío
        """
        if not self.configured:
            logger.error("No se puede enviar emails: SendGrid no configurado")
            return {
                'total': len(certificados),
                'exitosos': 0,
                'errores': len(certificados),
                'error': 'SendGrid no configurado'
            }

        exitosos = 0
        errores = 0
        resultados = []

        logger.info(f"Iniciando envío batch de {len(certificados)} emails")

        for i, cert in enumerate(certificados, 1):
            email = cert.get('email')
            nombre = cert.get('nombre')
            slug = cert.get('slug')

            if not email or not nombre or not slug:
                errores += 1
                resultados.append({
                    'email': email,
                    'success': False,
                    'error': 'Datos incompletos'
                })
                continue

            try:
                success = self.enviar_certificado(email, nombre, slug, asunto)
                if success:
                    exitosos += 1
                    resultados.append({
                        'email': email,
                        'success': True
                    })
                else:
                    errores += 1
                    resultados.append({
                        'email': email,
                        'success': False,
                        'error': 'Error al enviar'
                    })

                # Log progreso cada 50 emails
                if i % 50 == 0:
                    logger.info(f"Progreso: {i}/{len(certificados)} emails enviados")

            except Exception as e:
                errores += 1
                logger.error(f"Error al enviar email a {email}: {e}")
                resultados.append({
                    'email': email,
                    'success': False,
                    'error': str(e)
                })

        logger.info(f"Batch completado: {exitosos} exitosos, {errores} errores")

        return {
            'total': len(certificados),
            'exitosos': exitosos,
            'errores': errores,
            'resultados': resultados
        }

    def _generar_html_email(self, nombre: str, certificado_url: str) -> str:
        """
        Genera el HTML del email

        Args:
            nombre: Nombre del destinatario
            certificado_url: URL del certificado

        Returns:
            HTML del email
        """
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 40px 20px;
                    border-radius: 10px;
                    text-align: center;
                    color: white;
                }}
                .content {{
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    margin-top: 20px;
                    color: #333;
                }}
                .button {{
                    display: inline-block;
                    padding: 15px 40px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                    font-weight: bold;
                }}
                .footer {{
                    margin-top: 30px;
                    font-size: 12px;
                    color: #666;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>¡Felicitaciones, {nombre}!</h1>
                <p>Tu certificado está listo</p>
            </div>

            <div class="content">
                <p>Hola <strong>{nombre}</strong>,</p>

                <p>Nos complace informarte que tu certificado ha sido generado exitosamente.</p>

                <p>Puedes ver y descargar tu certificado haciendo clic en el siguiente botón:</p>

                <a href="{certificado_url}" class="button">Ver mi certificado</a>

                <p>O copia y pega este enlace en tu navegador:</p>
                <p style="word-break: break-all; color: #667eea;">{certificado_url}</p>

                <p>Este certificado es permanente y podrás acceder a él en cualquier momento.</p>
            </div>

            <div class="footer">
                <p>Este es un email automático, por favor no respondas a este mensaje.</p>
            </div>
        </body>
        </html>
        """
