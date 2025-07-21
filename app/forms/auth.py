"""
Formularios de autenticación para Buko AI
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, BooleanField, SubmitField,
    TextAreaField, SelectField, TelField, EmailField
)
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, ValidationError,
    Regexp, Optional
)
from email_validator import validate_email, EmailNotValidError

from app.models.user import User


class LoginForm(FlaskForm):
    """Formulario de inicio de sesión"""
    
    email = EmailField(
        'Email',
        validators=[
            DataRequired(message='El email es requerido'),
            Email(message='Formato de email inválido')
        ],
        render_kw={
            'placeholder': 'tu@email.com',
            'class': 'form-control',
            'autocomplete': 'email'
        }
    )
    
    password = PasswordField(
        'Contraseña',
        validators=[
            DataRequired(message='La contraseña es requerida')
        ],
        render_kw={
            'placeholder': 'Tu contraseña',
            'class': 'form-control',
            'autocomplete': 'current-password'
        }
    )
    
    remember_me = BooleanField(
        'Recordarme',
        render_kw={'class': 'form-check-input'}
    )
    
    submit = SubmitField(
        'Iniciar Sesión',
        render_kw={'class': 'btn btn-primary w-100'}
    )


class RegisterForm(FlaskForm):
    """Formulario de registro de usuario"""
    
    first_name = StringField(
        'Nombre',
        validators=[
            DataRequired(message='El nombre es requerido'),
            Length(min=2, max=50, message='El nombre debe tener entre 2 y 50 caracteres'),
            Regexp(
                r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$',
                message='El nombre solo puede contener letras y espacios'
            )
        ],
        render_kw={
            'placeholder': 'Tu nombre',
            'class': 'form-control',
            'autocomplete': 'given-name'
        }
    )
    
    last_name = StringField(
        'Apellido',
        validators=[
            DataRequired(message='El apellido es requerido'),
            Length(min=2, max=50, message='El apellido debe tener entre 2 y 50 caracteres'),
            Regexp(
                r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$',
                message='El apellido solo puede contener letras y espacios'
            )
        ],
        render_kw={
            'placeholder': 'Tu apellido',
            'class': 'form-control',
            'autocomplete': 'family-name'
        }
    )
    
    email = EmailField(
        'Email',
        validators=[
            DataRequired(message='El email es requerido'),
            Email(message='Formato de email inválido'),
            Length(max=120, message='El email es demasiado largo')
        ],
        render_kw={
            'placeholder': 'tu@email.com',
            'class': 'form-control',
            'autocomplete': 'email'
        }
    )
    
    country = SelectField(
        'País',
        validators=[DataRequired(message='El país es requerido')],
        choices=[
            ('', 'Selecciona tu país'),
            ('CO', 'Colombia'),
            ('MX', 'México'),
            ('AR', 'Argentina'),
            ('PE', 'Perú'),
            ('CL', 'Chile'),
            ('VE', 'Venezuela'),
            ('EC', 'Ecuador'),
            ('BO', 'Bolivia'),
            ('PY', 'Paraguay'),
            ('UY', 'Uruguay'),
            ('ES', 'España'),
            ('US', 'Estados Unidos'),
            ('CA', 'Canadá'),
            ('OTHER', 'Otro')
        ],
        render_kw={'class': 'form-select'}
    )
    
    city = StringField(
        'Ciudad',
        validators=[
            DataRequired(message='La ciudad es requerida'),
            Length(min=2, max=100, message='La ciudad debe tener entre 2 y 100 caracteres')
        ],
        render_kw={
            'placeholder': 'Tu ciudad',
            'class': 'form-control',
            'autocomplete': 'address-level2'
        }
    )
    
    phone_country = SelectField(
        'Código País (Opcional)',
        validators=[Optional()],
        choices=[
            ('', 'Código'),
            ('+57', '+57 (Colombia)'),
            ('+52', '+52 (México)'),
            ('+54', '+54 (Argentina)'),
            ('+51', '+51 (Perú)'),
            ('+56', '+56 (Chile)'),
            ('+58', '+58 (Venezuela)'),
            ('+593', '+593 (Ecuador)'),
            ('+591', '+591 (Bolivia)'),
            ('+595', '+595 (Paraguay)'),
            ('+598', '+598 (Uruguay)'),
            ('+34', '+34 (España)'),
            ('+1', '+1 (EE.UU./Canadá)')
        ],
        render_kw={'class': 'form-select'}
    )
    
    phone_number = StringField(
        'Teléfono (Opcional)',
        validators=[
            Optional(),
            Length(max=20, message='El teléfono es demasiado largo'),
            Regexp(
                r'^[0-9\s\-\(\)]+$',
                message='El teléfono solo puede contener números, espacios, guiones y paréntesis'
            )
        ],
        render_kw={
            'placeholder': '300 123 4567',
            'class': 'form-control',
            'autocomplete': 'tel'
        }
    )
    
    password = PasswordField(
        'Contraseña',
        validators=[
            DataRequired(message='La contraseña es requerida'),
            Length(min=8, max=128, message='La contraseña debe tener al menos 8 caracteres'),
            Regexp(
                r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
                message='La contraseña debe contener al menos: una minúscula, una mayúscula, un número y un símbolo'
            )
        ],
        render_kw={
            'placeholder': 'Mínimo 8 caracteres',
            'class': 'form-control',
            'autocomplete': 'new-password'
        }
    )
    
    confirm_password = PasswordField(
        'Confirmar Contraseña',
        validators=[
            DataRequired(message='Confirma tu contraseña'),
            EqualTo('password', message='Las contraseñas no coinciden')
        ],
        render_kw={
            'placeholder': 'Repite tu contraseña',
            'class': 'form-control',
            'autocomplete': 'new-password'
        }
    )
    
    preferred_language = SelectField(
        'Idioma Preferido',
        validators=[DataRequired(message='Selecciona tu idioma preferido')],
        choices=[
            ('es', 'Español'),
            ('en', 'English'),
            ('pt', 'Português'),
            ('fr', 'Français')
        ],
        default='es',
        render_kw={'class': 'form-select'}
    )
    
    terms_accepted = BooleanField(
        'Acepto los términos y condiciones y la política de privacidad',
        validators=[
            DataRequired(message='Debes aceptar los términos y condiciones')
        ],
        render_kw={'class': 'form-check-input'}
    )
    
    marketing_emails = BooleanField(
        'Deseo recibir emails sobre nuevas funcionalidades y promociones',
        render_kw={'class': 'form-check-input'}
    )
    
    submit = SubmitField(
        'Crear Cuenta',
        render_kw={'class': 'btn btn-success w-100'}
    )
    
    def validate_email(self, email):
        """Validación personalizada para email único"""
        try:
            # Validación adicional de email
            validate_email(email.data)
        except EmailNotValidError:
            raise ValidationError('Email inválido')
        
        # Verificar que el email no esté en uso
        user = User.find_by_email(email.data.lower())
        if user:
            raise ValidationError('Este email ya está registrado')


class PasswordResetRequestForm(FlaskForm):
    """Formulario para solicitar restablecimiento de contraseña"""
    
    email = EmailField(
        'Email',
        validators=[
            DataRequired(message='El email es requerido'),
            Email(message='Formato de email inválido')
        ],
        render_kw={
            'placeholder': 'tu@email.com',
            'class': 'form-control',
            'autocomplete': 'email'
        }
    )
    
    submit = SubmitField(
        'Enviar Enlace de Restablecimiento',
        render_kw={'class': 'btn btn-primary w-100'}
    )
    
    def validate_email(self, email):
        """Verificar que el email existe en el sistema"""
        user = User.find_by_email(email.data.lower())
        if not user:
            raise ValidationError('No existe una cuenta con este email')
        if not user.is_active:
            raise ValidationError('Esta cuenta está desactivada')


class PasswordResetForm(FlaskForm):
    """Formulario para restablecer contraseña con token"""
    
    password = PasswordField(
        'Nueva Contraseña',
        validators=[
            DataRequired(message='La contraseña es requerida'),
            Length(min=8, max=128, message='La contraseña debe tener al menos 8 caracteres'),
            Regexp(
                r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
                message='La contraseña debe contener al menos: una minúscula, una mayúscula, un número y un símbolo'
            )
        ],
        render_kw={
            'placeholder': 'Mínimo 8 caracteres',
            'class': 'form-control',
            'autocomplete': 'new-password'
        }
    )
    
    confirm_password = PasswordField(
        'Confirmar Nueva Contraseña',
        validators=[
            DataRequired(message='Confirma tu nueva contraseña'),
            EqualTo('password', message='Las contraseñas no coinciden')
        ],
        render_kw={
            'placeholder': 'Repite tu nueva contraseña',
            'class': 'form-control',
            'autocomplete': 'new-password'
        }
    )
    
    submit = SubmitField(
        'Cambiar Contraseña',
        render_kw={'class': 'btn btn-success w-100'}
    )


class ChangePasswordForm(FlaskForm):
    """Formulario para cambiar contraseña (usuario autenticado)"""
    
    current_password = PasswordField(
        'Contraseña Actual',
        validators=[
            DataRequired(message='La contraseña actual es requerida')
        ],
        render_kw={
            'placeholder': 'Tu contraseña actual',
            'class': 'form-control',
            'autocomplete': 'current-password'
        }
    )
    
    new_password = PasswordField(
        'Nueva Contraseña',
        validators=[
            DataRequired(message='La nueva contraseña es requerida'),
            Length(min=8, max=128, message='La contraseña debe tener al menos 8 caracteres'),
            Regexp(
                r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
                message='La contraseña debe contener al menos: una minúscula, una mayúscula, un número y un símbolo'
            )
        ],
        render_kw={
            'placeholder': 'Mínimo 8 caracteres',
            'class': 'form-control',
            'autocomplete': 'new-password'
        }
    )
    
    confirm_new_password = PasswordField(
        'Confirmar Nueva Contraseña',
        validators=[
            DataRequired(message='Confirma tu nueva contraseña'),
            EqualTo('new_password', message='Las contraseñas no coinciden')
        ],
        render_kw={
            'placeholder': 'Repite tu nueva contraseña',
            'class': 'form-control',
            'autocomplete': 'new-password'
        }
    )
    
    submit = SubmitField(
        'Cambiar Contraseña',
        render_kw={'class': 'btn btn-primary'}
    )


class EmailVerificationRequestForm(FlaskForm):
    """Formulario para reenviar verificación de email"""
    
    submit = SubmitField(
        'Reenviar Email de Verificación',
        render_kw={'class': 'btn btn-outline-primary'}
    )


class ProfileForm(FlaskForm):
    """Formulario para actualizar perfil de usuario"""
    
    first_name = StringField(
        'Nombre',
        validators=[
            DataRequired(message='El nombre es requerido'),
            Length(min=2, max=50, message='El nombre debe tener entre 2 y 50 caracteres'),
            Regexp(
                r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$',
                message='El nombre solo puede contener letras y espacios'
            )
        ],
        render_kw={
            'class': 'form-control',
            'autocomplete': 'given-name'
        }
    )
    
    last_name = StringField(
        'Apellido',
        validators=[
            DataRequired(message='El apellido es requerido'),
            Length(min=2, max=50, message='El apellido debe tener entre 2 y 50 caracteres'),
            Regexp(
                r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$',
                message='El apellido solo puede contener letras y espacios'
            )
        ],
        render_kw={
            'class': 'form-control',
            'autocomplete': 'family-name'
        }
    )
    
    country = SelectField(
        'País',
        validators=[DataRequired(message='El país es requerido')],
        choices=[
            ('', 'Selecciona tu país'),
            ('CO', 'Colombia'),
            ('MX', 'México'),
            ('AR', 'Argentina'),
            ('PE', 'Perú'),
            ('CL', 'Chile'),
            ('VE', 'Venezuela'),
            ('EC', 'Ecuador'),
            ('BO', 'Bolivia'),
            ('PY', 'Paraguay'),
            ('UY', 'Uruguay'),
            ('ES', 'España'),
            ('US', 'Estados Unidos'),
            ('CA', 'Canadá'),
            ('OTHER', 'Otro')
        ],
        render_kw={'class': 'form-select'}
    )
    
    city = StringField(
        'Ciudad',
        validators=[
            DataRequired(message='La ciudad es requerida'),
            Length(min=2, max=100, message='La ciudad debe tener entre 2 y 100 caracteres')
        ],
        render_kw={
            'class': 'form-control',
            'autocomplete': 'address-level2'
        }
    )
    
    phone_country = SelectField(
        'Código País',
        validators=[Optional()],
        choices=[
            ('', 'Código'),
            ('+57', '+57 (Colombia)'),
            ('+52', '+52 (México)'),
            ('+54', '+54 (Argentina)'),
            ('+51', '+51 (Perú)'),
            ('+56', '+56 (Chile)'),
            ('+58', '+58 (Venezuela)'),
            ('+593', '+593 (Ecuador)'),
            ('+591', '+591 (Bolivia)'),
            ('+595', '+595 (Paraguay)'),
            ('+598', '+598 (Uruguay)'),
            ('+34', '+34 (España)'),
            ('+1', '+1 (EE.UU./Canadá)')
        ],
        render_kw={'class': 'form-select'}
    )
    
    phone_number = StringField(
        'Teléfono',
        validators=[
            Optional(),
            Length(max=20, message='El teléfono es demasiado largo'),
            Regexp(
                r'^[0-9\s\-\(\)]+$',
                message='El teléfono solo puede contener números, espacios, guiones y paréntesis'
            )
        ],
        render_kw={
            'class': 'form-control',
            'autocomplete': 'tel'
        }
    )
    
    billing_address = TextAreaField(
        'Dirección de Facturación',
        validators=[
            Optional(),
            Length(max=500, message='La dirección es demasiado larga')
        ],
        render_kw={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Dirección completa para facturación (opcional)'
        }
    )
    
    preferred_language = SelectField(
        'Idioma Preferido',
        validators=[DataRequired(message='Selecciona tu idioma preferido')],
        choices=[
            ('es', 'Español'),
            ('en', 'English'),
            ('pt', 'Português'),
            ('fr', 'Français')
        ],
        render_kw={'class': 'form-select'}
    )
    
    timezone = SelectField(
        'Zona Horaria',
        validators=[DataRequired(message='Selecciona tu zona horaria')],
        choices=[
            ('UTC', 'UTC (Coordinated Universal Time)'),
            ('America/Bogota', 'América/Bogotá (COT)'),
            ('America/Mexico_City', 'América/México (CST)'),
            ('America/Argentina/Buenos_Aires', 'América/Buenos Aires (ART)'),
            ('America/Lima', 'América/Lima (PET)'),
            ('America/Santiago', 'América/Santiago (CLT)'),
            ('America/Caracas', 'América/Caracas (VET)'),
            ('America/Guayaquil', 'América/Guayaquil (ECT)'),
            ('America/La_Paz', 'América/La Paz (BOT)'),
            ('America/Asuncion', 'América/Asunción (PYT)'),
            ('America/Montevideo', 'América/Montevideo (UYT)'),
            ('Europe/Madrid', 'Europa/Madrid (CET)'),
            ('America/New_York', 'América/Nueva York (EST)'),
            ('America/Los_Angeles', 'América/Los Ángeles (PST)'),
            ('America/Toronto', 'América/Toronto (EST)')
        ],
        render_kw={'class': 'form-select'}
    )
    
    submit = SubmitField(
        'Actualizar Perfil',
        render_kw={'class': 'btn btn-primary'}
    )


class DeleteAccountForm(FlaskForm):
    """Formulario para eliminar cuenta"""
    
    current_password = PasswordField(
        'Confirma tu contraseña para eliminar la cuenta',
        validators=[
            DataRequired(message='La contraseña es requerida para eliminar la cuenta')
        ],
        render_kw={
            'placeholder': 'Tu contraseña actual',
            'class': 'form-control',
            'autocomplete': 'current-password'
        }
    )
    
    confirmation = StringField(
        'Escribe "ELIMINAR" para confirmar',
        validators=[
            DataRequired(message='Debes escribir ELIMINAR para confirmar')
        ],
        render_kw={
            'placeholder': 'ELIMINAR',
            'class': 'form-control'
        }
    )
    
    submit = SubmitField(
        'Eliminar Cuenta Permanentemente',
        render_kw={'class': 'btn btn-danger'}
    )

    def validate_confirmation(self, confirmation):
        """Validación personalizada para confirmación"""
        if confirmation.data != 'ELIMINAR':
            raise ValidationError('Debes escribir exactamente "ELIMINAR"')