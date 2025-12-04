"""
API de Generador de Certificados
Versión 3.0 - Optimizada para producción
"""
from flask import Flask, request, jsonify, render_template, session, redirect, send_file
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
import logging
from pythonjsonlogger import jsonlogger
from datetime import datetime
from pydantic import ValidationError
import os

# Módulos propios
from config import config
from database import Database
from cloudinary_storage import CloudinaryStorage
from generator import CertificateGenerator
from schemas import (
    GenerarCertificadosRequest,
    ParticipanteSchema
)

# Configuración de logging estructurado
def setup_logging():
    """Configura logging estructurado con JSON"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Handler para consola
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)

    return logging.getLogger(__name__)


# Setup
logger = setup_logging()
app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# CORS
CORS(app)

# Rate Limiting
if config.RATELIMIT_ENABLED:
    try:
        limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=[config.RATELIMIT_DEFAULT],
            storage_uri=config.RATELIMIT_STORAGE_URL
        )
        logger.info("Rate limiting habilitado")
    except Exception as e:
        logger.warning(f"No se pudo habilitar rate limiting: {e}")
        limiter = Limiter(app=app, key_func=get_remote_address)
else:
    limiter = Limiter(app=app, key_func=get_remote_address)

# Inicializar servicios
try:
    db = Database(config.DATABASE_URL)
    logger.info("Base de datos inicializada")
except Exception as e:
    logger.error(f"Error al inicializar base de datos: {e}")
    raise

try:
    cloudinary_storage = CloudinaryStorage(
        cloud_name=config.CLOUDINARY_CLOUD_NAME,
        api_key=config.CLOUDINARY_API_KEY,
        api_secret=config.CLOUDINARY_API_SECRET,
        folder=config.CLOUDINARY_FOLDER
    )
    logger.info("Cloudinary inicializado")
except Exception as e:
    logger.error(f"Error al inicializar Cloudinary: {e}")
    cloudinary_storage = None

try:
    generator = CertificateGenerator(
        template_path=config.TEMPLATE_PATH,
        database=db,
        cloudinary_storage=cloudinary_storage
    )
    logger.info("Generador de certificados inicializado")
except Exception as e:
    logger.error(f"Error al inicializar generador: {e}")
    raise


# === HEALTH & INFO ===

@app.route('/', methods=['GET'])
def index():
    """Información de la API"""
    return jsonify({
        'nombre': config.APP_NAME,
        'version': '3.0',
        'certificados_generados': db.contar_certificados(),
        'cloudinary_configurado': cloudinary_storage.configured if cloudinary_storage else False,
        'endpoints': {
            'health': '/health',
            'generar': '/generar-certificados (POST)',
            'ver_certificado': '/certificado/<slug> (GET)',
            'preview': '/preview/<slug> (GET)',
            'descargar': '/descargar/<slug> (GET)',
            'listar': '/listar-certificados (GET)',
            'buscar_email': '/buscar/email/<email> (GET)',
            'buscar_nombre': '/buscar/nombre/<nombre> (GET)',
            'admin': '/admin'
        }
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check para monitoring"""
    try:
        # Verificar DB
        total_certs = db.contar_certificados()

        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'cloudinary': 'configured' if cloudinary_storage and cloudinary_storage.configured else 'not_configured',
            'certificados_totales': total_certs,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


# === CERTIFICADOS ===

@app.route('/generar-certificados', methods=['POST'])
@limiter.limit("10 per minute")
def generar_certificados():
    """
    Genera certificados para una lista de participantes
    """
    try:
        data = request.get_json()

        # Validar con Pydantic
        try:
            request_data = GenerarCertificadosRequest(**data)
        except ValidationError as e:
            logger.warning(f"Validación fallida: {e}")
            return jsonify({'error': 'Datos inválidos', 'details': e.errors()}), 400

        # Generar certificados
        participantes = [p.dict() for p in request_data.participantes]
        resultado = generator.generar_batch(participantes)

        logger.info(f"Batch generado: {resultado['exitosos']} exitosos, {resultado['errores']} errores")

        return jsonify({
            'mensaje': f'Proceso completado. {resultado["exitosos"]} certificados generados',
            'total': resultado['total'],
            'exitosos': resultado['exitosos'],
            'errores': resultado['errores'],
            'resultados': resultado['resultados']
        })

    except Exception as e:
        logger.error(f"Error en generar_certificados: {e}", exc_info=True)
        return jsonify({'error': 'Error interno del servidor', 'details': str(e)}), 500


@app.route('/certificado/<slug>', methods=['GET'])
def ver_certificado(slug):
    """
    Muestra un certificado como HTML
    """
    try:
        # Buscar en base de datos
        certificado = db.obtener_certificado(slug)

        if not certificado:
            logger.warning(f"Certificado no encontrado: {slug}")
            return render_template('error.html', mensaje='Certificado no encontrado'), 404

        # Marcar como visto
        db.marcar_como_visto(slug)

        # Obtener SVG desde Cloudinary
        cloudinary_url = certificado.get('cloudinary_url')

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
            cloudinary_url=cloudinary_url,
            url=request.url
        )

    except Exception as e:
        logger.error(f"Error al ver certificado {slug}: {e}", exc_info=True)
        return render_template('error.html', mensaje='Error al cargar el certificado'), 500


@app.route('/preview/<slug>', methods=['GET'])
def preview_certificado(slug):
    """
    Genera una vista previa PNG del certificado para redes sociales (Open Graph)
    """
    try:
        certificado = db.obtener_certificado(slug)

        if not certificado:
            return jsonify({'error': 'Certificado no encontrado'}), 404

        # Obtener URL de preview PNG desde Cloudinary
        if cloudinary_storage and cloudinary_storage.configured:
            png_url = cloudinary_storage.get_png_url(slug, width=1200, height=675)
            return redirect(png_url)
        else:
            return jsonify({'error': 'Preview no disponible'}), 503

    except Exception as e:
        logger.error(f"Error al generar preview {slug}: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/descargar/<slug>', methods=['GET'])
def descargar_certificado(slug):
    """
    Redirige a la URL de Cloudinary para descargar el SVG
    """
    try:
        certificado = db.obtener_certificado(slug)

        if not certificado:
            return jsonify({'error': 'Certificado no encontrado'}), 404

        cloudinary_url = certificado.get('cloudinary_url')
        return redirect(cloudinary_url)

    except Exception as e:
        logger.error(f"Error al descargar certificado {slug}: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/listar-certificados', methods=['GET'])
@limiter.limit("60 per minute")
def listar_certificados():
    """
    Lista todos los certificados generados con paginación
    """
    try:
        limite = request.args.get('limite', 100, type=int)
        offset = request.args.get('offset', 0, type=int)

        # Límite máximo
        if limite > 500:
            limite = 500

        certificados = db.listar_certificados(limite=limite, offset=offset)
        total = db.contar_certificados()

        # Agregar URL completa
        for cert in certificados:
            cert['url'] = f"{config.APP_URL}/certificado/{cert['slug']}"

        return jsonify({
            'total': total,
            'limite': limite,
            'offset': offset,
            'certificados': certificados
        })

    except Exception as e:
        logger.error(f"Error al listar certificados: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/buscar/email/<email>', methods=['GET'])
@limiter.limit("30 per minute")
def buscar_por_email(email):
    """
    Busca certificados por email
    """
    try:
        certificados = db.buscar_por_email(email)

        for cert in certificados:
            cert['url'] = f"{config.APP_URL}/certificado/{cert['slug']}"

        return jsonify({
            'total': len(certificados),
            'certificados': certificados
        })

    except Exception as e:
        logger.error(f"Error al buscar por email: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/buscar/nombre/<nombre>', methods=['GET'])
@limiter.limit("30 per minute")
def buscar_por_nombre(nombre):
    """
    Busca certificados por nombre
    """
    try:
        certificados = db.buscar_por_nombre(nombre)

        for cert in certificados:
            cert['url'] = f"{config.APP_URL}/certificado/{cert['slug']}"

        return jsonify({
            'total': len(certificados),
            'certificados': certificados
        })

    except Exception as e:
        logger.error(f"Error al buscar por nombre: {e}")
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

        if password == config.ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            logger.info("Admin login exitoso")
            return redirect('/admin/dashboard')
        else:
            logger.warning("Intento de login fallido")
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

        # Estadísticas adicionales
        stats = {
            'total': total,
            'cloudinary_configurado': cloudinary_storage.configured if cloudinary_storage else False,
        }

        return render_template(
            'admin_dashboard.html',
            certificados=certificados,
            stats=stats
        )
    except Exception as e:
        logger.error(f"Error en admin dashboard: {e}")
        return f'Error: {e}', 500


@app.route('/admin/generar', methods=['POST'])
def admin_generar():
    """Genera certificados desde el admin"""
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'No autorizado'}), 401

    try:
        data = request.get_json()
        participantes = data.get('participantes', [])

        resultado = generator.generar_batch(participantes)

        return jsonify(resultado)

    except Exception as e:
        logger.error(f"Error en admin_generar: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/admin/exportar', methods=['GET'])
def admin_exportar():
    """Exporta lista de certificados en CSV"""
    if 'admin_logged_in' not in session:
        return redirect('/admin/login')

    try:
        import csv
        from io import StringIO

        certificados = db.listar_certificados(limite=10000)

        output = StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(['Nombre', 'Email', 'Slug', 'URL Completa', 'Visto', 'Fecha', 'Cloudinary URL'])

        # Datos
        for cert in certificados:
            url_completa = f"{config.APP_URL}/certificado/{cert['slug']}"
            writer.writerow([
                cert['nombre'],
                cert['email'],
                cert['slug'],
                url_completa,
                cert['visto'],
                cert['fecha_generacion'],
                cert['cloudinary_url']
            ])

        output.seek(0)
        return send_file(
            StringIO(output.getvalue()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'certificados_{datetime.now().strftime("%Y%m%d")}.csv'
        )

    except Exception as e:
        logger.error(f"Error al exportar: {e}")
        return f'Error: {e}', 500


@app.route('/admin/logout', methods=['GET'])
def admin_logout():
    """Cerrar sesión del admin"""
    session.pop('admin_logged_in', None)
    logger.info("Admin logout")
    return redirect('/admin/login')


# === ERROR HANDLERS ===

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint no encontrado'}), 404


@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'Demasiadas solicitudes', 'details': str(e.description)}), 429


@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Error interno: {e}")
    return jsonify({'error': 'Error interno del servidor'}), 500


# === STARTUP ===

if __name__ == '__main__':
    # Validar configuración
    config_errors = config.validate()
    if config_errors:
        print('\n' + '=' * 60)
        print('⚠️  ADVERTENCIAS DE CONFIGURACIÓN:')
        for error in config_errors:
            print(f'  {error}')
        print('=' * 60 + '\n')

    # Mostrar info de inicio
    print('=' * 60)
    print(f'🚀 {config.APP_NAME} v3.0 iniciado')
    print('=' * 60)
    print(f'📊 Base de datos: {config.DATABASE_URL.split("@")[-1] if "@" in config.DATABASE_URL else config.DATABASE_URL}')
    print(f'☁️  Cloudinary: {"✅ Configurado" if cloudinary_storage.configured else "❌ No configurado"}')
    print(f'🎓 Certificados registrados: {db.contar_certificados()}')
    print(f'🔐 Admin password: {"✅ Personalizado" if config.ADMIN_PASSWORD != "admin123" else "⚠️  Default"}')
    print('=' * 60)
    print(f'🌐 Puerto: {config.PORT}')
    print(f'🐛 Debug mode: {config.DEBUG}')
    print(f'🛡️  Rate limiting: {"✅ Habilitado" if config.RATELIMIT_ENABLED else "❌ Deshabilitado"}')
    print('=' * 60)

    app.run(debug=config.DEBUG, host='0.0.0.0', port=config.PORT)
