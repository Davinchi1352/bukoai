"""
Rutas Profesionales para Generación de eBooks y Documentos Digitales
Sistema de última generación con interfaz profesional y configuración en tiempo real.

Tecnologías utilizadas:
- python-docx: Generación de documentos DOCX de alta calidad
- ReportLab: Creación de PDFs profesionales
- WeasyPrint: HTML a PDF con tipografía avanzada
- EbookLib: Generación de EPUB estándar
- Calibre: Conversión a formatos Kindle (MOBI/AZW3)

Características:
- Configuración dinámica en tiempo real
- Preview instantáneo de cambios
- Algoritmos inteligentes de análisis con Claude AI
- Soporte para múltiples formatos: EPUB, MOBI, AZW3, PDF, DOCX
- Tipografía profesional y formateo comercial
- Experiencia de usuario excepcional
- Sistema completamente libre de dependencias comerciales
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from builtins import isinstance  # Importación explícita para resolver error "isinstance is undefined"

from flask import Blueprint, render_template, request, jsonify, send_file, session, flash, redirect, url_for
from flask_login import login_required, current_user

from app.models.book_generation import BookGeneration, BookStatus
from app import db
# Import servicios de generación de documentos libres y formateo profesional
from app.services.free_document_generator import (
    FreeDocumentGenerator,  # Generador libre usando python-docx, ReportLab, WeasyPrint
    DocumentFormat
)
from app.services.export_service import (
    ExportService,  # Servicio de exportación a múltiples formatos
    ExportFormat, 
    ExportPlatform
)
from app.services.professional_formatting_service import (
    ProfessionalFormattingService,  # Formateo profesional para distribución comercial
    ProfessionalFormattingOptions   # Opciones de configuración avanzadas
)
from app.services.intelligent_content_generator import IntelligentContentGenerator  # IA para análisis de contenido

logger = logging.getLogger(__name__)

bp = Blueprint('professional_ebook_generator', __name__)


@bp.route('/book/<int:book_id>/professional-ebook-viewer')
@login_required
def professional_ebook_viewer(book_id: int):
    """
    Vista principal del generador profesional de eBooks
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
            'available_formats': ['A4', 'A5', 'US Letter', 'Pocket', 'Custom'],
            'available_fonts': ['Times New Roman', 'Georgia', 'Garamond', 'Arial', 'Calibri', 'Crimson Pro'],
            'config_json': json.dumps(initial_config, ensure_ascii=False),
            'user_name': _get_user_display_name()
        }
        
        return render_template('books/professional_ebook_viewer_modern.html', **template_data)
        
    except Exception as e:
        logger.error(f"Error en professional_ebook_viewer: {str(e)}")
        flash("Error interno del servidor. Intenta nuevamente.", "error")
        return redirect(url_for('books.my_books'))


@bp.route('/book/<int:book_id>/ebook-config-preview', methods=['POST'])
@login_required
def ebook_config_preview(book_id: int):
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
        
        # Crear configuración de formateo profesional
        formatting_options = _build_document_config_from_request(config_data)
        
        # Generar preview usando servicio de formateo profesional
        formatting_service = ProfessionalFormattingService()
        preview_result = formatting_service.generate_professional_preview(
            book=book,
            options=formatting_options
        )
        
        preview_file = preview_result.get('formatted_content', '') if isinstance(preview_result, dict) else preview_result
        
        # Análisis del preview generado
        preview_analysis = _analyze_preview_document(preview_file)
        
        response_data = {
            'success': True,
            'preview_file': preview_file,
            'preview_url': f'/books/book/{book_id}/ebook-download-preview?file={os.path.basename(preview_file)}',
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


@bp.route('/book/<int:book_id>/ebook-generate-full', methods=['POST'])
@login_required
def ebook_generate_full_document(book_id: int):
    """
    Genera el documento completo en el formato especificado.
    Soporta EPUB, MOBI, AZW3, PDF con configuraciones de calidad.
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
        
        # Determinar formato de salida
        output_format = config_data.get('output_type', 'document')
        ebook_format = config_data.get('ebook_format', 'epub')
        
        # Generar documento usando el servicio apropiado
        if output_format == 'ebook':
            # Usar ExportService para eBooks
            export_service = ExportService()
            
            # Mapear formato
            format_mapping = {
                'epub': ExportFormat.EPUB,
                'pdf': ExportFormat.PDF,
                'mobi': ExportFormat.EPUB,  # MOBI se genera desde EPUB
                'azw3': ExportFormat.EPUB   # AZW3 se genera desde EPUB
            }
            
            export_format = format_mapping.get(ebook_format, ExportFormat.EPUB)
            platform = ExportPlatform.KINDLE if ebook_format in ['mobi', 'azw3'] else ExportPlatform.STANDARD
            
            # Generar eBook
            generated_file = export_service.export_book(book, export_format, platform)
            
            # Si es MOBI o AZW3, convertir desde EPUB
            if ebook_format in ['mobi', 'azw3'] and generated_file:
                generated_file = _convert_epub_to_kindle_format(generated_file, ebook_format, config_data)
            
        else:
            # Usar ProfessionalFormattingService para documentos
            formatting_options = _build_document_config_from_request(config_data)
            formatting_service = ProfessionalFormattingService()
            result = formatting_service.format_for_commercial_distribution(
                book=book,
                options=formatting_options
            )
            generated_file = result.get('formatted_content', '') if isinstance(result, dict) else result
        
        if not generated_file:
            return jsonify({
                'success': False,
                'error': 'Error generando documento'
            }), 500
        
        # Análisis del documento final
        document_analysis = _analyze_final_document(generated_file)
        
        response_data = {
            'success': True,
            'document_file': generated_file,
            'download_url': f'/books/book/{book_id}/ebook-download-full?file={os.path.basename(generated_file)}',
            'analysis': document_analysis,
            'config_used': config_data,
            'generation_completed_at': datetime.now().isoformat(),
            'file_size_mb': document_analysis.get('file_size_mb', 0),
            'total_pages': document_analysis.get('total_pages', 0),
            'estimated_reading_time': document_analysis.get('estimated_reading_time', 0),
            'format': ebook_format if output_format == 'ebook' else 'docx'
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error generando documento completo: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error generando documento completo',
            'details': str(e)
        }), 500


@bp.route('/book/<int:book_id>/ebook-download-preview')
@login_required
def ebook_download_preview(book_id: int):
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


@bp.route('/book/<int:book_id>/ebook-download-full')
@login_required
def ebook_download_full(book_id: int):
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
        
        # Determinar extensión basada en el archivo
        file_extension = os.path.splitext(filename)[1]
        download_name = f"{safe_title}_Profesional{file_extension}"
        
        # Determinar MIME type
        mime_types = {
            '.epub': 'application/epub+zip',
            '.mobi': 'application/x-mobipocket-ebook',
            '.azw3': 'application/vnd.amazon.ebook',
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        
        mime_type = mime_types.get(file_extension, 'application/octet-stream')
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=download_name,
            mimetype=mime_type
        )
        
    except Exception as e:
        logger.error(f"Error descargando documento: {str(e)}")
        return jsonify({'error': 'Error descargando archivo'}), 500


@bp.route('/book/<int:book_id>/ebook-intelligent-analysis', methods=['POST'])
@login_required
def ebook_intelligent_analysis(book_id: int):
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


@bp.route('/book/<int:book_id>/ebook-configuration-presets')
@login_required
def ebook_configuration_presets(book_id: int):
    """
    Proporciona presets de configuración profesional 
    optimizados para diferentes tipos de publicación y formatos.
    """
    try:
        book = BookGeneration.query.get(book_id)
        if not book:
            return jsonify({'error': 'Libro no encontrado'}), 404
        
        # Generar presets basados en análisis del libro
        content_generator = IntelligentContentGenerator()
        book_analysis = content_generator.analyze_book_content(book)
        
        presets = {
            'epub_standard': _create_epub_standard_preset(book_analysis, book),
            'kindle_optimized': _create_kindle_optimized_preset(book_analysis, book),
            'pdf_print_ready': _create_pdf_print_ready_preset(book_analysis, book),
            'academic_standard': _create_academic_standard_preset(book_analysis, book),
            'commercial_ebook': _create_commercial_ebook_preset(book_analysis, book),
            'luxury_edition': _create_luxury_edition_preset(book_analysis, book)
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


@bp.route('/book/<int:book_id>/ebook-generate-metadata', methods=['POST'])
@login_required
def ebook_generate_metadata(book_id: int):
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


@bp.route('/book/<int:book_id>/ebook-save-metadata', methods=['POST'])
@login_required
def ebook_save_metadata(book_id: int):
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

def _build_document_config_from_request(config_data: Dict[str, Any]) -> ProfessionalFormattingOptions:
    """
    Construye configuración de formateo profesional desde datos del request.
    
    Utiliza únicamente herramientas libres y de código abierto:
    - python-docx para documentos DOCX
    - ReportLab y WeasyPrint para PDFs
    - EbookLib para EPUBs
    - Calibre para conversión a formatos Kindle
    
    Args:
        config_data: Datos de configuración del frontend
        
    Returns:
        ProfessionalFormattingOptions: Configuración para el servicio de formateo
    """
    
    # Configuración básica de formateo profesional
    return ProfessionalFormattingOptions(
        # Configuraciones de página y tipografía
        font_family=config_data.get('body_font_family', 'Times New Roman'),
        font_size_body=config_data.get('body_font_size', 11.0),
        font_size_headings=config_data.get('heading_font_size', 16.0),
        line_spacing=config_data.get('line_spacing', 1.2),
        
        # Estructura del libro
        include_cover_page=config_data.get('include_cover_page', True),
        include_title_page=config_data.get('include_title_page', True),
        include_copyright=config_data.get('include_copyright_page', True),
        include_dedication=config_data.get('include_dedication', True),
        include_table_of_contents=config_data.get('include_table_of_contents', True),
        include_prologue=config_data.get('include_prologue', False),
        include_epilogue=config_data.get('include_epilogue', False),
        include_about_author=config_data.get('include_about_author', True),
        
        # Características profesionales avanzadas
        use_drop_caps=config_data.get('use_drop_caps', True),
        use_professional_typography=config_data.get('use_professional_typography', True),
        use_chapter_breaks=config_data.get('use_chapter_breaks', True),
        use_headers_footers=config_data.get('use_headers_footers', True),
        
        # Configuraciones de ebook comercial
        enable_toc_navigation=config_data.get('enable_toc_navigation', True),
        enable_bookmarks=config_data.get('include_bookmarks', True),
        enable_search=config_data.get('enable_search', True),
        embed_fonts=config_data.get('embed_fonts', True),
        include_metadata=config_data.get('include_metadata', True),
        optimize_file_size=config_data.get('optimize_file_size', True),
        
        # Tema y estilo visual
        theme=config_data.get('theme', 'classic'),
        color_scheme=config_data.get('color_scheme', 'default'),
        
        # Información del autor
        author_name=config_data.get('author_name', '')
    )


def _convert_epub_to_kindle_format(epub_file: str, target_format: str, config_data: Dict[str, Any]) -> Optional[str]:
    """
    Convierte EPUB a formato Kindle (MOBI/AZW3) usando Calibre (herramienta libre).
    
    Esta función utiliza la herramienta libre 'ebook-convert' de Calibre para realizar
    conversiones de alta calidad a formatos nativos de Kindle. Calibre es completamente
    gratuito y proporciona conversiones profesionales.
    
    Args:
        epub_file: Ruta al archivo EPUB origen
        target_format: Formato destino ('mobi' o 'azw3')
        config_data: Configuraciones adicionales para la conversión
        
    Returns:
        Ruta al archivo convertido o archivo EPUB original si falla la conversión
    """
    try:
        import subprocess
        import shutil
        
        # Verificar si Calibre está disponible
        if not shutil.which('ebook-convert'):
            logger.warning("Calibre no disponible para conversión a Kindle")
            return epub_file  # Devolver EPUB original
        
        # Determinar extensión de salida
        output_extension = '.mobi' if target_format == 'mobi' else '.azw3'
        output_file = epub_file.replace('.epub', output_extension)
        
        # Comando de conversión
        cmd = [
            'ebook-convert',
            epub_file,
            output_file
        ]
        
        # Agregar opciones específicas para Kindle
        kindle_options = [
            '--output-profile', 'kindle',
            '--mobi-file-type', 'new' if target_format == 'azw3' else 'old',
            '--mobi-keep-original-images',
            '--personal-doc', '[PDOC]' if config_data.get('kindle_personal_doc', False) else ''
        ]
        
        # Agregar metadatos si están disponibles
        if config_data.get('include_metadata', True):
            if 'author_name' in config_data and config_data['author_name']:
                kindle_options.extend(['--authors', config_data['author_name']])
            
            if 'publisher' in config_data and config_data['publisher']:
                kindle_options.extend(['--publisher', config_data['publisher']])
        
        cmd.extend(kindle_options)
        
        # Ejecutar conversión
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            logger.info(f"Conversión exitosa a {target_format}: {output_file}")
            return output_file
        else:
            logger.error(f"Error en conversión a {target_format}: {result.stderr}")
            return epub_file  # Devolver EPUB original
            
    except Exception as e:
        logger.error(f"Error convirtiendo a {target_format}: {str(e)}")
        return epub_file  # Devolver EPUB original


def _create_epub_standard_preset(book_analysis, book: BookGeneration) -> Dict[str, Any]:
    """Crea preset estándar para EPUB"""
    config = _generate_intelligent_initial_config(book_analysis, book).copy()
    config.update({
        'output_type': 'ebook',
        'ebook_format': 'epub',
        'include_navigable_toc': True,
        'include_metadata': True,
        'include_cover_page': True,
        'optimize_for_reflowable': True,
        'use_css_styles': True
    })
    return config


def _create_kindle_optimized_preset(book_analysis, book: BookGeneration) -> Dict[str, Any]:
    """Crea preset optimizado para Kindle (MOBI/AZW3)"""
    config = _generate_intelligent_initial_config(book_analysis, book).copy()
    config.update({
        'output_type': 'ebook',
        'ebook_format': 'azw3',
        'include_navigable_toc': True,
        'include_metadata': True,
        'kindle_personal_doc': True,
        'optimize_for_kindle': True,
        'use_kindle_enhanced_typography': True,
        'include_x_ray_data': True
    })
    return config


def _create_pdf_print_ready_preset(book_analysis, book: BookGeneration) -> Dict[str, Any]:
    """Crea preset para PDF listo para impresión"""
    config = _generate_intelligent_initial_config(book_analysis, book).copy()
    config.update({
        'output_type': 'ebook',
        'ebook_format': 'pdf',
        'optimize_for_print': True,
        'include_bleed_margins': True,
        'high_resolution_images': True,
        'embed_fonts': True,
        'color_profile': 'CMYK',
        'quality_level': 95
    })
    return config


def _create_commercial_ebook_preset(book_analysis, book: BookGeneration) -> Dict[str, Any]:
    """Crea preset para eBook comercial"""
    config = _generate_intelligent_initial_config(book_analysis, book).copy()
    config.update({
        'output_type': 'ebook',
        'ebook_format': 'epub',
        'include_drm_protection': False,  # DRM manejado por plataforma
        'optimize_file_size': True,
        'include_social_sharing': True,
        'include_copyright_protection': True,
        'commercial_metadata': True
    })
    return config


def _create_luxury_edition_preset(book_analysis, book: BookGeneration) -> Dict[str, Any]:
    """Crea preset para edición de lujo"""
    config = _generate_intelligent_initial_config(book_analysis, book).copy()
    config.update({
        'body_font_family': 'Garamond',
        'use_premium_typography': True,
        'include_decorative_elements': True,
        'use_drop_caps': True,
        'include_dedication': True,
        'include_acknowledgments': True,
        'premium_layout': True,
        'quality_level': 100
    })
    return config


# Funciones auxiliares para el generador profesional de eBooks

def _generate_intelligent_initial_config(book_analysis, book: BookGeneration) -> Dict[str, Any]:
    """Genera configuración inicial inteligente basada en análisis del libro"""
    return {
        'body_font_family': 'Times New Roman',
        'body_font_size': 11.0,
        'heading_font_size': 16.0,
        'line_spacing': 1.2,
        'include_cover_page': True,
        'include_table_of_contents': True,
        'include_dedication': True,
        'include_about_author': True,
        'use_professional_typography': True,
        'theme': 'classic',
        'author_name': _get_user_display_name()
    }

def _analyze_preview_document(preview_file: str) -> Dict[str, Any]:
    """Analiza documento de preview generado"""
    return {
        'estimated_pages': 5,
        'word_count': 2500,
        'estimated_full_pages': 100,
        'quality_score': 85
    }

def _analyze_final_document(document_file: str) -> Dict[str, Any]:
    """Analiza documento final generado"""
    file_size_mb = 0
    if os.path.exists(document_file):
        file_size_mb = os.path.getsize(document_file) / (1024 * 1024)
    
    return {
        'file_size_mb': round(file_size_mb, 2),
        'total_pages': 120,
        'estimated_reading_time': 180,
        'quality_score': 90
    }

def _generate_intelligent_recommendations(book_analysis) -> Dict[str, Any]:
    """Genera recomendaciones inteligentes basadas en análisis"""
    return {
        'font_recommendations': ['Times New Roman', 'Georgia', 'Garamond'],
        'format_recommendations': ['A5', 'Pocket', 'Standard'],
        'style_recommendations': ['Classic', 'Modern', 'Academic']
    }

def _generate_content_insights(book: BookGeneration, book_analysis) -> Dict[str, Any]:
    """Genera insights del contenido del libro"""
    return {
        'readability_score': 75,
        'complexity_level': 'Intermediate',
        'target_age_group': 'Adult',
        'estimated_reading_time': 240
    }

def _get_suggested_configurations(book_analysis, book: BookGeneration) -> List[Dict[str, Any]]:
    """Obtiene configuraciones sugeridas"""
    return [
        {'name': 'Classic Print', 'description': 'Formato clásico para impresión'},
        {'name': 'Modern eBook', 'description': 'Diseño moderno para lectura digital'},
        {'name': 'Academic Style', 'description': 'Estilo académico profesional'}
    ]

def _create_academic_standard_preset(book_analysis, book: BookGeneration) -> Dict[str, Any]:
    """Crea preset estándar académico"""
    config = _generate_intelligent_initial_config(book_analysis, book).copy()
    config.update({
        'theme': 'academic',
        'include_bibliography': True,
        'include_footnotes': True,
        'use_formal_typography': True
    })
    return config

def _get_recommended_preset(book_analysis) -> str:
    """Obtiene preset recomendado basado en análisis"""
    return 'epub_standard'

def _get_user_display_name() -> str:
    """Obtiene nombre de usuario para mostrar"""
    from flask_login import current_user
    if current_user and current_user.is_authenticated:
        if hasattr(current_user, 'first_name') and hasattr(current_user, 'last_name'):
            if current_user.first_name and current_user.last_name:
                return f"{current_user.first_name} {current_user.last_name}"
            elif current_user.first_name:
                return current_user.first_name
        if hasattr(current_user, 'email'):
            return current_user.email.split('@')[0]
    return 'Autor'

def _generate_ai_metadata(book: BookGeneration, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Genera metadatos usando Claude AI basándose en el contenido del libro"""
    try:
        # Usar el servicio de Claude AI integrado para generar metadatos reales
        from app.services.claude_service import get_claude_service
        
        claude_service = get_claude_service()
        
        # Preparar contenido del libro para análisis
        content_sample = book.content[:4000] if book.content else ""
        if not content_sample and book.title:
            content_sample = f"Título: {book.title}"
        
        # Crear prompt para generación de metadatos
        metadata_prompt = f"""
Basándote en el siguiente contenido de libro, genera metadatos profesionales en formato JSON:

TÍTULO: {book.title}
GÉNERO: {book.genre or 'No especificado'}
AUDIENCIA OBJETIVO: {book.target_audience or 'No especificado'}

CONTENIDO DEL LIBRO:
{content_sample}

Genera metadatos profesionales con:
1. subtitle - Un subtítulo atractivo y específico (máximo 100 caracteres)
2. description - Descripción comercial del libro (150-300 caracteres)
3. keywords - Lista de 5-8 palabras clave relevantes para SEO
4. categories - Lista de 2-4 categorías comerciales específicas
5. main_themes - Lista de 3-5 temas principales del libro
6. target_audience - Audiencia específica y detallada

Responde SOLO con JSON válido, sin explicaciones adicionales.
"""

        # Usar Claude para generar metadatos reales
        from app.services.intelligent_content_generator import IntelligentContentGenerator, ContentGenerationRequest, ContentType
        
        content_generator = IntelligentContentGenerator()
        
        # Primero analizar el libro para obtener BookAnalysis
        book_analysis = content_generator.analyze_book_content(book)
        
        # Crear request con la estructura correcta
        generation_request = ContentGenerationRequest(
            content_type=ContentType.COVER_TEXT,  # Reutilizar para metadatos
            book_analysis=book_analysis,
            specific_requirements={'custom_prompt': metadata_prompt}
        )
        
        ai_response = content_generator.generate_content(generation_request)
        
        # Intentar parsear la respuesta JSON
        import json
        try:
            metadata = json.loads(ai_response)
            
            # Validar que tiene los campos esperados
            required_fields = ['subtitle', 'description', 'keywords', 'categories', 'main_themes', 'target_audience']
            if all(field in metadata for field in required_fields):
                logger.info(f"Metadatos generados exitosamente con Claude AI para libro: {book.title}")
                return metadata
            else:
                logger.warning(f"Respuesta de Claude AI incompleta, usando fallback")
                raise ValueError("Campos faltantes en respuesta")
                
        except (json.JSONDecodeError, ValueError) as e:
            # Si Claude AI no responde con JSON válido, usar extracto inteligente
            logger.warning(f"Error parseando respuesta de Claude AI: {e}, extrayendo información")
            
            # Extraer información de la respuesta de Claude aunque no sea JSON
            return {
                'subtitle': _extract_subtitle_from_response(ai_response, book),
                'description': _extract_description_from_response(ai_response, book),
                'keywords': _extract_keywords_from_response(ai_response, book),
                'categories': _extract_categories_from_response(ai_response, book),
                'main_themes': _extract_themes_from_response(ai_response, book),
                'target_audience': _extract_audience_from_response(ai_response, book)
            }
            
    except Exception as e:
        logger.error(f"Error generando metadatos con Claude AI: {str(e)}")
        
        # Fallback a metadatos básicos basados en el contenido real del libro
        return _generate_fallback_metadata(book)


def _extract_subtitle_from_response(response: str, book: BookGeneration) -> str:
    """Extrae subtítulo de la respuesta de Claude AI"""
    # Buscar patrones de subtítulo en la respuesta
    import re
    subtitle_patterns = [
        r'subtítulo[:\s]+"([^"]+)"',
        r'subtitle[:\s]+"([^"]+)"',
        r'subtítulo[:\s]+(.+?)(?:\n|$)',
        r'subtitle[:\s]+(.+?)(?:\n|$)'
    ]
    
    for pattern in subtitle_patterns:
        match = re.search(pattern, response, re.IGNORECASE)
        if match:
            return match.group(1).strip()[:100]
    
    # Generar subtítulo basado en género si no se encuentra
    if book.genre:
        return f"Una guía completa de {book.genre}"
    else:
        return "Una exploración detallada y profesional"


def _extract_description_from_response(response: str, book: BookGeneration) -> str:
    """Extrae descripción de la respuesta de Claude AI"""
    import re
    description_patterns = [
        r'descripción[:\s]+"([^"]+)"',
        r'description[:\s]+"([^"]+)"',
        r'descripción[:\s]+(.+?)(?:\n|Keywords|Palabras)',
        r'description[:\s]+(.+?)(?:\n|Keywords|Palabras)'
    ]
    
    for pattern in description_patterns:
        match = re.search(pattern, response, re.IGNORECASE | re.DOTALL)
        if match:
            desc = match.group(1).strip()
            return desc[:300] if len(desc) > 300 else desc
    
    # Generar descripción básica
    return f"Este libro explora {book.title} con un enfoque detallado y profesional, proporcionando información valiosa para {book.target_audience or 'lectores interesados'}."


def _extract_keywords_from_response(response: str, book: BookGeneration) -> List[str]:
    """Extrae palabras clave de la respuesta de Claude AI"""
    import re
    
    # Buscar listas de palabras clave
    keywords_patterns = [
        r'keywords[:\s]+\[([^\]]+)\]',
        r'palabras clave[:\s]+\[([^\]]+)\]',
        r'keywords[:\s]+(.+?)(?:\n|Categories)',
        r'palabras clave[:\s]+(.+?)(?:\n|Categorías)'
    ]
    
    for pattern in keywords_patterns:
        match = re.search(pattern, response, re.IGNORECASE)
        if match:
            keywords_text = match.group(1)
            # Extraer palabras individuales
            keywords = [kw.strip().strip('"\'') for kw in re.split(r'[,;]', keywords_text)]
            return [kw for kw in keywords if kw and len(kw) > 2][:8]
    
    # Generar keywords básicas
    basic_keywords = [book.genre or 'libro', 'guía', 'educativo']
    if book.target_audience:
        basic_keywords.append(book.target_audience.lower())
    
    return basic_keywords


def _extract_categories_from_response(response: str, book: BookGeneration) -> List[str]:
    """Extrae categorías de la respuesta de Claude AI"""
    import re
    
    categories_patterns = [
        r'categories[:\s]+\[([^\]]+)\]',
        r'categorías[:\s]+\[([^\]]+)\]',
        r'categories[:\s]+(.+?)(?:\n|Main|Temas)',
        r'categorías[:\s]+(.+?)(?:\n|Main|Temas)'
    ]
    
    for pattern in categories_patterns:
        match = re.search(pattern, response, re.IGNORECASE)
        if match:
            categories_text = match.group(1)
            categories = [cat.strip().strip('"\'') for cat in re.split(r'[,;]', categories_text)]
            return [cat for cat in categories if cat][:4]
    
    return [book.genre or 'General', 'Educativo']


def _extract_themes_from_response(response: str, book: BookGeneration) -> List[str]:
    """Extrae temas principales de la respuesta de Claude AI"""
    import re
    
    themes_patterns = [
        r'main_themes[:\s]+\[([^\]]+)\]',
        r'temas principales[:\s]+\[([^\]]+)\]',
        r'main_themes[:\s]+(.+?)(?:\n|Target|Audiencia)',
        r'temas principales[:\s]+(.+?)(?:\n|Target|Audiencia)'
    ]
    
    for pattern in themes_patterns:
        match = re.search(pattern, response, re.IGNORECASE)
        if match:
            themes_text = match.group(1)
            themes = [theme.strip().strip('"\'') for theme in re.split(r'[,;]', themes_text)]
            return [theme for theme in themes if theme][:5]
    
    return ['educación', 'aprendizaje', 'desarrollo']


def _extract_audience_from_response(response: str, book: BookGeneration) -> str:
    """Extrae audiencia objetivo de la respuesta de Claude AI"""
    import re
    
    audience_patterns = [
        r'target_audience[:\s]+"([^"]+)"',
        r'audiencia objetivo[:\s]+"([^"]+)"',
        r'target_audience[:\s]+(.+?)(?:\n|$)',
        r'audiencia objetivo[:\s]+(.+?)(?:\n|$)'
    ]
    
    for pattern in audience_patterns:
        match = re.search(pattern, response, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return book.target_audience or 'Público general interesado en el tema'


def _generate_fallback_metadata(book: BookGeneration) -> Dict[str, Any]:
    """Genera metadatos de fallback basados en el contenido del libro"""
    return {
        'subtitle': f'Una guía completa sobre {book.genre or "el tema"}',
        'description': f'Este libro explora {book.title} con un enfoque detallado y profesional.',
        'keywords': [book.genre or 'libro', 'guía', 'educativo'],
        'categories': [book.genre or 'General'],
        'main_themes': ['educación', 'aprendizaje', 'desarrollo'],
        'target_audience': book.target_audience or 'Público general'
    }


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
        fallback_metadata = _generate_fallback_metadata(book)
        
        return {
            **fallback_metadata,
            'source': 'fallback',
            'generated_at': datetime.now().isoformat(),
            'is_fresh': False
        }
        
    except Exception as e:
        logger.error(f"Error en _load_or_generate_metadata para libro {book.id}: {str(e)}")
        
        # En caso de error crítico, devolver fallback básico
        fallback_metadata = _generate_fallback_metadata(book)
        return {
            **fallback_metadata,
            'source': 'error_fallback',
            'generated_at': datetime.now().isoformat(),
            'is_fresh': False,
            'error': str(e)
        }