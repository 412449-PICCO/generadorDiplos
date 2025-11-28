"""
Conversor de SVG a PNG usando Playwright (navegador headless)
Más confiable que cairosvg y funciona en cualquier plataforma
"""

import os
from pathlib import Path


def svg_to_png_playwright(svg_path, png_path, width=1200, height=675):
    """
    Convierte SVG a PNG usando Playwright

    Args:
        svg_path: Ruta al archivo SVG
        png_path: Ruta donde guardar el PNG
        width: Ancho de la imagen en píxeles
        height: Alto de la imagen en píxeles
    """
    try:
        from playwright.sync_api import sync_playwright

        # Leer SVG
        with open(svg_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()

        # Crear HTML temporal con el SVG
        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ margin: 0; padding: 0; width: {width}px; height: {height}px; }}
                svg {{ width: 100%; height: 100%; }}
            </style>
        </head>
        <body>
            {svg_content}
        </body>
        </html>
        '''

        # Renderizar con Playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': width, 'height': height})
            page.set_content(html_content)
            page.screenshot(path=png_path, full_page=True)
            browser.close()

        return True

    except ImportError:
        print("Playwright no está instalado. Instala con: pip install playwright && playwright install chromium")
        return False
    except Exception as e:
        print(f"Error al convertir SVG a PNG: {e}")
        return False


def svg_to_png_simple(svg_path, png_path, width=1200, height=675):
    """
    Fallback simple: copia el SVG si no hay conversor disponible
    """
    import shutil
    # Por ahora, simplemente indicamos que no se pudo convertir
    return False
