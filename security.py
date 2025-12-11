"""
Utilidades de seguridad para la aplicación
"""
import re
import logging
from functools import wraps
from flask import request, jsonify
from urllib.parse import urlparse
from config import config

logger = logging.getLogger(__name__)


def require_admin_ip(f):
    """
    Decorator que restringe acceso solo a IPs permitidas.
    Usado para proteger endpoints de administración.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr

        # Si no hay IPs configuradas, denegar acceso en producción
        if not config.ADMIN_ALLOWED_IPS:
            if not config.DEBUG:
                logger.warning(f"Acceso denegado desde {client_ip} - No hay IPs configuradas")
                return jsonify({
                    'error': 'Acceso denegado',
                    'message': 'Configurar ADMIN_ALLOWED_IPS en variables de entorno'
                }), 403

        # Verificar si la IP está en la lista permitida
        if config.ADMIN_ALLOWED_IPS and client_ip not in config.ADMIN_ALLOWED_IPS:
            logger.warning(f"Acceso denegado desde IP no autorizada: {client_ip}")
            return jsonify({
                'error': 'Acceso denegado',
                'message': 'Tu IP no tiene permisos para acceder a este recurso'
            }), 403

        logger.info(f"Acceso autorizado desde IP: {client_ip}")
        return f(*args, **kwargs)

    return decorated_function


def validate_slug(slug: str) -> bool:
    """
    Valida que el slug solo contenga caracteres seguros.

    Previene path traversal y otros ataques.
    Formato permitido: letras minúsculas, números, guiones y underscore

    Args:
        slug: El slug a validar

    Returns:
        True si es válido, False si no
    """
    if not slug:
        return False

    # Solo permitir: letras minúsculas, números, guiones y underscore
    # Longitud máxima 100 caracteres
    pattern = r'^[a-z0-9\-_]{1,100}$'

    if not re.match(pattern, slug):
        logger.warning(f"Slug inválido rechazado: {slug}")
        return False

    # Prevenir slugs que sean solo puntos o guiones
    if slug in ['.', '..', '-', '--']:
        return False

    return True


def validate_cloudinary_url(url: str) -> bool:
    """
    Valida que una URL sea de Cloudinary.

    Previene SSRF (Server-Side Request Forgery) verificando
    que solo se acceda a URLs de Cloudinary.

    Args:
        url: La URL a validar

    Returns:
        True si es una URL válida de Cloudinary, False si no
    """
    if not url:
        return False

    try:
        parsed = urlparse(url)

        # Verificar que sea HTTPS
        if parsed.scheme != 'https':
            logger.warning(f"URL rechazada (no HTTPS): {url}")
            return False

        # Dominios permitidos de Cloudinary
        allowed_domains = [
            'res.cloudinary.com',
            'cloudinary.com'
        ]

        # Verificar que el dominio esté en la lista permitida
        hostname = parsed.netloc.lower()
        is_valid = any(hostname == domain or hostname.endswith('.' + domain)
                      for domain in allowed_domains)

        if not is_valid:
            logger.warning(f"URL rechazada (dominio no permitido): {url}")

        return is_valid

    except Exception as e:
        logger.error(f"Error al validar URL: {e}")
        return False


def sanitize_error_message(error: Exception, debug: bool = False) -> str:
    """
    Sanitiza mensajes de error para no revelar información sensible.

    Args:
        error: La excepción original
        debug: Si está en modo debug, mostrar más detalles

    Returns:
        Mensaje de error sanitizado
    """
    if debug:
        return str(error)

    # En producción, retornar mensaje genérico
    return "Error interno del servidor"
