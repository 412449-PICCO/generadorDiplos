"""
Utilidades para el generador de certificados
"""

import re
import unicodedata


def nombre_to_slug(nombre):
    """
    Convierte un nombre a formato slug para URL

    Ejemplos:
        "Frank Vargas" -> "frank-vargas"
        "María José González" -> "maria-jose-gonzalez"
        "O'Brien" -> "obrien"

    Args:
        nombre: Nombre completo de la persona

    Returns:
        slug: Nombre en formato URL-friendly
    """
    # Convertir a minúsculas
    slug = nombre.lower()

    # Normalizar caracteres (quitar acentos)
    slug = unicodedata.normalize('NFKD', slug)
    slug = slug.encode('ascii', 'ignore').decode('ascii')

    # Reemplazar espacios y caracteres especiales con guiones
    slug = re.sub(r'[^a-z0-9]+', '-', slug)

    # Eliminar guiones al inicio y final
    slug = slug.strip('-')

    # Reemplazar múltiples guiones consecutivos con uno solo
    slug = re.sub(r'-+', '-', slug)

    return slug


def generar_slug_unico(nombre, database):
    """
    Genera un slug único para un nombre, agregando número si ya existe

    Ejemplos:
        "Frank Vargas" -> "frank-vargas"
        Si ya existe -> "frank-vargas-2"
        Si frank-vargas-2 existe -> "frank-vargas-3"

    Args:
        nombre: Nombre de la persona
        database: Instancia de Database para verificar existencia

    Returns:
        slug único
    """
    base_slug = nombre_to_slug(nombre)
    slug = base_slug
    contador = 2

    # Verificar si el slug ya existe en la base de datos
    while database.obtener_certificado(slug) is not None:
        slug = f"{base_slug}-{contador}"
        contador += 1

    return slug
