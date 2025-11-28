import sqlite3
from datetime import datetime
import os


class Database:
    def __init__(self, db_path='certificados.db'):
        """Inicializa la conexión a la base de datos"""
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        """Obtiene una conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Para obtener resultados como diccionarios
        return conn

    def init_db(self):
        """Crea las tablas si no existen"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS certificados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug TEXT UNIQUE NOT NULL,
                nombre TEXT NOT NULL,
                email TEXT NOT NULL,
                archivo_svg TEXT NOT NULL,
                fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                visto INTEGER DEFAULT 0,
                ultima_visita TIMESTAMP
            )
        ''')

        # Crear índice para búsquedas rápidas por slug
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_slug
            ON certificados(slug)
        ''')

        conn.commit()
        conn.close()

    def guardar_certificado(self, slug, nombre, email, archivo_svg):
        """Guarda un certificado en la base de datos"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO certificados (slug, nombre, email, archivo_svg)
                VALUES (?, ?, ?, ?)
            ''', (slug, nombre, email, archivo_svg))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # El slug ya existe
            return False
        finally:
            conn.close()

    def obtener_certificado(self, slug):
        """Obtiene un certificado por su slug"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM certificados WHERE slug = ?
        ''', (slug,))

        certificado = cursor.fetchone()
        conn.close()

        if certificado:
            return dict(certificado)
        return None

    def marcar_como_visto(self, slug):
        """Marca un certificado como visto y actualiza la última visita"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE certificados
            SET visto = visto + 1,
                ultima_visita = CURRENT_TIMESTAMP
            WHERE slug = ?
        ''', (slug,))

        conn.commit()
        conn.close()

    def listar_certificados(self, limite=100, offset=0):
        """Lista todos los certificados"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM certificados
            ORDER BY fecha_generacion DESC
            LIMIT ? OFFSET ?
        ''', (limite, offset))

        certificados = cursor.fetchall()
        conn.close()

        return [dict(cert) for cert in certificados]

    def contar_certificados(self):
        """Cuenta el total de certificados"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) as total FROM certificados')
        resultado = cursor.fetchone()
        conn.close()

        return resultado['total']

    def buscar_por_email(self, email):
        """Busca certificados por email"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM certificados
            WHERE email LIKE ?
            ORDER BY fecha_generacion DESC
        ''', (f'%{email}%',))

        certificados = cursor.fetchall()
        conn.close()

        return [dict(cert) for cert in certificados]

    def buscar_por_nombre(self, nombre):
        """Busca certificados por nombre"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM certificados
            WHERE nombre LIKE ?
            ORDER BY fecha_generacion DESC
        ''', (f'%{nombre}%',))

        certificados = cursor.fetchall()
        conn.close()

        return [dict(cert) for cert in certificados]
