"""
Convierte texto a paths SVG usando fonttools
"""
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from xml.etree import ElementTree as ET
import re


def text_to_svg_paths(text: str, font_path: str, font_size: float = 38, x: float = 0, y: float = 0, text_anchor: str = 'middle') -> str:
    """
    Convierte texto a paths SVG usando una fuente específica.

    Args:
        text: El texto a convertir
        font_path: Ruta al archivo .ttf de la fuente
        font_size: Tamaño de fuente en píxeles
        x: Posición x del texto
        y: Posición y del texto
        text_anchor: Alineación del texto ('start', 'middle', 'end')

    Returns:
        String con elementos <path> SVG
    """
    # Cargar la fuente
    font = TTFont(font_path)

    # Obtener la tabla de glyphs y métricas
    glyph_set = font.getGlyphSet()
    units_per_em = font['head'].unitsPerEm
    scale = font_size / units_per_em

    # Obtener tabla de kerning si existe
    kern_table = {}
    if 'GPOS' in font:
        # GPOS table for kerning (modern fonts)
        pass
    elif 'kern' in font:
        # Legacy kern table
        kern_table = font['kern'].kernTables[0].kernTable if font['kern'].kernTables else {}

    # Calcular el ancho total del texto
    total_width = 0
    glyph_names = []
    glyph_widths = []

    for char in text:
        # Obtener el nombre del glyph para este carácter
        cmap = font.getBestCmap()
        glyph_name = cmap.get(ord(char), '.notdef')
        glyph_names.append(glyph_name)

        # Obtener el ancho del glyph
        glyph = glyph_set[glyph_name]
        width = glyph.width * scale
        glyph_widths.append(width)
        total_width += width

    # Ajustar posición inicial según text-anchor
    if text_anchor == 'middle':
        current_x = x - (total_width / 2)
    elif text_anchor == 'end':
        current_x = x - total_width
    else:  # 'start'
        current_x = x

    # Generar paths para cada glyph
    paths = []

    for i, (char, glyph_name, width) in enumerate(zip(text, glyph_names, glyph_widths)):
        if glyph_name == '.notdef' or char == ' ':
            current_x += width
            continue

        # Crear un SVGPathPen para extraer el path del glyph
        pen = SVGPathPen(glyph_set)
        glyph = glyph_set[glyph_name]
        glyph.draw(pen)

        # Obtener el path string
        path_data = pen.getCommands()

        if path_data:
            # Aplicar transformaciones: escala, posición
            # Los glyphs están en coordenadas de fuente, necesitamos transformarlos
            transform = f"translate({current_x:.2f},{y:.2f}) scale({scale:.4f},-{scale:.4f})"

            paths.append(f'<path d="{path_data}" transform="{transform}" fill="#010101"/>')

        current_x += width

    return '\n'.join(paths)


def convert_svg_text_to_paths(svg_content: str, font_path: str) -> str:
    """
    Convierte los elementos <text> en un SVG a <path> usando la fuente especificada.

    Args:
        svg_content: Contenido del SVG como string
        font_path: Ruta al archivo .ttf de la fuente

    Returns:
        SVG con texto convertido a paths
    """
    # Registrar namespaces ANTES de parsear para preservarlos
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')

    try:
        root = ET.fromstring(svg_content.encode('utf-8'))
    except ET.ParseError as e:
        # Si falla, intentar limpiando namespaces
        svg_content_clean = re.sub(r'\sxmlns="[^"]+"', '', svg_content, count=1)
        try:
            root = ET.fromstring(svg_content_clean.encode('utf-8'))
        except ET.ParseError:
            # Si aún falla, devolver el contenido original
            print(f"Error al parsear SVG: {e}")
            return svg_content

    # Buscar todos los elementos <text> con namespace correcto
    # Usar búsqueda con namespace explícito
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    text_elements = root.findall('.//{http://www.w3.org/2000/svg}text')

    # Si no encuentra con namespace, buscar sin él
    if not text_elements:
        text_elements = root.findall('.//text')

    for text_elem in text_elements:
        # Solo convertir elementos que usan Montserrat
        style = text_elem.get('style', '')
        if 'Montserrat' not in style:
            continue

        # Buscar el tspan dentro del text
        tspan = text_elem.find('.//{http://www.w3.org/2000/svg}tspan')
        if tspan is None:
            tspan = text_elem.find('.//tspan')

        if tspan is None or not tspan.text:
            continue

        # Obtener atributos del text element
        transform_attr = text_elem.get('transform', '')
        text_anchor = text_elem.get('text-anchor', 'start')

        # Extraer posición del transform
        # Formato: "translate(420.94 270)"
        match = re.search(r'translate\(([0-9.]+)\s+([0-9.]+)\)', transform_attr)
        if match:
            x = float(match.group(1))
            y = float(match.group(2))
        else:
            x = float(text_elem.get('x', 0))
            y = float(text_elem.get('y', 0))

        # Obtener el texto
        text_content = tspan.text

        # Extraer tamaño de fuente del style o atributo
        style = text_elem.get('style', '')
        font_size = 38  # default
        size_match = re.search(r'font-size:\s*([0-9.]+)px', style)
        if size_match:
            font_size = float(size_match.group(1))

        # Convertir texto a paths
        paths_svg = text_to_svg_paths(
            text_content,
            font_path,
            font_size=font_size,
            x=x,
            y=y,
            text_anchor=text_anchor
        )

        # Crear un grupo para contener los paths
        group = ET.Element('g')
        group.set('id', 'converted-text')

        # Parsear los paths y agregarlos al grupo
        for path_line in paths_svg.split('\n'):
            if path_line.strip():
                try:
                    path_elem = ET.fromstring(path_line)
                    group.append(path_elem)
                except ET.ParseError:
                    # Si falla el parsing de un path, continuar con el siguiente
                    continue

        # Reemplazar el elemento text con el grupo
        parent = None
        for elem in root.iter():
            if text_elem in list(elem):
                parent = elem
                break

        if parent is not None:
            index = list(parent).index(text_elem)
            parent.remove(text_elem)
            parent.insert(index, group)

    # Convertir de vuelta a string preservando namespaces
    result = ET.tostring(root, encoding='unicode', method='xml')

    # Agregar declaración XML si no existe
    if not result.startswith('<?xml'):
        result = '<?xml version="1.0" encoding="UTF-8"?>\n' + result

    return result


if __name__ == '__main__':
    # Test
    import sys

    # Leer template.svg
    with open('template.svg', 'r', encoding='utf-8') as f:
        svg_content = f.read()

    # Reemplazar placeholder con nombre de prueba
    svg_content = svg_content.replace('{{NOMBRE}}', 'Juan Pérez González')

    # Convertir a paths
    result = convert_svg_text_to_paths(svg_content, '/tmp/Montserrat-ExtraBold.ttf')

    # Guardar resultado
    with open('/tmp/test_paths.svg', 'w', encoding='utf-8') as f:
        f.write(result)

    print("Test SVG generado en /tmp/test_paths.svg")
