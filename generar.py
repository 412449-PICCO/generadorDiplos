#!/usr/bin/env python3
"""
Script simple para generar certificados sin necesidad de levantar el servidor
"""

from generator import CertificateGenerator
from database import Database
import json
import sys


def main():
    print('🎓 Generador de Certificados')
    print('=' * 50)

    # Configuración
    template_path = 'template.svg'
    output_dir = 'certificados'
    data_file = 'participantes.json'
    db_path = 'certificados.db'

    # Inicializar base de datos
    db = Database(db_path)

    # Inicializar generador con base de datos
    try:
        generator = CertificateGenerator(template_path, output_dir, database=db)
    except FileNotFoundError as e:
        print(f'❌ Error: {e}')
        print('Asegúrate de que existe el archivo template.svg')
        sys.exit(1)

    # Leer archivo de participantes
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f'❌ Error: No se encontró el archivo {data_file}')
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f'❌ Error al leer JSON: {e}')
        sys.exit(1)

    participantes = data.get('participantes', [])

    if not participantes:
        print('⚠️  No hay participantes en el archivo')
        sys.exit(0)

    print(f'\n📋 Total de participantes: {len(participantes)}\n')

    # Generar certificados
    exitosos = 0
    errores = 0

    for i, participante in enumerate(participantes, 1):
        nombre = participante.get('nombre')
        email = participante.get('email')

        if not nombre or not email:
            print(f'⚠️  Participante {i}: Datos incompletos')
            errores += 1
            continue

        try:
            resultado = generator.generar_certificado(nombre, email)
            print(f'✅ {i}. {nombre} ({email})')
            print(f'   Slug: {resultado["slug"]}')
            print(f'   URL: {resultado["url"]}')
            print(f'   Archivo: {resultado["archivo_svg"]}\n')
            exitosos += 1
        except Exception as e:
            print(f'❌ {i}. Error con {nombre}: {e}\n')
            errores += 1

    # Resumen
    print('=' * 50)
    print('📊 Resumen:')
    print(f'   ✅ Exitosos: {exitosos}')
    print(f'   ❌ Errores: {errores}')
    print(f'   📁 Directorio: {output_dir}/')
    print(f'   💾 Base de datos: {db_path}')
    print(f'   🎓 Total en BD: {db.contar_certificados()}')
    print('=' * 50)
    print('\n💡 Los certificados están guardados y disponibles en:')
    print('   http://localhost:8000/certificado/<nombre-apellido>')
    print('\n📌 Para ver el certificado, inicia el servidor con:')
    print('   python app.py')
    print('=' * 50)


if __name__ == '__main__':
    main()
