# 📸 Guía de Configuración de Cloudinary

Esta guía te llevará paso a paso para configurar Cloudinary y tener tus certificados en la nube con CDN global.

## ¿Qué es Cloudinary?

Cloudinary es un servicio de almacenamiento de archivos multimedia en la nube con CDN integrado. Es ideal para:
- ✅ Almacenar SVGs de certificados sin límite local
- ✅ Entrega rápida desde CDN global (servidores en todo el mundo)
- ✅ Transformaciones automáticas (SVG → PNG para redes sociales)
- ✅ URLs permanentes que nunca caducan
- ✅ Plan gratuito generoso (25 GB, 25 créditos/mes)

## 📋 Paso 1: Crear Cuenta Gratuita

1. Ve a https://cloudinary.com
2. Click en **"Sign Up for Free"**
3. Completa el formulario:
   - Email
   - Contraseña
   - Nombre de la compañía/proyecto
4. Verifica tu email
5. ¡Listo! Ya tienes tu cuenta

**Plan Gratuito incluye:**
- 25 GB de almacenamiento
- 25,000 transformaciones/mes
- 25 GB de ancho de banda/mes
- Suficiente para miles de certificados

## 🔑 Paso 2: Obtener Credenciales

Una vez dentro del Dashboard de Cloudinary:

1. **Dashboard Principal** - Verás un panel con tus credenciales:

```
Account Details
┌─────────────────────────────────────┐
│ Cloud name:     tucloudname         │
│ API Key:        123456789012345     │
│ API Secret:     ●●●●●●●●●●● (mostrar)│
└─────────────────────────────────────┘
```

2. **Copiar Cloud Name:**
   - Está visible directamente
   - Ejemplo: `dj8k5m2p4`
   - Es tu identificador único

3. **Copiar API Key:**
   - Número largo visible
   - Ejemplo: `123456789012345`

4. **Copiar API Secret:**
   - Click en el ícono de ojo 👁️ para revelar
   - Copia el texto completo
   - Ejemplo: `abcdefg123456_ABCD`
   - ⚠️ **NO compartas este valor** (es secreto)

## 💻 Paso 3: Configurar en tu Proyecto

### Opción A: Variables de Entorno (.env)

1. Copia el archivo de ejemplo:
```bash
cp .env.example .env
```

2. Edita `.env` con tus credenciales:
```bash
# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=tu_cloud_name_aqui
CLOUDINARY_API_KEY=tu_api_key_aqui
CLOUDINARY_API_SECRET=tu_api_secret_aqui
CLOUDINARY_FOLDER=certificados
```

**Ejemplo real:**
```bash
CLOUDINARY_CLOUD_NAME=dj8k5m2p4
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=abcdefg123456_ABCD
CLOUDINARY_FOLDER=certificados
```

### Opción B: Docker Compose

Si usas Docker, edita `docker-compose.yml`:

```yaml
environment:
  - CLOUDINARY_CLOUD_NAME=tu_cloud_name
  - CLOUDINARY_API_KEY=tu_api_key
  - CLOUDINARY_API_SECRET=tu_api_secret
```

O mejor aún, crea un archivo `.env` y Docker lo usará automáticamente.

## ✅ Paso 4: Verificar Configuración

### Método 1: Iniciar la aplicación

```bash
# Con Docker
docker-compose up

# Sin Docker
python app.py
```

**Deberías ver en la consola:**
```
============================================================
🚀 Generador de Certificados v3.0 iniciado
============================================================
📊 Base de datos: sqlite:///certificados.db
☁️  Cloudinary: ✅ Configurado        <-- Debe decir esto
🎓 Certificados registrados: 0
============================================================
```

### Método 2: Health Check

```bash
curl http://localhost:8000/health
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "database": "connected",
  "cloudinary": "configured",     ← Debe decir "configured"
  "certificados_totales": 0,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Método 3: Generar un certificado de prueba

```bash
curl -X POST http://localhost:8000/generar-certificados \
  -H "Content-Type: application/json" \
  -d '{
    "participantes": [
      {"nombre": "Test Usuario", "email": "test@example.com"}
    ]
  }'
```

**Si funciona, recibirás:**
```json
{
  "mensaje": "Proceso completado. 1 certificados generados",
  "total": 1,
  "exitosos": 1,
  "errores": 0,
  "resultados": [
    {
      "nombre": "Test Usuario",
      "email": "test@example.com",
      "slug": "test-usuario",
      "cloudinary_url": "https://res.cloudinary.com/...",
      "url": "/certificado/test-usuario",
      "success": true
    }
  ]
}
```

## 🌐 Paso 5: Verificar en Cloudinary Dashboard

1. Ve al Dashboard de Cloudinary
2. Click en **"Media Library"** en el menú lateral
3. Verás una carpeta llamada **"certificados"**
4. Dentro encontrarás tus archivos SVG subidos
5. Click en cualquier archivo para ver preview y URL

## 🔍 Entender las URLs de Cloudinary

Cloudinary genera URLs permanentes con este formato:

```
https://res.cloudinary.com/[cloud_name]/raw/upload/v[version]/[folder]/[filename]
```

**Ejemplo:**
```
https://res.cloudinary.com/dj8k5m2p4/raw/upload/v1705320000/certificados/juan-perez.svg
```

**Partes de la URL:**
- `res.cloudinary.com` - CDN de Cloudinary
- `dj8k5m2p4` - Tu Cloud Name
- `raw/upload` - Tipo de recurso (SVG es "raw")
- `v1705320000` - Versión/timestamp
- `certificados` - Tu carpeta
- `juan-perez.svg` - Nombre del archivo

## 🎨 Transformaciones Automáticas

Cloudinary puede transformar tus SVGs sobre la marcha:

### Convertir a PNG (para redes sociales)

```
https://res.cloudinary.com/[cloud]/image/upload/f_png/certificados/juan-perez.svg
```

### Redimensionar

```
https://res.cloudinary.com/[cloud]/image/upload/w_1200,h_675/certificados/juan-perez.svg
```

### Optimizar para web

```
https://res.cloudinary.com/[cloud]/image/upload/q_auto,f_auto/certificados/juan-perez.svg
```

**La aplicación hace esto automáticamente** cuando alguien comparte en redes sociales gracias al endpoint `/preview/<slug>`.

## 🚨 Troubleshooting

### Error: "Cloudinary no configurado"

**Causa:** Credenciales incorrectas o faltantes

**Solución:**
```bash
# 1. Verificar que .env existe
ls -la .env

# 2. Verificar contenido
cat .env | grep CLOUDINARY

# 3. Verificar que no hay espacios extras
CLOUDINARY_CLOUD_NAME=tucloud    ✅ Correcto
CLOUDINARY_CLOUD_NAME = tucloud  ❌ Incorrecto (espacios)
```

### Error: "Upload failed"

**Causa:** API Secret incorrecto o permisos de cuenta

**Solución:**
1. Ve a Cloudinary Dashboard
2. Settings → Security
3. Verifica que "Unsigned uploads" esté habilitado para desarrollo
4. O usa signed uploads (configuración por defecto)

### Error: "Resource not found"

**Causa:** Folder no existe o nombre incorrecto

**Solución:**
```bash
# En .env, asegúrate de tener:
CLOUDINARY_FOLDER=certificados

# La carpeta se crea automáticamente al subir el primer archivo
```

### Límite de almacenamiento alcanzado

**Solución:**
1. Dashboard → Usage
2. Revisa tu uso actual
3. Elimina certificados antiguos si es necesario:
```python
from cloudinary_storage import CloudinaryStorage
storage = CloudinaryStorage(...)
storage.delete('certificados/viejo-certificado')
```

## 💰 Límites del Plan Gratuito

| Recurso | Límite Gratuito | Suficiente Para |
|---------|-----------------|-----------------|
| Almacenamiento | 25 GB | ~35,000 certificados SVG (700KB c/u) |
| Transformaciones | 25,000/mes | 800 certificados/día |
| Ancho de banda | 25 GB/mes | ~35,000 vistas/mes |

**Para 900 diplomas:**
- Espacio usado: ~630 MB
- Transformaciones: ~900 (primera generación)
- Ancho de banda: Depende de las vistas

✅ **El plan gratuito es más que suficiente para 900 diplomas**

## 📈 Monitorear Uso

1. Dashboard de Cloudinary
2. Click en **"Usage"**
3. Verás gráficas de:
   - Storage usado
   - Transformaciones
   - Bandwidth
   - Requests

## 🔐 Seguridad

### Buenas Prácticas:

✅ **DO:**
- Usa variables de entorno para credenciales
- Agrega `.env` a `.gitignore`
- Rota el API Secret cada 6 meses
- Usa folders para organizar (`certificados/`)
- Habilita "Media Library" protection en producción

❌ **DON'T:**
- Commitear credenciales en Git
- Compartir tu API Secret
- Usar unsigned uploads en producción
- Dejar el API Key visible en código frontend

### Regenerar API Secret (si se filtró)

1. Dashboard → Settings → Security
2. Click en "Regenerate API Secret"
3. Actualiza `.env` con el nuevo secret
4. Reinicia la aplicación

## 🎯 Siguiente Paso

Una vez configurado Cloudinary:

1. ✅ Genera tus 900 certificados
2. ✅ Todos se suben automáticamente a Cloudinary
3. ✅ Obtén URLs permanentes tipo `/certificado/nombre-apellido`
4. ✅ Envía los links por email (con tu sistema de emails)
5. ✅ Los participantes pueden ver y descargar sus certificados

## 📞 Soporte

- **Cloudinary Docs:** https://cloudinary.com/documentation
- **Support:** https://support.cloudinary.com
- **Community:** https://community.cloudinary.com

---

¿Listo? Copia tus credenciales a `.env` y ejecuta `python app.py` 🚀
