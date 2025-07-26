"""
Modelos base para Buko AI
"""

from datetime import datetime, timezone
from typing import Any, Dict

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, DateTime, Integer, String, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

db = SQLAlchemy()


class BaseModel(db.Model):
    """Modelo base con campos comunes"""
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            # Manejar tipos especiales para serialización JSON
            if value is None:
                result[column.name] = None
            elif hasattr(value, 'value'):  # Enum
                result[column.name] = value.value
            elif isinstance(value, datetime):
                result[column.name] = value.isoformat()
            elif isinstance(value, uuid.UUID):
                result[column.name] = str(value)
            else:
                result[column.name] = value
        return result
    
    def update(self, **kwargs) -> None:
        """Actualiza el modelo con los valores dados"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now(timezone.utc)
    
    def save(self) -> None:
        """Guarda el modelo en la base de datos"""
        db.session.add(self)
        db.session.commit()
    
    def delete(self) -> None:
        """Elimina el modelo de la base de datos"""
        db.session.delete(self)
        db.session.commit()
    
    @classmethod
    def find_by_id(cls, id: int):
        """Busca un modelo por ID"""
        return cls.query.get(id)
    
    @classmethod
    def find_by_uuid(cls, uuid: str):
        """Busca un modelo por UUID"""
        return cls.query.filter_by(uuid=uuid).first()
    
    @classmethod
    def find_all(cls):
        """Retorna todos los modelos"""
        return cls.query.all()
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.id}>"


class SoftDeleteMixin:
    """Mixin para eliminación suave"""
    
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    def soft_delete(self) -> None:
        """Marca el modelo como eliminado"""
        self.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
    
    def restore(self) -> None:
        """Restaura el modelo eliminado"""
        self.deleted_at = None
        db.session.commit()
    
    @property
    def is_deleted(self) -> bool:
        """Verifica si el modelo está eliminado"""
        return self.deleted_at is not None
    
    @classmethod
    def query_active(cls):
        """Query que excluye elementos eliminados"""
        return cls.query.filter(cls.deleted_at.is_(None))


class TimestampMixin:
    """Mixin para campos de timestamp"""
    
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)


class AuditMixin:
    """Mixin para auditoría"""
    
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    
    def set_created_by(self, user_id: int) -> None:
        """Establece el usuario que creó el registro"""
        self.created_by = user_id
    
    def set_updated_by(self, user_id: int) -> None:
        """Establece el usuario que actualizó el registro"""
        self.updated_by = user_id