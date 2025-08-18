"""
Rutas Profesionales para Generación de Documentos Aspose.Words
Sistema de última generación con interfaz profesional y configuración en tiempo real.

Características:
- Configuración dinámica en tiempo real
- Preview instantáneo de cambios
- Algoritmos inteligentes de análisis
- Soporte para cualquier tipo de libro
- Experiencia de usuario excepcional
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from flask import Blueprint, render_template, request, jsonify, send_file, session, flash, redirect, url_for
from flask_login import login_required, current_user

from app.models.book_generation import BookGeneration, BookStatus
from app import db
# Import FREE alternative instead of expensive Aspose.Words
from app.services.free_document_generator import (
    FreeDocumentGenerator,
    DocumentFormat
)
from app.services.aspose_professional_generator import (
    AsposeDocumentConfiguration,
    PageFormat,
    FontFamily,
    TypographySettings,
    BookStructureSettings,
    ExportSettings,
    PageDimensions
)
from app.services.intelligent_content_generator import IntelligentContentGenerator

logger = logging.getLogger(__name__)

bp = Blueprint('professional_aspose', __name__)


@bp.route('/book/<int:book_id>/professional-aspose-viewer')
@login_required
def professional_aspose_viewer(book_id: int):
    """
    Vista principal del generador profesional Aspose.Words
    con configuración en tiempo real y preview dinámico.
    """
    try:
        # Verificar que el libro existe y pertenece al usuario
        book = BookGeneration.query.filter_by(
            id=book_id,
            user_id=current_user.id
        ).first()
        
        if not book:
            flash("Libro no encontrado", "error")
            return redirect(url_for('books.my_books'))
        
        if book.status != BookStatus.COMPLETED:
            flash("El libro debe estar completado para generar documento profesional", "error")
            return redirect(url_for('books.my_books'))
        
        # Realizar análisis inteligente del libro
        content_generator = IntelligentContentGenerator()
        book_analysis = content_generator.analyze_book_content(book)
        
        # CARGA AUTOMÁTICA DE METADATOS (NUEVA FUNCIONALIDAD)
        book_metadata = _load_or_generate_metadata(book)
        
        # Configuración inicial respetando arquitectura aprobada y configuraciones existentes
        initial_config = _generate_intelligent_initial_config(book_analysis, book)
        
        # Preparar datos para el template
        template_data = {
            'book': book,
            'book_metadata': book_metadata,  # METADATOS AUTOMÁTICAMENTE CARGADOS
            'book_analysis': {
                'genre': book_analysis.genre.value,
                'main_themes': book_analysis.main_themes,
                'tone': book_analysis.tone,
                'target_audience': book_analysis.target_audience,
                'language_style': book_analysis.language_style,
                'key_concepts': book_analysis.key_concepts,
                'estimated_reading_level': book_analysis.estimated_reading_level,
                'cultural_context': book_analysis.cultural_context,
                'chapter_count': len(book_analysis.chapter_structure)
            },
            'initial_config': initial_config,
            'available_formats': [format.value for format in PageFormat],
            'available_fonts': [font.value for font in FontFamily],
            'config_json': json.dumps(initial_config, ensure_ascii=False),
            'user_name': _get_user_display_name()
        }
        
        return render_template('books/professional_aspose_viewer_modern.html', **template_data)
        
    except Exception as e:
        logger.error(f"Error en professional_aspose_viewer: {str(e)}")
        flash("Error interno del servidor. Intenta nuevamente.", "error")
        return redirect(url_for('books.my_books'))


@bp.route('/book/<int:book_id>/aspose-config-preview', methods=['POST'])
@login_required
def aspose_config_preview(book_id: int):
    """
    Genera preview dinámico basado en la configuración actual.
    Respuesta rápida para configuración en tiempo real.
    """
    try:
        # Verificar libro
        book = BookGeneration.query.filter_by(
            id=book_id,
            user_id=current_user.id
        ).first()
        
        if not book:
            return jsonify({'success': False, 'error': 'Libro no encontrado'}), 404
        
        # Obtener configuración del request
        config_data = request.get_json()
        if not config_data:
            return jsonify({'success': False, 'error': 'Configuración no válida'}), 400
        
        # Crear configuración Aspose
        aspose_config = _build_aspose_config_from_request(config_data)
        
        # Generar preview usando ALTERNATIVA GRATUITA
        generator = FreeDocumentGenerator()
        preview_file = generator.generate_preview_document(
            book=book,
            config=aspose_config,
            max_pages=5  # Limitar preview para velocidad
        )
        
        # Análisis del preview generado
        preview_analysis = _analyze_preview_document(preview_file)
        
        response_data = {
            'success': True,
            'preview_file': preview_file,
            'preview_url': f'/books/book/{book_id}/aspose-download-preview?file={os.path.basename(preview_file)}',
            'analysis': preview_analysis,
            'config_applied': config_data,
            'generation_time': datetime.now().isoformat(),
            'page_count': preview_analysis.get('estimated_pages', 5),
            'word_count': preview_analysis.get('word_count', 0),
            'estimated_full_pages': preview_analysis.get('estimated_full_pages', 0)
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error generando preview: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error generando preview',
            'details': str(e)
        }), 500


@bp.route('/book/<int:book_id>/aspose-generate-full', methods=['POST'])
@login_required
def aspose_generate_full_document(book_id: int):
    """
    Genera el documento completo con la configuración especificada.
    """
    try:
        # Verificar libro
        book = BookGeneration.query.filter_by(
            id=book_id,
            user_id=current_user.id
        ).first()
        
        if not book:
            return jsonify({'success': False, 'error': 'Libro no encontrado'}), 404
        
        # Obtener configuración
        config_data = request.get_json()
        if not config_data:
            return jsonify({'success': False, 'error': 'Configuración no válida'}), 400
        
        # Crear configuración Aspose
        aspose_config = _build_aspose_config_from_request(config_data)
        
        # Generar documento completo usando ALTERNATIVA GRATUITA
        generator = FreeDocumentGenerator()
        full_document_file = generator.generate_professional_document(
            book=book,
            config=aspose_config,
            format=DocumentFormat.DOCX  # Usar formato gratuito
        )
        
        # Análisis del documento final
        document_analysis = _analyze_final_document(full_document_file)
        
        response_data = {
            'success': True,
            'document_file': full_document_file,
            'download_url': f'/books/book/{book_id}/aspose-download-full?file={os.path.basename(full_document_file)}',
            'analysis': document_analysis,
            'config_used': config_data,
            'generation_completed_at': datetime.now().isoformat(),
            'file_size_mb': document_analysis.get('file_size_mb', 0),
            'total_pages': document_analysis.get('total_pages', 0),
            'estimated_reading_time': document_analysis.get('estimated_reading_time', 0)
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error generando documento completo: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error generando documento completo',
            'details': str(e)
        }), 500


@bp.route('/book/<int:book_id>/aspose-download-preview')
@login_required
def aspose_download_preview(book_id: int):
    """Descarga archivo de preview"""
    try:
        filename = request.args.get('file')
        if not filename:
            return jsonify({'error': 'Nombre de archivo requerido'}), 400
        
        file_path = f"/tmp/{filename}"
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Archivo no encontrado'}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"preview_{filename}",
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        logger.error(f"Error descargando preview: {str(e)}")
        return jsonify({'error': 'Error descargando archivo'}), 500


@bp.route('/book/<int:book_id>/aspose-download-full')
@login_required
def aspose_download_full(book_id: int):
    """Descarga documento completo"""
    try:
        filename = request.args.get('file')
        if not filename:
            return jsonify({'error': 'Nombre de archivo requerido'}), 400
        
        file_path = f"/tmp/{filename}"
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Archivo no encontrado'}), 404
        
        # Nombre de descarga personalizado
        book = BookGeneration.query.get(book_id)
        safe_title = "".join(c for c in book.title if c.isalnum() or c in (' ', '-', '_')).strip()
        download_name = f"{safe_title}_Profesional.docx"
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=download_name,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        logger.error(f"Error descargando documento: {str(e)}")
        return jsonify({'error': 'Error descargando archivo'}), 500


@bp.route('/book/<int:book_id>/aspose-intelligent-analysis', methods=['POST'])
@login_required
def aspose_intelligent_analysis(book_id: int):
    """
    Proporciona análisis inteligente y recomendaciones de configuración
    basadas en el contenido del libro.
    """
    try:
        book = BookGeneration.query.filter_by(
            id=book_id,
            user_id=current_user.id
        ).first()
        
        if not book:
            return jsonify({'success': False, 'error': 'Libro no encontrado'}), 404
        
        # Realizar análisis inteligente completo
        content_generator = IntelligentContentGenerator()
        book_analysis = content_generator.analyze_book_content(book)
        
        # Generar recomendaciones inteligentes
        recommendations = _generate_intelligent_recommendations(book_analysis)
        
        # Análisis de contenido avanzado
        content_insights = _generate_content_insights(book, book_analysis)
        
        response_data = {
            'success': True,
            'analysis': {
                'genre': book_analysis.genre.value,
                'main_themes': book_analysis.main_themes,
                'tone': book_analysis.tone,
                'target_audience': book_analysis.target_audience,
                'language_style': book_analysis.language_style,
                'key_concepts': book_analysis.key_concepts,
                'estimated_reading_level': book_analysis.estimated_reading_level,
                'cultural_context': book_analysis.cultural_context,
                'chapter_structure': [
                    {
                        'number': ch.get('number', i+1),
                        'title': ch.get('title', f'Capítulo {i+1}'),
                        'word_count': ch.get('word_count', 0),
                        'content_preview': ch.get('content_preview', '')[:100] + '...'
                    }
                    for i, ch in enumerate(book_analysis.chapter_structure[:10])
                ]
            },
            'recommendations': recommendations,
            'content_insights': content_insights,
            'suggested_configurations': _get_suggested_configurations(book_analysis, book)
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error en análisis inteligente: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error en análisis inteligente',
            'details': str(e)
        }), 500


@bp.route('/book/<int:book_id>/aspose-configuration-presets')
@login_required
def aspose_configuration_presets(book_id: int):
    """
    Proporciona presets de configuración profesional 
    optimizados para diferentes tipos de publicación.
    """
    try:
        book = BookGeneration.query.get(book_id)
        if not book:
            return jsonify({'error': 'Libro no encontrado'}), 404
        
        # Generar presets basados en análisis del libro
        content_generator = IntelligentContentGenerator()
        book_analysis = content_generator.analyze_book_content(book)
        
        presets = {
            'print_ready': _create_print_ready_preset(book_analysis, book),
            'ebook_optimized': _create_ebook_optimized_preset(book_analysis, book),
            'academic_standard': _create_academic_standard_preset(book_analysis, book),
            'commercial_paperback': _create_commercial_paperback_preset(book_analysis, book),
            'luxury_hardcover': _create_luxury_hardcover_preset(book_analysis, book),
            'pocket_edition': _create_pocket_edition_preset(book_analysis, book)
        }
        
        return jsonify({
            'success': True,
            'presets': presets,
            'book_genre': book_analysis.genre.value,
            'recommended_preset': _get_recommended_preset(book_analysis)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo presets: {str(e)}")
        return jsonify({'error': 'Error obteniendo configuraciones'}), 500


@bp.route('/book/<int:book_id>/aspose-generate-metadata', methods=['POST'])
@login_required
def aspose_generate_metadata(book_id: int):
    """
    Genera metadatos automáticamente usando Claude AI basándose en la arquitectura aprobada del libro.
    """
    try:
        # Verificar que el libro existe y pertenece al usuario
        book = BookGeneration.query.filter_by(
            id=book_id,
            user_id=current_user.id
        ).first()
        
        if not book:
            return jsonify({'success': False, 'error': 'Libro no encontrado'}), 404
        
        if book.status != BookStatus.COMPLETED:
            return jsonify({'success': False, 'error': 'El libro debe estar completado'}), 400
        
        # Obtener datos del request
        request_data = request.get_json() or {}
        
        # Generar metadatos usando Claude AI
        generated_metadata = _generate_ai_metadata(book, request_data)
        
        if not generated_metadata:
            return jsonify({
                'success': False, 
                'error': 'Error generando metadatos con Claude AI'
            }), 500
        
        # GUARDAR METADATOS EN LA BASE DE DATOS AUTOMÁTICAMENTE
        try:
            from app import db
            
            # Inicializar parameters si no existe
            if not book.parameters:
                book.parameters = {}
            
            # Guardar metadatos generados por IA
            book.parameters['ai_metadata'] = {
                'data': generated_metadata,
                'generated_at': datetime.now().isoformat(),
                'generated_by': 'claude_ai',
                'version': '1.0'
            }
            
            # Actualizar campos directos del libro si están en los metadatos
            if 'description' in generated_metadata:
                book.parameters['description'] = generated_metadata['description']
            
            # Commit a la base de datos
            db.session.commit()
            
            logger.info(f"Metadatos generados y guardados exitosamente para libro {book_id}")
            
        except Exception as save_error:
            logger.error(f"Error guardando metadatos en BD: {str(save_error)}")
            db.session.rollback()
            
            # Aún devolver los metadatos aunque no se hayan guardado
            return jsonify({
                'success': True,
                'metadata': generated_metadata,
                'saved_to_db': False,
                'save_error': str(save_error),
                'generated_at': datetime.now().isoformat()
            })
        
        response_data = {
            'success': True,
            'metadata': generated_metadata,
            'saved_to_db': True,
            'generated_at': datetime.now().isoformat(),
            'based_on': {
                'book_title': book.title,
                'genre': book.genre,
                'architecture_approved': book.architecture_approved_at is not None,
                'content_sample_length': len(str(book.content)[:2000]) if book.content else 0
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error generando metadatos con AI: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno generando metadatos',
            'details': str(e)
        }), 500


@bp.route('/book/<int:book_id>/aspose-save-metadata', methods=['POST'])
@login_required
def aspose_save_metadata(book_id: int):
    """
    Guarda los metadatos generados por Claude AI en el libro de forma permanente.
    """
    try:
        # Verificar que el libro existe y pertenece al usuario
        book = BookGeneration.query.filter_by(
            id=book_id,
            user_id=current_user.id
        ).first()
        
        if not book:
            return jsonify({'success': False, 'error': 'Libro no encontrado'}), 404
        
        if book.status != BookStatus.COMPLETED:
            return jsonify({'success': False, 'error': 'El libro debe estar completado'}), 400
        
        # Obtener metadatos del request
        request_data = request.get_json() or {}
        metadata = request_data.get('metadata', {})
        
        if not metadata:
            return jsonify({'success': False, 'error': 'No se proporcionaron metadatos'}), 400
        
        # Actualizar campos específicos del libro si están disponibles
        updated_fields = []
        
        # Actualizar target_audience si se proporcionó
        if 'target_audience' in metadata and metadata['target_audience']:
            book.target_audience = metadata['target_audience'][:200]  # Respetar límite de campo
            updated_fields.append('target_audience')
        
        # Actualizar key_topics con main_themes si se proporcionó
        if 'main_themes' in metadata and metadata['main_themes']:
            # Combinar con key_topics existentes si los hay
            existing_topics = book.key_topics or ''
            new_themes = ', '.join(metadata['main_themes'])
            book.key_topics = f"{existing_topics}\n\n--- TEMAS IA GENERADOS ---\n{new_themes}".strip()
            updated_fields.append('key_topics')
        
        # Guardar metadatos completos en el campo parameters (JSON)
        import json
        current_params = {}
        if book.parameters:
            current_params = json.loads(book.parameters) if isinstance(book.parameters, str) else book.parameters
        
        # Agregar sección de metadatos IA
        current_params['ai_metadata'] = {
            'subtitle': metadata.get('subtitle', ''),
            'description': metadata.get('description', ''),
            'keywords': metadata.get('keywords', []),
            'categories': metadata.get('categories', []),
            'main_themes': metadata.get('main_themes', []),
            'target_audience': metadata.get('target_audience', ''),
            'generated_at': datetime.now().isoformat(),
            'generated_by': 'claude_ai'
        }
        
        # SQLAlchemy JSON field change detection fix
        book.parameters = current_params
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(book, 'parameters')
        updated_fields.append('parameters')
        
        # Guardar cambios en la base de datos
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Metadatos guardados exitosamente',
            'updated_fields': updated_fields,
            'metadata_saved': {
                'subtitle': metadata.get('subtitle', ''),
                'description_length': len(metadata.get('description', '')),
                'keywords_count': len(metadata.get('keywords', [])),
                'categories_count': len(metadata.get('categories', [])),
                'themes_count': len(metadata.get('main_themes', []))
            },
            'saved_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error guardando metadatos: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno guardando metadatos',
            'details': str(e)
        }), 500


# Funciones auxiliares de configuración y análisis

def _build_aspose_config_from_request(config_data: Dict[str, Any]) -> AsposeDocumentConfiguration:
    """Construye configuración Aspose desde datos del request"""
    
    # Página y formato
    page_format = PageFormat(config_data.get('page_format', 'pocket'))
    
    # Dimensiones personalizadas si aplica
    page_dimensions = None
    if page_format == PageFormat.CUSTOM:
        dims_data = config_data.get('custom_dimensions', {})
        page_dimensions = PageDimensions(
            width=dims_data.get('width', 432),
            height=dims_data.get('height', 648),
            margin_top=dims_data.get('margin_top', 72),
            margin_bottom=dims_data.get('margin_bottom', 72),
            margin_left=dims_data.get('margin_left', 72),
            margin_right=dims_data.get('margin_right', 72)
        )
    
    # Tipografía
    typography = TypographySettings(
        body_font_family=FontFamily(config_data.get('body_font_family', 'Times New Roman')),
        body_font_size=config_data.get('body_font_size', 11.0),
        heading_font_family=FontFamily(config_data.get('heading_font_family', 'Times New Roman')),
        heading_font_size=config_data.get('heading_font_size', 16.0),
        line_spacing=config_data.get('line_spacing', 1.2),
        paragraph_spacing_before=config_data.get('paragraph_spacing_before', 6.0),
        paragraph_spacing_after=config_data.get('paragraph_spacing_after', 6.0),
        first_line_indent=config_data.get('first_line_indent', 18.0),
        use_drop_caps=config_data.get('use_drop_caps', True),
        drop_cap_lines=config_data.get('drop_cap_lines', 3),
        chapter_title_size=config_data.get('chapter_title_size', 18.0),
        use_small_caps_for_headers=config_data.get('use_small_caps_for_headers', True),
        justify_text=config_data.get('justify_text', True)
    )
    
    # Estructura
    structure = BookStructureSettings(
        include_cover_page=config_data.get('include_cover_page', True),
        include_title_page=config_data.get('include_title_page', True),
        include_copyright_page=config_data.get('include_copyright_page', True),
        include_dedication=config_data.get('include_dedication', True),
        include_table_of_contents=config_data.get('include_table_of_contents', True),
        include_prologue=config_data.get('include_prologue', False),
        include_epilogue=config_data.get('include_epilogue', False),
        include_acknowledgments=config_data.get('include_acknowledgments', False),
        include_about_author=config_data.get('include_about_author', True),
        include_bibliography=config_data.get('include_bibliography', False),
        page_numbering_start=config_data.get('page_numbering_start', 1),
        start_chapters_on_odd_page=config_data.get('start_chapters_on_odd_page', True),
        use_headers_footers=config_data.get('use_headers_footers', True)
    )
    
    # Exportación
    export = ExportSettings(
        format=config_data.get('export_format', 'DOCX'),
        include_bookmarks=config_data.get('include_bookmarks', True),
        optimize_for_print=config_data.get('optimize_for_print', True),
        embed_fonts=config_data.get('embed_fonts', False),
        compress_images=config_data.get('compress_images', True),
        quality_level=config_data.get('quality_level', 85)
    )
    
    return AsposeDocumentConfiguration(
        page_format=page_format,
        page_dimensions=page_dimensions,
        typography=typography,
        structure=structure,
        export=export,
        author_name=config_data.get('author_name', ''),
        custom_styles=config_data.get('custom_styles', {})
    )


def _generate_intelligent_initial_config(book_analysis, book: BookGeneration) -> Dict[str, Any]:
    """Genera configuración inicial respetando arquitectura aprobada y configuraciones existentes"""
    
    import json
    
    # PASO 1: Extraer configuraciones inmutables del libro
    book_params = {}
    if book.parameters:
        book_params = json.loads(book.parameters) if isinstance(book.parameters, str) else book.parameters
    
    # PASO 2: Extraer configuraciones de arquitectura aprobada
    approved_structure = {}
    if book.architecture and book.architecture_approved_at:
        arch = json.loads(book.architecture) if isinstance(book.architecture, str) else book.architecture
        approved_structure = {
            'include_table_of_contents': arch.get('include_toc', True),
            'include_introduction': arch.get('include_introduction', True), 
            'include_conclusion': arch.get('include_conclusion', True),
            'target_pages': arch.get('target_pages', book.page_count),
            'chapter_count': arch.get('chapter_count', book.chapter_count)
        }
    
    # PASO 3: Configuraciones INMUTABLES que NO se pueden cambiar
    immutable_config = {
        # RESPETANDO FORMATO YA ELEGIDO EN /books/generate
        'page_format': book.format_size or 'pocket',  # Respeta formato elegido
        
        # RESPETANDO CONFIGURACIONES DE LÍNEA YA ESTABLECIDAS
        'line_spacing': {
            'tight': 1.1,
            'medium': 1.2, 
            'loose': 1.5
        }.get(book.line_spacing, 1.2),
        
        # RESPETANDO ARQUITECTURA APROBADA
        'include_table_of_contents': approved_structure.get('include_table_of_contents', True),
        'include_introduction': approved_structure.get('include_introduction', True),
        'include_conclusion': approved_structure.get('include_conclusion', True),
        
        # RESPETANDO CONFIGURACIONES ESPECÍFICAS DEL LIBRO
        '_locked_format': book.format_size,  # Campo especial para marcar como bloqueado
        '_locked_spacing': book.line_spacing,  # Campo especial para marcar como bloqueado
        '_locked_chapters': book.chapter_count,  # Campo especial para marcar como bloqueado
        '_locked_pages': book.page_count,  # Campo especial para marcar como bloqueado
        '_approved_structure': approved_structure,  # Estructura completa aprobada
    }
    
    # PASO 4: Configuraciones adaptables (solo lo que NO está en conflicto)
    adaptable_config = {
        # Tipografía (adaptable según género, pero respetando restricciones)
        'body_font_family': 'Times New Roman',  # Profesional para educativo
        'body_font_size': 11.0,  # Apropiado para formato pocket
        'heading_font_family': 'Times New Roman',
        'heading_font_size': 16.0,
        'paragraph_spacing_before': 6.0,
        'paragraph_spacing_after': 6.0,
        'first_line_indent': 18.0,
        'use_drop_caps': False,  # Conservador para libro educativo
        'drop_cap_lines': 3,
        'chapter_title_size': 18.0,
        'use_small_caps_for_headers': True,
        'justify_text': True,
        
        # Estructura (respetando arquitectura aprobada)
        'include_cover_page': True,
        'include_title_page': True,
        'include_copyright_page': True,
        'include_dedication': True,
        'include_prologue': False,  # Conservador para libro educativo
        'include_epilogue': False,  # Conservador para libro educativo  
        'include_acknowledgments': False,
        'include_about_author': True,
        'include_bibliography': True,  # Apropiado para libro educativo
        'page_numbering_start': 1,
        'start_chapters_on_odd_page': True,
        'use_headers_footers': True,
        
        # Exportación
        'include_bookmarks': True,
        'optimize_for_print': True,
        'embed_fonts': False,
        'compress_images': True,
        'quality_level': 85,
        
        # Autor
        'author_name': _get_user_display_name()
    }
    
    # PASO 5: Combinar configuraciones inmutables + adaptables
    final_config = {**adaptable_config, **immutable_config}
    
    # PASO 6: Agregar metadatos para el frontend
    final_config.update({
        '_metadata': {
            'locked_fields': ['page_format', 'line_spacing'],  # Campos bloqueados en UI
            'approved_architecture': True,  # Indica que hay arquitectura aprobada
            'source_book_id': book.id,
            'approval_date': book.architecture_approved_at.isoformat() if book.architecture_approved_at else None,
            'original_params': book_params,
            'immutable_reason': f'Configuraciones establecidas en /books/generate y arquitectura aprobada el {book.architecture_approved_at.strftime("%Y-%m-%d") if book.architecture_approved_at else "N/A"}'
        }
    })
    
    return final_config


def _analyze_preview_document(file_path: str) -> Dict[str, Any]:
    """Analiza el documento preview generado"""
    try:
        file_size = os.path.getsize(file_path)
        
        # Análisis básico del archivo
        analysis = {
            'file_size_bytes': file_size,
            'file_size_mb': round(file_size / (1024 * 1024), 2),
            'estimated_pages': 5,  # Preview limitado
            'word_count': 0,  # Se calcularía leyendo el documento
            'estimated_full_pages': 0,  # Estimación para documento completo
            'generation_success': True,
            'quality_score': 85
        }
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error analizando preview: {str(e)}")
        return {'error': str(e), 'generation_success': False}


def _analyze_final_document(file_path: str) -> Dict[str, Any]:
    """Analiza el documento final generado"""
    try:
        file_size = os.path.getsize(file_path)
        
        analysis = {
            'file_size_bytes': file_size,
            'file_size_mb': round(file_size / (1024 * 1024), 2),
            'total_pages': 0,  # Se calcularía leyendo el documento
            'word_count': 0,  # Se calcularía leyendo el documento
            'estimated_reading_time': 0,  # Basado en word_count
            'generation_success': True,
            'quality_score': 90
        }
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error analizando documento final: {str(e)}")
        return {'error': str(e), 'generation_success': False}


def _generate_intelligent_recommendations(book_analysis) -> Dict[str, Any]:
    """Genera recomendaciones inteligentes de configuración"""
    recommendations = {
        'typography': [],
        'structure': [],
        'formatting': [],
        'audience_specific': []
    }
    
    # Recomendaciones tipográficas
    if book_analysis.target_audience == 'children':
        recommendations['typography'].append("Aumentar tamaño de fuente a 12pt para mejor legibilidad")
        recommendations['typography'].append("Usar mayor espaciado de línea (1.4x)")
    
    if book_analysis.genre.value == 'technical':
        recommendations['typography'].append("Considerar fuente monospace para código")
        recommendations['typography'].append("Usar justificación izquierda para mejor lectura técnica")
    
    # Recomendaciones estructurales
    if book_analysis.genre.value in ['educational', 'technical']:
        recommendations['structure'].append("Incluir bibliografía para referencias")
        recommendations['structure'].append("Considerar índice temático al final")
    
    if book_analysis.genre.value == 'fiction':
        recommendations['structure'].append("Incluir prólogo y epílogo")
        recommendations['structure'].append("Usar letras capitales para inicio de capítulos")
    
    # Recomendaciones de formato
    if len(book_analysis.chapter_structure) > 15:
        recommendations['formatting'].append("Considerar formato de libro grande por cantidad de capítulos")
    
    if book_analysis.estimated_reading_level == 'advanced':
        recommendations['formatting'].append("Usar márgenes académicos estándar")
    
    # Recomendaciones específicas de audiencia
    audience_tips = {
        'children': ["Usar formato cuadrado", "Incluir más espacios en blanco"],
        'professionals': ["Formato estándar de negocio", "Incluir tabla de contenidos detallada"],
        'students': ["Formato académico", "Incluir bibliografía y referencias"],
        'elderly': ["Fuente más grande", "Mayor contraste"]
    }
    
    recommendations['audience_specific'] = audience_tips.get(
        book_analysis.target_audience, 
        ["Configuración estándar apropiada"]
    )
    
    return recommendations


def _generate_content_insights(book, book_analysis) -> Dict[str, Any]:
    """Genera insights sobre el contenido del libro"""
    insights = {
        'content_density': 'medium',
        'structural_complexity': 'standard',
        'recommended_layout': 'standard',
        'special_considerations': []
    }
    
    word_count = len(book.content.split())
    
    # Densidad de contenido
    if word_count > 100000:
        insights['content_density'] = 'high'
        insights['special_considerations'].append("Considerar dividir en múltiples volúmenes")
    elif word_count < 30000:
        insights['content_density'] = 'low'
        insights['special_considerations'].append("Usar formato más compacto")
    
    # Complejidad estructural
    chapter_count = len(book_analysis.chapter_structure)
    if chapter_count > 20:
        insights['structural_complexity'] = 'high'
        insights['special_considerations'].append("Incluir índice detallado de capítulos")
    elif chapter_count < 5:
        insights['structural_complexity'] = 'low'
        insights['special_considerations'].append("Considerar secciones en lugar de capítulos")
    
    return insights


def _get_suggested_configurations(book_analysis, book: BookGeneration) -> List[Dict[str, Any]]:
    """Obtiene configuraciones sugeridas respetando arquitectura aprobada"""
    suggestions = []
    
    # Configuración optimizada para el género (respetando configuraciones inmutables)
    suggestions.append({
        'name': f'Optimizado para {book_analysis.genre.value.title()}',
        'description': f'Configuración profesional específica para libros de {book_analysis.genre.value} (respeta configuraciones aprobadas)',
        'config': _generate_intelligent_initial_config(book_analysis, book),
        'recommended': True
    })
    
    # Configuración para impresión (solo ajusta lo que se puede cambiar)
    print_config = _generate_intelligent_initial_config(book_analysis, book).copy()
    print_config.update({
        'optimize_for_print': True,
        'embed_fonts': True,
        'quality_level': 95
        # Nota: NO modificamos page_format ni line_spacing porque están bloqueados
    })
    
    suggestions.append({
        'name': 'Listo para Impresión',
        'description': 'Configuración optimizada para impresión profesional (respeta formato aprobado)',
        'config': print_config,
        'recommended': False
    })
    
    # Configuración de alta calidad (sin cambiar formato)
    quality_config = _generate_intelligent_initial_config(book_analysis, book).copy()
    quality_config.update({
        'body_font_family': 'Garamond',  # Solo tipografía
        'use_small_caps_for_headers': True,
        'quality_level': 95
        # Nota: NO modificamos page_format porque está bloqueado por arquitectura aprobada
    })
    
    suggestions.append({
        'name': 'Alta Calidad Tipográfica',
        'description': 'Configuración con tipografía premium (respeta formato aprobado)',
        'config': quality_config,
        'recommended': False
    })
    
    return suggestions


def _create_print_ready_preset(book_analysis, book: BookGeneration) -> Dict[str, Any]:
    """Crea preset listo para impresión (respeta configuraciones aprobadas)"""
    config = _generate_intelligent_initial_config(book_analysis, book).copy()
    config.update({
        'optimize_for_print': True,
        'embed_fonts': True,
        'quality_level': 95,
        'include_copyright_page': True
        # Nota: NO modificamos page_format porque respeta la arquitectura aprobada
    })
    return config


def _create_ebook_optimized_preset(book_analysis, book: BookGeneration) -> Dict[str, Any]:
    """Crea preset optimizado para ebook (respeta configuraciones aprobadas)"""
    config = _generate_intelligent_initial_config(book_analysis, book).copy()
    config.update({
        'optimize_for_print': False,
        'include_bookmarks': True,
        'compress_images': True,
        'quality_level': 75
    })
    return config


def _create_academic_standard_preset(book_analysis, book: BookGeneration) -> Dict[str, Any]:
    """Crea preset estándar académico (respeta configuraciones aprobadas)"""
    config = _generate_intelligent_initial_config(book_analysis, book).copy()
    config.update({
        # Solo modificamos lo que NO está bloqueado por la arquitectura aprobada
        'body_font_size': 12.0,
        'include_bibliography': True,
        'justify_text': True,
        'use_headers_footers': True
        # Nota: NO modificamos page_format ni line_spacing porque están bloqueados
    })
    return config


def _create_commercial_paperback_preset(book_analysis, book: BookGeneration) -> Dict[str, Any]:
    """Crea preset para paperback comercial (respeta configuraciones aprobadas)"""
    config = _generate_intelligent_initial_config(book_analysis, book).copy()
    config.update({
        # Solo modificamos tipografía, no formato
        'body_font_size': 11.0,
        'use_drop_caps': True,
        'include_cover_page': True,
        'include_about_author': True
        # Nota: NO modificamos page_format porque respeta la configuración aprobada
    })
    return config


def _create_luxury_hardcover_preset(book_analysis, book: BookGeneration) -> Dict[str, Any]:
    """Crea preset para hardcover de lujo (respeta configuraciones aprobadas)"""
    config = _generate_intelligent_initial_config(book_analysis, book).copy()
    config.update({
        # Solo modificamos tipografía y elementos decorativos
        'body_font_family': 'Garamond',
        'body_font_size': 11.5,
        'use_drop_caps': True,
        'use_small_caps_for_headers': True,
        'include_dedication': True,
        'include_acknowledgments': True
        # Nota: NO modificamos page_format porque respeta la arquitectura aprobada
    })
    return config


def _create_pocket_edition_preset(book_analysis, book: BookGeneration) -> Dict[str, Any]:
    """Crea preset para edición de bolsillo (respeta configuraciones aprobadas)"""
    config = _generate_intelligent_initial_config(book_analysis, book).copy()
    config.update({
        # Solo modificamos espaciado fino, no formato general
        'body_font_size': 9.5,
        'first_line_indent': 12.0,
        'paragraph_spacing_before': 3.0,
        'paragraph_spacing_after': 3.0
        # Nota: NO modificamos page_format ni line_spacing porque están bloqueados
    })
    return config


def _get_recommended_preset(book_analysis) -> str:
    """Determina el preset recomendado basado en análisis"""
    if book_analysis.genre.value in ['educational', 'technical']:
        return 'academic_standard'
    elif book_analysis.genre.value == 'fiction':
        return 'commercial_paperback'
    elif book_analysis.target_audience == 'professionals':
        return 'luxury_hardcover'
    else:
        return 'print_ready'


def _get_user_display_name() -> str:
    """Obtiene nombre para mostrar del usuario actual"""
    if current_user.is_authenticated:
        if hasattr(current_user, 'first_name') and hasattr(current_user, 'last_name'):
            if current_user.first_name and current_user.last_name:
                return f"{current_user.first_name} {current_user.last_name}"
            elif current_user.first_name:
                return current_user.first_name
        
        if hasattr(current_user, 'email') and current_user.email:
            return current_user.email.split('@')[0].title()
    
    return "Autor"


def _generate_ai_metadata(book: BookGeneration, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Genera metadatos automáticamente usando Claude AI basándose en la arquitectura aprobada del libro.
    """
    try:
        # Importar el servicio de Claude - USANDO EL MISMO PATRÓN QUE BOOK GENERATION
        from app.services.claude_service import get_claude_service
        import asyncio
        import json
        
        # Preparar datos para Claude AI
        book_data = {
            'title': book.title,
            'genre': book.genre,
            'language': getattr(book, 'language', 'es'),
            'target_audience': getattr(book, 'target_audience', 'general'),
            'content_sample': str(book.content)[:2000] if book.content else ""
        }
        
        # Obtener arquitectura aprobada si existe
        architecture_data = {}
        if book.architecture and book.architecture_approved_at:
            try:
                arch = json.loads(book.architecture) if isinstance(book.architecture, str) else book.architecture
                architecture_data = {
                    'themes': arch.get('themes', []),
                    'tone': arch.get('tone', ''),
                    'perspective': arch.get('perspective', ''),
                    'estimated_words': arch.get('estimated_words', 0),
                    'chapter_count': arch.get('chapter_count', 0),
                    'main_characters': arch.get('characters', [])[:3],  # Primeros 3 personajes
                    'setting': arch.get('setting', {}),
                    'plot_structure': arch.get('plot_structure', {})
                }
            except (json.JSONDecodeError, AttributeError):
                logger.warning(f"Error parseando arquitectura del libro {book.id}")
        
        # Construir prompt específico para metadatos
        prompt = f"""
Basándote en la siguiente información de un libro, genera metadatos profesionales para publicación:

**INFORMACIÓN DEL LIBRO:**
- Título: "{book_data['title']}"
- Género: {book_data['genre']}
- Idioma: {book_data['language']}
- Audiencia: {book_data['target_audience']}

**ARQUITECTURA APROBADA:**
{json.dumps(architecture_data, indent=2, ensure_ascii=False) if architecture_data else "No disponible"}

**MUESTRA DEL CONTENIDO:**
{book_data['content_sample']}

**INSTRUCCIONES:**
Genera metadatos profesionales en español que incluyan:

1. **Subtítulo**: Un subtítulo único y atractivo (máximo 80 caracteres). VARÍA el estilo: enfoque en beneficios, método, resultados, audiencia o propuesta única. Evita patrones repetitivos como "Domina las..." siempre. Ejemplos de estilos: "Tu guía completa para...", "El método revolucionario de...", "Transforma tu [habilidad] en 30 días", "Secretos profesionales de...", etc.
2. **Descripción**: Una descripción comercial atractiva para contraportada (150-250 palabras)
3. **Palabras clave**: 8-12 palabras clave relevantes para SEO y categorización
4. **Categorías**: 3-5 categorías de librería apropiadas
5. **Público objetivo**: Descripción específica del público objetivo
6. **Temas principales**: 4-6 temas centrales del libro

**FORMATO DE RESPUESTA (JSON):**
{{
    "subtitle": "Subtítulo aquí",
    "description": "Descripción aquí...",
    "keywords": ["palabra1", "palabra2", "palabra3"],
    "categories": ["Categoría 1", "Categoría 2"],
    "target_audience": "Descripción del público objetivo",
    "main_themes": ["Tema 1", "Tema 2", "Tema 3"]
}}

Asegúrate de que los metadatos sean profesionales, atractivos y apropiados para el mercado hispanohablante.
"""

        # Obtener servicio Claude - USANDO EL PATRÓN CORRECTO
        claude_service = get_claude_service()
        
        # Usar MessageBuilder para crear mensajes genéricos - siguiendo el patrón del facade
        system_prompt = """Eres un experto en marketing editorial y metadatos de libros.
Genera metadatos profesionales y atractivos basándote en la información proporcionada.
Responde ÚNICAMENTE en formato JSON válido."""
        
        # Crear estructura de mensaje usando el patrón correcto
        message_structure = {
            'system': system_prompt,
            'messages': [{'role': 'user', 'content': prompt}]
        }
        
        # USAR EL CLIENTE CLAUDE DIRECTAMENTE COMO EN BOOK GENERATION
        # Ejecutar la llamada async como en las tareas de Celery
        async def generate_metadata_async():
            response = await claude_service.claude_client.create_message(
                system=message_structure['system'],
                messages=message_structure['messages'],
                model=claude_service.model,
                max_tokens=4096,
                temperature=0.7
            )
            return response
        
        # Ejecutar de forma síncrona como en book generation
        response = asyncio.run(generate_metadata_async())
        
        # Extraer contenido de la respuesta - siguiendo el patrón de book generation
        if hasattr(response, 'content') and response.content:
            ai_response = response.content[0].text if hasattr(response.content[0], 'text') else str(response.content[0])
        else:
            ai_response = str(response)
        
        # Parsear respuesta JSON
        try:
            # Buscar JSON en la respuesta
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No se encontró JSON válido en la respuesta")
            
            json_str = ai_response[start_idx:end_idx]
            metadata = json.loads(json_str)
            
            # Validar que tenga los campos básicos requeridos
            required_fields = ['subtitle', 'description', 'keywords', 'categories', 'target_audience', 'main_themes']
            for field in required_fields:
                if field not in metadata:
                    logger.warning(f"Campo requerido '{field}' no encontrado en metadatos generados por Claude AI")
                    # Si falta algún campo, devolver None para indicar error
                    return None
            
            logger.info(f"Metadatos generados exitosamente con Claude AI para libro {book.id}")
            return metadata
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error parseando respuesta JSON de Claude AI: {str(e)}")
            return None
    
    except Exception as e:
        logger.error(f"Error generando metadatos con Claude AI: {str(e)}")
        return None


def _load_or_generate_metadata(book: BookGeneration) -> Dict[str, Any]:
    """
    Carga metadatos existentes de la BD o los genera automáticamente con Claude AI.
    
    Flujo inteligente:
    1. Si hay metadatos guardados → los devuelve
    2. Si NO hay metadatos → los genera automáticamente y los guarda
    """
    try:
        # Verificar si existen metadatos guardados en la base de datos
        if (book.parameters and 
            'ai_metadata' in book.parameters and 
            'data' in book.parameters['ai_metadata']):
            
            existing_metadata = book.parameters['ai_metadata']['data']
            generated_at = book.parameters['ai_metadata'].get('generated_at', 'Fecha desconocida')
            
            logger.info(f"Cargando metadatos existentes para libro {book.id} (generados: {generated_at})")
            
            # Devolver metadatos existentes con información adicional
            return {
                **existing_metadata,
                'source': 'database',
                'generated_at': generated_at,
                'is_fresh': False
            }
        
        # NO hay metadatos guardados → Generar automáticamente
        logger.info(f"Generando metadatos automáticamente para libro {book.id} (primera vez)")
        
        # Generar metadatos usando Claude AI
        generated_metadata = _generate_ai_metadata(book, {})
        
        if generated_metadata:
            # Guardar automáticamente en la base de datos
            from app import db
            
            # Inicializar parameters si no existe
            if not book.parameters:
                book.parameters = {}
            
            # Guardar metadatos generados automáticamente
            book.parameters['ai_metadata'] = {
                'data': generated_metadata,
                'generated_at': datetime.now().isoformat(),
                'generated_by': 'claude_ai_auto',
                'version': '1.0'
            }
            
            # Actualizar campos directos si aplica
            if 'description' in generated_metadata:
                book.parameters['description'] = generated_metadata['description']
            
            # Commit a la base de datos
            db.session.commit()
            
            logger.info(f"Metadatos generados automáticamente y guardados para libro {book.id}")
            
            # Devolver metadatos nuevos con información adicional
            return {
                **generated_metadata,
                'source': 'claude_ai_auto',
                'generated_at': datetime.now().isoformat(),
                'is_fresh': True
            }
        
        # Error generando con Claude AI → Usar fallback
        logger.warning(f"Error generando metadatos con Claude AI para libro {book.id}, usando fallback")
        fallback_metadata = {
            'subtitle': f'Una guía completa sobre {book.genre or "el tema"}',
            'description': f'Este libro explora {book.title} con un enfoque detallado y profesional.',
            'keywords': [book.genre or 'libro', 'guía', 'educativo'],
            'categories': [book.genre or 'General'],
            'main_themes': ['educación', 'aprendizaje', 'desarrollo'],
            'target_audience': book.target_audience or 'Público general'
        }
        
        return {
            **fallback_metadata,
            'source': 'fallback',
            'generated_at': datetime.now().isoformat(),
            'is_fresh': False
        }
        
    except Exception as e:
        logger.error(f"Error en _load_or_generate_metadata para libro {book.id}: {str(e)}")
        
        # En caso de error crítico, devolver fallback básico
        fallback_metadata = {
            'subtitle': f'Una guía completa sobre {book.genre or "el tema"}',
            'description': f'Este libro explora {book.title} con un enfoque detallado y profesional.',
            'keywords': [book.genre or 'libro', 'guía', 'educativo'],
            'categories': [book.genre or 'General'],
            'main_themes': ['educación', 'aprendizaje', 'desarrollo'],
            'target_audience': book.target_audience or 'Público general'
        }
        
        return {
            **fallback_metadata,
            'source': 'error_fallback',
            'generated_at': datetime.now().isoformat(),
            'is_fresh': False,
            'error': str(e)
        }

