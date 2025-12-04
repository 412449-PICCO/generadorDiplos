"""
Configuración centralizada de la aplicación
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()


class Config:
    """Configuración base de la aplicación"""

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    PORT = int(os.getenv('PORT', 8000))

    # Database
    DATABASE_URL = os.getenv(
        'DATABASE_URL',
        'sqlite:///certificados.db'  # Fallback a SQLite para desarrollo
    )

    # Fix para Railway/Heroku (postgres:// -> postgresql://)
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

    # Cloudinary
    CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')
    CLOUDINARY_FOLDER = os.getenv('CLOUDINARY_FOLDER', 'certificados')

    # Admin
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

    # SendGrid
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
    FROM_EMAIL = os.getenv('FROM_EMAIL', 'noreply@example.com')
    FROM_NAME = os.getenv('FROM_NAME', 'Generador de Certificados')

    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    RATELIMIT_STORAGE_URL = os.getenv('RATELIMIT_STORAGE_URL', 'redis://localhost:6379/1')

    # App Settings
    APP_NAME = os.getenv('APP_NAME', 'Generador de Certificados')
    APP_URL = os.getenv('APP_URL', 'http://localhost:8000')
    MAX_BATCH_SIZE = int(os.getenv('MAX_BATCH_SIZE', 1000))

    # Paths
    CERTIFICATES_DIR = 'certificados'
    TEMPLATE_PATH = 'template.svg'

    # Rate Limiting
    RATELIMIT_ENABLED = os.getenv('RATELIMIT_ENABLED', 'True').lower() == 'true'
    RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT', '100 per hour')

    @classmethod
    def validate(cls):
        """Valida que las configuraciones críticas estén presentes"""
        errors = []

        if cls.SECRET_KEY == 'dev-key-change-in-production':
            errors.append('⚠️  SECRET_KEY usando valor por defecto (cambiar en producción)')

        if cls.ADMIN_PASSWORD == 'admin123':
            errors.append('⚠️  ADMIN_PASSWORD usando valor por defecto (cambiar en producción)')

        if not cls.CLOUDINARY_CLOUD_NAME or not cls.CLOUDINARY_API_KEY:
            errors.append('❌ Cloudinary no configurado (CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY)')

        if not cls.SENDGRID_API_KEY:
            errors.append('⚠️  SendGrid no configurado (emails deshabilitados)')

        return errors


config = Config()
