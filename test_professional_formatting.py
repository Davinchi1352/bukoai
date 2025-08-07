#!/usr/bin/env python3
"""
Script de prueba para validar el formateo profesional con el libro #19
"""

import sys
import os
import traceback

# Agregar el directorio de la aplicación al path
sys.path.insert(0, '/home/davinchi/bukoai')

from app import create_app
from app.models.book_generation import BookGeneration
from app.services.professional_formatting_service import (
    ProfessionalFormattingService, 
    ProfessionalFormattingOptions
)

def test_professional_formatting():
    """Probar el formateo profesional con el libro #19"""
    
    app = create_app()
    
    with app.app_context():
        try:
            print("🧪 PRUEBA DEL FORMATEO PROFESIONAL")
            print("="*60)
            
            # Obtener el libro #19
            book = BookGeneration.query.filter_by(id=19).first()
            
            if not book:
                print("❌ Libro #19 no encontrado")
                return False
            
            print(f"📚 Libro encontrado: {book.title}")
            
            # Verificar contenido
            if not book.content and not book.content_html:
                print("❌ El libro no tiene contenido")
                return False
            
            content_type = "HTML" if book.content_html else "Markdown"
            content_length = len(book.content_html) if book.content_html else len(book.content)
            print(f"📄 Contenido: {content_type}, {content_length:,} caracteres")
            
            # Crear instancia del servicio de formateo
            print("\n🔧 Inicializando servicio de formateo profesional...")
            formatting_service = ProfessionalFormattingService()
            
            # Configurar opciones profesionales
            print("⚙️ Configurando opciones profesionales...")
            options = ProfessionalFormattingOptions(
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
            
            # Aplicar formateo profesional
            print("🎨 Aplicando formateo profesional...")
            formatting_result = formatting_service.format_for_commercial_distribution(
                book, options
            )
            
            print("✅ Formateo completado exitosamente")
            
            # Verificar resultados
            print("\n📊 ANÁLISIS DE RESULTADOS:")
            print("-" * 40)
            
            # Preview data
            preview_data = formatting_result.get('preview_data', {})
            if preview_data:
                stats = preview_data.get('statistics', {})
                print(f"📈 Estadísticas:")
                print(f"   - Capítulos: {stats.get('chapters', 'N/A')}")
                print(f"   - Palabras estimadas: {stats.get('words_estimated', 'N/A'):,}")
                print(f"   - Elementos totales: {stats.get('total_elements', 'N/A')}")
                print(f"   - Entradas TOC: {stats.get('toc_entries', 'N/A')}")
                print(f"   - Entradas índice: {stats.get('index_entries', 'N/A')}")
            
            # Quality analysis
            quality = formatting_result.get('quality_analysis', {})
            if quality:
                print(f"\n🏆 Análisis de Calidad:")
                print(f"   - Puntuación general: {quality.get('percentage', 'N/A')}%")
                print(f"   - Puntuación total: {quality.get('total_score', 'N/A')}")
                
                category_scores = quality.get('category_scores', {})
                for category, data in category_scores.items():
                    score = data.get('score', 'N/A')
                    print(f"   - {category.title()}: {score}")
            
            # Formatted content
            formatted_content = formatting_result.get('formatted_content', '')
            if formatted_content:
                print(f"\n📝 Contenido formateado: {len(formatted_content):,} caracteres")
                
                # Mostrar muestra del contenido
                sample = formatted_content[:500]
                print(f"\n🔍 Muestra del contenido formateado:")
                print("-" * 50)
                print(sample)
                print("-" * 50)
            
            # Export readiness
            export_ready = formatting_result.get('export_ready', False)
            print(f"\n🚀 Listo para exportación: {'✅ SÍ' if export_ready else '❌ NO'}")
            
            # Formatos disponibles
            if preview_data and 'export_formats' in preview_data:
                print(f"\n📦 Formatos de exportación disponibles:")
                for fmt in preview_data['export_formats']:
                    format_name = fmt.get('format', 'Desconocido')
                    platform = fmt.get('platform', 'General')
                    print(f"   - {format_name} ({platform})")
            
            # Verificar estructura del contenido
            print(f"\n🔍 VERIFICACIÓN DE ESTRUCTURA:")
            print("-" * 40)
            
            if formatted_content:
                # Buscar elementos H1, H2, H3
                import re
                h1_count = len(re.findall(r'<h1[^>]*>', formatted_content))
                h2_count = len(re.findall(r'<h2[^>]*>', formatted_content))
                h3_count = len(re.findall(r'<h3[^>]*>', formatted_content))
                
                print(f"   - Encabezados H1 (Capítulos): {h1_count}")
                print(f"   - Encabezados H2 (Secciones): {h2_count}")
                print(f"   - Encabezados H3 (Subsecciones): {h3_count}")
            
            print(f"\n✅ Prueba completada exitosamente")
            print(f"🌐 URL de prueba: http://localhost:5001/books/book/{book.id}/formatting-viewer")
            
            return True
            
        except Exception as e:
            print(f"❌ Error en la prueba: {str(e)}")
            print(f"🔍 Traceback completo:")
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = test_professional_formatting()
    exit(0 if success else 1)