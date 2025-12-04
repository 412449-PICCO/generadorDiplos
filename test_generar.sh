#!/bin/bash
# Script para generar certificado de prueba

curl -X POST https://generador-certificados-production.up.railway.app/generar-certificados \
  -H "Content-Type: application/json" \
  -d '{
    "participantes": [
      {
        "nombre": "Constantino Picco",
        "email": "constantino@ejemplo.com"
      }
    ]
  }'
