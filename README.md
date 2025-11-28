# 🎓 Generador de Certificados con Base de Datos

Backend súper liviano en Python con Flask para generar certificados personalizados con URLs únicas y verificables.

## ✨ Características

- 🎨 Genera certificados personalizados con fuente Montserrat
- 🔗 **URL única para cada certificado** (ej: `/certificado/abc123`)
- 💾 Base de datos SQLite integrada
- 🌐 Vista HTML responsive y hermosa
- 📥 Descarga directa de SVG
- 🖨️ Impresión directa a PDF desde el navegador
- 🔍 Búsqueda por nombre o email
- 📊 Tracking de visualizaciones
- 🚀 Listo para deployar (Render, Railway, Vercel, Heroku)
- 🎯 Sin dependencias del sistema, solo Python puro

## 🚀 Instalación Rápida

```bash
# Activar entorno virtual e instalar
source .venv/bin/activate
pip install -r requirements.txt
```

## 📖 Uso

### Opción 1: Script Simple (Generar por lotes)

1. Edita `participantes.json` con tus datos:

```json
{
  "participantes": [
    {
      "nombre": "Frank Vargas",
      "email": "frank@example.com"
    },
    {
      "nombre": "María González",
      "email": "maria@example.com"
    }
  ]
}
```

2. Genera todos los certificados:

```bash
python generar.py
```

3. ¡Listo! Los certificados están en la base de datos con URLs únicas.

### Opción 2: Servidor Web (Producción)

1. Inicia el servidor:

```bash
python app.py
```

2. El servidor estará en `http://localhost:5000`

## 🌐 Endpoints de la API

### Ver certificado (HTML)
```
GET /certificado/<hash>
```
Muestra el certificado en una página HTML hermosa y responsive.

**Ejemplo:**
```
http://localhost:5000/certificado/1981ea2f7ac2245b
```

### Descargar SVG
```
GET /descargar/<hash>
```

### Generar certificados (API)
```
POST /generar-certificados
Content-Type: application/json

{
  "participantes": [
    {"nombre": "Juan Pérez", "email": "juan@example.com"}
  ]
}
```

### Listar todos
```
GET /listar-certificados?limite=100&offset=0
```

### Buscar por email
```
GET /buscar/email/frank@example.com
```

### Buscar por nombre
```
GET /buscar/nombre/Frank
```

### Health check
```
GET /health
```

## 📁 Estructura del Proyecto

```
.
├── app.py                  # Servidor Flask con todos los endpoints
├── database.py             # Modelo de base de datos SQLite
├── generator.py            # Lógica de generación de certificados
├── generar.py              # Script de generación por lotes
├── template.svg            # Template del certificado (Montserrat)
├── participantes.json      # Lista de participantes
├── requirements.txt        # Solo Flask (súper liviano)
├── certificados.db         # Base de datos SQLite
├── certificados/           # SVGs generados
├── templates/              # Templates HTML
│   ├── certificado.html    # Vista del certificado
│   └── error.html          # Página de error
├── README.md               # Esta documentación
└── DEPLOYMENT.md           # Guía de deployment
```

## 🎨 Personalizar el Template

El archivo `template.svg` usa la fuente **Montserrat** en todo el certificado.

El placeholder `{{NOMBRE}}` se reemplaza automáticamente con el nombre del participante.

Para cambiar la posición del nombre, edita la línea 134 en `template.svg`:

```xml
<text transform="translate(420.94 270)" text-anchor="middle"
      style="font-family: 'Montserrat', sans-serif; font-size: 38px; font-weight: 800;">
  {{NOMBRE}}
</text>
```

## 💾 Base de Datos

La base de datos `certificados.db` guarda:

- Hash único del certificado
- Nombre del participante
- Email
- Archivo SVG
- Fecha de generación
- Número de veces visto
- Última visita

### Estructura de la tabla:

```sql
CREATE TABLE certificados (
    id INTEGER PRIMARY KEY,
    hash TEXT UNIQUE,
    nombre TEXT,
    email TEXT,
    archivo_svg TEXT,
    fecha_generacion TIMESTAMP,
    visto INTEGER,
    ultima_visita TIMESTAMP
)
```

## 🚀 Deployment

El proyecto está listo para deployar en cualquier plataforma. Ver **[DEPLOYMENT.md](DEPLOYMENT.md)** para instrucciones detalladas.

### Deployment Rápido en Render.com (Gratis)

1. Sube tu código a GitHub
2. Conecta el repo a Render.com
3. Render detecta Flask automáticamente
4. ¡Deploy!

**Tu certificado estará en:**
```
https://tu-app.onrender.com/certificado/<hash>
```

### Otras plataformas soportadas:

- ✅ Railway.app
- ✅ Vercel (serverless)
- ✅ Heroku
- ✅ AWS / DigitalOcean / VPS
- ✅ Google Cloud Run
- ✅ Azure App Service

## 🔗 Cómo Funcionan las URLs

Cada certificado tiene un hash único generado con SHA-256:

```python
hash = SHA256(nombre + email + timestamp)[:16]
# Resultado: "1981ea2f7ac2245b"
```

La URL del certificado será:
```
https://tudominio.com/certificado/1981ea2f7ac2245b
```

Esta URL es:
- ✅ **Única** - Cada persona tiene su propia URL
- ✅ **Verificable** - Está en la base de datos
- ✅ **Compartible** - Se puede enviar por email, WhatsApp, etc.
- ✅ **Permanente** - No cambia nunca

## 📱 Vista HTML

El certificado se muestra en una página HTML hermosa con:

- 🎨 Diseño moderno y responsive
- 📱 Funciona perfecto en móviles
- 🖨️ Botón para imprimir/guardar como PDF
- 📥 Botón para descargar SVG original
- 🔗 Botón para compartir (copia URL)
- ℹ️ Información del certificado (nombre, email, fecha, hash)
- ✅ Badge de verificación

## 🔍 Búsqueda y Consultas

```bash
# Buscar certificados de un email
curl http://localhost:5000/buscar/email/frank@example.com

# Buscar por nombre
curl http://localhost:5000/buscar/nombre/Frank

# Listar todos
curl http://localhost:5000/listar-certificados

# Ver estadísticas
curl http://localhost:5000/health
```

## 📧 Envío Automático de Certificados

Puedes crear un script para enviar los certificados por email:

```python
import smtplib
from email.mime.text import MIMEText
from database import Database

db = Database()
certificados = db.listar_certificados()

for cert in certificados:
    url = f"https://tudominio.com/certificado/{cert['hash']}"

    msg = MIMEText(f"""
    Hola {cert['nombre']},

    Tu certificado está listo:
    {url}

    Puedes descargarlo, imprimirlo o compartirlo.
    """)

    msg['Subject'] = 'Tu Certificado de Participación'
    msg['From'] = 'certificados@tudominio.com'
    msg['To'] = cert['email']

    # Enviar email (configura tu SMTP)
    # ...
```

## 🔒 Seguridad

- ✅ Los certificados son verificables por hash único
- ✅ No se pueden modificar sin cambiar el hash
- ✅ La base de datos no se expone públicamente
- ✅ Validación de inputs en todos los endpoints

## 📊 Estadísticas

Cada vez que alguien ve un certificado, se registra en la BD:

```python
# Ver cuántas veces fue visto un certificado
certificado = db.obtener_certificado('abc123')
print(f"Visto {certificado['visto']} veces")
print(f"Última visita: {certificado['ultima_visita']}")
```

## 🛠️ Desarrollo

```bash
# Modo desarrollo con auto-reload
python app.py

# Ver logs de la base de datos
sqlite3 certificados.db "SELECT * FROM certificados;"

# Backup de la base de datos
cp certificados.db backups/certificados_$(date +%Y%m%d).db
```

## 📝 Notas

- Los certificados se generan en formato SVG (vectorial, alta calidad)
- El hash es SHA-256 truncado a 16 caracteres (seguro y corto)
- La fuente Montserrat se carga desde Google Fonts en la vista HTML
- La base de datos SQLite funciona bien hasta ~100,000 certificados
- Para más escala, migra a PostgreSQL (ver DEPLOYMENT.md)

## 🆘 Soporte

¿Problemas? Revisa:

1. ¿Está el servidor corriendo? → `python app.py`
2. ¿Existe la base de datos? → `ls -la certificados.db`
3. ¿El template existe? → `ls -la template.svg`
4. ¿Flask está instalado? → `pip install flask`

## 📄 Licencia

MIT - Úsalo libremente para tus proyectos

---

Hecho con ❤️ usando Python + Flask + SQLite
