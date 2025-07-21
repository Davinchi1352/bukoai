"""
Tareas de Celery para procesamiento de pagos.
"""
import logging
from datetime import datetime, timedelta
from app import celery, db
from app.models.payment import Payment, PaymentStatus
from app.models.subscription import Subscription
from app.models.user import User
from app.services.paypal_service import PayPalService
from app.services.mercadopago_service import MercadoPagoService
from app.utils.logging import log_system_event

logger = logging.getLogger(__name__)


@celery.task(bind=True, max_retries=3, default_retry_delay=300)
def process_payment_task(self, payment_id):
    """
    Procesa un pago pendiente.
    """
    try:
        payment = Payment.query.get(payment_id)
        if not payment:
            logger.error(f"Pago {payment_id} no encontrado")
            return {'status': 'error', 'message': 'Pago no encontrado'}
        
        if payment.status != PaymentStatus.PENDING:
            logger.info(f"Pago {payment_id} ya fue procesado: {payment.status}")
            return {'status': 'already_processed', 'payment_status': payment.status.value}
        
        user = User.query.get(payment.user_id)
        if not user:
            raise Exception("Usuario no encontrado")
        
        # Log del inicio del procesamiento
        log_system_event(
            user_id=user.id,
            action="payment_processing_started",
            details={"payment_id": payment_id, "amount": float(payment.amount)}
        )
        
        # Procesar según el método de pago
        if payment.payment_method.value == 'PAYPAL':
            result = process_paypal_payment(payment)
        elif payment.payment_method.value == 'MERCADOPAGO':
            result = process_mercadopago_payment(payment)
        else:
            raise Exception(f"Método de pago no soportado: {payment.payment_method}")
        
        if result['status'] == 'completed':
            payment.status = PaymentStatus.COMPLETED
            payment.processed_at = datetime.utcnow()
            payment.provider_transaction_id = result.get('transaction_id')
            
            # Actualizar suscripción si corresponde
            if payment.subscription_id:
                update_subscription_after_payment(payment.subscription_id)
            
            # Log del éxito
            log_system_event(
                user_id=user.id,
                action="payment_completed",
                details={
                    "payment_id": payment_id,
                    "amount": float(payment.amount),
                    "transaction_id": result.get('transaction_id')
                }
            )
            
            # Enviar email de confirmación
            from app.tasks.email_tasks import send_template_email
            send_template_email.delay(
                template_name='payment_confirmed',
                recipient_email=user.email,
                context={
                    'user_name': f"{user.first_name} {user.last_name}",
                    'amount': float(payment.amount),
                    'currency': payment.currency,
                    'payment_id': payment_id
                }
            )
            
        elif result['status'] == 'failed':
            payment.status = PaymentStatus.FAILED
            payment.error_message = result.get('error', 'Error desconocido')
            
            # Log del error
            log_system_event(
                user_id=user.id,
                action="payment_failed",
                details={
                    "payment_id": payment_id,
                    "error": result.get('error')
                },
                level="ERROR"
            )
        
        db.session.commit()
        
        logger.info(f"Pago {payment_id} procesado: {payment.status}")
        return {'status': payment.status.value, 'payment_id': payment_id}
        
    except Exception as exc:
        logger.error(f"Error procesando pago {payment_id}: {str(exc)}")
        
        # Actualizar pago con error
        payment = Payment.query.get(payment_id)
        if payment:
            payment.status = PaymentStatus.FAILED
            payment.error_message = str(exc)
            db.session.commit()
        
        if self.request.retries < self.max_retries:
            logger.info(f"Reintentando procesamiento de pago {payment_id} en 5 minutos")
            raise self.retry(countdown=300, exc=exc)
        
        return {'status': 'failed', 'error': str(exc)}


def process_paypal_payment(payment):
    """
    Procesa un pago con PayPal.
    """
    try:
        paypal_service = PayPalService()
        
        # Verificar el estado del pago en PayPal
        paypal_payment = paypal_service.get_payment(payment.provider_payment_id)
        
        if paypal_payment['state'] == 'approved':
            # Ejecutar el pago
            execution_result = paypal_service.execute_payment(
                payment.provider_payment_id,
                paypal_payment['payer']['payer_info']['payer_id']
            )
            
            if execution_result['state'] == 'approved':
                return {
                    'status': 'completed',
                    'transaction_id': execution_result['id']
                }
        
        return {'status': 'failed', 'error': 'Pago no aprobado en PayPal'}
        
    except Exception as exc:
        logger.error(f"Error procesando pago PayPal: {str(exc)}")
        return {'status': 'failed', 'error': str(exc)}


def process_mercadopago_payment(payment):
    """
    Procesa un pago con MercadoPago.
    """
    try:
        mp_service = MercadoPagoService()
        
        # Verificar el estado del pago en MercadoPago
        mp_payment = mp_service.get_payment(payment.provider_payment_id)
        
        if mp_payment['status'] == 'approved':
            return {
                'status': 'completed',
                'transaction_id': mp_payment['id']
            }
        elif mp_payment['status'] == 'rejected':
            return {'status': 'failed', 'error': 'Pago rechazado por MercadoPago'}
        
        # Si está pendiente, mantener como pendiente
        return {'status': 'pending', 'message': 'Pago aún pendiente en MercadoPago'}
        
    except Exception as exc:
        logger.error(f"Error procesando pago MercadoPago: {str(exc)}")
        return {'status': 'failed', 'error': str(exc)}


def update_subscription_after_payment(subscription_id):
    """
    Actualiza una suscripción después de un pago exitoso.
    """
    try:
        subscription = Subscription.query.get(subscription_id)
        if not subscription:
            return
        
        user = User.query.get(subscription.user_id)
        if not user:
            return
        
        # Actualizar la suscripción del usuario
        user.subscription_type = subscription.plan_type
        user.subscription_start = subscription.current_period_start
        user.subscription_end = subscription.current_period_end
        
        # Resetear contador de libros si es inicio de período
        now = datetime.utcnow()
        if user.last_reset_date.date() != now.date():
            user.books_used_this_month = 0
            user.last_reset_date = now
        
        db.session.commit()
        
        logger.info(f"Suscripción {subscription_id} actualizada para usuario {user.id}")
        
    except Exception as exc:
        logger.error(f"Error actualizando suscripción {subscription_id}: {str(exc)}")


@celery.task
def check_pending_payments():
    """
    Revisa pagos pendientes y los procesa.
    """
    try:
        # Buscar pagos pendientes de más de 5 minutos
        cutoff_time = datetime.utcnow() - timedelta(minutes=5)
        pending_payments = Payment.query.filter(
            Payment.status == PaymentStatus.PENDING,
            Payment.created_at <= cutoff_time
        ).all()
        
        results = []
        for payment in pending_payments:
            result = process_payment_task.delay(payment.id)
            results.append({
                'payment_id': payment.id,
                'task_id': result.id
            })
        
        logger.info(f"Procesando {len(pending_payments)} pagos pendientes")
        return {'status': 'processing', 'count': len(pending_payments), 'results': results}
        
    except Exception as exc:
        logger.error(f"Error revisando pagos pendientes: {str(exc)}")
        return {'status': 'failed', 'error': str(exc)}


@celery.task
def check_expired_subscriptions():
    """
    Revisa y actualiza suscripciones expiradas.
    """
    try:
        now = datetime.utcnow()
        
        # Buscar usuarios con suscripciones expiradas
        expired_users = User.query.filter(
            User.subscription_end <= now,
            User.subscription_type != 'FREE'
        ).all()
        
        for user in expired_users:
            # Cambiar a plan gratuito
            user.subscription_type = 'FREE'
            user.subscription_start = None
            user.subscription_end = None
            
            # Log del evento
            log_system_event(
                user_id=user.id,
                action="subscription_expired",
                details={"previous_plan": user.subscription_type.value}
            )
            
            # Enviar email de notificación
            from app.tasks.email_tasks import send_template_email
            send_template_email.delay(
                template_name='subscription_expired',
                recipient_email=user.email,
                context={
                    'user_name': f"{user.first_name} {user.last_name}"
                }
            )
        
        db.session.commit()
        
        logger.info(f"Procesadas {len(expired_users)} suscripciones expiradas")
        return {'status': 'completed', 'expired_count': len(expired_users)}
        
    except Exception as exc:
        logger.error(f"Error procesando suscripciones expiradas: {str(exc)}")
        return {'status': 'failed', 'error': str(exc)}


@celery.task
def generate_payment_report():
    """
    Genera reporte de pagos para el día anterior.
    """
    try:
        from sqlalchemy import func
        
        yesterday = datetime.utcnow().date() - timedelta(days=1)
        start_date = datetime.combine(yesterday, datetime.min.time())
        end_date = datetime.combine(yesterday, datetime.max.time())
        
        # Estadísticas del día
        daily_stats = db.session.query(
            Payment.status,
            func.count(Payment.id).label('count'),
            func.sum(Payment.amount).label('total_amount')
        ).filter(
            Payment.created_at.between(start_date, end_date)
        ).group_by(Payment.status).all()
        
        report = {
            'date': yesterday.isoformat(),
            'stats': []
        }
        
        for stat in daily_stats:
            report['stats'].append({
                'status': stat.status.value,
                'count': stat.count,
                'total_amount': float(stat.total_amount or 0)
            })
        
        logger.info(f"Reporte de pagos generado para {yesterday}")
        return report
        
    except Exception as exc:
        logger.error(f"Error generando reporte de pagos: {str(exc)}")
        return {'status': 'failed', 'error': str(exc)}