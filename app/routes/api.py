"""
Rutas de API (placeholder para futuras épicas).
"""
import asyncio
import logging
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models.book_generation import BookGeneration
from app.services.claude_service import get_claude_service
from app import db

bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)


@bp.route('/status')
def api_status():
    """Status de API."""
    return jsonify({
        'message': 'API system ready',
        'status': 'active',
        'endpoints': ['/regenerate-chapter']
    })


@bp.route('/regenerate-chapter', methods=['POST'])
@login_required
def regenerate_chapter():
    """Regenera un capítulo específico del libro usando Claude AI."""
    try:
        # Validar datos de entrada
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No se recibieron datos'}), 400
        
        book_id = data.get('bookId')
        chapter_id = data.get('chapterId')
        chapter_title = data.get('chapterTitle')
        current_content = data.get('currentContent')
        feedback = data.get('feedback', {})
        
        # Validaciones
        if not all([book_id, chapter_id, chapter_title, current_content]):
            return jsonify({'success': False, 'error': 'Faltan datos requeridos'}), 400
        
        if not all([feedback.get('whatDislike'), feedback.get('whatChange'), feedback.get('howWant')]):
            return jsonify({'success': False, 'error': 'Se requiere feedback completo para la regeneración'}), 400
        
        # Verificar que el libro pertenece al usuario
        book = BookGeneration.query.get(book_id)
        if not book:
            return jsonify({'success': False, 'error': 'Libro no encontrado'}), 404
        
        if book.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'No tienes permisos para editar este libro'}), 403
        
        # Generar el nuevo contenido del capítulo con Claude AI
        claude_service = get_claude_service()
        
        # Llamar al nuevo método de regeneración de capítulos con información del libro
        result = asyncio.run(claude_service.regenerate_chapter_content(
            chapter_content=current_content,
            feedback=feedback,
            book=book
        ))
        
        if not result.get('success') or not result.get('content'):
            error_msg = result.get('error', 'Error al generar contenido con Claude AI')
            return jsonify({'success': False, 'error': error_msg}), 500
        
        new_content = result['content'].strip()
        
        # Actualizar el contenido del libro en la base de datos
        # Aquí reemplazamos el capítulo específico en el contenido completo del libro
        updated_book_content = replace_chapter_in_book_content(
            book.content, 
            chapter_title, 
            new_content
        )
        
        # Guardar el libro actualizado
        book.content = updated_book_content
        db.session.commit()
        
        logger.info(f"Chapter regenerated successfully for book {book_id}, chapter {chapter_id}")
        
        return jsonify({
            'success': True,
            'newContent': new_content,
            'message': 'Capítulo regenerado exitosamente'
        })
        
    except Exception as e:
        logger.error(f"Error regenerating chapter: {str(e)}")
        return jsonify({'success': False, 'error': f'Error interno: {str(e)}'}), 500


def replace_chapter_in_book_content(book_content, chapter_title, new_content):
    """
    Reemplaza un capítulo específico en el contenido completo del libro.
    """
    lines = book_content.split('\n')
    new_lines = []
    in_target_chapter = False
    chapter_found = False
    
    for line in lines:
        # Detectar el inicio del capítulo objetivo
        if line.strip().startswith('##') and chapter_title.lower() in line.lower():
            in_target_chapter = True
            chapter_found = True
            # Agregar el nuevo contenido completo
            new_lines.extend(new_content.split('\n'))
            continue
        
        # Detectar el inicio del siguiente capítulo (salir del capítulo objetivo)
        if in_target_chapter and line.strip().startswith('##') and chapter_title.lower() not in line.lower():
            in_target_chapter = False
        
        # Si no estamos en el capítulo objetivo, mantener la línea original
        if not in_target_chapter:
            new_lines.append(line)
    
    # Si no se encontró el capítulo, agregar el nuevo contenido al final
    if not chapter_found:
        new_lines.extend(['', new_content])
    
    return '\n'.join(new_lines)