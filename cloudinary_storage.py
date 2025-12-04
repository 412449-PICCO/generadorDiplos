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
            # Subir SVG como raw file
            result = cloudinary.uploader.upload(
                f"data:image/svg+xml;base64,{self._encode_svg(svg_content)}",
                folder=self.folder,
                public_id=public_id,
                resource_type='raw',
                overwrite=True,
                invalidate=True
            )

            logger.info(f"SVG subido exitosamente: {public_id}")

            return {
                'public_id': result['public_id'],
                'url': result['secure_url'],
                'format': result['format'],
                'bytes': result['bytes'],
                'created_at': result['created_at']
            }

        except Exception as e:
            logger.error(f"Error al subir SVG a Cloudinary: {e}")
            return None

    def get_url(self, public_id: str, transformation: Optional[Dict] = None) -> str:
        """
        Obtiene la URL de un archivo en Cloudinary

        Args:
            public_id: ID público del archivo
            transformation: Transformaciones opcionales (resize, format, etc)

        Returns:
            URL del archivo
        """
        try:
            if transformation:
                return cloudinary.CloudinaryImage(f"{self.folder}/{public_id}").build_url(**transformation)
            else:
                return cloudinary.CloudinaryImage(f"{self.folder}/{public_id}").build_url()
        except Exception as e:
            logger.error(f"Error al obtener URL de Cloudinary: {e}")
            return ""

    def get_png_url(self, public_id: str, width: int = 1200, height: int = 675) -> str:
        """
        Obtiene URL del SVG convertido a PNG

        Args:
            public_id: ID público del archivo
            width: Ancho del PNG
            height: Alto del PNG

        Returns:
            URL del PNG
        """
        return self.get_url(
            public_id,
            transformation={
                'format': 'png',
                'width': width,
                'height': height,
                'crop': 'fit'
            }
        )

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
