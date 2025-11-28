# Guía de Deployment

Esta guía te ayudará a deployar tu generador de certificados en producción.

## Opciones de Deployment

### 1. Render.com (Recomendado - Gratis)

**Paso 1:** Crea un archivo `render.yaml`

```yaml
services:
  - type: web
    name: generador-certificados
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.11
```

**Paso 2:** Agrega gunicorn a `requirements.txt`:
```
flask>=3.0.0
gunicorn>=21.2.0
```

**Paso 3:** Conecta tu repositorio de GitHub a Render.com

**Paso 4:** Render automáticamente detectará y deployará tu app

### 2. Railway.app (Fácil)

1. Conecta tu repo de GitHub a Railway
2. Railway detecta automáticamente Flask
3. Deploy automático

### 3. Vercel (Serverless)

**Paso 1:** Instala Vercel CLI
```bash
npm i -g vercel
```

**Paso 2:** Crea `vercel.json`:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```

**Paso 3:** Deploy
```bash
vercel
```

### 4. Heroku

**Paso 1:** Crea un `Procfile`:
```
web: gunicorn app:app
```

**Paso 2:** Crea `runtime.txt`:
```
python-3.11.0
```

**Paso 3:** Deploy
```bash
heroku create mi-generador-certificados
git push heroku main
```

### 5. VPS (DigitalOcean, AWS, etc.)

**Configuración con Nginx + Gunicorn:**

```bash
# Instalar dependencias
pip install gunicorn

# Crear servicio systemd
sudo nano /etc/systemd/system/certificados.service
```

```ini
[Unit]
Description=Generador de Certificados
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/certificados
Environment="PATH=/var/www/certificados/.venv/bin"
ExecStart=/var/www/certificados/.venv/bin/gunicorn --workers 4 --bind 0.0.0.0:8000 app:app

[Install]
WantedBy=multi-user.target
```

```bash
# Iniciar servicio
sudo systemctl start certificados
sudo systemctl enable certificados
```

**Configurar Nginx:**

```nginx
server {
    listen 80;
    server_name tudominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /certificados {
        alias /var/www/certificados/certificados;
    }
}
```

## Variables de Entorno

Para producción, puedes usar variables de entorno:

```python
# En app.py
import os

DB_PATH = os.getenv('DATABASE_PATH', 'certificados.db')
CERTIFICATES_DIR = os.getenv('CERTIFICATES_DIR', 'certificados')
```

## Consideraciones Importantes

### Base de Datos

**Opción 1: SQLite (Simple)**
- La BD se guarda en un archivo `certificados.db`
- Funciona bien para hasta 10,000 certificados
- Asegúrate de hacer backups regulares

**Opción 2: PostgreSQL (Escalable)**
- Para mayor escala, migra a PostgreSQL
- Modifica `database.py` para usar `psycopg2`

### Almacenamiento de Archivos

**Opción 1: Sistema de archivos local**
- Funciona en VPS
- No funciona en platforms serverless (Vercel, etc.)

**Opción 2: S3 o similar**
- Para serverless, guarda SVGs en S3/Cloudinary
- Modifica `generator.py` para subir a S3

### SSL/HTTPS

**Con Certbot (gratis):**
```bash
sudo certbot --nginx -d tudominio.com
```

## Dominio Personalizado

1. Compra un dominio (Namecheap, GoDaddy, etc.)
2. Configura DNS apuntando a tu servidor/plataforma
3. Espera propagación DNS (24-48 horas)

## Monitoreo

**Logs básicos:**
```bash
# Ver logs en tiempo real
tail -f /var/log/certificados.log
```

**Health check:**
- Configura un servicio como UptimeRobot
- Monitorea `/health` cada 5 minutos

## Backup

**Script de backup diario:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
cp certificados.db backups/certificados_$DATE.db
tar -czf backups/certificados_$DATE.tar.gz certificados/
```

**Cron job:**
```bash
0 2 * * * /path/to/backup.sh
```

## Seguridad

1. **No expongas la base de datos** - Solo Flask debe tener acceso
2. **Rate limiting** - Usa Flask-Limiter para prevenir spam
3. **CORS** - Configura CORS si necesitas acceso desde otros dominios
4. **Validación** - Valida todos los inputs

## URLs de Ejemplo

Después del deployment, tus certificados estarán en:

```
https://tudominio.com/certificado/abc123def456
```

Cada persona puede compartir su URL única y el certificado se mostrará en HTML con opción de descarga.
