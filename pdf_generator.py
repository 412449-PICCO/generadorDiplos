"""
Generador de PDF desde SVG usando Playwright
"""
import tempfile
import os
from playwright.sync_api import sync_playwright
import logging

logger = logging.getLogger(__name__)


def svg_to_pdf(svg_content: str, output_path: str = None) -> str:
    """
    Convierte contenido SVG a PDF usando Playwright.

    Args:
        svg_content: Contenido del SVG como string
        output_path: Ruta donde guardar el PDF (opcional)

    Returns:
        Ruta del archivo PDF generado
    """
    if output_path is None:
        # Crear archivo temporal para el PDF
        fd, output_path = tempfile.mkstemp(suffix='.pdf')
        os.close(fd)

    # Crear HTML temporal que contiene el SVG
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            html, body {{
                width: 100%;
                height: 100%;
            }}

            body {{
                display: flex;
                justify-content: center;
                align-items: center;
                background: white;
            }}

            svg {{
                max-width: 100%;
                max-height: 100%;
                width: auto;
                height: auto;
            }}
        </style>
    </head>
    <body>
        {svg_content}
    </body>
    </html>
    """

    # Crear archivo HTML temporal
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as tmp:
        tmp.write(html_content)
        html_path = tmp.name

    try:
        with sync_playwright() as p:
            # Iniciar navegador
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--no-sandbox',
                    '--disable-setuid-sandbox'
                ]
            )

            page = browser.new_page()

            # Cargar el HTML con el SVG
            page.goto(f'file://{html_path}')

            # Esperar a que el SVG se cargue completamente
            page.wait_for_timeout(2000)

            # Generar PDF
            # Tamaño A4 horizontal (landscape) para certificados
            page.pdf(
                path=output_path,
                format='A4',
                landscape=True,
                print_background=True,
                margin={
                    'top': '0',
                    'right': '0',
                    'bottom': '0',
                    'left': '0'
                }
            )

            browser.close()

        logger.info(f"PDF generado exitosamente: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Error al generar PDF: {e}")
        raise
    finally:
        # Limpiar archivo HTML temporal
        try:
            os.unlink(html_path)
        except:
            pass


def html_to_pdf(html_content: str, output_path: str = None, width: int = 1920, height: int = 1080) -> str:
    """
    Convierte contenido HTML a PDF usando Playwright.

    Args:
        html_content: Contenido HTML completo
        output_path: Ruta donde guardar el PDF (opcional)
        width: Ancho de la página en pixels
        height: Alto de la página en pixels

    Returns:
        Ruta del archivo PDF generado
    """
    if output_path is None:
        # Crear archivo temporal para el PDF
        fd, output_path = tempfile.mkstemp(suffix='.pdf')
        os.close(fd)

    # Crear archivo HTML temporal
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as tmp:
        tmp.write(html_content)
        html_path = tmp.name

    try:
        with sync_playwright() as p:
            # Iniciar navegador
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--no-sandbox',
                    '--disable-setuid-sandbox'
                ]
            )

            page = browser.new_page(viewport={'width': width, 'height': height})

            # Cargar el HTML
            page.goto(f'file://{html_path}')

            # Esperar a que todo se cargue
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(2000)

            # Generar PDF
            page.pdf(
                path=output_path,
                format='A4',
                landscape=True,
                print_background=True,
                margin={
                    'top': '0',
                    'right': '0',
                    'bottom': '0',
                    'left': '0'
                }
            )

            browser.close()

        logger.info(f"PDF generado exitosamente: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Error al generar PDF: {e}")
        raise
    finally:
        # Limpiar archivo HTML temporal
        try:
            os.unlink(html_path)
        except:
            pass


if __name__ == '__main__':
    # Test
    test_svg = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 100">
        <rect width="200" height="100" fill="#673de6"/>
        <text x="100" y="50" text-anchor="middle" fill="white" font-size="20">
            Test PDF
        </text>
    </svg>
    """

    pdf_path = svg_to_pdf(test_svg, '/tmp/test.pdf')
    print(f"PDF generado: {pdf_path}")
