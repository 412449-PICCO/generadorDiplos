# 🔐 Configurar IP Whitelist para Panel de Admin

## ✅ Protecciones Implementadas

Se han agregado las siguientes protecciones de seguridad:

### Endpoints Públicos (Diplomas) - CON Rate Limiting:
- ✅ `/certificado/<slug>` - 10 requests/minuto
- ✅ `/certificado/<slug>/pdf` - 10 requests/minuto
- ✅ `/preview/<slug>` - 30 requests/minuto
- ✅ `/descargar/<slug>` - 20 requests/minuto

**Protecciones aplicadas:**
- Validación de slug (solo caracteres seguros)
- Validación de URLs de Cloudinary (previene SSRF)
- Timeout reducido (3 segundos)
- Límite de tamaño de SVG (5MB máximo)

### Endpoints de Admin - PROTEGIDOS por IP Whitelist:
- 🔒 `/admin`
- 🔒 `/admin/login`
- 🔒 `/admin/dashboard`
- 🔒 `/admin/generar`
- 🔒 `/admin/exportar`
- 🔒 `/admin/logout`
- 🔒 `/generar-certificados`

**Solo IPs autorizadas pueden acceder a estos endpoints.**

---

## 📋 Paso 1: Obtener Tu IP

### Opción A: Desde tu navegador
```bash
# Abre este link en tu navegador:
https://api.ipify.org?format=json

# O usa curl:
curl https://api.ipify.org
```

### Opción B: Desde Railway
1. Ve a https://railway.app
2. Abre tu proyecto "generador-certificados"
3. Ve a la pestaña "Logs"
4. Intenta acceder a `/admin` desde tu navegador
5. Verás un log que dice: "Acceso denegado desde IP no autorizada: X.X.X.X"
6. Esa es tu IP

---

## 📋 Paso 2: Configurar Variable de Entorno en Railway

1. **Ve a Railway Dashboard:**
   - https://railway.app
   - Proyecto: "generador-certificados"
   - Service: "generador-certificados"

2. **Click en "Variables"**

3. **Agregar variable `ADMIN_ALLOWED_IPS`:**
   ```
   Variable name: ADMIN_ALLOWED_IPS
   Value: 123.456.789.012
   ```

   **Si tienes múltiples IPs (casa, oficina, etc.):**
   ```
   Value: 123.456.789.012,98.765.432.109,192.168.1.100
   ```

   ⚠️ **IMPORTANTE:** Separar las IPs con comas, sin espacios.

4. **Click en "Add"**

5. **Railway hará redeploy automáticamente** con la nueva configuración.

---

## 📋 Paso 3: Verificar que Funciona

### Test 1: Acceso desde IP autorizada (tú)
```bash
# Intenta acceder al admin desde tu navegador:
https://tu-app.railway.app/admin

# Deberías ver la página de login ✅
```

### Test 2: Acceso desde IP NO autorizada (otros)
```bash
# Pide a alguien con otra IP que intente acceder:
https://tu-app.railway.app/admin

# Deberían ver:
# {
#   "error": "Acceso denegado",
#   "message": "Tu IP no tiene permisos para acceder a este recurso"
# }
```

### Test 3: Los diplomas siguen públicos ✅
```bash
# Cualquier persona debería poder ver diplomas:
https://tu-app.railway.app/certificado/test-slug

# Sin restricciones de IP (solo rate limiting)
```

---

## 🔄 Cambiar tu IP en el Futuro

Si tu IP cambia (cambias de ubicación, proveedor, etc.):

1. Obtén tu nueva IP (Paso 1)
2. Ve a Railway Variables
3. Edita `ADMIN_ALLOWED_IPS`
4. Agrega tu nueva IP (separada por coma)
5. Guarda

Railway hará redeploy automático.

---

## 🌐 IP Dinámica vs Estática

### Si tienes IP dinámica (cambia frecuentemente):

**Opción 1: Agregar rango de IPs**
```
ADMIN_ALLOWED_IPS=123.456.789.0,123.456.789.1,123.456.789.2,...
```

**Opción 2: Usar VPN con IP fija**
Servicios como:
- Tailscale (gratis)
- ZeroTier (gratis)
- NordVPN, ExpressVPN, etc.

**Opción 3: NO configurar `ADMIN_ALLOWED_IPS`**
⚠️ En ese caso, el admin estará protegido solo por password.
Solo en desarrollo/testing.

### Si tienes IP estática:
✅ Perfecto! Solo agrega tu IP una vez.

---

## 🚨 Qué hacer si te bloqueas

Si configuraste mal y no puedes acceder al admin:

1. **Ve a Railway Variables**
2. **Borra la variable `ADMIN_ALLOWED_IPS` temporalmente**
3. **Accede al admin**
4. **Agrega nuevamente la variable con la IP correcta**

O:

1. **Edita `ADMIN_ALLOWED_IPS` desde Railway CLI:**
   ```bash
   railway variables --set ADMIN_ALLOWED_IPS=tu-ip-correcta
   ```

---

## 📊 Resumen de Protecciones

| Endpoint | Público | Rate Limit | IP Whitelist | Validación Slug | Validación URL |
|----------|---------|------------|--------------|-----------------|----------------|
| `/certificado/<slug>` | ✅ | 10/min | ❌ | ✅ | ✅ |
| `/certificado/<slug>/pdf` | ✅ | 10/min | ❌ | ✅ | ✅ |
| `/preview/<slug>` | ✅ | 30/min | ❌ | ✅ | ❌ |
| `/descargar/<slug>` | ✅ | 20/min | ❌ | ✅ | ✅ |
| `/admin` | ❌ | ❌ | ✅ | ❌ | ❌ |
| `/generar-certificados` | ❌ | 10/min | ✅ | ❌ | ❌ |

---

## 🎯 Ejemplo de Configuración Completa

Variables de entorno en Railway:

```env
# Admin
ADMIN_PASSWORD=tu-password-super-seguro
ADMIN_ALLOWED_IPS=123.456.789.012,98.765.432.109

# Cloudinary
CLOUDINARY_CLOUD_NAME=tu-cloud-name
CLOUDINARY_API_KEY=tu-api-key
CLOUDINARY_API_SECRET=tu-api-secret

# Base de datos (Railway la configura automáticamente)
DATABASE_URL=postgresql://...

# Opcionales
PORT=8000
DEBUG=false
SECRET_KEY=tu-secret-key-aleatoria
```

---

## ✅ Checklist Final

- [ ] He obtenido mi IP pública
- [ ] He configurado `ADMIN_ALLOWED_IPS` en Railway
- [ ] El servicio se ha redeployado
- [ ] Puedo acceder a `/admin` desde mi IP
- [ ] Otros NO pueden acceder a `/admin`
- [ ] Los diplomas `/certificado/<slug>` siguen siendo públicos
- [ ] He guardado mi IP en un lugar seguro

---

¡Listo! Tu panel de admin ahora está protegido y solo tú puedes acceder. 🔒
