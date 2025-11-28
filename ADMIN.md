# 🔐 Panel de Administración

Panel web para gestionar los certificados de forma visual y segura.

## 🚀 Acceso

**URL:** `http://localhost:8000/admin`

**Clave por defecto:** `admin123`

⚠️ **IMPORTANTE:** Cambia la clave antes de deployar en producción.

## 🔑 Cambiar la Clave

### Opción 1: Variable de Entorno (Recomendado)

```bash
export ADMIN_PASSWORD="tu-clave-super-segura-aqui"
python app.py
```

### Opción 2: En Render/Railway/Vercel

Agrega la variable de entorno en el panel de tu plataforma:
```
ADMIN_PASSWORD=tu-clave-super-segura-aqui
```

### Opción 3: Hardcodeado (No recomendado para producción)

Edita `app.py` línea 17:
```python
ADMIN_PASSWORD = 'tu-clave-aqui'
```

## 📋 Funcionalidades

### 1. Generar Certificados

**Formato de entrada:**
```
Nombre Completo, email@example.com
María José González, maria@example.com
Carlos Rodríguez, carlos@example.com
```

**Proceso:**
1. Ingresa participantes (uno por línea)
2. Haz clic en "Generar Certificados"
3. Los certificados se crean automáticamente
4. La página se recarga mostrando los nuevos certificados

### 2. Ver Lista de Certificados

Muestra todos los certificados con:
- ✅ Nombre completo
- ✅ Email
- ✅ Slug (nombre-apellido)
- ✅ URL clickeable
- ✅ Número de veces visto
- ✅ Fecha de generación

### 3. Exportar Lista (CSV)

**Botón:** "📥 Exportar Lista"

**Archivo generado:** `certificados_YYYYMMDD.csv`

**Contenido:**
```csv
Nombre,Email,Slug,URL Completa,Visto,Fecha
Frank Vargas,frank@example.com,frank-vargas,https://tu-dominio.com/certificado/frank-vargas,5,2025-11-28
```

**Usos del CSV:**
- 📧 Enviar emails masivos con URLs personalizadas
- 📊 Análisis en Excel/Google Sheets
- 🔗 Compartir lista de URLs
- 💾 Backup de registros

## 🔒 Seguridad

### Protección por Sesión

- ✅ Login con clave
- ✅ Sesión cifrada con Flask
- ✅ Logout automático
- ✅ No se puede acceder sin login

### Recomendaciones de Seguridad

**1. Clave Fuerte:**
```bash
# Generar clave aleatoria segura (Linux/Mac)
openssl rand -base64 32
```

**2. HTTPS en Producción:**
- Siempre usa HTTPS cuando deploys
- Render/Railway/Vercel incluyen HTTPS gratis

**3. Rate Limiting (Opcional):**
Para evitar ataques de fuerza bruta, instala:
```bash
pip install flask-limiter
```

Agrega en `app.py`:
```python
from flask_limiter import Limiter

limiter = Limiter(app, default_limits=["100 per hour"])

@app.route('/admin/login', methods=['POST'])
@limiter.limit("5 per minute")  # Solo 5 intentos por minuto
def admin_login():
    # ...
```

## 📧 Envío Masivo de Certificados

Después de exportar el CSV, puedes usar este script de ejemplo:

```python
import csv
import smtplib
from email.mime.text import MIMEText

# Leer CSV exportado
with open('certificados_20251128.csv', 'r') as f:
    reader = csv.DictReader(f)

    for row in reader:
        nombre = row['Nombre']
        email = row['Email']
        url = row['URL Completa']

        # Crear email
        msg = MIMEText(f"""
        Hola {nombre},

        Tu certificado está listo:
        {url}

        Puedes descargarlo, imprimirlo o compartirlo.

        Saludos!
        """)

        msg['Subject'] = f'Tu Certificado - {nombre}'
        msg['From'] = 'certificados@tudominio.com'
        msg['To'] = email

        # Enviar (configura tu SMTP)
        # servidor.send_message(msg)

        print(f'Email enviado a {email}')
```

## 🎨 Personalización del Panel

### Cambiar Logo o Colores

Edita `templates/admin_login.html` y `templates/admin_dashboard.html`:

**Colores principales:**
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

**Cambiar a otros colores:**
```css
/* Azul/Verde */
background: linear-gradient(135deg, #36D1DC 0%, #5B86E5 100%);

/* Naranja/Rojo */
background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);

/* Verde */
background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
```

### Agregar Logo

En `admin_dashboard.html`, línea 156, reemplaza:
```html
<h1>🎓 Panel de Certificados</h1>
```

Por:
```html
<img src="/static/logo.png" alt="Logo" height="40">
<h1>Panel de Certificados</h1>
```

## 📱 Uso Móvil

El panel es completamente responsive y funciona en:
- ✅ iPhone/iPad
- ✅ Android
- ✅ Tablets
- ✅ Desktop

## 🔄 Flujo de Trabajo Recomendado

1. **Recolectar participantes** (Google Forms, Excel, etc.)
2. **Formatear datos** (Nombre, Email)
3. **Login en /admin**
4. **Pegar lista y generar**
5. **Exportar CSV con URLs**
6. **Enviar emails** con links personalizados
7. **Monitorear visualizaciones** en el dashboard

## ⚡ Atajos de Teclado

- `/admin` - Panel de administración
- `/admin/dashboard` - Dashboard principal
- `/admin/exportar` - Descargar CSV directamente
- `/admin/logout` - Cerrar sesión

## 🆘 Troubleshooting

**"Clave incorrecta"**
→ Verifica que estés usando la clave correcta (default: `admin123`)

**"No se generan certificados"**
→ Verifica el formato: `Nombre Completo, email@example.com`

**"No puedo exportar CSV"**
→ Verifica que haya certificados generados primero

**"Session expired"**
→ Vuelve a hacer login en `/admin/login`
