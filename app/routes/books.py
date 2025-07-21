"""
Rutas para generación de libros con IA.
"""
from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.book_generation import BookGeneration, BookStatus
from app.models.subscription import Subscription
from app.services.claude_service import ClaudeService
from app import db, cache
from app.utils.decorators import subscription_required
import json
from datetime import datetime, timezone

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
        {'id': 'pt', 'name': 'Portugués', 'flag': '🇵🇹'},
        {'id': 'fr', 'name': 'Francés', 'flag': '🇫🇷'}
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
    
    # Calcular páginas efectivas basado en tamaño y espaciado
    base_pages = {
        'short': 75,
        'medium': 150,
        'long': 250
    }
    
    # Factores de ajuste por tamaño de página (relativo a Letter)
    page_size_factors = {
        'pocket': 0.5,   # Pocket (como Kindle) - mucho menos contenido
        'A5': 0.65,      # A5 libro de bolsillo
        'B5': 0.8,       # B5 tamaño intermedio
        'letter': 1.0    # Letter es la referencia máxima
    }
    
    # Factores de ajuste por interlineado
    line_spacing_factors = {
        'single': 1.0,   # Más contenido por página
        'medium': 0.8,   # 20% menos contenido
        'double': 0.6    # 40% menos contenido
    }
    
    # Calcular páginas ajustadas
    length = data.get('length', 'medium')
    page_size = data.get('pageSize', 'A4')
    line_spacing = data.get('lineSpacing', 'medium')
    
    effective_pages = int(
        base_pages.get(length, 150) * 
        page_size_factors.get(page_size, 1.0) * 
        line_spacing_factors.get(line_spacing, 0.8)
    )
    
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
    
    # Enviar a cola de procesamiento
    from app import celery
    task = celery.send_task('app.tasks.book_generation.generate_book_task', args=[book.id], queue='celery')
    
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
    
    return render_template('books/generation_status.html', book=book)


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
    """Vista detallada de un libro."""
    book = BookGeneration.query.filter_by(
        id=book_id, 
        user_id=current_user.id
    ).first_or_404()
    
    return render_template('books/view_book.html', book=book)


@bp.route('/book/<int:book_id>/download/<format>')
@login_required
def download_book(book_id, format):
    """Descarga un libro en el formato especificado."""
    book = BookGeneration.query.filter_by(
        id=book_id, 
        user_id=current_user.id,
        status='completed'
    ).first_or_404()
    
    # Verificar formato válido
    valid_formats = ['pdf', 'epub', 'docx']
    if format not in valid_formats:
        flash('Formato inválido', 'error')
        return redirect(url_for('books.view_book', book_id=book_id))
    
    # TODO: Implementar generación de archivos
    flash(f'Descarga en formato {format.upper()} próximamente', 'info')
    return redirect(url_for('books.view_book', book_id=book_id))


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
            'pages': book.final_pages or book.get_estimated_pages(),
            'words': book.final_words or book.get_word_count(),
            'chapters': book.chapter_count or book.get_chapter_count()
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


@bp.route('/<int:book_id>/retry', methods=['POST'])
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
        task = celery.send_task('app.tasks.book_generation.generate_book_task', args=[book_id], queue='celery')
        
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


