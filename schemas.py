"""
Schemas de validación con Pydantic
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional
from datetime import datetime


class ParticipanteSchema(BaseModel):
    """Schema para validar datos de un participante"""
    nombre: str = Field(..., min_length=1, max_length=255, description="Nombre completo del participante")
    email: EmailStr = Field(..., description="Email del participante")

    @validator('nombre')
    def validar_nombre(cls, v):
        """Valida que el nombre no esté vacío y no contenga solo espacios"""
        if not v or v.strip() == '':
            raise ValueError('El nombre no puede estar vacío')
        return v.strip()

    class Config:
        schema_extra = {
            "example": {
                "nombre": "Juan Pérez",
                "email": "juan.perez@example.com"
            }
        }


class GenerarCertificadosRequest(BaseModel):
    """Schema para el request de generación de certificados"""
    participantes: List[ParticipanteSchema] = Field(..., min_items=1, description="Lista de participantes")

    @validator('participantes')
    def validar_limite_participantes(cls, v):
        """Valida que no se exceda el límite de participantes por batch"""
        if len(v) > 1000:
            raise ValueError('El límite máximo es 1000 participantes por batch')
        return v

    class Config:
        schema_extra = {
            "example": {
                "participantes": [
                    {"nombre": "Juan Pérez", "email": "juan@example.com"},
                    {"nombre": "María García", "email": "maria@example.com"}
                ]
            }
        }


class EnviarEmailsRequest(BaseModel):
    """Schema para el request de envío de emails"""
    slugs: List[str] = Field(..., min_items=1, description="Lista de slugs de certificados")
    asunto: Optional[str] = Field(None, max_length=200, description="Asunto personalizado")

    @validator('slugs')
    def validar_limite_emails(cls, v):
        """Valida que no se exceda el límite de emails por batch"""
        if len(v) > 1000:
            raise ValueError('El límite máximo es 1000 emails por batch')
        return v

    class Config:
        schema_extra = {
            "example": {
                "slugs": ["juan-perez", "maria-garcia"],
                "asunto": "Tu certificado está listo"
            }
        }


class CertificadoResponse(BaseModel):
    """Schema para la respuesta de un certificado"""
    id: int
    slug: str
    nombre: str
    email: str
    cloudinary_url: str
    fecha_generacion: str
    visto: int
    ultima_visita: Optional[str]
    url: str

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "slug": "juan-perez",
                "nombre": "Juan Pérez",
                "email": "juan@example.com",
                "cloudinary_url": "https://res.cloudinary.com/...",
                "fecha_generacion": "2024-01-15 10:30:00",
                "visto": 5,
                "ultima_visita": "2024-01-20 15:45:00",
                "url": "/certificado/juan-perez"
            }
        }


class GenerarResponse(BaseModel):
    """Schema para la respuesta de generación de certificados"""
    total: int
    exitosos: int
    errores: int
    resultados: List[dict]

    class Config:
        schema_extra = {
            "example": {
                "total": 2,
                "exitosos": 2,
                "errores": 0,
                "resultados": [
                    {
                        "nombre": "Juan Pérez",
                        "email": "juan@example.com",
                        "slug": "juan-perez",
                        "url": "/certificado/juan-perez",
                        "success": True
                    }
                ]
            }
        }


class EmailResponse(BaseModel):
    """Schema para la respuesta de envío de emails"""
    total: int
    exitosos: int
    errores: int
    resultados: List[dict]

    class Config:
        schema_extra = {
            "example": {
                "total": 2,
                "exitosos": 2,
                "errores": 0,
                "resultados": [
                    {"email": "juan@example.com", "success": True}
                ]
            }
        }


class ErrorResponse(BaseModel):
    """Schema para respuestas de error"""
    error: str
    details: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "error": "Certificado no encontrado",
                "details": "El slug 'juan-perez' no existe en la base de datos"
            }
        }
