# 🚂 Deployment en Railway

Guía completa para deployar el Generador de Certificados en Railway.app

## 🚀 Opción 1: Deploy desde GitHub (Recomendado)

### Paso 1: Preparar repositorio

```bash
# Si no tienes git inicializado
git init
git add .
git commit -m "Initial commit"

# Crear repo en GitHub y subir
git remote add origin https://github.com/tu-usuario/generador-certificados.git
git branch -M main
git push -u origin main
```

### Paso 2: Deploy en Railway

1. Ve a [Railway.app](https://railway.app)
2. Click en **"New Project"**
3. Selecciona **"Deploy from GitHub repo"**
4. Autoriza Railway a acceder a tu GitHub
5. Selecciona el repositorio
6. Railway detectará automáticamente el `Dockerfile`

### Paso 3: Configurar Variables de Entorno

En el dashboard de Railway, agrega estas variables:

```
ADMIN_PASSWORD=tu-clave-super-secreta-aqui
SECRET_KEY=genera-una-clave-aleatoria-larga-aqui
PORT=8000
DEBUG=false
```

**Generar SECRET_KEY segura:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Paso 4: Deploy!

Railway deployará automáticamente. Espera 3-5 minutos.

## 🚀 Opción 2: Deploy desde CLI

### Instalar Railway CLI

```bash
# macOS/Linux
curl -fsSL https://railway.app/install.sh | sh

# Windows (PowerShell)
iwr https://railway.app/install.ps1 | iex
```

### Login y Deploy

```bash
# Login
railway login

# Inicializar proyecto
railway init

# Configurar variables
railway variables set ADMIN_PASSWORD="tu-clave-aqui"
railway variables set SECRET_KEY="tu-secret-key-aqui"

# Deploy
railway up
```

## 📊 Verificar Deployment

Después del deploy, Railway te dará una URL:
```
https://tu-proyecto.railway.app
```

**Verifica:**
```bash
# Health check
curl https://tu-proyecto.railway.app/health

# Admin panel
https://tu-proyecto.railway.app/admin
```

## 🔧 Configuración Avanzada

### Variables de Entorno Completas

```env
# Requeridas
PORT=8000
ADMIN_PASSWORD=tu-clave-super-secreta

# Opcionales
SECRET_KEY=clave-aleatoria-larga-64-caracteres
DEBUG=false
```

### Volúmenes Persistentes (Opcional)

Railway automáticamente persiste:
- Base de datos SQLite (`certificados.db`)
- Certificados generados (`certificados/`)

**No necesitas configurar nada adicional.**

### Dominio Personalizado

1. En Railway dashboard, ve a **Settings**
2. Click en **Domains**
3. Agrega tu dominio personalizado
4. Configura DNS según instrucciones de Railway

## 🐛 Troubleshooting

### Error: "Port already in use"
Railway maneja el puerto automáticamente. Asegúrate de que tu código use:
```python
PORT = int(os.getenv('PORT', 8000))
```
✅ Ya está configurado en `app.py`

### Error: "Playwright browser not found"
El Dockerfile instala Chromium automáticamente.
Si hay problemas, verifica que el build completó correctamente.

### Error: "Database locked"
SQLite puede tener problemas con múltiples workers.
Solución: Usar un solo worker (ya configurado por defecto).

### Logs en tiempo real

```bash
railway logs
```

O en el dashboard: **View Logs**

## 📦 Estructura del Proyecto para Railway

```
.
├── Dockerfile          ← Railway usa esto automáticamente
├── railway.json        ← Configuración de Railway
├── requirements.txt    ← Dependencias Python
├── app.py             ← Aplicación Flask
├── .dockerignore      ← Archivos a ignorar en build
└── ...
```

## 🔄 Actualizar Deployment

### Automático (con GitHub)

```bash
git add .
git commit -m "Update feature"
git push
```

Railway detecta el push y redeploys automáticamente.

### Manual (con CLI)

```bash
railway up
```

## 💾 Backup de Base de Datos

### Descargar BD desde Railway

```bash
railway run cat certificados.db > backup.db
```

### Restaurar BD

```bash
railway run -- sh -c "cat > certificados.db" < backup.db
```

## 📈 Monitoreo

Railway provee:
- ✅ Logs en tiempo real
- ✅ Métricas de CPU/RAM
- ✅ Uptime monitoring
- ✅ Health checks automáticos

## 💰 Costos

**Plan Starter (Gratis):**
- $5 de crédito gratis/mes
- Suficiente para ~10,000 certificados/mes
- Sin tarjeta de crédito requerida

**Plan Developer ($5/mes):**
- $5 + $0.000463 por GB-hora
- Para producción con más tráfico

## 🔗 URLs Finales

Después del deploy:

```
Aplicación:  https://tu-proyecto.railway.app
Admin Panel: https://tu-proyecto.railway.app/admin
API Docs:    https://tu-proyecto.railway.app/
Certificado: https://tu-proyecto.railway.app/certificado/nombre-apellido
```

## ✅ Checklist Pre-Deploy

- [ ] Código subido a GitHub
- [ ] `Dockerfile` presente
- [ ] `requirements.txt` actualizado
- [ ] Variables de entorno configuradas
- [ ] `ADMIN_PASSWORD` cambiada
- [ ] `SECRET_KEY` generada
- [ ] Template SVG incluido
- [ ] .gitignore correcto

## 🎯 Después del Deploy

1. **Verifica health:** `/health`
2. **Login admin:** `/admin`
3. **Genera certificado de prueba**
4. **Verifica URL del certificado**
5. **Exporta CSV de prueba**
6. **Prueba Open Graph** en LinkedIn Post Inspector

## 📚 Recursos

- [Railway Docs](https://docs.railway.app)
- [Railway Discord](https://discord.gg/railway)
- [Railway Status](https://status.railway.app)

---

¿Problemas? Revisa los logs con `railway logs` o en el dashboard.
