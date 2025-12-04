"""
Capa de acceso a datos usando SQLAlchemy
Soporta SQLite (desarrollo) y PostgreSQL (producción)
"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


class Certificado(Base):
    """Modelo de Certificado"""
    __tablename__ = 'certificados'

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    nombre = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    cloudinary_url = Column(String(500), nullable=False)  # URL de Cloudinary
    cloudinary_public_id = Column(String(255), nullable=False)  # Public ID de Cloudinary
    fecha_generacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    visto = Column(Integer, default=0, nullable=False)
    ultima_visita = Column(DateTime, nullable=True)

    # Índices adicionales
    __table_args__ = (
        Index('idx_email', 'email'),
        Index('idx_nombre', 'nombre'),
        Index('idx_fecha_generacion', 'fecha_generacion'),
    )

    def to_dict(self) -> Dict:
        """Convierte el modelo a diccionario"""
        return {
            'id': self.id,
            'slug': self.slug,
            'nombre': self.nombre,
            'email': self.email,
            'cloudinary_url': self.cloudinary_url,
            'cloudinary_public_id': self.cloudinary_public_id,
            'fecha_generacion': self.fecha_generacion.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_generacion else None,
            'visto': self.visto,
            'ultima_visita': self.ultima_visita.strftime('%Y-%m-%d %H:%M:%S') if self.ultima_visita else None
        }


class Database:
    """Clase para manejar operaciones de base de datos"""

    def __init__(self, database_url: str = 'sqlite:///certificados.db'):
        """
        Inicializa la conexión a la base de datos

        Args:
            database_url: URL de conexión a la base de datos
                         - SQLite: sqlite:///certificados.db
                         - PostgreSQL: postgresql://user:pass@host:port/db
        """
        self.database_url = database_url
        self.engine = create_engine(
            database_url,
            echo=False,  # Cambiar a True para debug SQL
            pool_pre_ping=True,  # Verificar conexiones antes de usar
            pool_size=10,  # Tamaño del pool de conexiones
            max_overflow=20  # Conexiones adicionales permitidas
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.init_db()
        logger.info(f"Base de datos inicializada: {database_url.split('@')[-1] if '@' in database_url else database_url}")

    def init_db(self):
        """Crea las tablas si no existen"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Tablas de base de datos creadas/verificadas")
        except Exception as e:
            logger.error(f"Error al crear tablas: {e}")
            raise

    def get_session(self) -> Session:
        """Obtiene una sesión de base de datos"""
        return self.SessionLocal()

    def guardar_certificado(
        self,
        slug: str,
        nombre: str,
        email: str,
        cloudinary_url: str,
        cloudinary_public_id: str
    ) -> bool:
        """
        Guarda un certificado en la base de datos

        Args:
            slug: Slug único del certificado
            nombre: Nombre del participante
            email: Email del participante
            cloudinary_url: URL del certificado en Cloudinary
            cloudinary_public_id: Public ID en Cloudinary

        Returns:
            True si se guardó correctamente, False si ya existe
        """
        session = self.get_session()
        try:
            certificado = Certificado(
                slug=slug,
                nombre=nombre,
                email=email,
                cloudinary_url=cloudinary_url,
                cloudinary_public_id=cloudinary_public_id
            )
            session.add(certificado)
            session.commit()
            logger.info(f"Certificado guardado: {slug}")
            return True
        except IntegrityError:
            session.rollback()
            logger.warning(f"Certificado duplicado: {slug}")
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error al guardar certificado: {e}")
            return False
        finally:
            session.close()

    def obtener_certificado(self, slug: str) -> Optional[Dict]:
        """
        Obtiene un certificado por su slug

        Args:
            slug: Slug del certificado

        Returns:
            Diccionario con datos del certificado o None si no existe
        """
        session = self.get_session()
        try:
            certificado = session.query(Certificado).filter(Certificado.slug == slug).first()
            if certificado:
                return certificado.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error al obtener certificado: {e}")
            return None
        finally:
            session.close()

    def marcar_como_visto(self, slug: str) -> bool:
        """
        Marca un certificado como visto y actualiza la última visita

        Args:
            slug: Slug del certificado

        Returns:
            True si se actualizó correctamente
        """
        session = self.get_session()
        try:
            certificado = session.query(Certificado).filter(Certificado.slug == slug).first()
            if certificado:
                certificado.visto += 1
                certificado.ultima_visita = datetime.utcnow()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error al marcar como visto: {e}")
            return False
        finally:
            session.close()

    def listar_certificados(self, limite: int = 100, offset: int = 0) -> List[Dict]:
        """
        Lista todos los certificados con paginación

        Args:
            limite: Número máximo de resultados
            offset: Desplazamiento para paginación

        Returns:
            Lista de diccionarios con certificados
        """
        session = self.get_session()
        try:
            certificados = (
                session.query(Certificado)
                .order_by(Certificado.fecha_generacion.desc())
                .limit(limite)
                .offset(offset)
                .all()
            )
            return [cert.to_dict() for cert in certificados]
        except Exception as e:
            logger.error(f"Error al listar certificados: {e}")
            return []
        finally:
            session.close()

    def contar_certificados(self) -> int:
        """
        Cuenta el total de certificados

        Returns:
            Número total de certificados
        """
        session = self.get_session()
        try:
            count = session.query(Certificado).count()
            return count
        except Exception as e:
            logger.error(f"Error al contar certificados: {e}")
            return 0
        finally:
            session.close()

    def buscar_por_email(self, email: str) -> List[Dict]:
        """
        Busca certificados por email

        Args:
            email: Email a buscar (búsqueda parcial)

        Returns:
            Lista de certificados que coinciden
        """
        session = self.get_session()
        try:
            certificados = (
                session.query(Certificado)
                .filter(Certificado.email.ilike(f'%{email}%'))
                .order_by(Certificado.fecha_generacion.desc())
                .all()
            )
            return [cert.to_dict() for cert in certificados]
        except Exception as e:
            logger.error(f"Error al buscar por email: {e}")
            return []
        finally:
            session.close()

    def buscar_por_nombre(self, nombre: str) -> List[Dict]:
        """
        Busca certificados por nombre

        Args:
            nombre: Nombre a buscar (búsqueda parcial)

        Returns:
            Lista de certificados que coinciden
        """
        session = self.get_session()
        try:
            certificados = (
                session.query(Certificado)
                .filter(Certificado.nombre.ilike(f'%{nombre}%'))
                .order_by(Certificado.fecha_generacion.desc())
                .all()
            )
            return [cert.to_dict() for cert in certificados]
        except Exception as e:
            logger.error(f"Error al buscar por nombre: {e}")
            return []
        finally:
            session.close()
