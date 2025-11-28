import os
from datetime import datetime
from utils import generar_slug_unico


class CertificateGenerator:
    def __init__(self, template_path, output_dir, database=None):
        """
        Inicializa el generador de certificados

        Args:
            template_path: Ruta al archivo SVG template
            output_dir: Directorio donde se guardarán los certificados
            database: Instancia opcional de Database para guardar en BD
        """
        self.template_path = template_path
        self.output_dir = output_dir
        self.database = database

        # Verificar que el template existe
        if not os.path.exists(template_path):
            raise FileNotFoundError(f'Template no encontrado: {template_path}')

        # Crear directorio de salida si no existe
        os.makedirs(output_dir, exist_ok=True)

    def generar_certificado(self, nombre, email):
        """
        Genera un certificado personalizado para una persona

        Args:
            nombre: Nombre de la persona
            email: Email de la persona

        Returns:
            dict con información del certificado generado
        """
        # Leer template SVG
        with open(self.template_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()

        # Reemplazar el placeholder del nombre
        # Busca {{NOMBRE}} en el SVG y lo reemplaza
        svg_personalizado = svg_content.replace('{{NOMBRE}}', nombre)

        # Generar slug único para este certificado (ej: "frank-vargas")
        if self.database:
            slug = generar_slug_unico(nombre, self.database)
        else:
            from utils import nombre_to_slug
            slug = nombre_to_slug(nombre)

        # Guardar SVG personalizado
        svg_path = os.path.join(self.output_dir, f'{slug}.svg')
        with open(svg_path, 'w', encoding='utf-8') as f:
            f.write(svg_personalizado)

        # Guardar en base de datos si está disponible
        if self.database:
            self.database.guardar_certificado(
                slug=slug,
                nombre=nombre,
                email=email,
                archivo_svg=f'{slug}.svg'
            )

        return {
            'nombre': nombre,
            'email': email,
            'slug': slug,
            'archivo_svg': f'{slug}.svg',
            'ruta_completa': svg_path,
            'url': f'/certificado/{slug}'
        }

    def generar_desde_archivo(self, archivo_json):
        """
        Genera certificados desde un archivo JSON

        Args:
            archivo_json: Ruta al archivo JSON con los participantes

        Returns:
            lista de resultados
        """
        import json

        with open(archivo_json, 'r', encoding='utf-8') as f:
            data = json.load(f)

        participantes = data.get('participantes', [])
        resultados = []

        for participante in participantes:
            nombre = participante.get('nombre')
            email = participante.get('email')

            if not nombre or not email:
                resultados.append({
                    'error': 'Participante sin nombre o email',
                    'participante': participante
                })
                continue

            try:
                resultado = self.generar_certificado(nombre, email)
                resultados.append(resultado)
            except Exception as e:
                resultados.append({
                    'nombre': nombre,
                    'email': email,
                    'error': str(e)
                })

        return resultados
