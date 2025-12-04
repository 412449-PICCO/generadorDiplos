# ✅ Completar Setup de Railway

Tu proyecto **generador-certificados** ya está creado en Railway!

**URL del proyecto:** https://railway.com/project/74494bec-3871-4ea6-8030-58eca60c3c85

## 🎯 Pasos para Completar (5 minutos)

### 1. Agregar PostgreSQL (2 minutos)

1. Ve a tu proyecto: https://railway.com/project/74494bec-3871-4ea6-8030-58eca60c3c85
2. Click en botón **"+ New"**
3. Selecciona **"Database"**
4. Selecciona **"Add PostgreSQL"**
5. ✅ PostgreSQL se crea automáticamente con la variable `DATABASE_URL`

### 2. Agregar Redis (1 minuto)

1. En el mismo proyecto, click **"+ New"** otra vez
2. Selecciona **"Database"**
3. Selecciona **"Add Redis"**
4. ✅ Redis se crea con la variable `REDIS_URL`

### 3. Configurar Variables de Entorno (2 minutos)

1. Click en el servicio de tu **aplicación** (no las bases de datos)
2. Tab **"Variables"**
3. Click **"+ New Variable"**
4. Agregar estas variables una por una:

```bash
# Cloudinary (OBLIGATORIO - obtener de cloudinary.com)
CLOUDINARY_CLOUD_NAME=tu_cloud_name_aqui
CLOUDINARY_API_KEY=tu_api_key_aqui
CLOUDINARY_API_SECRET=tu_api_secret_aqui
CLOUDINARY_FOLDER=certificados

# Seguridad (OBLIGATORIO - generar nuevo)
SECRET_KEY=pegar_output_del_comando_abajo
ADMIN_PASSWORD=elige_un_password_seguro

# App
APP_NAME=Generador de Certificados
APP_URL=pegar_url_de_railway_aqui

# Rate Limiting (usar variable de Redis)
RATELIMIT_STORAGE_URL=${{Redis.REDIS_URL}}
RATELIMIT_ENABLED=True
```

### 4. Generar SECRET_KEY

Corre este comando en tu terminal:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Copia el output y pégalo como valor de `SECRET_KEY` en Railway.

### 5. Obtener URL de Railway

1. En tu servicio de aplicación
2. Tab **"Settings"**
3. Sección **"Domains"**
4. Verás una URL tipo: `generador-certificados-production.up.railway.app`
5. Copia esa URL (sin el https://) y agrégala a:
   - Variable `APP_URL` = `https://tu-url.up.railway.app`

### 6. Verificar Deployment

Una vez configuradas las variables, Railway hace redeploy automático.

Monitorea en el tab **"Deployments"** - debería decir **"Active"**

### 7. Probar que Funciona

```bash
# Health check
curl https://tu-url.up.railway.app/health

# Debe responder:
{
  "status": "healthy",
  "database": "connected",
  "cloudinary": "configured"
}
```

## 📋 Checklist Rápido

```
☐ PostgreSQL agregado
☐ Redis agregado
☐ Variables de entorno configuradas:
  ☐ CLOUDINARY_CLOUD_NAME
  ☐ CLOUDINARY_API_KEY
  ☐ CLOUDINARY_API_SECRET
  ☐ SECRET_KEY (generado)
  ☐ ADMIN_PASSWORD
  ☐ APP_URL
  ☐ RATELIMIT_STORAGE_URL
☐ Deployment activo (verde)
☐ Health check pasa
```

## 🎓 Usar tu App

Una vez todo esté verde:

### Admin Panel:
```
https://tu-url.up.railway.app/admin
```

### Generar certificados:
```bash
curl -X POST https://tu-url.up.railway.app/generar-certificados \
  -H "Content-Type: application/json" \
  -d '{
    "participantes": [
      {"nombre": "Test Usuario", "email": "test@example.com"}
    ]
  }'
```

### Ver certificado:
```
https://tu-url.up.railway.app/certificado/test-usuario
```

## 🚨 Si algo falla

### Ver logs:
1. Tab "Logs" en tu servicio
2. Busca errores en rojo

### Redeploy manual:
1. Tab "Deployments"
2. Click en los 3 puntos del último deploy
3. "Redeploy"

### Variables faltantes:
Verifica que todas las variables estén configuradas sin errores de tipeo.

## 💡 Tips

- **Cloudinary**: Si aún no lo configuraste, ve a `CLOUDINARY_SETUP.md`
- **Custom Domain**: Settings → Domains → Add Custom Domain
- **Logs en tiempo real**: Usa `railway logs --follow` en terminal
- **Variables**: Puedes editarlas en cualquier momento, habrá redeploy automático

## 🎯 Siguiente: Generar 900 Diplomas

Una vez verificado que todo funciona:

1. Prepara tu JSON con 900 participantes
2. Usa el endpoint `/generar-certificados`
3. O el Admin Panel
4. Exporta CSV con URLs
5. ¡Envía los links por tu sistema de emails!

---

**Tu proyecto:** https://railway.com/project/74494bec-3871-4ea6-8030-58eca60c3c85

¿Problemas? Revisa los logs o avísame! 🚀
