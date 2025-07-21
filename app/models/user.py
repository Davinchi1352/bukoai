"""
Modelo de Usuario para Buko AI
"""

from datetime import datetime, timedelta, timezone
from typing import List, Optional
import bcrypt
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from .base import BaseModel, SoftDeleteMixin, db


class UserStatus(enum.Enum):
    """Estados del usuario"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class SubscriptionType(enum.Enum):
    """Tipos de suscripción"""
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


class User(BaseModel, SoftDeleteMixin, UserMixin):
    """Modelo de Usuario"""
    
    __tablename__ = "users"
    
    # Información básica
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    
    # Información de contacto
    phone_country = Column(String(5), nullable=True)
    phone_number = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    billing_address = Column(Text, nullable=True)
    
    # Suscripción
    subscription_type = Column(SQLEnum(SubscriptionType), default=SubscriptionType.FREE, nullable=False)
    subscription_start = Column(DateTime(timezone=True), nullable=True)
    subscription_end = Column(DateTime(timezone=True), nullable=True)
    
    # Uso mensual
    books_used_this_month = Column(Integer, default=0, nullable=False)
    last_reset_date = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    # Autenticación
    last_login = Column(DateTime(timezone=True), nullable=True)
    email_verified = Column(Boolean, default=False, nullable=False)
    email_verification_token = Column(String(255), nullable=True)
    email_verification_expires = Column(DateTime(timezone=True), nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Preferencias
    preferred_language = Column(String(5), default="es", nullable=False)
    timezone = Column(String(50), default="UTC", nullable=False)
    
    # Estado
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    
    # Relaciones
    books = relationship("BookGeneration", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    downloads = relationship("BookDownload", back_populates="user", cascade="all, delete-orphan")
    referrals_made = relationship("Referral", foreign_keys="Referral.referrer_id", back_populates="referrer")
    referrals_received = relationship("Referral", foreign_keys="Referral.referred_id", back_populates="referred")
    
    def __init__(self, **kwargs):
        """Inicializa un nuevo usuario"""
        password = kwargs.pop('password', None)  # Extraer password antes del super
        super().__init__(**kwargs)
        if password:
            self.set_password(password)
    
    def set_password(self, password: str) -> None:
        """Establece la contraseña hasheada con bcrypt"""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        self.password_hash = hashed.decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """Verifica la contraseña con bcrypt"""
        password_bytes = password.encode('utf-8')
        hash_bytes = self.password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    
    @property
    def full_name(self) -> str:
        """Retorna el nombre completo"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_active(self) -> bool:
        """Verifica si el usuario está activo"""
        return self.status == UserStatus.ACTIVE and not self.is_deleted
    
    @property
    def is_email_verified(self) -> bool:
        """Verifica si el email está verificado"""
        return self.email_verified
    
    @property
    def has_active_subscription(self) -> bool:
        """Verifica si el usuario tiene una suscripción activa"""
        if self.subscription_type == SubscriptionType.FREE:
            return True
        return (
            self.subscription_end is not None and
            self.subscription_end > datetime.now(timezone.utc)
        )
    
    @property
    def subscription_plan(self) -> dict:
        """Retorna los detalles del plan de suscripción"""
        plans = {
            'free': {'name': 'Free', 'books_per_month': 1, 'max_pages': 30},
            'starter': {'name': 'Starter', 'books_per_month': 5, 'max_pages': 50},
            'pro': {'name': 'Pro', 'books_per_month': 20, 'max_pages': 100},
            'business': {'name': 'Business', 'books_per_month': 50, 'max_pages': 200},
            'enterprise': {'name': 'Enterprise', 'books_per_month': 999, 'max_pages': 500}
        }
        return plans.get(self.subscription_type.value, plans['free'])
    
    @property
    def books_limit(self) -> int:
        """Retorna el límite de libros por mes"""
        plan = self.subscription_plan
        return plan.get("books_per_month", 1)
    
    @property
    def pages_limit(self) -> int:
        """Retorna el límite de páginas por libro"""
        plan = self.subscription_plan
        return plan.get("max_pages", 30)
    
    @property
    def can_generate_book(self) -> bool:
        """Verifica si el usuario puede generar un libro"""
        return (
            self.is_active and
            self.has_active_subscription and
            self.books_used_this_month < self.books_limit
        )
    
    def get_book_generation_limit(self) -> int:
        """Retorna el límite de generación de libros"""
        return self.books_limit
    
    @property
    def books_generated_this_month(self) -> int:
        """Retorna los libros generados este mes"""
        return self.books_used_this_month
    
    def increment_books_generated(self) -> None:
        """Incrementa el contador de libros generados"""
        self.increment_book_usage()
    
    @property
    def remaining_books(self) -> int:
        """Retorna los libros restantes para el mes"""
        return max(0, self.books_limit - self.books_used_this_month)
    
    def reset_monthly_usage(self) -> None:
        """Reinicia el uso mensual"""
        self.books_used_this_month = 0
        self.last_reset_date = datetime.now(timezone.utc)
        db.session.commit()
    
    def increment_book_usage(self) -> None:
        """Incrementa el contador de libros usados"""
        self.books_used_this_month += 1
        db.session.commit()
    
    def update_last_login(self) -> None:
        """Actualiza el último login"""
        self.last_login = datetime.now(timezone.utc)
        db.session.commit()
    
    def verify_email(self) -> None:
        """Marca el email como verificado"""
        self.email_verified = True
        self.email_verification_token = None
        self.email_verification_expires = None
        db.session.commit()
    
    def generate_email_verification_token(self) -> str:
        """Genera un token de verificación de email"""
        import secrets
        token = secrets.token_urlsafe(32)
        self.email_verification_token = token
        self.email_verification_expires = datetime.now(timezone.utc) + timedelta(hours=24)
        db.session.commit()
        return token
    
    def generate_password_reset_token(self) -> str:
        """Genera un token para restablecer contraseña"""
        import secrets
        token = secrets.token_urlsafe(32)
        self.password_reset_token = token
        self.password_reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        db.session.commit()
        return token
    
    def is_password_reset_token_valid(self, token: str) -> bool:
        """Verifica si el token de restablecimiento es válido"""
        return (
            self.password_reset_token == token and
            self.password_reset_expires is not None and
            self.password_reset_expires > datetime.now(timezone.utc)
        )
    
    def clear_password_reset_token(self) -> None:
        """Limpia el token de restablecimiento"""
        self.password_reset_token = None
        self.password_reset_expires = None
        db.session.commit()
    
    def upgrade_subscription(self, new_type: SubscriptionType, end_date: datetime) -> None:
        """Actualiza la suscripción del usuario"""
        self.subscription_type = new_type
        self.subscription_end = end_date
        if not self.subscription_start:
            self.subscription_start = datetime.now(timezone.utc)
        db.session.commit()
    
    def cancel_subscription(self) -> None:
        """Cancela la suscripción del usuario"""
        self.subscription_type = SubscriptionType.FREE
        self.subscription_end = None
        db.session.commit()
    
    def get_active_subscription(self):
        """Retorna un objeto de suscripción activa simulado"""
        # Crear un objeto simulado para compatibilidad con el template
        class MockSubscription:
            def __init__(self, user):
                self.user = user
                self.plan = self.get_plan()
                self.books_generated_this_month = user.books_generated_this_month
                
            def get_plan(self):
                plans = {
                    'free': {'name': 'Free', 'books_per_month': 1},
                    'starter': {'name': 'Starter', 'books_per_month': 5},
                    'pro': {'name': 'Pro', 'books_per_month': 20},
                    'business': {'name': 'Business', 'books_per_month': 50},
                    'enterprise': {'name': 'Enterprise', 'books_per_month': 999}
                }
                return plans.get(self.user.subscription_type.value, plans['free'])
                
            def can_generate_book(self):
                return self.user.can_generate_book
        
        return MockSubscription(self)
    
    def get_statistics(self) -> dict:
        """Retorna estadísticas del usuario"""
        total_books = len(self.books)
        completed_books = len([b for b in self.books if b.status == "completed"])
        total_pages = sum(b.final_pages or 0 for b in self.books if b.final_pages)
        total_words = sum(b.final_words or 0 for b in self.books if b.final_words)
        
        return {
            "total_books": total_books,
            "completed_books": completed_books,
            "failed_books": total_books - completed_books,
            "total_pages": total_pages,
            "total_words": total_words,
            "books_this_month": self.books_used_this_month,
            "remaining_books": self.remaining_books,
            "subscription_type": self.subscription_type.value,
            "member_since": self.created_at.isoformat(),
        }
    
    @classmethod
    def find_by_email(cls, email: str) -> Optional['User']:
        """Busca un usuario por email"""
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def find_by_verification_token(cls, token: str) -> Optional['User']:
        """Busca un usuario por token de verificación"""
        return cls.query.filter_by(email_verification_token=token).first()
    
    @classmethod
    def find_by_password_reset_token(cls, token: str) -> Optional['User']:
        """Busca un usuario por token de restablecimiento"""
        return cls.query.filter_by(password_reset_token=token).first()
    
    @classmethod
    def get_active_users(cls) -> List['User']:
        """Retorna usuarios activos"""
        return cls.query.filter_by(status=UserStatus.ACTIVE).all()
    
    @classmethod
    def get_by_subscription_type(cls, subscription_type: SubscriptionType) -> List['User']:
        """Retorna usuarios por tipo de suscripción"""
        return cls.query.filter_by(subscription_type=subscription_type).all()
    
    def __repr__(self) -> str:
        return f"<User {self.email}>"