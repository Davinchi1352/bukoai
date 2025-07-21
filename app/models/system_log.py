"""
Modelos de Sistema para Buko AI
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Enum as SQLEnum, DECIMAL, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import INET
import enum

from .base import BaseModel, db


class LogLevel(enum.Enum):
    """Niveles de log"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogStatus(enum.Enum):
    """Estados de log"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


class BookFormat(enum.Enum):
    """Formatos de libro"""
    PDF = "pdf"
    EPUB = "epub"
    DOCX = "docx"
    TXT = "txt"


class SystemLog(BaseModel):
    """Modelo de logs del sistema"""
    
    __tablename__ = "system_logs"
    
    # Relación con usuario (opcional)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User")
    
    # Información del log
    action = Column(String(200), nullable=False)
    details = Column(JSON, nullable=True)
    level = Column(SQLEnum(LogLevel), default=LogLevel.INFO, nullable=False)
    status = Column(SQLEnum(LogStatus), default=LogStatus.SUCCESS, nullable=False)
    
    # Información de la sesión
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    session_id = Column(String(255), nullable=True)
    
    # Información del error
    error_message = Column(Text, nullable=True)
    error_traceback = Column(Text, nullable=True)
    
    # Métricas de rendimiento
    execution_time = Column(Integer, nullable=True)  # En milisegundos
    
    @property
    def is_error(self) -> bool:
        """Verifica si es un error"""
        return self.level in [LogLevel.ERROR, LogLevel.CRITICAL]
    
    @property
    def formatted_execution_time(self) -> Optional[str]:
        """Retorna el tiempo de ejecución formateado"""
        if self.execution_time:
            if self.execution_time < 1000:
                return f"{self.execution_time}ms"
            else:
                return f"{self.execution_time / 1000:.2f}s"
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario"""
        base_dict = super().to_dict()
        base_dict.update({
            "level": self.level.value,
            "status": self.status.value,
            "is_error": self.is_error,
            "formatted_execution_time": self.formatted_execution_time,
            "user_email": self.user.email if self.user else None,
        })
        return base_dict
    
    @classmethod
    def log_action(cls, action: str, user_id: int = None, details: Dict[str, Any] = None, 
                   level: LogLevel = LogLevel.INFO, status: LogStatus = LogStatus.SUCCESS,
                   ip_address: str = None, user_agent: str = None, session_id: str = None,
                   error_message: str = None, execution_time: int = None) -> 'SystemLog':
        """Crea un nuevo log"""
        log = cls(
            action=action,
            user_id=user_id,
            details=details,
            level=level,
            status=status,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            error_message=error_message,
            execution_time=execution_time
        )
        log.save()
        return log
    
    @classmethod
    def get_recent_logs(cls, limit: int = 100) -> List['SystemLog']:
        """Retorna logs recientes"""
        return cls.query.order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_error_logs(cls, limit: int = 100) -> List['SystemLog']:
        """Retorna logs de error"""
        return cls.query.filter(
            cls.level.in_([LogLevel.ERROR, LogLevel.CRITICAL])
        ).order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_user_logs(cls, user_id: int, limit: int = 100) -> List['SystemLog']:
        """Retorna logs de un usuario"""
        return cls.query.filter_by(user_id=user_id).order_by(
            cls.created_at.desc()
        ).limit(limit).all()
    
    @classmethod
    def get_logs_by_action(cls, action: str, limit: int = 100) -> List['SystemLog']:
        """Retorna logs por acción"""
        return cls.query.filter_by(action=action).order_by(
            cls.created_at.desc()
        ).limit(limit).all()
    
    def __repr__(self) -> str:
        return f"<SystemLog {self.action} - {self.level.value}>"


class BookDownload(BaseModel):
    """Modelo de descargas de libros"""
    
    __tablename__ = "book_downloads"
    
    # Relaciones
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="downloads")
    
    book_id = Column(Integer, ForeignKey("book_generations.id"), nullable=False)
    book = relationship("BookGeneration", back_populates="downloads")
    
    # Información de la descarga
    format = Column(SQLEnum(BookFormat), nullable=False)
    file_path = Column(String(500), nullable=True)
    file_size = Column(BigInteger, nullable=True)
    download_count = Column(Integer, default=0, nullable=False)
    
    # Información de la sesión
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Última descarga
    last_downloaded_at = Column(DateTime(timezone=True), nullable=True)
    
    @property
    def formatted_file_size(self) -> Optional[str]:
        """Retorna el tamaño del archivo formateado"""
        if self.file_size:
            size = self.file_size
            units = ['B', 'KB', 'MB', 'GB', 'TB']
            unit_index = 0
            
            while size >= 1024 and unit_index < len(units) - 1:
                size /= 1024
                unit_index += 1
            
            return f"{size:.2f} {units[unit_index]}"
        return None
    
    def increment_download_count(self) -> None:
        """Incrementa el contador de descargas"""
        self.download_count += 1
        self.last_downloaded_at = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario"""
        base_dict = super().to_dict()
        base_dict.update({
            "format": self.format.value,
            "formatted_file_size": self.formatted_file_size,
            "book_title": self.book.title if self.book else None,
            "user_email": self.user.email if self.user else None,
        })
        return base_dict
    
    @classmethod
    def get_by_user(cls, user_id: int) -> List['BookDownload']:
        """Retorna descargas de un usuario"""
        return cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_by_book(cls, book_id: int) -> List['BookDownload']:
        """Retorna descargas de un libro"""
        return cls.query.filter_by(book_id=book_id).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_popular_formats(cls) -> List[Dict[str, Any]]:
        """Retorna formatos más populares"""
        results = db.session.query(
            cls.format,
            func.count(cls.id).label('count'),
            func.sum(cls.download_count).label('total_downloads')
        ).group_by(cls.format).order_by(func.sum(cls.download_count).desc()).all()
        
        return [
            {
                "format": result.format.value,
                "unique_downloads": result.count,
                "total_downloads": result.total_downloads
            }
            for result in results
        ]
    
    def __repr__(self) -> str:
        return f"<BookDownload {self.format.value} - {self.book.title if self.book else 'Unknown'}>"



class Referral(BaseModel):
    """Modelo de referidos"""
    
    __tablename__ = "referrals"
    
    # Relaciones
    referrer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    referrer = relationship("User", foreign_keys=[referrer_id], back_populates="referrals_made")
    
    referred_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    referred = relationship("User", foreign_keys=[referred_id], back_populates="referrals_received")
    
    # Información del referido
    referral_code = Column(String(20), nullable=True)
    
    # Comisiones
    commission_rate = Column(DECIMAL(5, 4), default=0.1000, nullable=False)
    commission_earned = Column(DECIMAL(10, 2), default=0.00, nullable=False)
    commission_paid = Column(DECIMAL(10, 2), default=0.00, nullable=False)
    
    # Estado
    status = Column(String(20), default="active", nullable=False)
    
    @property
    def commission_pending(self) -> float:
        """Retorna la comisión pendiente"""
        return float(self.commission_earned - self.commission_paid)
    
    def add_commission(self, amount: float) -> None:
        """Agrega comisión"""
        self.commission_earned += amount
        db.session.commit()
    
    def pay_commission(self, amount: float) -> None:
        """Marca comisión como pagada"""
        self.commission_paid += amount
        db.session.commit()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario"""
        base_dict = super().to_dict()
        base_dict.update({
            "commission_rate": float(self.commission_rate),
            "commission_earned": float(self.commission_earned),
            "commission_paid": float(self.commission_paid),
            "commission_pending": self.commission_pending,
            "referrer_email": self.referrer.email if self.referrer else None,
            "referred_email": self.referred.email if self.referred else None,
        })
        return base_dict
    
    @classmethod
    def get_by_referrer(cls, referrer_id: int) -> List['Referral']:
        """Retorna referidos de un usuario"""
        return cls.query.filter_by(referrer_id=referrer_id).all()
    
    @classmethod
    def get_by_referral_code(cls, code: str) -> Optional['Referral']:
        """Busca por código de referido"""
        return cls.query.filter_by(referral_code=code).first()
    
    def __repr__(self) -> str:
        return f"<Referral {self.referrer.email if self.referrer else 'Unknown'} -> {self.referred.email if self.referred else 'Unknown'}>"