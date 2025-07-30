"""
Rutas para generación de libros con IA.
"""
from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from app.models.book_generation import BookGeneration, BookStatus
from app.models.subscription import Subscription
from app.services.claude_service import ClaudeService
from app import db, cache
from app.utils.decorators import subscription_required
from app.utils.page_calculations import calculate_pages_from_words
import json
import os
import mimetypes
import structlog
from datetime import datetime, timezone

logger = structlog.get_logger()

bp = Blueprint('books', __name__)


@bp.route('/generate')
@login_required
def generate():
    """Vista principal del wizard de generación de libros."""
    # Verificar suscripción del usuario
    subscription = current_user.get_active_subscription()
    if not subscription:
        flash('Necesitas una suscripción activa para generar libros.', 'warning')
        return redirect(url_for('main.pricing'))
    
    # Verificar límites mensuales
    if not subscription.can_generate_book():
        flash('Has alcanzado el límite de libros para este mes.', 'error')
        return redirect(url_for('books.my_books'))
    
    # Géneros disponibles
    genres = [
        {'id': 'fiction', 'name': 'Ficción', 'icon': 'book'},
        {'id': 'non_fiction', 'name': 'No Ficción', 'icon': 'graduation-cap'},
        {'id': 'children', 'name': 'Infantil', 'icon': 'child'},
        {'id': 'poetry', 'name': 'Poesía', 'icon': 'feather'},
        {'id': 'technical', 'name': 'Técnico', 'icon': 'laptop'},
        {'id': 'self_help', 'name': 'Autoayuda', 'icon': 'heart'},
        {'id': 'biography', 'name': 'Biografía', 'icon': 'user'},
        {'id': 'history', 'name': 'Historia', 'icon': 'clock'},
        {'id': 'science_fiction', 'name': 'Ciencia Ficción', 'icon': 'rocket'},
        {'id': 'romance', 'name': 'Romance', 'icon': 'heart'},
        {'id': 'mystery', 'name': 'Misterio', 'icon': 'search'},
        {'id': 'fantasy', 'name': 'Fantasía', 'icon': 'magic'}
    ]
    
    # Tonos disponibles
    tones = [
        {'id': 'formal', 'name': 'Formal'},
        {'id': 'casual', 'name': 'Casual'},
        {'id': 'humorous', 'name': 'Humorístico'},
        {'id': 'serious', 'name': 'Serio'},
        {'id': 'inspirational', 'name': 'Inspiracional'},
        {'id': 'educational', 'name': 'Educativo'}
    ]
    
    # Idiomas disponibles
    languages = [
        {'id': 'es', 'name': 'Español', 'flag': '🇪🇸'},
        {'id': 'en', 'name': 'Inglés', 'flag': '🇺🇸'},
        {'id': 'de', 'name': 'Alemán', 'flag': '🇩🇪'}
    ]
    
    return render_template('books/generate.html',
                         genres=genres,
                         tones=tones,
                         languages=languages,
                         subscription=subscription)


@bp.route('/generate/validate', methods=['POST'])
@login_required
@subscription_required()
def validate_step():
    """Validación en tiempo real de cada paso del wizard."""
    data = request.get_json()
    step = data.get('step')
    
    # Validación según el paso
    if step == 1:
        # Validar información básica
        title = data.get('title', '').strip()
        genre = data.get('genre')
        
        errors = []
        if not title:
            errors.append({'field': 'title', 'message': 'El título es requerido'})
        elif len(title) < 3:
            errors.append({'field': 'title', 'message': 'El título debe tener al menos 3 caracteres'})
        elif len(title) > 100:
            errors.append({'field': 'title', 'message': 'El título no puede exceder 100 caracteres'})
            
        if not genre:
            errors.append({'field': 'genre', 'message': 'Debes seleccionar un género'})
            
        return jsonify({'valid': len(errors) == 0, 'errors': errors})
    
    elif step == 2:
        # Validar descripción y audiencia
        description = data.get('description', '').strip()
        audience = data.get('audience')
        
        errors = []
        if not description:
            errors.append({'field': 'description', 'message': 'La descripción es requerida'})
        elif len(description) < 20:
            errors.append({'field': 'description', 'message': 'La descripción debe tener al menos 20 caracteres'})
        elif len(description) > 1000:
            errors.append({'field': 'description', 'message': 'La descripción no puede exceder 1000 caracteres'})
            
        if not audience:
            errors.append({'field': 'audience', 'message': 'Debes especificar la audiencia objetivo'})
            
        return jsonify({'valid': len(errors) == 0, 'errors': errors})
    
    elif step == 3:
        # Validar configuración avanzada
        chapters = data.get('chapters', 10)
        length = data.get('length', 'medium')
        
        errors = []
        try:
            chapters = int(chapters)
            if chapters < 1 or chapters > 50:
                errors.append({'field': 'chapters', 'message': 'El número de capítulos debe estar entre 1 y 50'})
        except:
            errors.append({'field': 'chapters', 'message': 'Número de capítulos inválido'})
            
        if length not in ['short', 'medium', 'long']:
            errors.append({'field': 'length', 'message': 'Longitud inválida'})
            
        return jsonify({'valid': len(errors) == 0, 'errors': errors})
    
    elif step == 4:
        # Validar paso final - revisión y confirmación
        errors = []
        
        # Validar que todos los campos requeridos estén presentes
        required_fields = ['title', 'genre', 'description', 'audience', 'tone', 'language']
        for field in required_fields:
            if not data.get(field):
                errors.append({'field': field, 'message': f'Campo requerido: {field}'})
        
        # Validar nuevos campos
        page_size = data.get('pageSize')
        line_spacing = data.get('lineSpacing')
        
        if not page_size or page_size not in ['pocket', 'A5', 'B5', 'letter']:
            errors.append({'field': 'pageSize', 'message': 'Tamaño de página inválido'})
            
        if not line_spacing or line_spacing not in ['single', 'medium', 'double']:
            errors.append({'field': 'lineSpacing', 'message': 'Interlineado inválido'})
        
        return jsonify({'valid': len(errors) == 0, 'errors': errors})
    
    return jsonify({'valid': False, 'errors': [{'message': 'Paso inválido'}]})


@bp.route('/generate/preview', methods=['POST'])
@login_required
@subscription_required()
def preview_book():
    """Genera un preview del libro basado en los datos ingresados."""
    data = request.get_json()
    
    # Extraer datos del formulario
    title = data.get('title', 'Sin título')
    genre = data.get('genre', 'fiction')
    description = data.get('description', '')
    tone = data.get('tone', 'formal')
    language = data.get('language', 'es')
    chapters = int(data.get('chapters', 10))
    
    # Generar estructura de preview
    preview = {
        'title': title,
        'genre': genre,
        'language': language,
        'estimated_pages': chapters * 15,  # Estimación
        'estimated_words': chapters * 3000,  # Estimación
        'table_of_contents': []
    }
    
    # Generar tabla de contenidos de ejemplo
    for i in range(1, min(chapters + 1, 6)):  # Máximo 5 capítulos en preview
        preview['table_of_contents'].append({
            'number': i,
            'title': f'Capítulo {i}',
            'preview': f'Vista previa del capítulo {i}...'
        })
    
    if chapters > 5:
        preview['table_of_contents'].append({
            'number': '...',
            'title': f'... y {chapters - 5} capítulos más',
            'preview': ''
        })
    
    return jsonify(preview)


@bp.route('/generate/start', methods=['POST'])
@login_required
@subscription_required()
def start_generation():
    """Inicia el proceso de generación del libro."""
    data = request.get_json()
    
    # Validar todos los datos
    required_fields = ['title', 'genre', 'description', 'audience', 'tone', 'language']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Campo requerido: {field}'}), 400
    
    # CÁLCULO SÚPER GENEROSO: Usar máximo del rango + 20% holgura arriba/abajo
    # Rangos prometidos al usuario (pero entregamos MÁS)
    promised_ranges = {
        'short': {
            'promised_min': 50, 'promised_max': 100,
            'generous_target': 100,  # Usar el MÁXIMO como base
            'generous_min': 80,      # 100 * 0.8 = 80 (aún supera promesa de 50)
            'generous_max': 120      # 100 * 1.2 = 120 (20% más que prometido)
        },
        'medium': {
            'promised_min': 100, 'promised_max': 200,
            'generous_target': 200,  # Usar el MÁXIMO como base
            'generous_min': 160,     # 200 * 0.8 = 160 (supera promesa de 100)
            'generous_max': 240      # 200 * 1.2 = 240 (20% más que prometido)
        },
        'long': {
            'promised_min': 200, 'promised_max': 300,
            'generous_target': 300,  # Usar el MÁXIMO como base
            'generous_min': 240,     # 300 * 0.8 = 240 (supera promesa de 200)
            'generous_max': 360      # 300 * 1.2 = 360 (20% más que prometido)
        }
    }
    
    # Factores de ajuste por tamaño de página (SÚPER GENEROSOS - algunos dan más del máximo)
    page_size_factors = {
        'pocket': 0.9,   # Más generoso para pocket
        'A5': 1.0,       # A5 da el máximo completo
        'B5': 1.05,      # B5 da 5% más que el máximo prometido
        'letter': 1.1    # Letter da 10% más que el máximo prometido
    }
    
    # Factores de ajuste por interlineado (SÚPER GENEROSOS)
    line_spacing_factors = {
        'single': 1.1,   # Single da 10% MÁS contenido
        'medium': 1.0,   # Medium da exactamente el target
        'double': 0.95   # Double da solo 5% menos
    }
    
    # Calcular páginas ajustadas
    length = data.get('length', 'medium')
    page_size = data.get('pageSize', 'letter')
    line_spacing = data.get('lineSpacing', 'medium')
    
    # Obtener configuración generosa
    length_config = promised_ranges.get(length, promised_ranges['medium'])
    
    # Calcular páginas usando el MÁXIMO GENEROSO como base
    calculated_pages = int(
        length_config['generous_target'] * 
        page_size_factors.get(page_size, 1.0) * 
        line_spacing_factors.get(line_spacing, 0.95)
    )
    
    # APLICAR RANGO GENEROSO: 20% arriba y abajo del máximo prometido
    effective_pages = max(calculated_pages, length_config['generous_min'])
    effective_pages = min(effective_pages, length_config['generous_max'])
    
    # GARANTÍA FINAL: Nunca menos del mínimo prometido original
    effective_pages = max(effective_pages, length_config['promised_min'])
    
    # Crear registro de generación
    book = BookGeneration(
        user_id=current_user.id,
        title=data['title'],
        genre=data['genre'],
        target_audience=data['audience'],
        tone=data['tone'],
        language=data['language'],
        chapter_count=int(data.get('chapters', 10)),
        page_count=effective_pages,  # Usar páginas calculadas
        format_size=page_size,
        line_spacing=line_spacing,
        additional_instructions=data.get('additional_instructions', ''),
        key_topics=data['description'],  # description mapped to key_topics
        writing_style=data.get('writing_style', 'Professional and engaging'),
        include_toc=data.get('include_toc', True),
        include_introduction=data.get('include_introduction', True),
        include_conclusion=data.get('include_conclusion', True),
        parameters={
            'audience': data['audience'],
            'tone': data['tone'],
            'chapters': int(data.get('chapters', 10)),
            'length': data.get('length', 'medium'),
            'page_size': page_size,
            'line_spacing': line_spacing,
            'effective_pages': effective_pages,
            'description': data['description'],
            'additional_instructions': data.get('additional_instructions', ''),
            'writing_style': data.get('writing_style', 'Professional and engaging')
        },
        status=BookStatus.QUEUED
    )
    
    db.session.add(book)
    db.session.commit()
    
    # Enviar a cola de procesamiento para generar arquitectura (primera etapa)
    from app import celery
    task = celery.send_task('app.tasks.book_generation.generate_book_architecture_task', args=[book.id], queue='book_generation')
    
    # Actualizar con task_id
    book.task_id = task.id
    db.session.commit()
    
    return jsonify({
        'success': True,
        'book_id': book.id,
        'redirect_url': url_for('books.generation_status', book_id=book.id)
    })


@bp.route('/generation/<int:book_id>')
@login_required
def generation_status(book_id):
    """Vista de estado de generación del libro."""
    book = BookGeneration.query.filter_by(
        id=book_id, 
        user_id=current_user.id
    ).first_or_404()
    
    # REDIRECCIÓN AUTOMÁTICA SEGÚN STATUS
    if book.status == BookStatus.ARCHITECTURE_REVIEW:
        logger.info(f"Redirigiendo libro {book_id} a revisión de arquitectura")
        return redirect(url_for('books.review_architecture', book_id=book_id))
    elif book.status == BookStatus.COMPLETED:
        logger.info(f"Redirigiendo libro {book_id} completado a vista de libro")
        return redirect(url_for('books.view_book', book_id=book_id))
    
    # Si está en PROCESSING, PENDING, FAILED - mostrar página de generación
    logger.info(f"Mostrando página de generación para libro {book_id} con status {book.status}")
    
    # Calcular páginas y palabras objetivo
    target_pages = 0
    target_words = 0
    
    # 1. Si tiene arquitectura aprobada, usar esos valores
    if book.architecture:
        target_pages = book.architecture.get('target_pages', 0)
        target_words = book.architecture.get('estimated_words', 0)
    
    # 2. Si no hay arquitectura, calcular desde configuración original del usuario
    if target_pages == 0:
        target_pages = book.page_count or 0
        
    if target_words == 0 and target_pages > 0:
        # Calcular palabras basado en formato
        format_multipliers = {
            'pocket': 220,
            'A5': 250, 
            'B5': 280,
            'letter': 350
        }
        # Usar formato del libro (compatibilidad con nombres de atributo)
        book_format = getattr(book, 'format_size', None) or getattr(book, 'page_size', None) or 'pocket'
        multiplier = format_multipliers.get(book_format, 220)
        target_words = target_pages * multiplier
    
    # Información adicional para el template
    book_info = {
        'target_pages': target_pages,
        'target_words': target_words,
        'has_architecture': bool(book.architecture),
        'architecture_chapters': len(book.architecture.get('structure', {}).get('chapters', [])) if book.architecture else 0
    }
    
    return render_template('books/generation_status.html', book=book, book_info=book_info)


@bp.route('/my-books')
@login_required
def my_books():
    """Lista de libros del usuario."""
    books = BookGeneration.query.filter_by(
        user_id=current_user.id
    ).order_by(BookGeneration.created_at.desc()).all()
    
    return render_template('books/my_books.html', books=books)


@bp.route('/book/<int:book_id>')
@login_required
def view_book(book_id):
    """Vista detallada de un libro con formato profesional compacto."""
    book = BookGeneration.query.filter_by(
        id=book_id, 
        user_id=current_user.id
    ).first_or_404()
    
    # Calcular estadísticas si no existen (para libros completados sin estadísticas)
    if book.status == BookStatus.COMPLETED and book.content:
        if not book.final_pages or not book.final_words:
            # Calcular desde el contenido actual usando formato específico
            content_words = len(book.content.split()) if book.content else 0
            content_pages = calculate_pages_from_words(
                content_words, 
                book.format_size or 'pocket', 
                book.line_spacing or 'medium'
            )
            
            # Actualizar si no existen valores
            if not book.final_words:
                book.final_words = content_words
            if not book.final_pages:
                book.final_pages = content_pages
                
            # Guardar en base de datos
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
    
    # Asegurar valores mínimos para mostrar
    display_pages = book.final_pages or (
        calculate_pages_from_words(
            len(book.content.split()) if book.content else 0,
            book.format_size or 'pocket',
            book.line_spacing or 'medium'
        ) if book.content else 0
    ) or 0
    display_words = book.final_words or (len(book.content.split()) if book.content else 0) or 0
    
    return render_template('books/view_book_compact.html', 
                         book=book,
                         display_pages=display_pages,
                         display_words=display_words)




@bp.route('/book/<int:book_id>/download/<format>')
@login_required
def download_book(book_id, format):
    """Descarga un libro en el formato especificado."""
    book = BookGeneration.query.filter_by(
        id=book_id, 
        user_id=current_user.id,
        status=BookStatus.COMPLETED
    ).first_or_404()
    
    # Verificar formato válido
    valid_formats = ['pdf', 'epub', 'docx', 'txt']
    if format not in valid_formats:
        flash('Formato inválido', 'error')
        return redirect(url_for('books.view_book', book_id=book_id))
    
    # Usar el servicio de exportación estándar
    return _export_and_download(book, format, 'standard')


@bp.route('/book/<int:book_id>/download/<format>/<platform>')
@login_required
def download_book_platform(book_id, format, platform):
    """Descarga un libro en el formato especificado para una plataforma específica."""
    book = BookGeneration.query.filter_by(
        id=book_id, 
        user_id=current_user.id,
        status=BookStatus.COMPLETED
    ).first_or_404()
    
    # Verificar formato válido
    valid_formats = ['pdf', 'epub', 'docx']
    if format not in valid_formats:
        flash('Formato inválido', 'error')
        return redirect(url_for('books.view_book', book_id=book_id))
    
    # Verificar plataforma válida
    valid_platforms = [
        'standard', 'amazon_kdp', 'google_play', 'apple_books', 
        'kobo', 'smashwords', 'gumroad', 'payhip'
    ]
    if platform not in valid_platforms:
        flash('Plataforma inválida', 'error')
        return redirect(url_for('books.view_book', book_id=book_id))
    
    return _export_and_download(book, format, platform)


def _export_and_download(book, format: str, platform: str):
    """Helper function to export and download book."""
    try:
        logger.info("book_download_started", 
                   book_id=book.id, 
                   format=format, 
                   platform=platform)
        
        from app.services.export_service import BookExportService, ExportFormat, ExportPlatform
        
        # Convert string to enum
        export_format = ExportFormat(format)
        export_platform = ExportPlatform(platform)
        
        # Create export service and export book
        export_service = BookExportService()
        file_path = export_service.export_book(book, export_format, export_platform)
        
        if not file_path or not os.path.exists(file_path):
            logger.error("book_export_failed", 
                        book_id=book.id,
                        format=format,
                        platform=platform,
                        file_path=file_path)
            flash('Error al generar el archivo. Por favor, inténtalo de nuevo.', 'error')
            return redirect(url_for('books.view_book', book_id=book.id))
        
        # Convert to absolute path for send_file
        file_path = os.path.abspath(file_path)
        
        # Get filename for download
        platform_suffix = f"_{platform}" if platform != 'standard' else ""
        download_filename = f"{book.title}_{book.id}{platform_suffix}.{format}"
        
        # Clean filename
        import re
        download_filename = re.sub(r'[<>:"/\\|?*]', '_', download_filename)
        
        logger.info("book_download_started", 
                   book_id=book.id,
                   format=format,
                   platform=platform,
                   filename=download_filename)
        
        # Set correct mimetype based on format
        mime_types = {
            'pdf': 'application/pdf',
            'epub': 'application/epub+zip',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'txt': 'text/plain'
        }
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=download_filename,
            mimetype=mime_types.get(format, 'application/octet-stream')
        )
        
    except Exception as e:
        logger.error("book_download_failed", 
                    book_id=book.id,
                    format=format, 
                    platform=platform,
                    error=str(e))
        flash('Error al descargar el archivo. Por favor, inténtalo de nuevo.', 'error')
        return redirect(url_for('books.view_book', book_id=book.id))


# API Endpoints para monitoreo
@bp.route('/api/<int:book_id>/status')
@login_required
def api_book_status(book_id):
    """API endpoint para obtener el estado de un libro."""
    book = BookGeneration.query.filter_by(
        id=book_id,
        user_id=current_user.id
    ).first()
    
    if not book:
        return jsonify({'error': 'Libro no encontrado'}), 404
    
    # Calcular tiempo transcurrido si está en proceso
    elapsed_time = None
    if book.started_at:
        if book.completed_at:
            elapsed_time = (book.completed_at - book.started_at).total_seconds()
        else:
            elapsed_time = (datetime.now(timezone.utc) - book.started_at).total_seconds()
    
    # Force 100% progress for completed books
    progress = getattr(book, 'progress', 0)
    if book.status.value == 'completed':
        progress = 100
    
    # Calcular páginas y palabras objetivo (mismo cálculo que generation_status)
    target_pages = 0
    target_words = 0
    
    # 1. Si tiene arquitectura aprobada, usar esos valores
    if book.architecture:
        target_pages = book.architecture.get('target_pages', 0)
        target_words = book.architecture.get('estimated_words', 0)
    
    # 2. Si no hay arquitectura, calcular desde configuración original del usuario
    if target_pages == 0:
        target_pages = book.page_count or 0
        
    if target_words == 0 and target_pages > 0:
        # Calcular palabras basado en formato
        format_multipliers = {
            'pocket': 220,
            'A5': 250, 
            'B5': 280,
            'letter': 350
        }
        # Usar formato del libro (compatibilidad con nombres de atributo)
        book_format = getattr(book, 'format_size', None) or getattr(book, 'page_size', None) or 'pocket'
        multiplier = format_multipliers.get(book_format, 220)
        target_words = target_pages * multiplier
    
    # Determinar qué valores mostrar según el estado del libro
    if book.status.value == 'completed':
        display_pages = book.final_pages or 0
        display_words = book.final_words or 0
    else:
        display_pages = target_pages
        display_words = target_words
    
    return jsonify({
        'book_id': book.id,
        'status': book.status.value,
        'progress': progress,
        'message': getattr(book, 'current_step', 'Sin mensaje'),
        'error_message': book.error_message,
        'elapsed_time': elapsed_time,
        'created_at': book.created_at.isoformat() if book.created_at else None,
        'started_at': book.started_at.isoformat() if book.started_at else None,
        'completed_at': book.completed_at.isoformat() if book.completed_at else None,
        'final_pages': book.final_pages,
        'final_words': book.final_words,
        'task_id': book.task_id,
        'retry_count': book.retry_count,
        'title': book.title,
        'format_size': book.format_size,
        'line_spacing': book.line_spacing,
        'stats': {
            'pages': display_pages,
            'words': display_words,
            'chapters': book.chapter_count or 0
        }
    })


@bp.route('/api/<int:book_id>/progress')
@login_required  
def api_book_progress(book_id):
    """API endpoint simplificado para progreso del libro."""
    book = BookGeneration.query.filter_by(
        id=book_id,
        user_id=current_user.id
    ).first()
    
    if not book:
        return jsonify({'error': 'Libro no encontrado'}), 404
    
    # Force 100% progress for completed books
    progress = getattr(book, 'progress', 0)
    if book.status.value == 'completed':
        progress = 100
    
    return jsonify({
        'book_id': book.id,
        'status': book.status.value,
        'progress': progress,
        'message': getattr(book, 'current_step', 'Sin mensaje')
    })


@bp.route('/api/<int:book_id>/thinking')
@login_required
def api_book_thinking(book_id):
    """API endpoint para obtener el thinking content de un libro."""
    book = BookGeneration.query.filter_by(
        id=book_id,
        user_id=current_user.id
    ).first()
    
    if not book:
        return jsonify({'error': 'Libro no encontrado'}), 404
    
    return jsonify({
        'book_id': book.id,
        'title': book.title,
        'thinking_content': book.thinking_content or '',
        'thinking_length': len(book.thinking_content) if book.thinking_content else 0,
        'thinking_words': len(book.thinking_content.split()) if book.thinking_content else 0,
        'status': book.status.value
    })


@bp.route('/book/<int:book_id>/retry', methods=['POST'])
@login_required
def retry_book_generation(book_id):
    """Reintenta la generación de un libro fallido."""
    book = BookGeneration.query.filter_by(
        id=book_id,
        user_id=current_user.id
    ).first()
    
    if not book:
        return jsonify({'error': 'Libro no encontrado'}), 404
    
    if book.status != BookStatus.FAILED:
        return jsonify({'error': 'Solo se pueden reintentar libros fallidos'}), 400
    
    try:
        # Reset del libro para reintento
        book.status = BookStatus.QUEUED
        book.error_message = None
        book.started_at = None
        book.completed_at = None
        book.retry_count = getattr(book, 'retry_count', 0)  # Mantener contador actual
        
        db.session.commit()
        
        # Programar la tarea
        from app import celery
        task = celery.send_task('app.tasks.book_generation.generate_book_task', args=[book_id], queue='book_generation')
        
        # Actualizar con task_id
        book.task_id = task.id
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Reintento programado exitosamente',
            'book_id': book.id,
            'task_id': task.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al programar reintento: {str(e)}'}), 500


# RUTAS PARA EL NUEVO FLUJO DE DOS ETAPAS

@bp.route('/architecture/<int:book_id>')
@login_required
def review_architecture(book_id):
    """Vista para revisar y aprobar la arquitectura del libro."""
    book = BookGeneration.query.filter_by(
        id=book_id, 
        user_id=current_user.id
    ).first_or_404()
    
    # Verificar que el libro esté en estado de revisión de arquitectura
    if book.status != BookStatus.ARCHITECTURE_REVIEW:
        flash('Este libro no está en estado de revisión de arquitectura.', 'error')
        return redirect(url_for('books.view_book', book_id=book_id))
    
    # Verificar que tenga arquitectura
    if not book.has_architecture:
        flash('Este libro no tiene arquitectura generada.', 'error')
        return redirect(url_for('books.my_books'))
    
    return render_template('books/review_architecture.html', book=book)


@bp.route('/architecture/<int:book_id>/approve', methods=['POST'])
@login_required
def approve_architecture(book_id):
    """Aprueba la arquitectura del libro e inicia la generación completa."""
    book = BookGeneration.query.filter_by(
        id=book_id, 
        user_id=current_user.id
    ).first_or_404()
    
    # Verificar que el libro esté en estado correcto
    if book.status != BookStatus.ARCHITECTURE_REVIEW:
        return jsonify({'error': 'El libro no está en estado de revisión de arquitectura'}), 400
    
    try:
        data = request.get_json() or {}
        updated_architecture = data.get('architecture')
        
        # VALIDACIÓN CRÍTICA: Verificar que la arquitectura esté completa
        if not updated_architecture:
            return jsonify({'error': 'Arquitectura requerida para aprobación'}), 400
        
        # DEBUG: Log la arquitectura recibida para diagnóstico
        logger.info("architecture_approval_debug", 
                   book_id=book_id,
                   architecture_keys=list(updated_architecture.keys()) if updated_architecture else [],
                   has_title=bool(updated_architecture.get('title')),
                   has_summary=bool(updated_architecture.get('summary')),
                   has_structure=bool(updated_architecture.get('structure')),
                   has_chapters_direct=bool(updated_architecture.get('chapters')),
                   has_structure_chapters=bool(updated_architecture.get('structure', {}).get('chapters')))
            
        # Validar estructura mínima requerida - Compatible con ambos formatos
        validation_errors = []
        
        # Obtener capítulos - pueden estar en structure.chapters O directamente en chapters
        chapters = []
        if updated_architecture.get('structure', {}).get('chapters'):
            # Formato: architecture.structure.chapters
            chapters = updated_architecture['structure']['chapters']
        elif updated_architecture.get('chapters'):
            # Formato: architecture.chapters (nuevo formato)
            chapters = updated_architecture['chapters']
        else:
            validation_errors.append('Capítulos del libro faltantes')
            
        if not chapters or len(chapters) == 0:
            validation_errors.append('Debe haber al menos un capítulo')
            
        if not updated_architecture.get('title'):
            validation_errors.append('Título del libro faltante')
            
        if not updated_architecture.get('summary'):
            validation_errors.append('Descripción del libro faltante')
            
        # Validar que cada capítulo tenga la información mínima
        for i, chapter in enumerate(chapters):
            if not chapter.get('title'):
                validation_errors.append(f'Capítulo {i+1} no tiene título')
            if not chapter.get('summary'):
                validation_errors.append(f'Capítulo {i+1} no tiene resumen')
                
        if validation_errors:
            logger.warning("architecture_validation_failed",
                         book_id=book_id,
                         validation_errors=validation_errors,
                         chapters_found=len(chapters),
                         title_present=bool(updated_architecture.get('title')),
                         summary_present=bool(updated_architecture.get('summary')))
            return jsonify({
                'error': 'Arquitectura incompleta',
                'validation_errors': validation_errors
            }), 400
            
        # Log para verificar arquitectura antes de aprobar
        from app.utils.logging import log_system_event
        
        # Obtener introduction y conclusion - pueden estar en structure O directamente
        has_introduction = bool(
            updated_architecture.get('structure', {}).get('introduction') or 
            updated_architecture.get('introduction')
        )
        has_conclusion = bool(
            updated_architecture.get('structure', {}).get('conclusion') or 
            updated_architecture.get('conclusion')
        )
        
        log_system_event(
            user_id=current_user.id,
            action="architecture_approval_validation",
            details={
                "book_id": book_id,
                "chapters_count": len(chapters),
                "characters_count": len(updated_architecture.get('characters', [])),
                "special_sections_count": len(updated_architecture.get('special_sections', [])),
                "has_introduction": has_introduction,
                "has_conclusion": has_conclusion,
                "target_pages": updated_architecture.get('target_pages'),
                "estimated_words": updated_architecture.get('estimated_words'),
                "architecture_format": "nested" if updated_architecture.get('structure') else "flat"
            }
        )
        
        # Aprobar la arquitectura (con modificaciones si las hay)
        book.approve_architecture(updated_architecture)
        
        # Programar la tarea de generación completa
        from app import celery
        task = celery.send_task('app.tasks.book_generation.generate_book_task', args=[book.id], queue='book_generation')
        
        # Actualizar con task_id
        book.task_id = task.id
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Arquitectura aprobada. Iniciando generación completa del libro.',
            'book_id': book.id,
            'redirect_url': url_for('books.generation_status', book_id=book.id)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al aprobar arquitectura: {str(e)}'}), 500


@bp.route('/architecture/<int:book_id>/edit', methods=['POST'])
@login_required
def edit_architecture(book_id):
    """Permite editar la arquitectura del libro."""
    book = BookGeneration.query.filter_by(
        id=book_id, 
        user_id=current_user.id
    ).first_or_404()
    
    # Verificar que el libro esté en estado correcto
    if book.status != BookStatus.ARCHITECTURE_REVIEW:
        return jsonify({'error': 'El libro no está en estado de revisión de arquitectura'}), 400
    
    try:
        data = request.get_json()
        updated_architecture = data.get('architecture')
        
        if not updated_architecture:
            return jsonify({'error': 'Arquitectura requerida'}), 400
        
        # Actualizar la arquitectura sin aprobar aún
        book.architecture = updated_architecture
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Arquitectura actualizada exitosamente.'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al actualizar arquitectura: {str(e)}'}), 500


@bp.route('/api/<int:book_id>/architecture')
@login_required
def api_get_architecture(book_id):
    """API endpoint para obtener la arquitectura de un libro."""
    book = BookGeneration.query.filter_by(
        id=book_id,
        user_id=current_user.id
    ).first()
    
    if not book:
        return jsonify({'error': 'Libro no encontrado'}), 404
    
    return jsonify({
        'book_id': book.id,
        'title': book.title,
        'status': book.status.value,
        'has_architecture': book.has_architecture,
        'is_architecture_approved': book.is_architecture_approved,
        'architecture': book.architecture,
        'architecture_approved_at': book.architecture_approved_at.isoformat() if book.architecture_approved_at else None,
        'created_at': book.created_at.isoformat() if book.created_at else None
    })


@bp.route('/architecture/help')
@bp.route('/architecture/help/<int:book_id>')
def architecture_help(book_id=None):
    """Página de ayuda para la revisión, edición y aprobación de arquitectura."""
    return render_template('books/architecture_help.html', book_id=book_id)


@bp.route('/architecture/<int:book_id>/regenerate', methods=['POST'])
@login_required
def regenerate_architecture(book_id):
    """Regenera la arquitectura del libro basado en feedback del usuario."""
    book = BookGeneration.query.filter_by(
        id=book_id, 
        user_id=current_user.id
    ).first_or_404()
    
    # Verificar que el libro esté en estado correcto
    if book.status != BookStatus.ARCHITECTURE_REVIEW:
        return jsonify({'error': 'El libro no está en estado de revisión de arquitectura'}), 400
    
    try:
        data = request.get_json()
        feedback_what = data.get('feedback_what', '').strip()
        feedback_how = data.get('feedback_how', '').strip()
        current_architecture = data.get('current_architecture', {})
        
        # Validar feedback
        if not feedback_what or not feedback_how:
            return jsonify({'error': 'Se requiere feedback completo'}), 400
            
        if len(feedback_what) < 20 or len(feedback_how) < 20:
            return jsonify({'error': 'El feedback debe ser más detallado (mínimo 20 caracteres cada campo)'}), 400
        
        # Guardar feedback en la base de datos para estadísticas usando el método del modelo
        book.add_regeneration_feedback(feedback_what, feedback_how, current_architecture)
        
        # Log del evento
        from app.utils.logging import log_system_event
        log_system_event(
            user_id=current_user.id,
            action="architecture_regeneration_requested",
            details={
                "book_id": book_id,
                "feedback_what_length": len(feedback_what),
                "feedback_how_length": len(feedback_how),
                "has_current_architecture": bool(current_architecture),
                "regeneration_count": book.regeneration_count
            }
        )
        
        # Programar tarea de regeneración de arquitectura
        from app import celery
        task = celery.send_task(
            'app.tasks.book_generation.regenerate_book_architecture_task', 
            args=[book_id, feedback_what, feedback_how, current_architecture],
            queue='book_generation'
        )
        
        # Actualizar estado del libro
        book.status = BookStatus.PROCESSING
        book.task_id = task.id
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Regeneración de arquitectura iniciada',
            'task_id': task.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al iniciar regeneración: {str(e)}'}), 500


@bp.route('/book/<int:book_id>/reject', methods=['DELETE'])
@login_required
def reject_book(book_id):
    """Rechaza y elimina completamente un libro."""
    book = BookGeneration.query.filter_by(
        id=book_id, 
        user_id=current_user.id
    ).first_or_404()
    
    try:
        # Log del evento antes de eliminar
        from app.utils.logging import log_system_event
        log_system_event(
            user_id=current_user.id,
            action="book_rejected_and_deleted",
            details={
                "book_id": book_id,
                "title": book.title,
                "status": book.status.value,
                "had_architecture": book.has_architecture
            }
        )
        
        # Cancelar tarea si está en proceso
        if book.task_id:
            try:
                from app import celery
                celery.control.revoke(book.task_id, terminate=True)
            except Exception as task_error:
                # Log pero continuar con la eliminación
                print(f"Error canceling task {book.task_id}: {task_error}")
        
        # Eliminar el libro de la base de datos
        db.session.delete(book)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Libro eliminado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al eliminar libro: {str(e)}'}), 500


@bp.route('/book/<int:book_id>/formatting-viewer')
@login_required
def formatting_viewer(book_id):
    """Visor profesional de formateo de libros mejorado."""
    try:
        logger.info(f"Acceso al visor de formateo profesional para libro {book_id}, usuario {current_user.id}")
        
        # Obtener el libro
        book = BookGeneration.query.filter_by(
            id=book_id, 
            user_id=current_user.id
        ).first_or_404()
        
        logger.info(f"Libro encontrado: {book.title}, estado: {book.status}")
        
        # DEBUG: Logs detallados para debuggear el problema de redirect
        logger.info(f"DEBUG - Estado del libro: {book.status}")
        logger.info(f"DEBUG - book.status == BookStatus.COMPLETED: {book.status == BookStatus.COMPLETED}")
        logger.info(f"DEBUG - Tiene book.content: {bool(book.content)}")
        logger.info(f"DEBUG - Tiene book.content_html: {bool(book.content_html)}")
        if book.content:
            logger.info(f"DEBUG - Longitud book.content: {len(book.content)}")
        if book.content_html:
            logger.info(f"DEBUG - Longitud book.content_html: {len(book.content_html)}")
        
        # Verificar que el libro esté completado
        if book.status != BookStatus.COMPLETED:
            logger.warning(f"REDIRECT CAUSA 1: Libro {book_id} no completado, estado: {book.status}")
            flash('El libro debe estar completado para acceder al visor de formateo.', 'warning')
            return redirect(url_for('books.view_book', book_id=book_id))
        
        # Verificar que tenga contenido
        if not book.content and not book.content_html:
            logger.warning(f"REDIRECT CAUSA 2: Libro {book_id} sin contenido")
            flash('El libro no tiene contenido para formatear.', 'error')
            return redirect(url_for('books.view_book', book_id=book_id))
        
        # Usar el servicio de formateo profesional
        try:
            logger.info(f"DEBUG - Iniciando servicio de formateo profesional para libro {book_id}")
            from app.services.professional_formatting_service import (
                ProfessionalFormattingService, 
                ProfessionalFormattingOptions
            )
            
            logger.info(f"DEBUG - Importación exitosa del servicio de formateo")
            formatting_service = ProfessionalFormattingService()
            logger.info(f"DEBUG - Instancia de ProfessionalFormattingService creada")
            
            # Opciones por defecto profesionales  
            default_options = ProfessionalFormattingOptions(
                font_family="Crimson Pro",
                font_size_body=12,
                line_spacing=1.5,
                include_table_of_contents=True,
                include_copyright_page=True,
                include_title_page=True,
                use_professional_typography=True,
                enable_toc_navigation=True,
                enable_index_generation=True,
                enable_bookmarks=True,
                enable_search=True,
                theme="classic",
                optimize_file_size=True,
                include_publisher_info=True
            )
            
            # Formatear para distribución comercial
            logger.info(f"DEBUG - Llamando a format_for_commercial_distribution para libro {book_id}")
            formatting_result = formatting_service.format_for_commercial_distribution(
                book, default_options
            )
            
            logger.info(f"DEBUG - format_for_commercial_distribution completado exitosamente")
            preview_data = formatting_result['preview_data']
            formatted_content = formatting_result.get('formatted_content', '')
            logger.info(f"Formateo profesional generado exitosamente para libro {book_id}")
            
        except Exception as formatting_error:
            logger.error(f"Error en servicio de formateo profesional: {str(formatting_error)}")
            
            # Datos de fallback si el servicio falla
            formatted_content = book.content_html if book.content_html else book.content or ""
            preview_data = {
                'statistics': {
                    'total_elements': 100,
                    'chapters': book.chapter_count or 10,
                    'words_estimated': book.get_word_count(),
                    'index_entries': 0,
                    'toc_entries': 0
                },
                'quality_score': {
                    'percentage': 70,
                    'total_score': 70,
                    'category_scores': {
                        'structure': {'score': 18},
                        'formatting': {'score': 18}, 
                        'navigation': {'score': 17},
                        'commercial': {'score': 17}
                    },
                    'recommendations': ['Error al cargar el servicio de formateo'],
                    'platform_compliance': {},
                    'market_readiness': {'ready_for_market': False}
                },
                'sample_elements': [],
                'platform_settings': {},
                'export_formats': [],
                'estimated_pages': book.page_count or 150
            }
        
        return render_template(
            'books/formatting_viewer_professional.html',
            book=book,
            preview_data=preview_data,
            formatted_content=formatted_content,
            page_title=f"Formateo Profesional - {book.title}"
        )
        
    except Exception as e:
        logger.error(f"ERROR GENERAL EN FORMATTING VIEWER - Libro {book_id}: {str(e)}")
        logger.error(f"REDIRECT CAUSA 3: Excepción general - {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"Traceback completo: {traceback.format_exc()}")
        flash('Error al cargar el visor de formateo. Por favor, inténtalo de nuevo.', 'error')
        return redirect(url_for('books.view_book', book_id=book_id))


@bp.route('/book/<int:book_id>/professional-format', methods=['POST'])
@login_required
def professional_format(book_id):
    """Genera formato profesional del libro."""
    try:
        logger.info(f"Generando formato profesional para libro {book_id}, usuario {current_user.id}")
        
        # Obtener el libro
        book = BookGeneration.query.filter_by(
            id=book_id, 
            user_id=current_user.id
        ).first_or_404()
        
        # Verificar que el libro esté completado
        if book.status != BookStatus.COMPLETED:
            return jsonify({'success': False, 'error': 'El libro debe estar completado'}), 400
        
        # Obtener datos del request
        data = request.get_json()
        platform = data.get('platform', 'universal')
        options = data.get('options', {})
        
        # Usar el servicio de formateo profesional
        from app.services.professional_formatting_service import (
            ProfessionalFormattingService, 
            ProfessionalFormattingOptions
        )
        
        formatting_service = ProfessionalFormattingService()
        
        # Construir opciones profesionales desde los datos del formulario
        professional_options = ProfessionalFormattingOptions(
            # Estructura del libro
            include_cover_page=options.get('include_cover_page', True),
            include_title_page=options.get('include_title_page', True),
            include_copyright_page=options.get('include_copyright_page', True),
            include_table_of_contents=options.get('include_table_of_contents', True),
            include_dedication=options.get('include_dedication', False),
            include_acknowledgments=options.get('include_acknowledgments', False),
            include_prologue=options.get('include_prologue', False),
            include_epilogue=options.get('include_epilogue', False),
            include_about_author=options.get('include_about_author', True),
            include_index=options.get('include_index', False),
            
            # Tipografía
            font_family=options.get('font_family', 'Crimson Pro'),
            font_size_body=int(options.get('font_size_body', 12)),
            line_spacing=float(options.get('line_spacing', 1.5)),
            paragraph_spacing=float(options.get('paragraph_spacing', 6.0)),
            
            # Características comerciales
            include_isbn=options.get('include_isbn', ''),
            theme=options.get('theme', 'classic'),
            enable_toc_navigation=options.get('enable_toc_navigation', True),
            enable_index_generation=options.get('enable_index_generation', True),
            enable_bookmarks=options.get('enable_bookmarks', True),
            enable_search=options.get('enable_search', True),
            optimize_file_size=options.get('optimize_file_size', True),
            include_publisher_info=options.get('include_publisher_info', True),
            
            # Estilo profesional
            use_drop_caps=options.get('use_drop_caps', False),
            use_chapter_breaks=options.get('use_chapter_breaks', True),
            use_headers_footers=options.get('use_headers_footers', True),
            use_professional_typography=options.get('use_professional_typography', True),
            highlight_expressions=options.get('highlight_expressions', True),
            emphasize_translations=options.get('emphasize_translations', True)
        )
        
        # Formatear para distribución comercial
        formatting_result = formatting_service.format_for_commercial_distribution(
            book, professional_options
        )
        
        # Guardar contenido HTML formateado en el libro
        if formatting_result['export_ready']:
            book.content_html = formatting_result['formatted_content']
            db.session.commit()
            
            logger.info(f"Formato profesional generado y guardado para libro {book_id}")
            
            return jsonify({
                'success': True,
                'message': 'Formato profesional generado exitosamente',
                'quality_score': formatting_result['quality_analysis']['percentage'],
                'export_ready': formatting_result['export_ready'],
                'formats_available': [f['format'] for f in formatting_result['preview_data']['export_formats']]
            })
        else:
            return jsonify({
                'success': False,
                'error': 'El libro no cumple los requisitos mínimos para formato comercial',
                'quality_score': formatting_result['quality_analysis']['percentage'],
                'recommendations': formatting_result['quality_analysis']['recommendations']
            }), 400
        
    except Exception as e:
        logger.error(f"Error generando formato profesional para libro {book_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/book/<int:book_id>/formatting-preview', methods=['POST'])
@login_required
def formatting_preview(book_id):
    """Genera vista previa con opciones de formateo personalizadas."""
    try:
        # Obtener el libro
        book = BookGeneration.query.filter_by(
            id=book_id, 
            user_id=current_user.id
        ).first_or_404()
        
        # Obtener opciones de formateo del request
        form_data = request.get_json() or request.form.to_dict()
        
        # Importar servicios
        from app.services.book_formatting_service import (
            BookFormattingService, 
            FormattingOptions, 
            FormattingPlatform
        )
        
        # Crear opciones de formateo personalizadas
        platform = FormattingPlatform(form_data.get('platform', 'universal'))
        
        custom_options = FormattingOptions(
            platform=platform,
            include_cover_page=form_data.get('include_cover_page', True),
            include_title_page=form_data.get('include_title_page', True),
            include_copyright_page=form_data.get('include_copyright_page', True),
            include_dedication=form_data.get('include_dedication', False),
            include_acknowledgments=form_data.get('include_acknowledgments', False),
            include_prologue=form_data.get('include_prologue', True),
            include_table_of_contents=form_data.get('include_table_of_contents', True),
            include_introduction=form_data.get('include_introduction', True),
            include_epilogue=form_data.get('include_epilogue', False),
            include_about_author=form_data.get('include_about_author', True),
            include_bibliography=form_data.get('include_bibliography', False),
            include_index=form_data.get('include_index', False),
            
            # Opciones de formato
            font_family=form_data.get('font_family', 'Times New Roman'),
            font_size_body=int(form_data.get('font_size_body', 12)),
            line_spacing=float(form_data.get('line_spacing', 1.5)),
            paragraph_spacing=float(form_data.get('paragraph_spacing', 6.0)),
            first_line_indent=float(form_data.get('first_line_indent', 12.0)),
            
            # Opciones de elementos especiales
            highlight_expressions=form_data.get('highlight_expressions', True),
            show_phonetic_pronunciation=form_data.get('show_phonetic_pronunciation', True),
            emphasize_translations=form_data.get('emphasize_translations', True),
            number_chapters=form_data.get('number_chapters', True),
            number_sections=form_data.get('number_sections', False),
            
            # Opciones de estilo profesional
            use_drop_caps=form_data.get('use_drop_caps', False),
            use_chapter_breaks=form_data.get('use_chapter_breaks', True),
            use_headers_footers=form_data.get('use_headers_footers', True),
            use_professional_typography=form_data.get('use_professional_typography', True),
        )
        
        # Inicializar servicio y procesar
        formatting_service = BookFormattingService()
        book_structure = formatting_service.analyze_content_structure(book.content or "")
        book_structure.title = book.title
        book_structure.author = "Buko AI Editorial"
        
        # Generar elementos profesionales
        formatted_structure = formatting_service.generate_professional_elements(
            book_structure, custom_options
        )
        
        # Obtener datos de vista previa
        preview_data = formatting_service.get_formatting_preview_data(
            formatted_structure, custom_options
        )
        
        # Verificar que los datos sean serializables
        try:
            import json
            json.dumps(preview_data)  # Test serialization
        except (TypeError, ValueError) as serialize_error:
            logger.error(f"Error de serialización JSON: {str(serialize_error)}")
            # Datos de fallback mínimos
            preview_data = {
                'book_info': {
                    'title': book.title,
                    'platform': custom_options.platform.value,
                    'total_elements': 0
                },
                'formatting_options': {'platform': custom_options.platform.value},
                'elements_sample': [],
                'formatting_quality_score': {'overall_score': 0}
            }
        
        return jsonify({
            "success": True,
            "preview_data": preview_data
        })
        
    except Exception as e:
        logger.error(f"Error generando vista previa de formateo: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


