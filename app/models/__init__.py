"""
Modelos de Buko AI
"""

from .base import db, BaseModel, SoftDeleteMixin, TimestampMixin, AuditMixin
from .user import User, UserStatus, SubscriptionType
from .book_generation import BookGeneration, BookStatus, BookFormat
from .subscription import Subscription, Payment, PaymentStatus, PaymentMethod
from .system_log import SystemLog, BookDownload, Referral, LogLevel, LogStatus
from .email_template import EmailTemplate

# Importar todos los modelos para que SQLAlchemy los reconozca
__all__ = [
    'db',
    'BaseModel',
    'SoftDeleteMixin', 
    'TimestampMixin',
    'AuditMixin',
    'User',
    'UserStatus',
    'SubscriptionType',
    'BookGeneration',
    'BookStatus',
    'BookFormat',
    'Subscription',
    'Payment',
    'PaymentStatus',
    'PaymentMethod',
    'SystemLog',
    'BookDownload',
    'EmailTemplate',
    'Referral',
    'LogLevel',
    'LogStatus',
]


def init_db(app):
    """Inicializa la base de datos con la aplicacion Flask"""
    db.init_app(app)
    
    # Crear todas las tablas
    with app.app_context():
        db.create_all()
        
        # Insertar datos iniciales si es necesario
        create_default_data()


def create_default_data():
    """Crea datos por defecto"""
    # Crear plantillas de email por defecto
    create_default_email_templates()
    
    # Crear usuario administrador si no existe
    create_admin_user()


def create_default_email_templates():
    """Crea plantillas de email por defecto"""
    templates = [
        {
            'name': 'welcome',
            'subject': 'Bienvenido a Buko AI',
            'html_content': '''
            <html>
                <body>
                    <h1>�Bienvenido a Buko AI!</h1>
                    <p>Hola {{ first_name }},</p>
                    <p>Gracias por registrarte en Buko AI. �Estamos emocionados de ayudarte a crear libros incre�bles!</p>
                    <p>Puedes comenzar a crear tu primer libro visitando tu <a href="{{ dashboard_url }}">dashboard</a>.</p>
                    <p>Si tienes alguna pregunta, no dudes en contactarnos.</p>
                    <p>�Saludos!<br>El equipo de Buko AI</p>
                </body>
            </html>
            ''',
            'text_content': '''
            �Bienvenido a Buko AI!
            
            Hola {{ first_name }},
            
            Gracias por registrarte en Buko AI. �Estamos emocionados de ayudarte a crear libros incre�bles!
            
            Puedes comenzar a crear tu primer libro visitando tu dashboard: {{ dashboard_url }}
            
            Si tienes alguna pregunta, no dudes en contactarnos.
            
            �Saludos!
            El equipo de Buko AI
            ''',
            'variables': {
                'first_name': 'string',
                'dashboard_url': 'string'
            }
        },
        {
            'name': 'book_completed',
            'subject': 'Tu libro "{{ book_title }}" est� listo',
            'html_content': '''
            <html>
                <body>
                    <h1>�Tu libro est� listo!</h1>
                    <p>Hola {{ first_name }},</p>
                    <p>Tu libro <strong>"{{ book_title }}"</strong> ha sido generado exitosamente.</p>
                    <p><strong>Estad�sticas:</strong></p>
                    <ul>
                        <li>P�ginas: {{ pages }}</li>
                        <li>Palabras: {{ words }}</li>
                        <li>Tiempo de generaci�n: {{ generation_time }}</li>
                    </ul>
                    <p>Puedes descargarlo desde tu <a href="{{ download_url }}">dashboard</a>.</p>
                    <p>�Esperamos que disfrutes tu nuevo libro!</p>
                    <p>�Saludos!<br>El equipo de Buko AI</p>
                </body>
            </html>
            ''',
            'text_content': '''
            �Tu libro est� listo!
            
            Hola {{ first_name }},
            
            Tu libro "{{ book_title }}" ha sido generado exitosamente.
            
            Estad�sticas:
            - P�ginas: {{ pages }}
            - Palabras: {{ words }}
            - Tiempo de generaci�n: {{ generation_time }}
            
            Puedes descargarlo desde tu dashboard: {{ download_url }}
            
            �Esperamos que disfrutes tu nuevo libro!
            
            �Saludos!
            El equipo de Buko AI
            ''',
            'variables': {
                'first_name': 'string',
                'book_title': 'string',
                'pages': 'number',
                'words': 'number',
                'generation_time': 'string',
                'download_url': 'string'
            }
        },
        {
            'name': 'password_reset',
            'subject': 'Restablece tu contrase�a en Buko AI',
            'html_content': '''
            <html>
                <body>
                    <h1>Restablece tu contrase�a</h1>
                    <p>Hola {{ first_name }},</p>
                    <p>Hemos recibido una solicitud para restablecer tu contrase�a.</p>
                    <p>Haz clic en el siguiente enlace para crear una nueva contrase�a:</p>
                    <p><a href="{{ reset_url }}">Restablecer contrase�a</a></p>
                    <p>Este enlace expirar� en {{ expiry_hours }} hora(s).</p>
                    <p>Si no solicitaste este cambio, puedes ignorar este email.</p>
                    <p>�Saludos!<br>El equipo de Buko AI</p>
                </body>
            </html>
            ''',
            'text_content': '''
            Restablece tu contrase�a
            
            Hola {{ first_name }},
            
            Hemos recibido una solicitud para restablecer tu contrase�a.
            
            Haz clic en el siguiente enlace para crear una nueva contrase�a:
            {{ reset_url }}
            
            Este enlace expirar� en {{ expiry_hours }} hora(s).
            
            Si no solicitaste este cambio, puedes ignorar este email.
            
            �Saludos!
            El equipo de Buko AI
            ''',
            'variables': {
                'first_name': 'string',
                'reset_url': 'string',
                'expiry_hours': 'number'
            }
        },
        {
            'name': 'email_verification',
            'subject': 'Verifica tu cuenta en Buko AI',
            'html_content': '''
            <html>
                <body>
                    <h1>Verifica tu cuenta</h1>
                    <p>Hola {{ first_name }},</p>
                    <p>Gracias por registrarte en Buko AI. Para completar tu registro, necesitamos verificar tu direcci�n de email.</p>
                    <p>Haz clic en el siguiente enlace para verificar tu cuenta:</p>
                    <p><a href="{{ verification_url }}">Verificar cuenta</a></p>
                    <p>Este enlace expirar� en {{ expiry_hours }} hora(s).</p>
                    <p>Si no te registraste en Buko AI, puedes ignorar este email.</p>
                    <p>�Saludos!<br>El equipo de Buko AI</p>
                </body>
            </html>
            ''',
            'text_content': '''
            Verifica tu cuenta
            
            Hola {{ first_name }},
            
            Gracias por registrarte en Buko AI. Para completar tu registro, necesitamos verificar tu direcci�n de email.
            
            Haz clic en el siguiente enlace para verificar tu cuenta:
            {{ verification_url }}
            
            Este enlace expirar� en {{ expiry_hours }} hora(s).
            
            Si no te registraste en Buko AI, puedes ignorar este email.
            
            �Saludos!
            El equipo de Buko AI
            ''',
            'variables': {
                'first_name': 'string',
                'verification_url': 'string',
                'expiry_hours': 'number'
            }
        }
    ]
    
    for template_data in templates:
        existing_template = EmailTemplate.query.filter_by(name=template_data['name']).first()
        if not existing_template:
            template = EmailTemplate(**template_data)
            template.save()


def create_admin_user():
    """Crea usuario administrador si no existe"""
    from flask import current_app
    
    admin_email = current_app.config.get('ADMIN_EMAIL', 'admin@buko-ai.com')
    admin_password = current_app.config.get('ADMIN_PASSWORD', 'admin123')
    
    existing_admin = User.find_by_email(admin_email)
    if not existing_admin:
        admin = User(
            email=admin_email,
            password=admin_password,
            first_name='Admin',
            last_name='User',
            subscription_type=SubscriptionType.ENTERPRISE,
            email_verified=True,
            status=UserStatus.ACTIVE
        )
        admin.save()
        
        # Log de creaci�n del administrador
        SystemLog.log_action(
            action='admin_user_created',
            details={'email': admin_email},
            level=LogLevel.INFO
        )


def reset_monthly_usage():
    """Resetea el uso mensual de todos los usuarios"""
    from datetime import datetime, timedelta
    
    # Resetear usuarios cuyo �ltimo reset fue hace m�s de un mes
    one_month_ago = datetime.utcnow() - timedelta(days=30)
    
    users_to_reset = User.query.filter(
        User.last_reset_date < one_month_ago
    ).all()
    
    for user in users_to_reset:
        user.reset_monthly_usage()
    
    # Log de reset mensual
    SystemLog.log_action(
        action='monthly_usage_reset',
        details={'users_reset': len(users_to_reset)},
        level=LogLevel.INFO
    )


def cleanup_old_logs(days: int = 30):
    """Limpia logs antiguos"""
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    old_logs = SystemLog.query.filter(
        SystemLog.created_at < cutoff_date
    ).all()
    
    for log in old_logs:
        log.delete()
    
    # Log de limpieza
    SystemLog.log_action(
        action='logs_cleanup',
        details={'logs_deleted': len(old_logs), 'days': days},
        level=LogLevel.INFO
    )


def get_database_statistics():
    """Retorna estad�sticas de la base de datos"""
    stats = {
        'users': {
            'total': User.query.count(),
            'active': User.query.filter_by(status=UserStatus.ACTIVE).count(),
            'verified': User.query.filter_by(email_verified=True).count(),
            'by_subscription': {}
        },
        'books': {
            'total': BookGeneration.query.count(),
            'completed': BookGeneration.query.filter_by(status=BookStatus.COMPLETED).count(),
            'processing': BookGeneration.query.filter_by(status=BookStatus.PROCESSING).count(),
            'failed': BookGeneration.query.filter_by(status=BookStatus.FAILED).count(),
            'queued': BookGeneration.query.filter_by(status=BookStatus.QUEUED).count(),
        },
        'subscriptions': {
            'total': Subscription.query.count(),
            'active': len(Subscription.get_active_subscriptions()),
        },
        'payments': {
            'total': Payment.query.count(),
            'completed': Payment.query.filter_by(status=PaymentStatus.COMPLETED).count(),
            'total_revenue': Payment.get_total_revenue(),
        },
        'downloads': {
            'total': BookDownload.query.count(),
            'popular_formats': BookDownload.get_popular_formats(),
        }
    }
    
    # Estad�sticas por tipo de suscripci�n
    for sub_type in SubscriptionType:
        stats['users']['by_subscription'][sub_type.value] = User.query.filter_by(
            subscription_type=sub_type
        ).count()
    
    return stats