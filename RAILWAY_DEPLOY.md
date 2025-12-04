# 🚂 Guía de Deployment en Railway

Esta guía te llevará paso a paso para deployar tu aplicación de certificados en Railway con PostgreSQL incluido.

## 🎯 Requisitos Previos

- ✅ Cuenta de Railway (gratis)
- ✅ Cuenta de Cloudinary configurada
- ✅ Repositorio en GitHub (opcional pero recomendado)

## 📋 Paso 1: Crear Cuenta en Railway

1. Ve a https://railway.app
2. Click en **"Start a New Project"** o **"Login"**
3. Inicia sesión con GitHub (recomendado)
4. Railway te da **$5 de crédito gratis** cada mes

**Créditos gratuitos incluyen:**
- $5 USD/mes de uso
- Suficiente para:
  - PostgreSQL pequeño
  - 1 app web
  - ~550 horas de ejecución

## 🚀 Paso 2: Opciones de Deployment

### Opción A: Deploy desde GitHub (Recomendado)

#### 2.1. Pushear código a GitHub

```bash
# Si no tienes repo aún
git init
git add .
git commit -m "Ready for Railway deployment"
git branch -M main
git remote add origin https://github.com/tu-usuario/tu-repo.git
git push -u origin main
```

#### 2.2. Conectar Railway con GitHub

1. En Railway Dashboard, click **"New Project"**
2. Selecciona **"Deploy from GitHub repo"**
3. Autoriza Railway a acceder a tu GitHub
4. Selecciona el repositorio `generadorPdf`
5. Click **"Deploy Now"**

### Opción B: Deploy con Railway CLI

```bash
# 1. Instalar Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Inicializar proyecto (desde el directorio del código)
cd /Users/costipicco/Documents/GitHub/generadorPdf
railway init

# 4. Deploy
railway up
```

## 🗄️ Paso 3: Agregar PostgreSQL

### 3.1. En el Dashboard de Railway:

1. Click en tu proyecto
2. Click en **"New"** → **"Database"** → **"PostgreSQL"**
3. Railway crea automáticamente la base de datos
4. Genera variable `DATABASE_URL` automáticamente

### 3.2. Verificar DATABASE_URL:

1. Click en el servicio de PostgreSQL
2. Tab **"Variables"**
3. Verás `DATABASE_URL` con valor tipo:
```
postgresql://postgres:password@host:5432/railway
```

**✅ Esta variable ya está disponible para tu app automáticamente**

## 🗄️ Paso 4: Agregar Redis (para Rate Limiting)

1. En tu proyecto de Railway
2. Click **"New"** → **"Database"** → **"Redis"**
3. Railway crea Redis y genera `REDIS_URL`

**✅ Variables automáticas:**
- `REDIS_URL` - Para conexión
- Usaremos esta para rate limiting

## ⚙️ Paso 5: Configurar Variables de Entorno

### 5.1. En Railway Dashboard:

1. Click en tu servicio de aplicación (no la DB)
2. Tab **"Variables"**
3. Click **"New Variable"**

### 5.2. Agregar estas variables:

#### Variables Obligatorias:

```bash
# Cloudinary (OBLIGATORIO)
CLOUDINARY_CLOUD_NAME=tu_cloud_name
CLOUDINARY_API_KEY=tu_api_key
CLOUDINARY_API_SECRET=tu_api_secret
CLOUDINARY_FOLDER=certificados

# Seguridad (OBLIGATORIO)
SECRET_KEY=genera-una-clave-aleatoria-segura-64-caracteres
ADMIN_PASSWORD=tu-password-seguro-aqui

# App
APP_NAME=Generador de Certificados
APP_URL=https://tu-proyecto.up.railway.app
```

#### Variables Automáticas (Railway las crea):

```bash
DATABASE_URL=postgresql://...  (Auto-generada)
REDIS_URL=redis://...          (Auto-generada)
PORT=8000                      (Auto-generada)
```

#### Variables Opcionales:

```bash
# Rate Limiting (usando REDIS_URL)
RATELIMIT_STORAGE_URL=$REDIS_URL
RATELIMIT_ENABLED=True

# Debug (NUNCA true en producción)
DEBUG=False
```

### 5.3. Generar SECRET_KEY segura:

```bash
# En tu terminal local
python -c "import secrets; print(secrets.token_urlsafe(64))"

# Copia el output a la variable SECRET_KEY en Railway
```

## 🔧 Paso 6: Configurar URLs

### 6.1. Obtener tu URL de Railway:

1. En el Dashboard, tu app tiene una URL tipo:
```
https://generadorpdf-production-XXXX.up.railway.app
```

2. Copia esta URL completa

### 6.2. Actualizar APP_URL:

1. Variables → Editar `APP_URL`
2. Pegar tu URL de Railway
3. Ejemplo: `https://generadorpdf-production-a1b2.up.railway.app`

### 6.3. (Opcional) Custom Domain:

Si tienes un dominio propio:

1. Settings → **"Domains"**
2. Click **"Custom Domain"**
3. Ingresa tu dominio: `certificados.tudominio.com`
4. Configura DNS según instrucciones
5. Railway genera certificado SSL automático

## 🏗️ Paso 7: Deploy Automático

Railway hace build y deploy automáticamente:

### 7.1. Proceso de Build:

```
1. 📥 Pull del código desde GitHub
2. 🐳 Build Docker image con Dockerfile
3. 📦 Instala dependencias (requirements.txt)
4. 🎭 Instala Playwright + Chromium
5. 🚀 Inicia con Gunicorn
```

### 7.2. Monitorear el Deploy:

1. Tab **"Deployments"**
2. Verás logs en tiempo real:
```
Building...
Installing dependencies...
playwright install chromium...
Starting Gunicorn...
✅ Deployment successful!
```

### 7.3. Verificar Health:

Una vez deployado:
```bash
curl https://tu-app.up.railway.app/health
```

Respuesta esperada:
```json
{
  "status": "healthy",
  "database": "connected",
  "cloudinary": "configured",
  "certificados_totales": 0,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## ✅ Paso 8: Verificar Todo Funciona

### 8.1. Acceder a tu app:

```
https://tu-app.up.railway.app
```

### 8.2. Acceder al Admin:

```
https://tu-app.up.railway.app/admin
```

Login con tu `ADMIN_PASSWORD`

### 8.3. Generar certificado de prueba:

```bash
curl -X POST https://tu-app.up.railway.app/generar-certificados \
  -H "Content-Type: application/json" \
  -d '{
    "participantes": [
      {"nombre": "Test Usuario", "email": "test@example.com"}
    ]
  }'
```

### 8.4. Ver certificado:

```
https://tu-app.up.railway.app/certificado/test-usuario
```

## 🎓 Paso 9: Generar 900 Diplomas

### Opción 1: Via API

```bash
# Preparar JSON con 900 participantes
curl -X POST https://tu-app.up.railway.app/generar-certificados \
  -H "Content-Type: application/json" \
  -d @participantes_900.json
```

### Opción 2: Desde Admin Panel

1. Acceder a `/admin`
2. Pegar JSON con participantes
3. Click **"Generar"**
4. Monitorear progreso

### Opción 3: Script Python

```python
import requests

url = "https://tu-app.up.railway.app/generar-certificados"

# Cargar participantes
with open('participantes_900.json') as f:
    data = json.load(f)

# Enviar request
response = requests.post(url, json=data)
print(response.json())
```

## 📊 Paso 10: Monitorear Performance

### 10.1. Logs en Railway:

1. Tab **"Logs"**
2. Verás logs en tiempo real:
```
INFO: Batch generado: 100 exitosos, 0 errores
INFO: Certificado subido a Cloudinary: juan-perez
```

### 10.2. Metrics:

1. Tab **"Metrics"**
2. Monitorea:
   - CPU usage
   - Memory usage
   - Network traffic
   - Request count

### 10.3. Database Size:

1. Click en servicio PostgreSQL
2. Tab **"Metrics"**
3. Revisa storage usado

## 💰 Costos y Límites

### Plan Gratuito de Railway:

| Recurso | Incluido |
|---------|----------|
| Crédito | $5/mes |
| Apps | Ilimitadas |
| PostgreSQL | Incluido |
| Redis | Incluido |
| RAM | 512 MB por servicio |
| CPU | Compartido |
| Build time | Ilimitado |

### Uso Estimado para 900 Diplomas:

```
App Web:        ~$2/mes
PostgreSQL:     ~$1/mes
Redis:          ~$0.50/mes
TOTAL:          ~$3.50/mes ✅ Dentro del crédito gratuito
```

### Si excedes $5/mes:

1. Railway te avisa por email
2. Puedes agregar tarjeta de crédito
3. O reducir uso (pausar servicios)

## 🔄 Auto-Deploy desde GitHub

### Configurar Continuous Deployment:

1. Settings → **"Deployment Triggers"**
2. Habilitar **"Auto-deploy on push"**
3. Ahora cada `git push` → deploy automático

### Workflow:

```bash
# 1. Hacer cambios locales
vim app.py

# 2. Commit
git add .
git commit -m "Update feature"

# 3. Push
git push origin main

# 4. Railway auto-deploys 🚀
```

## 🚨 Troubleshooting

### Error: Build Failed

**Causa:** Dependencias no se instalan

**Solución:**
```bash
# Verificar requirements.txt está completo
cat requirements.txt

# Debe incluir:
flask>=3.0.0
gunicorn>=21.2.0
cloudinary>=1.36.0
# ... etc
```

### Error: Cloudinary not configured

**Causa:** Variables de entorno no configuradas

**Solución:**
1. Variables → Verificar `CLOUDINARY_*`
2. Redeploy: Click **"Redeploy"**

### Error: Database connection failed

**Causa:** PostgreSQL no agregado o `DATABASE_URL` incorrecta

**Solución:**
1. Verificar PostgreSQL está activo
2. Variables → Verificar `DATABASE_URL`
3. Formato debe ser: `postgresql://user:pass@host:port/db`

### Error: Port binding failed

**Causa:** App no usa variable `$PORT`

**Solución:**
- Railway inyecta `PORT` automáticamente
- Gunicorn usa: `--bind 0.0.0.0:$PORT` ✅

### App no responde / 503

**Causa:** Health check fallando

**Solución:**
1. Logs → Verificar errores
2. Verificar `/health` endpoint funciona
3. Aumentar timeout: `railway.json` → `healthcheckTimeout: 200`

## 🔐 Seguridad en Producción

### Checklist de Seguridad:

- ✅ `DEBUG=False`
- ✅ `SECRET_KEY` aleatorio y único
- ✅ `ADMIN_PASSWORD` fuerte
- ✅ Cloudinary API Secret no expuesto
- ✅ HTTPS habilitado (automático en Railway)
- ✅ Rate limiting habilitado
- ✅ CORS configurado correctamente

### Rotar Secrets:

```bash
# Cada 6 meses, generar nuevo SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(64))"

# Actualizar en Railway Variables
# Redeploy
```

## 📈 Escalar (si creces)

### Aumentar RAM:

1. Settings → **"Resources"**
2. Ajustar RAM slider
3. Costo aumenta proporcionalmente

### Aumentar Workers Gunicorn:

En `railway.json`:
```json
"startCommand": "gunicorn --workers 8 ..."
```

### Agregar más instancias:

1. **"New Service"** → Duplicate existing
2. Load balancer automático de Railway

## 📞 Soporte

- **Railway Docs:** https://docs.railway.app
- **Discord:** https://discord.gg/railway
- **Status:** https://status.railway.app

## 🎯 Resumen: Lista de Verificación

```
☐ 1. Cuenta de Railway creada
☐ 2. Código pusheado a GitHub
☐ 3. Proyecto creado en Railway
☐ 4. PostgreSQL agregado
☐ 5. Redis agregado
☐ 6. Variables de entorno configuradas:
     ☐ CLOUDINARY_CLOUD_NAME
     ☐ CLOUDINARY_API_KEY
     ☐ CLOUDINARY_API_SECRET
     ☐ SECRET_KEY
     ☐ ADMIN_PASSWORD
     ☐ APP_URL
☐ 7. Deploy completado exitosamente
☐ 8. Health check pasa (verde)
☐ 9. Certificado de prueba generado
☐ 10. 900 diplomas generados
```

## 🚀 ¡Listo para Producción!

Tu app está ahora:
- ✅ Deployada en Railway
- ✅ Con PostgreSQL escalable
- ✅ Con Redis para rate limiting
- ✅ Con Cloudinary CDN
- ✅ Con HTTPS automático
- ✅ Con monitoreo y logs
- ✅ Lista para generar 900 diplomas

**URL de tu app:**
```
https://tu-proyecto.up.railway.app
```

¿Problemas? Revisa los logs en Railway → Tab "Logs" 🔍
