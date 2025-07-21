"""
Modelos de Suscripción y Pagos para Buko AI
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Enum as SQLEnum, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from .base import BaseModel, db
from .user import SubscriptionType


class PaymentStatus(enum.Enum):
    """Estados de pago"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentMethod(enum.Enum):
    """Métodos de pago"""
    PAYPAL = "paypal"
    MERCADOPAGO = "mercadopago"
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"


class Subscription(BaseModel):
    """Modelo de Suscripción"""
    
    __tablename__ = "subscriptions"
    
    # Relación con usuario
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="subscriptions")
    
    # Información de la suscripción
    plan_type = Column(SQLEnum(SubscriptionType), nullable=False)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    
    # Período de suscripción
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    
    # Cancelación
    cancel_at_period_end = Column(Boolean, default=False, nullable=False)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Trial
    trial_start = Column(DateTime(timezone=True), nullable=True)
    trial_end = Column(DateTime(timezone=True), nullable=True)
    
    # IDs de proveedores de pago
    paypal_subscription_id = Column(String(255), nullable=True)
    mp_subscription_id = Column(String(255), nullable=True)
    
    # Relaciones
    payments = relationship("Payment", back_populates="subscription", cascade="all, delete-orphan")
    
    @property
    def is_active(self) -> bool:
        """Verifica si la suscripción está activa"""
        return (
            self.status == PaymentStatus.COMPLETED and
            self.current_period_end is not None and
            self.current_period_end > datetime.utcnow() and
            not self.is_cancelled
        )
    
    @property
    def is_cancelled(self) -> bool:
        """Verifica si la suscripción está cancelada"""
        return self.cancelled_at is not None
    
    @property
    def is_trial(self) -> bool:
        """Verifica si está en período de prueba"""
        now = datetime.utcnow()
        return (
            self.trial_start is not None and
            self.trial_end is not None and
            self.trial_start <= now <= self.trial_end
        )
    
    @property
    def days_until_renewal(self) -> Optional[int]:
        """Días hasta la renovación"""
        if self.current_period_end:
            delta = self.current_period_end - datetime.utcnow()
            return max(0, delta.days)
        return None
    
    @property
    def plan_details(self) -> Dict[str, Any]:
        """Retorna los detalles del plan"""
        from flask import current_app
        
        plans = current_app.config.get("SUBSCRIPTION_PLANS", {})
        return plans.get(self.plan_type.value, {})
    
    def start_subscription(self, period_months: int = 1) -> None:
        """Inicia la suscripción"""
        now = datetime.utcnow()
        self.current_period_start = now
        self.current_period_end = now + timedelta(days=30 * period_months)
        self.status = PaymentStatus.COMPLETED
        db.session.commit()
    
    def renew_subscription(self, period_months: int = 1) -> None:
        """Renueva la suscripción"""
        if self.current_period_end:
            self.current_period_start = self.current_period_end
            self.current_period_end = self.current_period_end + timedelta(days=30 * period_months)
        else:
            self.start_subscription(period_months)
        
        self.status = PaymentStatus.COMPLETED
        db.session.commit()
    
    def cancel_subscription(self, at_period_end: bool = True) -> None:
        """Cancela la suscripción"""
        if at_period_end:
            self.cancel_at_period_end = True
        else:
            self.cancelled_at = datetime.utcnow()
            self.status = PaymentStatus.CANCELLED
        
        db.session.commit()
    
    def reactivate_subscription(self) -> None:
        """Reactiva la suscripción"""
        self.cancel_at_period_end = False
        self.cancelled_at = None
        self.status = PaymentStatus.COMPLETED
        db.session.commit()
    
    def start_trial(self, trial_days: int = 7) -> None:
        """Inicia período de prueba"""
        now = datetime.utcnow()
        self.trial_start = now
        self.trial_end = now + timedelta(days=trial_days)
        self.status = PaymentStatus.COMPLETED
        db.session.commit()
    
    def upgrade_plan(self, new_plan: SubscriptionType) -> None:
        """Actualiza el plan de suscripción"""
        self.plan_type = new_plan
        db.session.commit()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario"""
        base_dict = super().to_dict()
        base_dict.update({
            "plan_type": self.plan_type.value,
            "status": self.status.value,
            "is_active": self.is_active,
            "is_cancelled": self.is_cancelled,
            "is_trial": self.is_trial,
            "days_until_renewal": self.days_until_renewal,
            "plan_details": self.plan_details,
        })
        return base_dict
    
    @classmethod
    def get_active_subscriptions(cls) -> List['Subscription']:
        """Retorna suscripciones activas"""
        return cls.query.filter(
            cls.status == PaymentStatus.COMPLETED,
            cls.current_period_end > datetime.utcnow()
        ).all()
    
    @classmethod
    def get_expiring_subscriptions(cls, days: int = 7) -> List['Subscription']:
        """Retorna suscripciones que expiran pronto"""
        expiry_date = datetime.utcnow() + timedelta(days=days)
        return cls.query.filter(
            cls.status == PaymentStatus.COMPLETED,
            cls.current_period_end <= expiry_date,
            cls.current_period_end > datetime.utcnow()
        ).all()
    
    def __repr__(self) -> str:
        return f"<Subscription {self.plan_type.value} for {self.user.email if self.user else 'Unknown'}>"


class Payment(BaseModel):
    """Modelo de Pago"""
    
    __tablename__ = "payments"
    
    # Relaciones
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="payments")
    
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
    subscription = relationship("Subscription", back_populates="payments")
    
    # Información del pago
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    
    # Método de pago
    payment_method = Column(SQLEnum(PaymentMethod), nullable=True)
    payment_provider = Column(String(50), nullable=True)
    
    # IDs de proveedores
    provider_payment_id = Column(String(255), nullable=True)
    provider_transaction_id = Column(String(255), nullable=True)
    invoice_id = Column(String(255), nullable=True)
    
    # Descripción y metadatos
    description = Column(Text, nullable=True)
    payment_metadata = Column(JSON, nullable=True)
    
    # Timestamp de procesamiento
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    @property
    def is_completed(self) -> bool:
        """Verifica si el pago está completado"""
        return self.status == PaymentStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Verifica si el pago falló"""
        return self.status == PaymentStatus.FAILED
    
    @property
    def is_refunded(self) -> bool:
        """Verifica si el pago fue reembolsado"""
        return self.status == PaymentStatus.REFUNDED
    
    @property
    def formatted_amount(self) -> str:
        """Retorna el monto formateado"""
        return f"{self.amount:.2f} {self.currency}"
    
    def mark_completed(self, provider_transaction_id: str = None) -> None:
        """Marca el pago como completado"""
        self.status = PaymentStatus.COMPLETED
        self.processed_at = datetime.utcnow()
        if provider_transaction_id:
            self.provider_transaction_id = provider_transaction_id
        db.session.commit()
    
    def mark_failed(self, error_message: str = None) -> None:
        """Marca el pago como fallido"""
        self.status = PaymentStatus.FAILED
        self.processed_at = datetime.utcnow()
        if error_message and self.payment_metadata:
            self.payment_metadata["error_message"] = error_message
        db.session.commit()
    
    def mark_refunded(self, refund_amount: float = None) -> None:
        """Marca el pago como reembolsado"""
        self.status = PaymentStatus.REFUNDED
        if refund_amount and self.payment_metadata:
            self.payment_metadata["refund_amount"] = refund_amount
        db.session.commit()
    
    def update_provider_info(self, provider_payment_id: str, provider_transaction_id: str = None) -> None:
        """Actualiza información del proveedor"""
        self.provider_payment_id = provider_payment_id
        if provider_transaction_id:
            self.provider_transaction_id = provider_transaction_id
        db.session.commit()
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Agrega metadatos al pago"""
        if not self.payment_metadata:
            self.payment_metadata = {}
        self.payment_metadata[key] = value
        db.session.commit()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario"""
        base_dict = super().to_dict()
        base_dict.update({
            "amount": float(self.amount),
            "currency": self.currency,
            "status": self.status.value,
            "payment_method": self.payment_method.value if self.payment_method else None,
            "formatted_amount": self.formatted_amount,
            "is_completed": self.is_completed,
            "is_failed": self.is_failed,
            "is_refunded": self.is_refunded,
        })
        return base_dict
    
    @classmethod
    def get_by_user(cls, user_id: int) -> List['Payment']:
        """Retorna pagos de un usuario"""
        return cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_completed_payments(cls) -> List['Payment']:
        """Retorna pagos completados"""
        return cls.query.filter_by(status=PaymentStatus.COMPLETED).all()
    
    @classmethod
    def get_failed_payments(cls) -> List['Payment']:
        """Retorna pagos fallidos"""
        return cls.query.filter_by(status=PaymentStatus.FAILED).all()
    
    @classmethod
    def get_total_revenue(cls) -> float:
        """Retorna el total de ingresos"""
        result = db.session.query(func.sum(cls.amount)).filter(
            cls.status == PaymentStatus.COMPLETED
        ).scalar()
        return float(result) if result else 0.0
    
    @classmethod
    def get_monthly_revenue(cls, year: int, month: int) -> float:
        """Retorna ingresos mensuales"""
        result = db.session.query(func.sum(cls.amount)).filter(
            cls.status == PaymentStatus.COMPLETED,
            func.extract('year', cls.created_at) == year,
            func.extract('month', cls.created_at) == month
        ).scalar()
        return float(result) if result else 0.0
    
    def __repr__(self) -> str:
        return f"<Payment {self.formatted_amount} for {self.user.email if self.user else 'Unknown'}>"