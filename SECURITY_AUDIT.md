# 🔒 Auditoría de Seguridad - Sistema de Certificados

**Fecha:** 2025-12-11
**Alcance:** Endpoints públicos (solo diplomados expuestos al público)

---

## ⚠️ VULNERABILIDADES CRÍTICAS

### 1. **DoS via Generación Masiva de PDFs** (CRÍTICO - Prioridad 1)

**Descripción:**
Los endpoints `/certificado/<slug>` y `/certificado/<slug>/pdf` generan un PDF usando Playwright **en cada request**, sin rate limiting ni caché.

**Impacto:**
- Un atacante puede hacer 100+ requests simultáneos
- Cada generación de PDF consume ~500MB RAM + CPU intensivo
- El servidor se colapsaría en segundos

**Archivos afectados:**
- `app.py:205-253` - endpoint `/certificado/<slug>`
- `app.py:298-344` - endpoint `/certificado/<slug>/pdf`

**Prueba de concepto:**
```bash
# Esto tiraría tu servidor en segundos:
for i in {1..100}; do
  curl https://tu-app.railway.app/certificado/test-slug &
done
```

**Solución URGENTE:**
```python
# Opción 1: Agregar rate limiting (RÁPIDO)
@app.route('/certificado/<slug>', methods=['GET'])
@limiter.limit("10 per minute")  # Máximo 10 requests por minuto por IP
def ver_certificado(slug):
    ...

# Opción 2: Implementar caché de PDFs (MEJOR)
# - Generar PDF solo una vez
# - Guardar en Cloudinary o filesystem
# - Servir el PDF cacheado en requests siguientes

# Opción 3: Queue de generación (ÓPTIMO)
# - Usar Celery/RQ para generar PDFs en background
# - Primeros requests ponen en cola
# - Siguientes requests obtienen PDF ya generado
```

---

### 2. **Resource Exhaustion - Sin Límites** (CRÍTICO)

**Descripción:**
- No hay límite de tamaño para SVG descargado de Cloudinary
- No hay límite de PDFs generados simultáneamente
- Playwright lanza navegadores sin límite de procesos

**Impacto:**
- Un SVG de 100MB consumiría toda la memoria
- 50 requests simultáneos = 50 navegadores Chromium activos
- Out of Memory (OOM) crash garantizado

**Solución:**
```python
# En pdf_generator.py
MAX_SVG_SIZE = 5 * 1024 * 1024  # 5MB
MAX_CONCURRENT_GENERATIONS = 3

# Verificar tamaño antes de procesar
if len(svg_content) > MAX_SVG_SIZE:
    raise ValueError("SVG too large")

# Usar semáforo para limitar generaciones concurrentes
import threading
pdf_semaphore = threading.Semaphore(MAX_CONCURRENT_GENERATIONS)

def svg_to_pdf(svg_content: str, output_path: str = None) -> str:
    with pdf_semaphore:
        # ... generación de PDF
```

---

## ⚠️ VULNERABILIDADES ALTAS

### 3. **SSRF (Server-Side Request Forgery)** (ALTO)

**Descripción:**
El código hace `requests.get(cloudinary_url)` donde `cloudinary_url` viene de la base de datos sin validación.

**Archivos afectados:**
- `app.py:230` - `requests.get(cloudinary_url, timeout=10)`

**Impacto:**
Si un atacante logra modificar la BD (o existe otra vulnerabilidad), podría:
- Hacer que tu servidor ataque otros servicios (ej: `http://localhost:6379` - Redis)
- Leer archivos internos si hay SSRF a file://
- Escanear red interna

**Solución:**
```python
import re
from urllib.parse import urlparse

ALLOWED_DOMAINS = ['res.cloudinary.com', 'cloudinary.com']

def validate_cloudinary_url(url: str) -> bool:
    parsed = urlparse(url)
    return any(parsed.netloc.endswith(domain) for domain in ALLOWED_DOMAINS)

# En ver_certificado():
if not validate_cloudinary_url(cloudinary_url):
    logger.error(f"URL no permitida: {cloudinary_url}")
    return render_template('error.html', mensaje='Error de configuración'), 500
```

---

### 4. **Path Traversal en Slug** (MEDIO-ALTO)

**Descripción:**
El `slug` no se valida para caracteres peligrosos como `../`, `./`, etc.

**Impacto:**
Aunque SQLAlchemy protege la BD, el slug se podría usar en:
- Nombres de archivo temporal
- Logs que se escriben a disco
- Futuros features que usen el slug como path

**Solución:**
```python
import re

def validate_slug(slug: str) -> bool:
    # Solo permitir letras, números, guiones y underscore
    return bool(re.match(r'^[a-z0-9\-_]+$', slug))

@app.route('/certificado/<slug>', methods=['GET'])
def ver_certificado(slug):
    if not validate_slug(slug):
        return render_template('error.html', mensaje='Slug inválido'), 400
    ...
```

---

## ⚠️ VULNERABILIDADES MEDIAS

### 5. **Falta de Rate Limiting en Endpoints Públicos** (MEDIO)

**Endpoints sin protección:**
- `/certificado/<slug>` ❌
- `/certificado/<slug>/pdf` ❌
- `/preview/<slug>` ❌
- `/descargar/<slug>` ❌

**Solo protegido:**
- `/listar-certificados` ✅ (60 per minute)

**Solución:**
```python
@app.route('/certificado/<slug>', methods=['GET'])
@limiter.limit("30 per minute")  # 30 requests por minuto por IP
def ver_certificado(slug):
    ...

@app.route('/preview/<slug>', methods=['GET'])
@limiter.limit("60 per minute")
def preview_certificado(slug):
    ...
```

---

### 6. **Timeout Muy Alto en Requests Externos** (MEDIO)

**Descripción:**
`timeout=10` segundos es muy alto para requests a Cloudinary.

**Impacto:**
- Permite slowloris attacks
- Si Cloudinary responde lento, el servidor se bloquea esperando

**Solución:**
```python
# Cambiar de 10 segundos a 3 segundos
response = requests.get(cloudinary_url, timeout=3)
```

---

### 7. **Tempfiles no se Limpian en Caso de Error** (MEDIO)

**Descripción:**
Si hay error al servir el PDF, el archivo temporal no se borra.

**Archivos afectados:**
- `pdf_generator.py:23-26` - mkstemp crea archivo temporal
- No hay limpieza garantizada después de `send_file()`

**Solución:**
```python
# En app.py
import os
from werkzeug.utils import secure_filename

@app.route('/certificado/<slug>', methods=['GET'])
def ver_certificado(slug):
    pdf_path = None
    try:
        pdf_path = svg_to_pdf(svg_content)
        return send_file(pdf_path, ...)
    finally:
        # Limpiar siempre
        if pdf_path and os.path.exists(pdf_path):
            try:
                os.unlink(pdf_path)
            except:
                pass
```

---

### 8. **Error Messages Revelan Información** (BAJO-MEDIO)

**Descripción:**
Mensajes de error pueden revelar:
- Estructura de la BD
- Paths del sistema
- Stack traces en modo debug

**Ejemplo:**
```python
# MALO
return jsonify({'error': str(e)}), 500

# BUENO
logger.error(f"Error interno: {e}", exc_info=True)
return jsonify({'error': 'Error interno del servidor'}), 500
```

---

### 9. **CORS está Totalmente Abierto** (MEDIO)

**Descripción:**
```python
CORS(app)  # Permite requests desde CUALQUIER origen
```

**Impacto:**
Cualquier sitio web puede hacer requests a tu API.

**Solución:**
```python
# Solo si necesitas CORS (para APIs públicas está OK)
# Si no, quítalo:
# CORS(app, resources={r"/api/*": {"origins": "https://tu-dominio.com"}})
```

---

## ✅ COSAS QUE ESTÁN BIEN

1. ✅ **SQLAlchemy ORM** - Protege contra SQL Injection
2. ✅ **Pydantic Schemas** - Validación de input en endpoints admin
3. ✅ **Logging estructurado** - JSON logs para monitoring
4. ✅ **HTTPS en Railway** - Tráfico encriptado
5. ✅ **Secret key configurada** - Sessions seguras
6. ✅ **Admin password** - Endpoints de generación protegidos
7. ✅ **Rate limiting configurado** - Aunque no aplicado a todos los endpoints

---

## 🛠️ PLAN DE ACCIÓN RECOMENDADO

### Prioridad URGENTE (hacer HOY):
1. ✅ Agregar rate limiting a `/certificado/<slug>`:
   ```python
   @limiter.limit("10 per minute")
   ```

2. ✅ Validar slug:
   ```python
   if not re.match(r'^[a-z0-9\-_]+$', slug):
       return 400
   ```

3. ✅ Validar URL de Cloudinary:
   ```python
   if not url.startswith('https://res.cloudinary.com/'):
       return 500
   ```

### Prioridad ALTA (hacer esta semana):
4. Implementar caché de PDFs (guardar en Cloudinary o filesystem)
5. Reducir timeout a 3 segundos
6. Agregar límite de tamaño de SVG
7. Agregar limpieza de tempfiles

### Prioridad MEDIA (hacer próximo sprint):
8. Implementar queue para generación de PDFs (Celery/RQ)
9. Agregar monitoring de recursos (CPU, RAM, disk)
10. Implementar circuit breaker para Cloudinary

---

## 📊 RESUMEN

| Vulnerabilidad | Severidad | Explotabilidad | Impacto | Prioridad |
|----------------|-----------|----------------|---------|-----------|
| DoS via PDF masivo | CRÍTICA | ALTA | Server crash | 1 |
| Resource exhaustion | CRÍTICA | ALTA | OOM crash | 1 |
| SSRF | ALTA | BAJA | Red interna | 2 |
| Path traversal | MEDIA | BAJA | Info disclosure | 3 |
| Sin rate limiting | MEDIA | ALTA | Server slow | 2 |
| Timeout alto | MEDIA | MEDIA | Slowloris | 3 |
| Tempfile leak | MEDIA | MEDIA | Disk full | 3 |

---

## 🔒 COMANDOS PARA PROBAR (SOLO EN TU ENTORNO DE PRUEBA)

```bash
# Test 1: Rate limiting (no debería tirar el sistema)
for i in {1..50}; do curl https://tu-app/certificado/test & done

# Test 2: Slug inválido (debería devolver 400)
curl https://tu-app/certificado/../../../etc/passwd

# Test 3: Load test (usar con cuidado)
# ab -n 100 -c 10 https://tu-app/certificado/test-slug
```

---

**Conclusión:** El sistema tiene vulnerabilidades de DoS que DEBEN ser arregladas antes de exponerlo públicamente. La más crítica es la generación de PDFs sin rate limiting ni caché.
