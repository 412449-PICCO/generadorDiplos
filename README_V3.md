# 🎓 Generador de Certificados v3.0 - Edición Producción

Sistema profesional de generación de certificados personalizados con almacenamiento en la nube, base de datos escalable y envío automático de emails.

**✨ Optimizado para generar 900+ diplomas de manera eficiente**

## 🚀 ¿Qué hay de nuevo en v3.0?

### Mejoras Principales

✅ **Almacenamiento en Cloudinary** - CDN global, sin límites de almacenamiento local
✅ **PostgreSQL** - Base de datos robusta y escalable (con fallback a SQLite)
✅ **Sistema de Emails** - Envío automático con SendGrid
✅ **Rate Limiting** - Protección contra abuso con Redis
✅ **Validación con Pydantic** - Validación de datos estricta
✅ **Logging Estructurado** - JSON logs para producción
✅ **Batch Processing** - Generación optimizada de múltiples certificados
✅ **Buenas Prácticas** - Código limpio, type hints, manejo de errores

### Arquitectura

```
┌─────────────┐
│   Cliente   │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│   Flask API v3.0    │
│  (Rate Limited)     │
└──────┬──────────────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌─────────────┐   ┌────────────┐
│ PostgreSQL  │   │ Cloudinary │
│  Database   │   │   (CDN)    │
└─────────────┘   └────────────┘
       │
       ▼
┌─────────────┐
│  SendGrid   │
│   (Email)   │
└─────────────┘
```

## 📋 Requisitos

- Python 3.11+
- Docker & Docker Compose (recomendado)
- Cuenta de [Cloudinary](https://cloudinary.com) (gratis)
- Cuenta de [SendGrid](https://sendgrid.com) (gratis) - opcional
- PostgreSQL o SQLite

## 🛠️ Instalación

### Opción 1: Docker Compose (Recomendado)

```bash
# 1. Clonar repositorio
git clone <repo-url>
cd generadorPdf

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# 3. Iniciar servicios
docker-compose up -d

# 4. Verificar que todo funciona
curl http://localhost:8000/health
```

### Opción 2: Local (Desarrollo)

```bash
# 1. Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# 4. Iniciar servidor
python app.py
```

## ⚙️ Configuración

### Variables de Entorno Críticas

Edita `.env` con tus credenciales:

```bash
# Cloudinary (REQUERIDO)
CLOUDINARY_CLOUD_NAME=tu_cloud_name
CLOUDINARY_API_KEY=tu_api_key
CLOUDINARY_API_SECRET=tu_api_secret

# Base de Datos (Producción)
DATABASE_URL=postgresql://user:pass@localhost:5432/certificados_db

# SendGrid (Opcional - para emails)
SENDGRID_API_KEY=tu_sendgrid_key
FROM_EMAIL=noreply@tudominio.com

# Seguridad
SECRET_KEY=genera-una-clave-secreta-aleatoria-aqui
ADMIN_PASSWORD=cambia-esto-en-produccion

# App
APP_URL=https://tudominio.com
```

### Obtener Credenciales de Cloudinary

1. Crear cuenta en https://cloudinary.com (gratis)
2. Dashboard → Cloud Name, API Key, API Secret
3. Copiar a `.env`

### Obtener API Key de SendGrid (Opcional)

1. Crear cuenta en https://sendgrid.com (gratis)
2. Settings → API Keys → Create API Key
3. Copiar a `.env`

## 📖 Uso

### Generar 900 Diplomas

#### Opción 1: Via API (Recomendado para grandes volúmenes)

```bash
curl -X POST http://localhost:8000/generar-certificados \
  -H "Content-Type: application/json" \
  -d '{
    "participantes": [
      {"nombre": "Juan Pérez", "email": "juan@example.com"},
      {"nombre": "María García", "email": "maria@example.com"}
      # ... hasta 1000 por request
    ],
    "enviar_email": true,
    "asunto_email": "Tu certificado está listo"
  }'
```

#### Opción 2: Desde JSON file

```bash
# 1. Crear participantes.json
{
  "participantes": [
    {"nombre": "Nombre Completo", "email": "email@example.com"}
  ]
}

# 2. Ejecutar script
python generar.py
```

#### Opción 3: Panel de Admin

1. Acceder a `http://localhost:8000/admin`
2. Login (password configurado en `.env`)
3. Generar certificados desde interfaz web

### URLs de Certificados

Los certificados están disponibles en:

```
https://tudominio.com/certificado/nombre-apellido
```

Ejemplos:
- `https://tudominio.com/certificado/juan-perez`
- `https://tudominio.com/certificado/maria-garcia`

## 🌐 API Endpoints

### Certificados

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/generar-certificados` | Generar batch de certificados |
| GET | `/certificado/<slug>` | Ver certificado HTML |
| GET | `/preview/<slug>` | Preview PNG (redes sociales) |
| GET | `/descargar/<slug>` | Descargar SVG original |
| GET | `/listar-certificados` | Listar todos (paginado) |
| GET | `/buscar/email/<email>` | Buscar por email |
| GET | `/buscar/nombre/<nombre>` | Buscar por nombre |

### Emails

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/enviar-emails` | Enviar emails a certificados específicos |

### Admin

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/admin` | Panel de administración |
| GET | `/admin/exportar` | Exportar CSV |

### Ejemplos de Uso

**Generar certificados con emails automáticos:**

```bash
curl -X POST http://localhost:8000/generar-certificados \
  -H "Content-Type: application/json" \
  -d '{
    "participantes": [
      {"nombre": "Juan Pérez", "email": "juan@example.com"}
    ],
    "enviar_email": true
  }'
```

**Enviar emails a certificados existentes:**

```bash
curl -X POST http://localhost:8000/enviar-emails \
  -H "Content-Type: application/json" \
  -d '{
    "slugs": ["juan-perez", "maria-garcia"],
    "asunto": "Tu certificado está disponible"
  }'
```

**Buscar certificados:**

```bash
# Por email
curl http://localhost:8000/buscar/email/juan@example.com

# Por nombre
curl http://localhost:8000/buscar/nombre/Juan
```

## 🚢 Deployment

### Railway (Recomendado)

```bash
# 1. Instalar Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Inicializar proyecto
railway init

# 4. Agregar PostgreSQL
railway add postgresql

# 5. Agregar Redis
railway add redis

# 6. Configurar variables de entorno
railway variables set CLOUDINARY_CLOUD_NAME=xxx
railway variables set CLOUDINARY_API_KEY=xxx
railway variables set CLOUDINARY_API_SECRET=xxx
railway variables set SECRET_KEY=xxx
railway variables set ADMIN_PASSWORD=xxx

# 7. Deploy
railway up
```

### Render.com

1. Crear cuenta en https://render.com
2. New → Web Service
3. Conectar repositorio
4. Configurar:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
5. Agregar PostgreSQL desde Dashboard
6. Configurar variables de entorno

### Docker (Producción)

```bash
# Build
docker build -t generador-certificados .

# Run
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e CLOUDINARY_CLOUD_NAME=xxx \
  -e CLOUDINARY_API_KEY=xxx \
  -e CLOUDINARY_API_SECRET=xxx \
  generador-certificados
```

## 🔐 Seguridad

### Configuraciones Importantes

- ✅ Cambiar `SECRET_KEY` en producción
- ✅ Cambiar `ADMIN_PASSWORD` en producción
- ✅ Habilitar HTTPS en producción
- ✅ Configurar CORS correctamente
- ✅ Rate limiting habilitado por defecto

### Rate Limits

- `/generar-certificados`: 10 requests/minuto
- `/enviar-emails`: 5 requests/minuto
- `/listar-certificados`: 60 requests/minuto
- Otros endpoints: 100 requests/hora

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

Respuesta:
```json
{
  "status": "healthy",
  "database": "connected",
  "cloudinary": "configured",
  "email": "configured",
  "certificados_totales": 900,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Logs

Los logs son estructurados en formato JSON:

```json
{
  "asctime": "2024-01-15 10:30:00",
  "name": "app",
  "levelname": "INFO",
  "message": "Batch generado: 100 exitosos, 0 errores"
}
```

## 🐛 Troubleshooting

### Error: Cloudinary no configurado

```bash
# Verificar variables de entorno
echo $CLOUDINARY_CLOUD_NAME
echo $CLOUDINARY_API_KEY

# Configurar correctamente en .env
CLOUDINARY_CLOUD_NAME=tu_cloud_name
CLOUDINARY_API_KEY=tu_api_key
CLOUDINARY_API_SECRET=tu_api_secret
```

### Error: Database connection failed

```bash
# Verificar PostgreSQL está corriendo
docker ps | grep postgres

# Verificar DATABASE_URL
echo $DATABASE_URL

# Reiniciar servicios
docker-compose restart
```

### Error: Rate limit exceeded

```bash
# Esperar 1 minuto o deshabilitar temporalmente
RATELIMIT_ENABLED=False python app.py
```

## 📈 Performance

### Benchmarks

- Generación: ~10 certificados/segundo
- Límite recomendado: 1000 certificados por batch
- Tiempo para 900 diplomas: ~90 segundos

### Optimizaciones

- ✅ Batch processing eficiente
- ✅ Índices de base de datos optimizados
- ✅ CDN de Cloudinary para entrega rápida
- ✅ Connection pooling de PostgreSQL
- ✅ Rate limiting con Redis

## 🤝 Contribución

1. Fork el proyecto
2. Crear branch (`git checkout -b feature/nueva-caracteristica`)
3. Commit cambios (`git commit -m 'Agregar nueva caracteristica'`)
4. Push al branch (`git push origin feature/nueva-caracteristica`)
5. Crear Pull Request

## 📝 Changelog

### v3.0 (2024-01)
- ✨ Integración con Cloudinary
- ✨ PostgreSQL con SQLAlchemy
- ✨ Sistema de emails con SendGrid
- ✨ Rate limiting con Redis
- ✨ Validación con Pydantic
- ✨ Logging estructurado
- 🐛 Múltiples mejoras de estabilidad

### v2.0 (2023)
- Versión inicial con SQLite
- Panel de administración
- API REST básica

## 📄 Licencia

MIT License

## 👥 Autor

Desarrollado para generar certificados universitarios de manera eficiente y escalable.

## 🔗 Links Útiles

- [Cloudinary Docs](https://cloudinary.com/documentation)
- [SendGrid Docs](https://docs.sendgrid.com)
- [Flask Docs](https://flask.palletsprojects.com)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org)
- [Pydantic Docs](https://docs.pydantic.dev)

## 💡 Preguntas Frecuentes

**P: ¿Cuántos certificados puedo generar?**
R: El límite por batch es 1000, pero puedes hacer múltiples batches. Cloudinary free tier soporta 25GB.

**P: ¿Los certificados se pierden si redeploy?**
R: No, están en Cloudinary y PostgreSQL, son persistentes.

**P: ¿Necesito SendGrid obligatoriamente?**
R: No, es opcional. Puedes generar certificados sin enviar emails.

**P: ¿Funciona sin Docker?**
R: Sí, puedes correrlo local con Python. Docker es recomendado pero no obligatorio.

**P: ¿Cuánto cuesta?**
R: Cloudinary free: 25GB, SendGrid free: 100 emails/día, PostgreSQL: gratis en Railway/Render.

## 🎯 Próximos Pasos

Una vez instalado:

1. ✅ Configurar Cloudinary
2. ✅ Configurar SendGrid (opcional)
3. ✅ Preparar lista de 900 participantes en JSON
4. ✅ Ejecutar generación batch
5. ✅ Verificar emails enviados
6. ✅ Compartir URLs: `https://tudominio.com/certificado/nombre-apellido`

¡Listo para generar 900 diplomas eficientemente! 🚀
