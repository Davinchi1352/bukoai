"""
Rutas de autenticación para Buko AI
"""

from flask import (
    Blueprint, render_template, redirect, url_for, flash, 
    request, jsonify, current_app, session
)
from flask_login import (
    login_user, logout_user, login_required, current_user
)
from urllib.parse import urlparse
import secrets
from datetime import datetime

from app import db
from app.models.user import User, UserStatus, SubscriptionType
from app.forms.auth import (
    LoginForm, RegisterForm, PasswordResetRequestForm,
    PasswordResetForm, ChangePasswordForm, ProfileForm,
    DeleteAccountForm, EmailVerificationRequestForm
)
from app.utils.structured_logging import StructuredLogger, security_logger
from app.services.email_service import email_service

bp = Blueprint('auth', __name__)

# Configurar logger
logger = StructuredLogger('auth')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Ruta de inicio de sesión"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        try:
            user = User.find_by_email(form.email.data.lower())
            
            if user and user.check_password(form.password.data):
                if not user.is_active:
                    flash('Tu cuenta está desactivada. Contacta al soporte.', 'error')
                    security_logger.log_authentication_attempt(
                        email=form.email.data,
                        success=False,
                        failure_reason='inactive_account',
                        ip_address=request.remote_addr
                    )
                    return render_template('auth/login.html', form=form)
                
                # Login exitoso
                login_user(user, remember=form.remember_me.data)
                user.update_last_login()
                
                security_logger.log_authentication_attempt(
                    email=user.email,
                    success=True,
                    ip_address=request.remote_addr
                )
                
                flash(f'¡Bienvenido de vuelta, {user.first_name}!', 'success')
                
                # Redireccionar a la página solicitada o al dashboard
                next_page = request.args.get('next')
                if not next_page or urlparse(next_page).netloc != '':
                    next_page = url_for('main.index')
                
                return redirect(next_page)
            else:
                flash('Email o contraseña incorrectos', 'error')
                security_logger.log_authentication_attempt(
                    email=form.email.data,
                    success=False,
                    failure_reason='invalid_credentials',
                    ip_address=request.remote_addr
                )
        except Exception as e:
            logger.error('login_error', error=str(e), email=form.email.data)
            flash('Error interno del servidor. Intenta nuevamente.', 'error')
    
    return render_template('auth/login.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    """Ruta de cierre de sesión"""
    user_email = current_user.email
    logger.info('user_logout', 
        user_id=current_user.id,
        email=user_email,
        ip=request.remote_addr
    )
    
    logout_user()
    flash('Has cerrado sesión exitosamente', 'info')
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Ruta de registro de usuario"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        try:
            # Crear nuevo usuario
            user = User(
                first_name=form.first_name.data.strip(),
                last_name=form.last_name.data.strip(),
                email=form.email.data.lower().strip(),
                country=form.country.data,
                city=form.city.data.strip(),
                phone_country=form.phone_country.data if form.phone_country.data else None,
                phone_number=form.phone_number.data.strip() if form.phone_number.data else None,
                preferred_language=form.preferred_language.data,
                password=form.password.data,
                subscription_type=SubscriptionType.FREE,
                status=UserStatus.ACTIVE
            )
            
            # Generar token de verificación de email
            verification_token = user.generate_email_verification_token()
            
            db.session.add(user)
            db.session.commit()
            
            logger.info('user_registered', 
                user_id=user.id,
                email=user.email,
                country=user.country,
                ip=request.remote_addr
            )
            
            # Enviar email de verificación
            email_sent = email_service.send_verification_email(user, verification_token)
            
            if email_sent:
                flash(
                    'Cuenta creada exitosamente. Te hemos enviado un email de verificación.',
                    'success'
                )
            else:
                flash(
                    'Cuenta creada exitosamente. El email de verificación se enviará en breve.',
                    'success'
                )
            
            # Enviar email de bienvenida
            email_service.send_welcome_email(user)
            
            # Login automático después del registro
            login_user(user)
            user.update_last_login()
            
            return redirect(url_for('main.index'))
            
        except Exception as e:
            db.session.rollback()
            logger.error('registration_error', error=str(e), email=form.email.data)
            flash('Error al crear la cuenta. Intenta nuevamente.', 'error')
    
    return render_template('auth/register.html', form=form)


@bp.route('/password-reset-request', methods=['GET', 'POST'])
def password_reset_request():
    """Solicitar restablecimiento de contraseña"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = PasswordResetRequestForm()
    
    if form.validate_on_submit():
        try:
            user = User.find_by_email(form.email.data.lower())
            if user and user.is_active:
                # Generar token de restablecimiento
                reset_token = user.generate_password_reset_token()
                
                logger.info('password_reset_requested', 
                    user_id=user.id,
                    email=user.email,
                    ip=request.remote_addr
                )
                
                # Enviar email con enlace de restablecimiento
                email_sent = email_service.send_password_reset_email(user, reset_token)
                
                flash(
                    'Te hemos enviado un email con instrucciones para restablecer tu contraseña.',
                    'info'
                )
            else:
                # Por seguridad, siempre mostrar el mismo mensaje
                flash(
                    'Te hemos enviado un email con instrucciones para restablecer tu contraseña.',
                    'info'
                )
                
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            logger.error('password_reset_request_error', error=str(e))
            flash('Error interno. Intenta nuevamente.', 'error')
    
    return render_template('auth/password_reset_request.html', form=form)


@bp.route('/password-reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    """Restablecer contraseña con token"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    user = User.find_by_password_reset_token(token)
    if not user or not user.is_password_reset_token_valid(token):
        flash('El enlace de restablecimiento es inválido o ha expirado.', 'error')
        return redirect(url_for('auth.password_reset_request'))
    
    form = PasswordResetForm()
    
    if form.validate_on_submit():
        try:
            user.set_password(form.password.data)
            user.clear_password_reset_token()
            
            logger.info('password_reset_completed', 
                user_id=user.id,
                email=user.email,
                ip=request.remote_addr
            )
            
            flash('Tu contraseña ha sido actualizada exitosamente.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            logger.error('password_reset_error', error=str(e), user_id=user.id)
            flash('Error al actualizar la contraseña. Intenta nuevamente.', 'error')
    
    return render_template('auth/password_reset.html', form=form)


@bp.route('/verify-email/<token>')
def verify_email(token):
    """Verificar email con token"""
    if current_user.is_authenticated and current_user.email_verified:
        flash('Tu email ya está verificado.', 'info')
        return redirect(url_for('main.index'))
    
    user = User.find_by_verification_token(token)
    if not user:
        flash('El enlace de verificación es inválido o ha expirado.', 'error')
        return redirect(url_for('main.index'))
    
    if user.email_verification_expires and user.email_verification_expires < datetime.utcnow():
        flash('El enlace de verificación ha expirado.', 'error')
        return redirect(url_for('auth.resend_verification'))
    
    try:
        user.verify_email()
        
        logger.info('email_verified', 
            user_id=user.id,
            email=user.email,
            ip=request.remote_addr
        )
        
        flash('¡Email verificado exitosamente!', 'success')
        
        if not current_user.is_authenticated:
            login_user(user)
            user.update_last_login()
        
        return redirect(url_for('main.index'))
        
    except Exception as e:
        logger.error('email_verification_error', error=str(e), user_id=user.id)
        flash('Error al verificar el email. Intenta nuevamente.', 'error')
        return redirect(url_for('main.index'))


@bp.route('/resend-verification', methods=['GET', 'POST'])
@login_required
def resend_verification():
    """Reenviar email de verificación"""
    if current_user.email_verified:
        flash('Tu email ya está verificado.', 'info')
        return redirect(url_for('main.index'))
    
    form = EmailVerificationRequestForm()
    
    if form.validate_on_submit():
        try:
            verification_token = current_user.generate_email_verification_token()
            
            logger.info('verification_email_resent', 
                user_id=current_user.id,
                email=current_user.email,
                ip=request.remote_addr
            )
            
            # Enviar email de verificación
            email_sent = email_service.send_verification_email(current_user, verification_token)
            
            if email_sent:
                flash('Te hemos enviado un nuevo email de verificación.', 'success')
            else:
                flash('El email de verificación se enviará en breve.', 'info')
                
            return redirect(url_for('main.index'))
            
        except Exception as e:
            logger.error('resend_verification_error', error=str(e))
            flash('Error al enviar el email. Intenta nuevamente.', 'error')
    
    return render_template('auth/resend_verification.html', form=form)


@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Perfil de usuario"""
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        try:
            current_user.update(
                first_name=form.first_name.data.strip(),
                last_name=form.last_name.data.strip(),
                country=form.country.data,
                city=form.city.data.strip(),
                phone_country=form.phone_country.data if form.phone_country.data else None,
                phone_number=form.phone_number.data.strip() if form.phone_number.data else None,
                billing_address=form.billing_address.data.strip() if form.billing_address.data else None,
                preferred_language=form.preferred_language.data,
                timezone=form.timezone.data
            )
            
            db.session.commit()
            
            logger.info('profile_updated', 
                user_id=current_user.id,
                email=current_user.email,
                ip=request.remote_addr
            )
            
            flash('Perfil actualizado exitosamente.', 'success')
            return redirect(url_for('auth.profile'))
            
        except Exception as e:
            db.session.rollback()
            logger.error('profile_update_error', error=str(e), user_id=current_user.id)
            flash('Error al actualizar el perfil. Intenta nuevamente.', 'error')
    
    return render_template('auth/profile.html', form=form, user=current_user)


@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Cambiar contraseña"""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        try:
            if not current_user.check_password(form.current_password.data):
                flash('La contraseña actual es incorrecta.', 'error')
                return render_template('auth/change_password.html', form=form)
            
            current_user.set_password(form.new_password.data)
            db.session.commit()
            
            logger.info('password_changed', 
                user_id=current_user.id,
                email=current_user.email,
                ip=request.remote_addr
            )
            
            flash('Contraseña actualizada exitosamente.', 'success')
            return redirect(url_for('auth.profile'))
            
        except Exception as e:
            db.session.rollback()
            logger.error('password_change_error', error=str(e), user_id=current_user.id)
            flash('Error al cambiar la contraseña. Intenta nuevamente.', 'error')
    
    return render_template('auth/change_password.html', form=form)


@bp.route('/delete-account', methods=['GET', 'POST'])
@login_required
def delete_account():
    """Eliminar cuenta de usuario"""
    form = DeleteAccountForm()
    
    if form.validate_on_submit():
        try:
            if not current_user.check_password(form.current_password.data):
                flash('La contraseña es incorrecta.', 'error')
                return render_template('auth/delete_account.html', form=form)
            
            if form.confirmation.data != 'ELIMINAR':
                flash('Debes escribir exactamente "ELIMINAR" para confirmar.', 'error')
                return render_template('auth/delete_account.html', form=form)
            
            user_email = current_user.email
            user_id = current_user.id
            
            # Soft delete del usuario
            current_user.soft_delete()
            current_user.update(status=UserStatus.DELETED)
            
            db.session.commit()
            
            logger.info('account_deleted', 
                user_id=user_id,
                email=user_email,
                ip=request.remote_addr
            )
            
            logout_user()
            flash('Tu cuenta ha sido eliminada permanentemente.', 'info')
            return redirect(url_for('main.index'))
            
        except Exception as e:
            db.session.rollback()
            logger.error('account_deletion_error', error=str(e), user_id=current_user.id)
            flash('Error al eliminar la cuenta. Intenta nuevamente.', 'error')
    
    return render_template('auth/delete_account.html', form=form)


# API Routes para autenticación
@bp.route('/api/check-email', methods=['POST'])
def api_check_email():
    """API para verificar si email está disponible"""
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()
        
        if not email:
            return jsonify({'available': False, 'message': 'Email requerido'})
        
        user = User.find_by_email(email)
        available = user is None
        
        return jsonify({
            'available': available,
            'message': 'Email disponible' if available else 'Email ya está en uso'
        })
        
    except Exception as e:
        logger.error('api_check_email_error', error=str(e))
        return jsonify({'available': False, 'message': 'Error interno'}), 500


@bp.route('/api/session', methods=['GET'])
def api_session():
    """API para obtener información de sesión"""
    try:
        if current_user.is_authenticated:
            return jsonify({
                'authenticated': True,
                'user': {
                    'id': current_user.id,
                    'email': current_user.email,
                    'full_name': current_user.full_name,
                    'subscription_type': current_user.subscription_type.value,
                    'email_verified': current_user.email_verified,
                    'books_remaining': current_user.remaining_books
                }
            })
        else:
            return jsonify({'authenticated': False})
            
    except Exception as e:
        logger.error('api_session_error', error=str(e))
        return jsonify({'authenticated': False, 'error': 'Error interno'}), 500


@bp.route('/verify-password', methods=['POST'])
@login_required
def verify_password():
    """API para verificar la contraseña del usuario actual"""
    try:
        data = request.get_json()
        password = data.get('password', '')
        
        if not password:
            return jsonify({'error': 'Contraseña requerida'}), 400
        
        if not current_user.check_password(password):
            return jsonify({'error': 'Contraseña incorrecta'}), 401
        
        return jsonify({'success': True, 'message': 'Contraseña verificada'})
        
    except Exception as e:
        logger.error('verify_password_error', error=str(e), user_id=current_user.id)
        return jsonify({'error': 'Error interno'}), 500


@bp.route('/status')
def auth_status():
    """Status de autenticación."""
    return jsonify({
        'message': 'Authentication system fully implemented',
        'status': 'active',
        'routes': [
            'login', 'logout', 'register', 'password-reset-request',
            'password-reset', 'verify-email', 'resend-verification',
            'profile', 'change-password', 'delete-account'
        ],
        'api_routes': ['api/check-email', 'api/session', 'verify-password']
    })