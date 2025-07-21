"""
Servicio de correo electrónico para Buko AI
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import os

from flask import current_app, render_template, url_for
from flask_mail import Mail, Message
from jinja2 import Template

from app.utils.structured_logging import StructuredLogger


class EmailService:
    """Servicio centralizado para envío de emails"""
    
    def __init__(self, app=None, mail=None):
        self.app = app
        self.mail = mail
        self.logger = StructuredLogger('email_service')
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializar con la aplicación Flask"""
        self.app = app
        
        # Configurar Flask-Mail si no está configurado
        if self.mail is None:
            self.mail = Mail(app)
    
    def send_email(
        self,
        to: List[str],
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
        sender: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        reply_to: Optional[str] = None
    ) -> bool:
        """
        Enviar email con soporte para HTML y texto plano
        
        Args:
            to: Lista de destinatarios
            subject: Asunto del email
            html_body: Cuerpo HTML del email
            text_body: Cuerpo de texto plano (opcional)
            sender: Remitente (opcional, usa el configurado por defecto)
            cc: Lista de copia (opcional)
            bcc: Lista de copia oculta (opcional)
            attachments: Lista de archivos adjuntos (opcional)
            reply_to: Email de respuesta (opcional)
        
        Returns:
            bool: True si se envió exitosamente, False en caso contrario
        """
        try:
            # Validar configuración
            if not self._is_email_configured():
                self.logger.warning('Email service not configured, skipping send')
                return False
            
            # Crear mensaje
            msg = Message(
                subject=subject,
                recipients=to,
                html=html_body,
                body=text_body,
                sender=sender or current_app.config.get('MAIL_DEFAULT_SENDER'),
                cc=cc,
                bcc=bcc,
                reply_to=reply_to
            )
            
            # Agregar archivos adjuntos si existen
            if attachments:
                for attachment in attachments:
                    if 'filename' in attachment and 'data' in attachment:
                        msg.attach(
                            attachment['filename'],
                            attachment.get('content_type', 'application/octet-stream'),
                            attachment['data']
                        )
            
            # Enviar email
            self.mail.send(msg)
            
            self.logger.info('Email sent successfully',
                to=to,
                subject=subject,
                sender=sender or current_app.config.get('MAIL_DEFAULT_SENDER'),
                has_attachments=bool(attachments),
                cc_count=len(cc) if cc else 0,
                bcc_count=len(bcc) if bcc else 0
            )
            
            return True
            
        except Exception as e:
            self.logger.error('Email send error',
                error=str(e),
                to=to,
                subject=subject,
                sender=sender
            )
            return False
    
    def send_verification_email(self, user, verification_token: str) -> bool:
        """
        Enviar email de verificación de cuenta
        
        Args:
            user: Objeto User
            verification_token: Token de verificación
            
        Returns:
            bool: True si se envió exitosamente
        """
        try:
            # Generar URL de verificación
            verification_url = url_for(
                'auth.verify_email',
                token=verification_token,
                _external=True
            )
            
            # Renderizar template HTML
            html_body = render_template(
                'emails/email_verification.html',
                user=user,
                verification_url=verification_url,
                app_name=current_app.config.get('APP_NAME', 'Buko AI')
            )
            
            # Renderizar template de texto plano
            text_body = render_template(
                'emails/email_verification.txt',
                user=user,
                verification_url=verification_url,
                app_name=current_app.config.get('APP_NAME', 'Buko AI')
            )
            
            subject = f"Verifica tu cuenta en {current_app.config.get('APP_NAME', 'Buko AI')}"
            
            success = self.send_email(
                to=[user.email],
                subject=subject,
                html_body=html_body,
                text_body=text_body
            )
            
            if success:
                self.logger.info('Verification email sent',
                    user_id=user.id,
                    email=user.email,
                    token_length=len(verification_token)
                )
            
            return success
            
        except Exception as e:
            self.logger.error('Verification email error',
                error=str(e),
                user_id=user.id,
                email=user.email
            )
            return False
    
    def send_password_reset_email(self, user, reset_token: str) -> bool:
        """
        Enviar email de restablecimiento de contraseña
        
        Args:
            user: Objeto User
            reset_token: Token de restablecimiento
            
        Returns:
            bool: True si se envió exitosamente
        """
        try:
            # Generar URL de restablecimiento
            reset_url = url_for(
                'auth.password_reset',
                token=reset_token,
                _external=True
            )
            
            # Renderizar template HTML
            html_body = render_template(
                'emails/password_reset.html',
                user=user,
                reset_url=reset_url,
                app_name=current_app.config.get('APP_NAME', 'Buko AI'),
                expires_hours=1  # Token expira en 1 hora
            )
            
            # Renderizar template de texto plano
            text_body = render_template(
                'emails/password_reset.txt',
                user=user,
                reset_url=reset_url,
                app_name=current_app.config.get('APP_NAME', 'Buko AI'),
                expires_hours=1
            )
            
            subject = f"Restablece tu contraseña en {current_app.config.get('APP_NAME', 'Buko AI')}"
            
            success = self.send_email(
                to=[user.email],
                subject=subject,
                html_body=html_body,
                text_body=text_body
            )
            
            if success:
                self.logger.info('Password reset email sent',
                    user_id=user.id,
                    email=user.email,
                    token_length=len(reset_token)
                )
            
            return success
            
        except Exception as e:
            self.logger.error('Password reset email error',
                error=str(e),
                user_id=user.id,
                email=user.email
            )
            return False
    
    def send_welcome_email(self, user) -> bool:
        """
        Enviar email de bienvenida
        
        Args:
            user: Objeto User
            
        Returns:
            bool: True si se envió exitosamente
        """
        try:
            # Renderizar template HTML
            html_body = render_template(
                'emails/welcome.html',
                user=user,
                app_name=current_app.config.get('APP_NAME', 'Buko AI'),
                login_url=url_for('auth.login', _external=True),
                dashboard_url=url_for('main.index', _external=True)
            )
            
            # Renderizar template de texto plano
            text_body = render_template(
                'emails/welcome.txt',
                user=user,
                app_name=current_app.config.get('APP_NAME', 'Buko AI'),
                login_url=url_for('auth.login', _external=True),
                dashboard_url=url_for('main.index', _external=True)
            )
            
            subject = f"¡Bienvenido a {current_app.config.get('APP_NAME', 'Buko AI')}!"
            
            success = self.send_email(
                to=[user.email],
                subject=subject,
                html_body=html_body,
                text_body=text_body
            )
            
            if success:
                self.logger.info('Welcome email sent',
                    user_id=user.id,
                    email=user.email
                )
            
            return success
            
        except Exception as e:
            self.logger.error('Welcome email error',
                error=str(e),
                user_id=user.id,
                email=user.email
            )
            return False
    
    def send_book_completion_email(self, user, book) -> bool:
        """
        Enviar email cuando un libro está listo
        
        Args:
            user: Objeto User
            book: Objeto BookGeneration
            
        Returns:
            bool: True si se envió exitosamente
        """
        try:
            # URL para descargar el libro
            download_url = url_for(
                'main.download_book',
                book_id=book.id,
                _external=True
            )
            
            # Renderizar template HTML
            html_body = render_template(
                'emails/book_completion.html',
                user=user,
                book=book,
                download_url=download_url,
                app_name=current_app.config.get('APP_NAME', 'Buko AI')
            )
            
            # Renderizar template de texto plano
            text_body = render_template(
                'emails/book_completion.txt',
                user=user,
                book=book,
                download_url=download_url,
                app_name=current_app.config.get('APP_NAME', 'Buko AI')
            )
            
            subject = f"Tu libro '{book.title}' está listo para descargar"
            
            success = self.send_email(
                to=[user.email],
                subject=subject,
                html_body=html_body,
                text_body=text_body
            )
            
            if success:
                self.logger.info('Book completion email sent',
                    user_id=user.id,
                    email=user.email,
                    book_id=book.id,
                    book_title=book.title
                )
            
            return success
            
        except Exception as e:
            self.logger.error('Book completion email error',
                error=str(e),
                user_id=user.id,
                email=user.email,
                book_id=getattr(book, 'id', None)
            )
            return False
    
    def send_subscription_email(self, user, subscription_type: str, action: str = 'activated') -> bool:
        """
        Enviar email de cambios en suscripción
        
        Args:
            user: Objeto User
            subscription_type: Tipo de suscripción
            action: Acción realizada (activated, cancelled, expired)
            
        Returns:
            bool: True si se envió exitosamente
        """
        try:
            # Renderizar template HTML
            html_body = render_template(
                'emails/subscription_change.html',
                user=user,
                subscription_type=subscription_type,
                action=action,
                app_name=current_app.config.get('APP_NAME', 'Buko AI'),
                dashboard_url=url_for('main.index', _external=True)
            )
            
            # Renderizar template de texto plano
            text_body = render_template(
                'emails/subscription_change.txt',
                user=user,
                subscription_type=subscription_type,
                action=action,
                app_name=current_app.config.get('APP_NAME', 'Buko AI'),
                dashboard_url=url_for('main.index', _external=True)
            )
            
            # Determinar asunto según la acción
            subjects = {
                'activated': f"Suscripción {subscription_type} activada",
                'cancelled': f"Suscripción {subscription_type} cancelada",
                'expired': f"Suscripción {subscription_type} expirada"
            }
            
            subject = subjects.get(action, f"Cambio en tu suscripción {subscription_type}")
            
            success = self.send_email(
                to=[user.email],
                subject=subject,
                html_body=html_body,
                text_body=text_body
            )
            
            if success:
                self.logger.info('Subscription email sent',
                    user_id=user.id,
                    email=user.email,
                    subscription_type=subscription_type,
                    action=action
                )
            
            return success
            
        except Exception as e:
            self.logger.error('Subscription email error',
                error=str(e),
                user_id=user.id,
                email=user.email,
                subscription_type=subscription_type,
                action=action
            )
            return False
    
    def send_notification_email(
        self,
        user,
        title: str,
        message: str,
        action_url: Optional[str] = None,
        action_text: Optional[str] = None
    ) -> bool:
        """
        Enviar email de notificación general
        
        Args:
            user: Objeto User
            title: Título de la notificación
            message: Mensaje de la notificación
            action_url: URL de acción opcional
            action_text: Texto del botón de acción opcional
            
        Returns:
            bool: True si se envió exitosamente
        """
        try:
            # Renderizar template HTML
            html_body = render_template(
                'emails/notification.html',
                user=user,
                title=title,
                message=message,
                action_url=action_url,
                action_text=action_text,
                app_name=current_app.config.get('APP_NAME', 'Buko AI'),
                timestamp=datetime.utcnow()
            )
            
            # Renderizar template de texto plano
            text_body = render_template(
                'emails/notification.txt',
                user=user,
                title=title,
                message=message,
                action_url=action_url,
                action_text=action_text,
                app_name=current_app.config.get('APP_NAME', 'Buko AI'),
                timestamp=datetime.utcnow()
            )
            
            subject = f"{current_app.config.get('APP_NAME', 'Buko AI')}: {title}"
            
            success = self.send_email(
                to=[user.email],
                subject=subject,
                html_body=html_body,
                text_body=text_body
            )
            
            if success:
                self.logger.info('Notification email sent',
                    user_id=user.id,
                    email=user.email,
                    title=title,
                    has_action=bool(action_url)
                )
            
            return success
            
        except Exception as e:
            self.logger.error('Notification email error',
                error=str(e),
                user_id=user.id,
                email=user.email,
                title=title
            )
            return False
    
    def _is_email_configured(self) -> bool:
        """Verificar si el servicio de email está configurado"""
        if not current_app:
            return False
            
        required_configs = ['MAIL_SERVER', 'MAIL_PORT']
        return all(current_app.config.get(config) for config in required_configs)
    
    def test_email_connection(self) -> Dict[str, Any]:
        """
        Probar la conexión de email
        
        Returns:
            dict: Resultado del test con información de conexión
        """
        try:
            # Verificar configuración
            if not self._is_email_configured():
                return {
                    'success': False,
                    'error': 'Email service not configured',
                    'details': 'Missing MAIL_SERVER or MAIL_PORT configuration'
                }
            
            # Intentar conectar al servidor SMTP
            server = smtplib.SMTP(
                current_app.config['MAIL_SERVER'],
                current_app.config['MAIL_PORT']
            )
            
            if current_app.config.get('MAIL_USE_TLS'):
                server.starttls()
            
            if current_app.config.get('MAIL_USERNAME'):
                server.login(
                    current_app.config['MAIL_USERNAME'],
                    current_app.config['MAIL_PASSWORD']
                )
            
            server.quit()
            
            self.logger.info('Email connection test successful',
                server=current_app.config['MAIL_SERVER'],
                port=current_app.config['MAIL_PORT'],
                tls=current_app.config.get('MAIL_USE_TLS', False),
                authenticated=bool(current_app.config.get('MAIL_USERNAME'))
            )
            
            return {
                'success': True,
                'server': current_app.config['MAIL_SERVER'],
                'port': current_app.config['MAIL_PORT'],
                'tls': current_app.config.get('MAIL_USE_TLS', False),
                'authenticated': bool(current_app.config.get('MAIL_USERNAME'))
            }
            
        except Exception as e:
            self.logger.error('Email connection test error',
                error=str(e),
                server=current_app.config.get('MAIL_SERVER'),
                port=current_app.config.get('MAIL_PORT')
            )
            
            return {
                'success': False,
                'error': str(e),
                'server': current_app.config.get('MAIL_SERVER'),
                'port': current_app.config.get('MAIL_PORT')
            }


# Instancia global del servicio de email
email_service = EmailService()