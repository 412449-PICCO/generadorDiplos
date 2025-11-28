from flask import Flask, request, jsonify, send_file, render_template, url_for, session, redirect
import os
from datetime import datetime
from generator import CertificateGenerator
from database import Database
import csv
from io import StringIO

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'cambia-esta-clave-super-secreta-en-produccion-12345')

# Configuración
CERTIFICATES_DIR = 'certificados'
TEMPLATE_PATH = 'template.svg'
DATA_FILE = 'participantes.json'
DB_PATH = 'certificados.db'
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')  # Cambiar en producción

# Crear directorio para certificados si no existe
os.makedirs(CERTIFICATES_DIR, exist_ok=True)

# Inicializar base de datos
db = Database(DB_PATH)

# Inicializar generador con base de datos
generator = CertificateGenerator(TEMPLATE_PATH, CERTIFICATES_DIR, database=db)


@app.route('/', methods=['GET'])
def index():
    """Página de inicio"""
    total = db.contar_certificados()
    return jsonify({
        'mensaje': 'Generador de Certificados API',
        'version': '2.0',
        'certificados_generados': total,
        'endpoints': {
            'health': '/health',
            'generar': '/generar-certificados (POST)',
            'ver_certificado': '/certificado/<hash> (GET - HTML)',
            'descargar_certificado': '/descargar/<hash> (GET - SVG)',
            'listar': '/listar-certificados (GET)',
            'buscar_email': '/buscar/email/<email> (GET)',
            'buscar_nombre': '/buscar/nombre/<nombre> (GET)'
        }
    })


@app.route('/health', methods=['GET'])
def health():
    """Endpoint para verificar que el servidor está funcionando"""
    return jsonify({
        'status': 'ok',
        'message': 'Servidor funcionando correctamente',
        'database': 'conectada',
        'certificados_totales': db.contar_certificados()
    })


@app.route('/generar-certificados', methods=['POST'])
def generar_certificados():
    """
    Genera certificados para una lista de participantes
    Body esperado: { "participantes": [{"nombre": "...", "email": "..."}] }
    """
    try:
        data = request.get_json()

        if not data or 'participantes' not in data:
            return jsonify({'error': 'Debe enviar una lista de participantes'}), 400

        participantes = data['participantes']

        if not isinstance(participantes, list) or len(participantes) == 0:
            return jsonify({'error': 'La lista de participantes está vacía'}), 400

        resultados = []

        for participante in participantes:
            if 'nombre' not in participante or 'email' not in participante:
                resultados.append({
                    'error': 'Participante sin nombre o email',
                    'participante': participante
                })
                continue

            nombre = participante['nombre']
            email = participante['email']

            try:
                # Generar certificado (se guarda automáticamente en BD)
                resultado = generator.generar_certificado(nombre, email)
                resultados.append(resultado)
            except Exception as e:
                resultados.append({
                    'nombre': nombre,
                    'email': email,
                    'error': str(e)
                })

        return jsonify({
            'mensaje': f'Proceso completado. {len(resultados)} certificados procesados',
            'resultados': resultados
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/certificado/<slug>', methods=['GET'])
def ver_certificado(slug):
    """
    Muestra un certificado como HTML
    """
    try:
        # Buscar en base de datos
        certificado = db.obtener_certificado(slug)

        if not certificado:
            return render_template('error.html', mensaje='Certificado no encontrado'), 404

        # Marcar como visto
        db.marcar_como_visto(slug)

        # Leer archivo SVG
        archivo = os.path.join(CERTIFICATES_DIR, certificado['archivo_svg'])

        if not os.path.exists(archivo):
            return render_template('error.html', mensaje='Archivo de certificado no encontrado'), 404

        with open(archivo, 'r', encoding='utf-8') as f:
            svg_content = f.read()

        # Formatear fecha
        fecha = certificado['fecha_generacion']
        try:
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')
            fecha_formateada = fecha_obj.strftime('%d de %B de %Y')
        except:
            fecha_formateada = fecha

        # Renderizar template HTML
        return render_template(
            'certificado.html',
            nombre=certificado['nombre'],
            email=certificado['email'],
            slug=certificado['slug'],
            fecha=fecha_formateada,
            svg_content=svg_content,
            url=request.url
        )

    except Exception as e:
        return render_template('error.html', mensaje=str(e)), 500


@app.route('/preview/<slug>', methods=['GET'])
def preview_certificado(slug):
    """
    Genera una vista previa PNG del certificado para redes sociales (Open Graph)
    Convierte SVG a PNG bajo demanda para compatibilidad con LinkedIn
    """
    try:
        # Buscar en base de datos
        certificado = db.obtener_certificado(slug)

        if not certificado:
            return jsonify({'error': 'Certificado no encontrado'}), 404

        archivo_svg = os.path.join(CERTIFICATES_DIR, certificado['archivo_svg'])

        if not os.path.exists(archivo_svg):
            return jsonify({'error': 'Archivo no encontrado'}), 404

        # Verificar si ya existe PNG en caché
        archivo_png = os.path.join(CERTIFICATES_DIR, f'{slug}_preview.png')

        if not os.path.exists(archivo_png):
            # Convertir SVG a PNG usando Playwright
            try:
                from svg_to_png import svg_to_png_playwright

                # Convertir con dimensiones optimizadas para LinkedIn
                # LinkedIn recomienda 1200x627, usamos 1200x675 para mejor proporción
                success = svg_to_png_playwright(
                    svg_path=archivo_svg,
                    png_path=archivo_png,
                    width=1200,
                    height=675
                )

                if not success:
                    # Si falla, devolver SVG como fallback
                    return send_file(
                        archivo_svg,
                        mimetype='image/svg+xml'
                    )

            except ImportError:
                # Si Playwright no está disponible, devolver SVG
                return send_file(
                    archivo_svg,
                    mimetype='image/svg+xml'
                )
            except Exception as e:
                print(f'Error al convertir SVG a PNG: {e}')
                # Fallback a SVG
                return send_file(
                    archivo_svg,
                    mimetype='image/svg+xml'
                )

        # Devolver PNG
        return send_file(
            archivo_png,
            mimetype='image/png'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/descargar/<slug>', methods=['GET'])
def descargar_certificado(slug):
    """
    Descarga un certificado SVG
    """
    try:
        # Buscar en base de datos
        certificado = db.obtener_certificado(slug)

        if not certificado:
            return jsonify({'error': 'Certificado no encontrado'}), 404

        archivo = os.path.join(CERTIFICATES_DIR, certificado['archivo_svg'])

        if not os.path.exists(archivo):
            return jsonify({'error': 'Archivo no encontrado'}), 404

        return send_file(
            archivo,
            mimetype='image/svg+xml',
            as_attachment=True,
            download_name=f'certificado_{certificado["nombre"].replace(" ", "_")}.svg'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/listar-certificados', methods=['GET'])
def listar_certificados():
    """
    Lista todos los certificados generados
    """
    try:
        limite = request.args.get('limite', 100, type=int)
        offset = request.args.get('offset', 0, type=int)

        certificados = db.listar_certificados(limite=limite, offset=offset)
        total = db.contar_certificados()

        # Agregar URL completa a cada certificado
        for cert in certificados:
            cert['url'] = url_for('ver_certificado', slug=cert['slug'], _external=True)

        return jsonify({
            'total': total,
            'limite': limite,
            'offset': offset,
            'certificados': certificados
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/buscar/email/<email>', methods=['GET'])
def buscar_por_email(email):
    """
    Busca certificados por email
    """
    try:
        certificados = db.buscar_por_email(email)

        # Agregar URL completa
        for cert in certificados:
            cert['url'] = url_for('ver_certificado', slug=cert['slug'], _external=True)

        return jsonify({
            'total': len(certificados),
            'certificados': certificados
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/buscar/nombre/<nombre>', methods=['GET'])
def buscar_por_nombre(nombre):
    """
    Busca certificados por nombre
    """
    try:
        certificados = db.buscar_por_nombre(nombre)

        # Agregar URL completa
        for cert in certificados:
            cert['url'] = url_for('ver_certificado', slug=cert['slug'], _external=True)

        return jsonify({
            'total': len(certificados),
            'certificados': certificados
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# === ADMIN PANEL ===

@app.route('/admin', methods=['GET'])
def admin_redirect():
    """Redirige a login o dashboard"""
    if 'admin_logged_in' in session:
        return redirect('/admin/dashboard')
    return redirect('/admin/login')


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Página de login del admin"""
    if request.method == 'POST':
        password = request.form.get('password')

        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect('/admin/dashboard')
        else:
            return render_template('admin_login.html', error='Clave incorrecta')

    return render_template('admin_login.html')


@app.route('/admin/dashboard', methods=['GET'])
def admin_dashboard():
    """Dashboard principal del admin"""
    if 'admin_logged_in' not in session:
        return redirect('/admin/login')

    try:
        certificados = db.listar_certificados(limite=1000)
        total = db.contar_certificados()

        return render_template(
            'admin_dashboard.html',
            certificados=certificados,
            total=total
        )
    except Exception as e:
        return f'Error: {e}', 500


@app.route('/admin/generar', methods=['POST'])
def admin_generar():
    """Genera certificados desde el admin"""
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'No autorizado'}), 401

    try:
        data = request.get_json()
        participantes = data.get('participantes', [])

        exitosos = 0
        errores = 0
        resultados = []

        for p in participantes:
            nombre = p.get('nombre')
            email = p.get('email')

            if not nombre or not email:
                errores += 1
                continue

            try:
                resultado = generator.generar_certificado(nombre, email)
                exitosos += 1
                resultados.append(resultado)
            except Exception as e:
                errores += 1

        return jsonify({
            'exitosos': exitosos,
            'errores': errores,
            'resultados': resultados
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/admin/exportar', methods=['GET'])
def admin_exportar():
    """Exporta lista de certificados en CSV"""
    if 'admin_logged_in' not in session:
        return redirect('/admin/login')

    try:
        certificados = db.listar_certificados(limite=10000)

        # Crear CSV en memoria
        output = StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(['Nombre', 'Email', 'Slug', 'URL Completa', 'Visto', 'Fecha'])

        # Datos
        for cert in certificados:
            url_completa = url_for('ver_certificado', slug=cert['slug'], _external=True)
            writer.writerow([
                cert['nombre'],
                cert['email'],
                cert['slug'],
                url_completa,
                cert['visto'],
                cert['fecha_generacion']
            ])

        # Preparar respuesta
        output.seek(0)
        return send_file(
            StringIO(output.getvalue()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'certificados_{datetime.now().strftime("%Y%m%d")}.csv'
        )

    except Exception as e:
        return f'Error: {e}', 500


@app.route('/admin/logout', methods=['GET'])
def admin_logout():
    """Cerrar sesión del admin"""
    session.pop('admin_logged_in', None)
    return redirect('/admin/login')


if __name__ == '__main__':
    import os

    # Puerto configurable (Railway usa variable PORT)
    PORT = int(os.getenv('PORT', 8000))

    # Modo debug solo en desarrollo
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

    print('=' * 60)
    print('🚀 Servidor de Certificados iniciado')
    print('=' * 60)
    print(f'📊 Base de datos: {DB_PATH}')
    print(f'📁 Directorio certificados: {CERTIFICATES_DIR}')
    print(f'📄 Template: {TEMPLATE_PATH}')
    print(f'🎓 Certificados registrados: {db.contar_certificados()}')
    print(f'🔐 Admin password configurado: {"✅" if ADMIN_PASSWORD != "admin123" else "⚠️  usando default"}')
    print('=' * 60)
    print(f'🌐 Puerto: {PORT}')
    print(f'🐛 Debug mode: {DEBUG}')
    print('=' * 60)
    app.run(debug=DEBUG, host='0.0.0.0', port=PORT)
