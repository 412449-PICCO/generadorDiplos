"""
Módulo para manejar almacenamiento en Cloudinary
"""
import cloudinary
import cloudinary.uploader
import cloudinary.api
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class CloudinaryStorage:
    """Maneja operaciones de almacenamiento en Cloudinary"""

    def __init__(self, cloud_name: str, api_key: str, api_secret: str, folder: str = 'certificados'):
        """
        Inicializa la conexión con Cloudinary

        Args:
            cloud_name: Nombre del cloud en Cloudinary
            api_key: API key de Cloudinary
            api_secret: API secret de Cloudinary
            folder: Carpeta en Cloudinary donde se guardarán los certificados
        """
        self.folder = folder
        self.configured = False

        try:
            cloudinary.config(
                cloud_name=cloud_name,
                api_key=api_key,
                api_secret=api_secret,
                secure=True
            )
            self.configured = True
            logger.info(f"Cloudinary configurado correctamente: {cloud_name}/{folder}")
        except Exception as e:
            logger.error(f"Error al configurar Cloudinary: {e}")
            self.configured = False

    def upload_svg(self, svg_content: str, public_id: str) -> Optional[Dict[str, Any]]:
        """
        Sube un archivo SVG a Cloudinary

        Args:
            svg_content: Contenido del SVG como string
            public_id: ID público del archivo (ej: "frank-vargas")

        Returns:
            Diccionario con información del archivo subido o None si falla
        """
        if not self.configured:
            logger.error("Cloudinary no está configurado")
            return None

        try:
            import tempfile
            import os

            # Crear archivo temporal con el SVG
            with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False, encoding='utf-8') as tmp:
                tmp.write(svg_content)
                tmp_path = tmp.name

            try:
                # Subir el archivo temporal a Cloudinary como raw
                # raw permite que el navegador lo muestre inline sin forzar descarga
                result = cloudinary.uploader.upload(
                    tmp_path,
                    folder=self.folder,
                    public_id=public_id,
                    resource_type='raw',  # Usar 'raw' para servir sin procesar
                    overwrite=True,
                    invalidate=True,
                    access_mode='public'  # Acceso público sin forzar descarga
                )

                logger.info(f"SVG subido exitosamente: {public_id}")

                return {
                    'public_id': result['public_id'],
                    'url': result['secure_url'],
                    'format': result.get('format', 'svg'),
                    'bytes': result.get('bytes', 0),
                    'created_at': result.get('created_at', '')
                }
            finally:
                # Limpiar archivo temporal
                try:
                    os.unlink(tmp_path)
                except:
                    pass

        except Exception as e:
            logger.error(f"Error al subir SVG a Cloudinary: {e}")
            return None

    def get_url(self, public_id: str, transformation: Optional[Dict] = None) -> str:
        """
        Obtiene la URL de un archivo en Cloudinary para visualización inline

        Args:
            public_id: ID público del archivo
            transformation: Transformaciones opcionales (resize, format, etc)

        Returns:
            URL del archivo para visualización inline en navegador
        """
        try:
            # Construir URL directa para raw resources - se muestra inline por defecto
            # Formato: https://res.cloudinary.com/{cloud_name}/raw/upload/{folder}/{public_id}.svg
            from cloudinary import config as cloudinary_config
            cloud_name = cloudinary_config().cloud_name

            return f"https://res.cloudinary.com/{cloud_name}/raw/upload/{self.folder}/{public_id}.svg"
        except Exception as e:
            logger.error(f"Error al obtener URL de Cloudinary: {e}")
            return ""

    def get_svg_content(self, public_id: str) -> Optional[str]:
        """
        Descarga el contenido del SVG desde Cloudinary

        Args:
            public_id: ID público del archivo

        Returns:
            Contenido del SVG como string o None si falla
        """
        try:
            import requests
            url = self.get_url(public_id)
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error al descargar SVG de Cloudinary: {e}")
            return None

    def get_png_url(self, public_id: str, width: int = 1200, height: int = 675) -> str:
        """
        Obtiene URL del SVG convertido a PNG
        NOTA: No disponible con resource_type='raw', retorna URL del SVG

        Args:
            public_id: ID público del archivo
            width: Ancho del PNG
            height: Alto del PNG

        Returns:
            URL del SVG (conversión a PNG no disponible con raw)
        """
        # Con resource_type='raw' no hay transformaciones disponibles
        # Retornar la URL del SVG directamente
        return self.get_url(public_id)

    def delete(self, public_id: str) -> bool:
        """
        Elimina un archivo de Cloudinary

        Args:
            public_id: ID público del archivo

        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        if not self.configured:
            logger.error("Cloudinary no está configurado")
            return False

        try:
            result = cloudinary.uploader.destroy(
                f"{self.folder}/{public_id}",
                resource_type='raw',
                invalidate=True
            )
            logger.info(f"Archivo eliminado de Cloudinary: {public_id}")
            return result.get('result') == 'ok'
        except Exception as e:
            logger.error(f"Error al eliminar archivo de Cloudinary: {e}")
            return False

    def exists(self, public_id: str) -> bool:
        """
        Verifica si un archivo existe en Cloudinary

        Args:
            public_id: ID público del archivo

        Returns:
            True si existe, False en caso contrario
        """
        if not self.configured:
            return False

        try:
            cloudinary.api.resource(
                f"{self.folder}/{public_id}",
                resource_type='raw'
            )
            return True
        except cloudinary.exceptions.NotFound:
            return False
        except Exception as e:
            logger.error(f"Error al verificar existencia en Cloudinary: {e}")
            return False

    @staticmethod
    def _encode_svg(svg_content: str) -> str:
        """
        Codifica contenido SVG a base64

        Args:
            svg_content: Contenido del SVG

        Returns:
            SVG codificado en base64
        """
        import base64
        return base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')

    def get_usage(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene información de uso de Cloudinary

        Returns:
            Diccionario con información de uso o None si falla
        """
        if not self.configured:
            return None

        try:
            usage = cloudinary.api.usage()
            return {
                'used_credits': usage.get('credits', {}).get('usage', 0),
                'limit_credits': usage.get('credits', {}).get('limit', 0),
                'storage_used': usage.get('storage', {}).get('usage', 0),
                'storage_limit': usage.get('storage', {}).get('limit', 0),
                'bandwidth_used': usage.get('bandwidth', {}).get('usage', 0),
                'bandwidth_limit': usage.get('bandwidth', {}).get('limit', 0)
            }
        except Exception as e:
            logger.error(f"Error al obtener uso de Cloudinary: {e}")
            return None
