"""
Tareas de Celery para envío de emails.
"""
import logging
from celery import shared_task
from flask_mail import Message
from app import mail, db
from app.models.email_template import EmailTemplate
from app.models.user import User
from app.utils.logging import log_system_event

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60, name='app.tasks.email_tasks.send_email_task')
def send_email_task(self, subject, recipient, body, html_body=None):
    """
    Envía un email básico.
    """
    try:
        msg = Message(
            subject=subject,
            recipients=[recipient],
            body=body,
            html=html_body
        )
        mail.send(msg)
        
        logger.info(f"Email enviado exitosamente a {recipient}")
        return {'status': 'sent', 'recipient': recipient}
        
    except Exception as exc:
        logger.error(f"Error enviando email a {recipient}: {str(exc)}")
        
        # El manejo de reintentos será configurado en la registración de la tarea
        raise exc


@shared_task(bind=True, max_retries=3, default_retry_delay=60, name='app.tasks.email_tasks.send_template_email')
def send_template_email(self, template_name, recipient_email, context=None, language='es'):
    """
    Envía un email usando un template predefinido.
    """
    try:
        # Obtener el template
        template = EmailTemplate.query.filter_by(
            name=template_name,
            language=language,
            is_active=True
        ).first()
        
        if not template:
            logger.error(f"Template '{template_name}' no encontrado para idioma '{language}'")
            return {'status': 'failed', 'error': 'Template no encontrado'}
        
        # Preparar contexto
        context = context or {}
        
        # Renderizar contenido
        subject = template.render_subject(context)
        html_content = template.render_html_content(context)
        text_content = template.render_text_content(context)
        
        # Crear y enviar mensaje
        msg = Message(
            subject=subject,
            recipients=[recipient_email],
            body=text_content,
            html=html_content
        )
        mail.send(msg)
        
        # Log del evento
        log_system_event(
            action="email_sent",
            details={
                "template": template_name,
                "recipient": recipient_email,
                "subject": subject
            }
        )
        
        logger.info(f"Email template '{template_name}' enviado a {recipient_email}")
        return {'status': 'sent', 'template': template_name, 'recipient': recipient_email}
        
    except Exception as exc:
        logger.error(f"Error enviando email template '{template_name}' a {recipient_email}: {str(exc)}")
        
        # Log del error
        log_system_event(
            action="email_send_failed",
            details={
                "template": template_name,
                "recipient": recipient_email,
                "error": str(exc)
            },
            level="ERROR"
        )
        
        # El manejo de reintentos será configurado en la registración de la tarea
        raise exc


@shared_task(name='app.tasks.email_tasks.send_welcome_email')
def send_welcome_email(user_id):
    """
    Envía email de bienvenida a un nuevo usuario.
    """
    try:
        user = User.query.get(user_id)
        if not user:
            logger.error(f"Usuario {user_id} no encontrado")
            return {'status': 'failed', 'error': 'Usuario no encontrado'}
        
        context = {
            'user_name': f"{user.first_name} {user.last_name}",
            'email': user.email,
            'subscription_type': user.subscription_type.value,
            'verification_url': f"/auth/verify-email?token={user.email_verification_token}"
        }
        
        return send_template_email(
            template_name='welcome',
            recipient_email=user.email,
            context=context,
            language=user.preferred_language
        )
        
    except Exception as exc:
        logger.error(f"Error enviando email de bienvenida a usuario {user_id}: {str(exc)}")
        return {'status': 'failed', 'error': str(exc)}


@shared_task(name='app.tasks.email_tasks.send_password_reset_email')
def send_password_reset_email(user_id, reset_token):
    """
    Envía email para resetear contraseña.
    """
    try:
        user = User.query.get(user_id)
        if not user:
            logger.error(f"Usuario {user_id} no encontrado")
            return {'status': 'failed', 'error': 'Usuario no encontrado'}
        
        context = {
            'user_name': f"{user.first_name} {user.last_name}",
            'reset_url': f"/auth/reset-password?token={reset_token}",
            'expires_in': '24 horas'
        }
        
        return send_template_email(
            template_name='password_reset',
            recipient_email=user.email,
            context=context,
            language=user.preferred_language
        )
        
    except Exception as exc:
        logger.error(f"Error enviando email de reset a usuario {user_id}: {str(exc)}")
        return {'status': 'failed', 'error': str(exc)}


@shared_task(name='app.tasks.email_tasks.send_subscription_confirmation_email')
def send_subscription_confirmation_email(user_id, subscription_id):
    """
    Envía email de confirmación de suscripción.
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return {'status': 'failed', 'error': 'Usuario no encontrado'}
        
        from app.models.subscription import Subscription
        subscription = Subscription.query.get(subscription_id)
        if not subscription:
            return {'status': 'failed', 'error': 'Suscripción no encontrada'}
        
        context = {
            'user_name': f"{user.first_name} {user.last_name}",
            'plan_type': subscription.plan_type.value,
            'current_period_start': subscription.current_period_start.strftime('%d/%m/%Y'),
            'current_period_end': subscription.current_period_end.strftime('%d/%m/%Y')
        }
        
        return send_template_email(
            template_name='subscription_confirmed',
            recipient_email=user.email,
            context=context,
            language=user.preferred_language
        )
        
    except Exception as exc:
        logger.error(f"Error enviando email de suscripción a usuario {user_id}: {str(exc)}")
        return {'status': 'failed', 'error': str(exc)}


@shared_task(name='app.tasks.email_tasks.send_bulk_email')
def send_bulk_email(template_name, user_ids, context=None):
    """
    Envía emails masivos a una lista de usuarios.
    """
    try:
        users = User.query.filter(User.id.in_(user_ids)).all()
        results = []
        
        for user in users:
            if user.email_verified and user.status.value == 'ACTIVE':
                user_context = context.copy() if context else {}
                user_context.update({
                    'user_name': f"{user.first_name} {user.last_name}",
                    'email': user.email
                })
                
                result = send_template_email(
                    template_name=template_name,
                    recipient_email=user.email,
                    context=user_context,
                    language=user.preferred_language
                )
                
                results.append({
                    'user_id': user.id,
                    'email': user.email,
                    'result': result
                })
        
        logger.info(f"Enviados {len(results)} emails masivos con template '{template_name}'")
        return {'status': 'sent', 'count': len(results), 'results': results}
        
    except Exception as exc:
        logger.error(f"Error enviando emails masivos: {str(exc)}")
        return {'status': 'failed', 'error': str(exc)}