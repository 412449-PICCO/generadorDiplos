"""
Generador de certificados con integración a Cloudinary
"""
import os
from datetime import datetime
from utils import generar_slug_unico
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class CertificateGenerator:
    def __init__(
        self,
        template_path: str,
        database=None,
        cloudinary_storage=None
    ):
        """
        Inicializa el generador de certificados

        Args:
            template_path: Ruta al archivo SVG template
            database: Instancia de Database para guardar en BD
            cloudinary_storage: Instancia de CloudinaryStorage para subir archivos
        """
        self.template_path = template_path
        self.database = database
        self.cloudinary_storage = cloudinary_storage

        # Verificar que el template existe
        if not os.path.exists(template_path):
            raise FileNotFoundError(f'Template no encontrado: {template_path}')

        # Verificar configuración
        if not database:
            logger.warning("Generador inicializado sin base de datos")
        if not cloudinary_storage:
            logger.warning("Generador inicializado sin Cloudinary")

    def generar_certificado(self, nombre: str, email: str) -> Dict[str, Any]:
        """
        Genera un certificado personalizado para una persona

        Args:
            nombre: Nombre de la persona
            email: Email de la persona

        Returns:
            dict con información del certificado generado
        """
        try:
            # Leer template SVG
            with open(self.template_path, 'r', encoding='utf-8') as f:
                svg_content = f.read()

            # Reemplazar el placeholder del nombre
            svg_personalizado = svg_content.replace('{{NOMBRE}}', nombre)

            # Generar slug único para este certificado (ej: "frank-vargas")
            if self.database:
                slug = generar_slug_unico(nombre, self.database)
            else:
                from utils import nombre_to_slug
                slug = nombre_to_slug(nombre)

            # Subir a Cloudinary
            cloudinary_url = None
            cloudinary_public_id = None

            if self.cloudinary_storage and self.cloudinary_storage.configured:
                upload_result = self.cloudinary_storage.upload_svg(svg_personalizado, slug)
                if upload_result:
                    cloudinary_url = upload_result['url']
                    cloudinary_public_id = upload_result['public_id']
                    logger.info(f"Certificado subido a Cloudinary: {slug}")
                else:
                    logger.error(f"Error al subir certificado a Cloudinary: {slug}")
                    raise Exception("Error al subir certificado a Cloudinary")
            else:
                logger.error("Cloudinary no está configurado")
                raise Exception("Cloudinary no está configurado")

            # Guardar en base de datos
            if self.database:
                self.database.guardar_certificado(
                    slug=slug,
                    nombre=nombre,
                    email=email,
                    cloudinary_url=cloudinary_url,
                    cloudinary_public_id=cloudinary_public_id
                )
                logger.info(f"Certificado guardado en BD: {slug}")

            return {
                'nombre': nombre,
                'email': email,
                'slug': slug,
                'cloudinary_url': cloudinary_url,
                'cloudinary_public_id': cloudinary_public_id,
                'url': f'/certificado/{slug}',
                'success': True
            }

        except Exception as e:
            logger.error(f"Error al generar certificado para {nombre}: {e}")
            return {
                'nombre': nombre,
                'email': email,
                'success': False,
                'error': str(e)
            }

    def generar_batch(self, participantes: list) -> Dict[str, Any]:
        """
        Genera certificados en batch para múltiples participantes

        Args:
            participantes: Lista de diccionarios con 'nombre' y 'email'

        Returns:
            dict con resumen y resultados
        """
        resultados = []
        exitosos = 0
        errores = 0

        logger.info(f"Iniciando generación batch de {len(participantes)} certificados")

        for i, participante in enumerate(participantes, 1):
            nombre = participante.get('nombre')
            email = participante.get('email')

            if not nombre or not email:
                errores += 1
                resultados.append({
                    'error': 'Participante sin nombre o email',
                    'participante': participante,
                    'success': False
                })
                continue

            try:
                resultado = self.generar_certificado(nombre, email)
                if resultado.get('success'):
                    exitosos += 1
                else:
                    errores += 1
                resultados.append(resultado)

                # Log progreso cada 50 certificados
                if i % 50 == 0:
                    logger.info(f"Progreso: {i}/{len(participantes)} certificados procesados")

            except Exception as e:
                errores += 1
                logger.error(f"Error al procesar participante {nombre}: {e}")
                resultados.append({
                    'nombre': nombre,
                    'email': email,
                    'error': str(e),
                    'success': False
                })

        logger.info(f"Batch completado: {exitosos} exitosos, {errores} errores")

        return {
            'total': len(participantes),
            'exitosos': exitosos,
            'errores': errores,
            'resultados': resultados
        }

    def generar_desde_archivo(self, archivo_json: str) -> Dict[str, Any]:
        """
        Genera certificados desde un archivo JSON

        Args:
            archivo_json: Ruta al archivo JSON con los participantes

        Returns:
            dict con resultados del batch
        """
        import json

        try:
            with open(archivo_json, 'r', encoding='utf-8') as f:
                data = json.load(f)

            participantes = data.get('participantes', [])
            return self.generar_batch(participantes)

        except Exception as e:
            logger.error(f"Error al leer archivo JSON: {e}")
            return {
                'total': 0,
                'exitosos': 0,
                'errores': 1,
                'error': str(e),
                'resultados': []
            }
