#!/usr/bin/env python3
"""
Script para inicializar la base de datos con datos de prueba
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from typing import List
import random

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import create_app
from app.models import (
    db, User, UserStatus, SubscriptionType, BookGeneration, BookStatus,
    Subscription, Payment, PaymentStatus, PaymentMethod, SystemLog,
    BookDownload, EmailTemplate, Referral, LogLevel, BookFormat
)


def create_sample_users(count: int = 10) -> List[User]:
    """Crea usuarios de ejemplo"""
    users = []
    
    # Datos de ejemplo
    sample_data = [
        {"first_name": "Juan", "last_name": "Pérez", "email": "juan.perez@example.com"},
        {"first_name": "María", "last_name": "García", "email": "maria.garcia@example.com"},
        {"first_name": "Carlos", "last_name": "López", "email": "carlos.lopez@example.com"},
        {"first_name": "Ana", "last_name": "Martínez", "email": "ana.martinez@example.com"},
        {"first_name": "Luis", "last_name": "Rodríguez", "email": "luis.rodriguez@example.com"},
        {"first_name": "Carmen", "last_name": "Sánchez", "email": "carmen.sanchez@example.com"},
        {"first_name": "José", "last_name": "Fernández", "email": "jose.fernandez@example.com"},
        {"first_name": "Isabel", "last_name": "González", "email": "isabel.gonzalez@example.com"},
        {"first_name": "Miguel", "last_name": "Ruiz", "email": "miguel.ruiz@example.com"},
        {"first_name": "Laura", "last_name": "Jiménez", "email": "laura.jimenez@example.com"},
    ]
    
    subscription_types = list(SubscriptionType)
    countries = ["España", "México", "Argentina", "Colombia", "Chile", "Perú", "Venezuela"]
    cities = ["Madrid", "Barcelona", "Ciudad de México", "Buenos Aires", "Bogotá", "Santiago", "Lima"]
    
    for i in range(min(count, len(sample_data))):
        user_data = sample_data[i]
        
        # Verificar si el usuario ya existe
        existing_user = User.find_by_email(user_data["email"])
        if existing_user:
            continue
        
        user = User(
            email=user_data["email"],
            password="password123",  # Contraseña de ejemplo
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            phone_country="+34" if i % 3 == 0 else "+52",
            phone_number=f"60{random.randint(0, 9)}{''.join([str(random.randint(0, 9)) for _ in range(6)])}",
            country=random.choice(countries),
            city=random.choice(cities),
            subscription_type=random.choice(subscription_types),
            email_verified=random.choice([True, False]),
            preferred_language="es",
            status=UserStatus.ACTIVE,
            books_used_this_month=random.randint(0, 5),
        )
        
        # Configurar suscripción si no es free
        if user.subscription_type != SubscriptionType.FREE:
            user.subscription_start = datetime.utcnow() - timedelta(days=random.randint(1, 365))
            user.subscription_end = user.subscription_start + timedelta(days=30)
        
        user.save()
        users.append(user)
        print(f"Created user: {user.email}")
    
    return users


def create_sample_books(users: List[User], count: int = 20) -> List[BookGeneration]:
    """Crea libros de ejemplo"""
    books = []
    
    sample_books = [
        {
            "title": "Inteligencia Artificial para Principiantes",
            "genre": "Técnico",
            "target_audience": "Principiantes en tecnología",
            "tone": "Educativo y accesible",
            "key_topics": "Machine Learning, Deep Learning, Aplicaciones de IA",
        },
        {
            "title": "Cocina Mediterránea Saludable",
            "genre": "Cocina",
            "target_audience": "Entusiastas de la cocina saludable",
            "tone": "Práctico y motivador",
            "key_topics": "Recetas saludables, Ingredientes mediterráneos, Nutrición",
        },
        {
            "title": "Mindfulness en la Vida Cotidiana",
            "genre": "Autoayuda",
            "target_audience": "Personas que buscan bienestar",
            "tone": "Calmado y reflexivo",
            "key_topics": "Meditación, Reducción del estrés, Mindfulness",
        },
        {
            "title": "Emprendimiento Digital",
            "genre": "Negocios",
            "target_audience": "Aspirantes a emprendedores",
            "tone": "Motivador y práctico",
            "key_topics": "Startups, Marketing digital, Estrategias de negocio",
        },
        {
            "title": "Historia del Arte Moderno",
            "genre": "Arte",
            "target_audience": "Estudiantes y aficionados al arte",
            "tone": "Académico pero accesible",
            "key_topics": "Movimientos artísticos, Artistas famosos, Evolución del arte",
        },
        {
            "title": "Jardinería Urbana",
            "genre": "Hogar y jardín",
            "target_audience": "Habitantes de la ciudad",
            "tone": "Práctico y esperanzador",
            "key_topics": "Plantas de interior, Huertos urbanos, Sostenibilidad",
        },
        {
            "title": "Filosofía para la Vida Moderna",
            "genre": "Filosofía",
            "target_audience": "Personas reflexivas",
            "tone": "Profundo pero comprensible",
            "key_topics": "Filosofía práctica, Ética, Sentido de la vida",
        },
        {
            "title": "Cuentos para Dormir",
            "genre": "Infantil",
            "target_audience": "Niños de 3-8 años",
            "tone": "Tierno y educativo",
            "key_topics": "Valores, Imaginación, Aventuras",
        },
        {
            "title": "Finanzas Personales",
            "genre": "Finanzas",
            "target_audience": "Adultos jóvenes",
            "tone": "Práctico y claro",
            "key_topics": "Ahorro, Inversión, Presupuestos",
        },
        {
            "title": "Viajes por América Latina",
            "genre": "Viajes",
            "target_audience": "Viajeros aventureros",
            "tone": "Inspirador y descriptivo",
            "key_topics": "Destinos, Cultura, Experiencias",
        },
    ]
    
    statuses = [BookStatus.COMPLETED, BookStatus.PROCESSING, BookStatus.FAILED, BookStatus.QUEUED]
    
    for i in range(min(count, len(sample_books) * 2)):
        book_data = sample_books[i % len(sample_books)]
        user = random.choice(users)
        
        book = BookGeneration(
            user_id=user.id,
            title=book_data["title"] + f" {i+1}" if i >= len(sample_books) else book_data["title"],
            genre=book_data["genre"],
            target_audience=book_data["target_audience"],
            tone=book_data["tone"],
            key_topics=book_data["key_topics"],
            chapter_count=random.randint(5, 15),
            page_count=random.randint(30, 200),
            language="es",
            status=random.choice(statuses),
            priority=random.randint(0, 5),
            prompt_tokens=random.randint(1000, 5000),
            completion_tokens=random.randint(10000, 50000),
            thinking_tokens=random.randint(500, 2000),
            estimated_cost=round(random.uniform(0.5, 5.0), 4),
            final_pages=random.randint(30, 200),
            final_words=random.randint(5000, 50000),
        )
        
        # Configurar timestamps según el estado
        if book.status in [BookStatus.COMPLETED, BookStatus.FAILED]:
            book.started_at = datetime.utcnow() - timedelta(minutes=random.randint(5, 60))
            book.completed_at = book.started_at + timedelta(minutes=random.randint(1, 30))
        elif book.status == BookStatus.PROCESSING:
            book.started_at = datetime.utcnow() - timedelta(minutes=random.randint(1, 10))
        
        # Configurar rutas de archivos para libros completados
        if book.status == BookStatus.COMPLETED:
            book.file_paths = {
                "pdf": f"/storage/books/{book.uuid}.pdf",
                "epub": f"/storage/books/{book.uuid}.epub",
                "docx": f"/storage/books/{book.uuid}.docx",
            }
        
        book.save()
        books.append(book)
        print(f"Created book: {book.title} for {user.email}")
    
    return books


def create_sample_subscriptions_and_payments(users: List[User]) -> None:
    """Crea suscripciones y pagos de ejemplo"""
    payment_methods = [PaymentMethod.PAYPAL, PaymentMethod.MERCADOPAGO, PaymentMethod.CREDIT_CARD]
    
    for user in users:
        if user.subscription_type != SubscriptionType.FREE:
            # Crear suscripción
            subscription = Subscription(
                user_id=user.id,
                plan_type=user.subscription_type,
                status=PaymentStatus.COMPLETED,
                current_period_start=user.subscription_start,
                current_period_end=user.subscription_end,
            )
            subscription.save()
            
            # Crear pago
            plan_details = user.subscription_plan
            payment = Payment(
                user_id=user.id,
                subscription_id=subscription.id,
                amount=plan_details.get("price", 0),
                currency="USD",
                status=PaymentStatus.COMPLETED,
                payment_method=random.choice(payment_methods),
                payment_provider=random.choice(["PayPal", "MercadoPago", "Stripe"]),
                provider_payment_id=f"pay_{random.randint(100000, 999999)}",
                description=f"Suscripción {subscription.plan_type.value}",
                processed_at=subscription.current_period_start,
            )
            payment.save()
            
            print(f"Created subscription and payment for {user.email}")


def create_sample_downloads(books: List[BookGeneration]) -> None:
    """Crea descargas de ejemplo"""
    formats = [BookFormat.PDF, BookFormat.EPUB, BookFormat.DOCX]
    
    completed_books = [book for book in books if book.status == BookStatus.COMPLETED]
    
    for book in completed_books:
        # Crear algunas descargas aleatorias
        for _ in range(random.randint(1, 5)):
            chosen_format = random.choice(formats)
            download = BookDownload(
                user_id=book.user_id,
                book_id=book.id,
                format=chosen_format,
                file_path=f"/storage/books/{book.uuid}.{chosen_format.value}",
                file_size=random.randint(1024*1024, 10*1024*1024),  # 1MB - 10MB
                download_count=random.randint(1, 10),
                last_downloaded_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            )
            download.save()


def create_sample_logs(users: List[User]) -> None:
    """Crea logs de ejemplo"""
    actions = [
        "user_login", "user_logout", "book_generated", "book_downloaded",
        "subscription_created", "payment_processed", "password_reset",
        "email_sent", "api_request", "system_maintenance"
    ]
    
    levels = [LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR]
    
    for _ in range(50):
        user = random.choice(users) if random.random() > 0.3 else None
        
        log = SystemLog(
            user_id=user.id if user else None,
            action=random.choice(actions),
            level=random.choice(levels),
            details={
                "ip_address": f"192.168.1.{random.randint(1, 255)}",
                "user_agent": "Mozilla/5.0 (compatible; Buko AI)",
                "additional_info": f"Sample log entry {random.randint(1, 1000)}"
            },
            execution_time=random.randint(50, 2000),
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
        )
        log.save()


def create_sample_referrals(users: List[User]) -> None:
    """Crea referidos de ejemplo"""
    for _ in range(5):
        if len(users) >= 2:
            referrer = random.choice(users)
            referred = random.choice([u for u in users if u.id != referrer.id])
            
            referral = Referral(
                referrer_id=referrer.id,
                referred_id=referred.id,
                referral_code=f"REF{random.randint(1000, 9999)}",
                commission_rate=0.1,
                commission_earned=round(random.uniform(0, 50), 2),
                commission_paid=round(random.uniform(0, 25), 2),
                status="active",
            )
            referral.save()
            
            print(f"Created referral: {referrer.email} -> {referred.email}")


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Inicializar base de datos con datos de prueba")
    parser.add_argument("--environment", choices=["development", "staging", "production"], 
                        default="development", help="Entorno de ejecución")
    parser.add_argument("--users", type=int, default=10, help="Número de usuarios a crear")
    parser.add_argument("--books", type=int, default=20, help="Número de libros a crear")
    parser.add_argument("--clean", action="store_true", help="Limpiar base de datos antes de crear")
    
    args = parser.parse_args()
    
    # Crear aplicación
    app = create_app(args.environment)
    
    with app.app_context():
        print(f"Inicializando base de datos para entorno: {args.environment}")
        
        # Limpiar base de datos si se solicita
        if args.clean:
            print("Limpiando base de datos...")
            db.drop_all()
        
        # Crear todas las tablas
        print("Creando tablas...")
        db.create_all()
        
        # Crear datos por defecto
        print("Creando datos por defecto...")
        from app.models import create_default_data
        create_default_data()
        
        # Crear datos de ejemplo solo en desarrollo
        if args.environment == "development":
            print("Creando datos de ejemplo...")
            
            # Crear usuarios
            users = create_sample_users(args.users)
            
            # Crear libros
            books = create_sample_books(users, args.books)
            
            # Crear suscripciones y pagos
            create_sample_subscriptions_and_payments(users)
            
            # Crear descargas
            create_sample_downloads(books)
            
            # Crear logs
            create_sample_logs(users)
            
            # Crear referidos
            create_sample_referrals(users)
            
            print(f"\n✅ Base de datos inicializada exitosamente!")
            print(f"   - Usuarios creados: {len(users)}")
            print(f"   - Libros creados: {len(books)}")
            print(f"   - Plantillas de email: {EmailTemplate.query.count()}")
            print(f"   - Logs del sistema: {SystemLog.query.count()}")
            print(f"   - Referidos: {Referral.query.count()}")
            
        else:
            print("✅ Base de datos de producción inicializada con datos básicos")
        
        # Mostrar estadísticas
        from app.models import get_database_statistics
        stats = get_database_statistics()
        
        print("\n📊 Estadísticas de la base de datos:")
        print(f"   - Total usuarios: {stats['users']['total']}")
        print(f"   - Total libros: {stats['books']['total']}")
        print(f"   - Total suscripciones: {stats['subscriptions']['total']}")
        print(f"   - Total pagos: {stats['payments']['total']}")
        print(f"   - Ingresos totales: ${stats['payments']['total_revenue']:.2f}")


if __name__ == "__main__":
    main()