#!/usr/bin/env python3
"""
Script para extraer el contenido crudo del libro con ID 34 para análisis
"""

import os
import sys
import json

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from main import create_app
from app.models import db, BookGeneration


def save_content_to_file(content: str, filename: str, description: str) -> None:
    """Guarda contenido en un archivo"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {description} guardado en: {filename}")
        print(f"   Tamaño: {len(content):,} caracteres")
    except Exception as e:
        print(f"❌ Error guardando {description}: {e}")


def extract_json_content(content: str) -> dict:
    """Intenta extraer contenido JSON si existe"""
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return None


def analyze_content_type(content: str) -> dict:
    """Analiza el tipo y estructura del contenido"""
    analysis = {
        'type': 'unknown',
        'encoding': 'utf-8',
        'length': len(content),
        'lines': len(content.splitlines()),
        'words': len(content.split()),
        'structure_info': {}
    }
    
    # Intentar detectar JSON
    json_content = extract_json_content(content)
    if json_content:
        analysis['type'] = 'json'
        analysis['structure_info'] = {
            'keys': list(json_content.keys()) if isinstance(json_content, dict) else [],
            'is_dict': isinstance(json_content, dict),
            'is_list': isinstance(json_content, list)
        }
        return analysis
    
    # Detectar Markdown
    if any(line.startswith('#') for line in content.splitlines()[:50]):
        analysis['type'] = 'markdown'
        # Contar elementos markdown
        import re
        analysis['structure_info'] = {
            'headers': len(re.findall(r'^#+\s+', content, re.MULTILINE)),
            'code_blocks': len(re.findall(r'```', content)),
            'bold_text': len(re.findall(r'\*\*[^*]+\*\*', content)),
            'italic_text': len(re.findall(r'\*[^*]+\*', content))
        }
        return analysis
    
    # Si no es JSON ni Markdown, es texto plano
    analysis['type'] = 'plain_text'
    
    return analysis


def main():
    """Función principal"""
    print("📤 Extrayendo contenido crudo del libro con ID 34...")
    
    # Crear aplicación
    app = create_app("development")
    
    with app.app_context():
        # Buscar el libro por ID
        book = BookGeneration.query.get(34)
        
        if not book:
            print("❌ No se encontró el libro con ID 34")
            return
        
        print(f"✅ Libro encontrado: {book.title}")
        print(f"📊 Estado: {book.status.value if book.status else 'Unknown'}")
        print()
        
        # Crear directorio de salida
        output_dir = "book_34_extracted_content"
        os.makedirs(output_dir, exist_ok=True)
        print(f"📁 Creando directorio: {output_dir}")
        
        # Extraer y analizar contenido principal
        if book.content:
            print("\n" + "=" * 80)
            print("📝 PROCESANDO CONTENIDO PRINCIPAL")
            print("=" * 80)
            
            content_analysis = analyze_content_type(book.content)
            print(f"Tipo detectado: {content_analysis['type']}")
            print(f"Longitud: {content_analysis['length']:,} caracteres")
            print(f"Líneas: {content_analysis['lines']:,}")
            print(f"Palabras: {content_analysis['words']:,}")
            
            if content_analysis['structure_info']:
                print("Estructura detectada:")
                for key, value in content_analysis['structure_info'].items():
                    print(f"  - {key}: {value}")
            
            # Guardar contenido principal
            filename = os.path.join(output_dir, "book_content.md")
            save_content_to_file(book.content, filename, "Contenido principal")
            
            # Si es JSON, también guardarlo como JSON formateado
            if content_analysis['type'] == 'json':
                json_content = extract_json_content(book.content)
                json_filename = os.path.join(output_dir, "book_content.json")
                formatted_json = json.dumps(json_content, indent=2, ensure_ascii=False)
                save_content_to_file(formatted_json, json_filename, "Contenido JSON formateado")
        else:
            print("❌ No hay contenido principal disponible")
        
        # Extraer thinking content si existe
        if book.thinking_content:
            print("\n" + "=" * 80)
            print("🧠 PROCESANDO THINKING CONTENT")
            print("=" * 80)
            
            thinking_analysis = analyze_content_type(book.thinking_content)
            print(f"Tipo detectado: {thinking_analysis['type']}")
            print(f"Longitud: {thinking_analysis['length']:,} caracteres")
            print(f"Líneas: {thinking_analysis['lines']:,}")
            print(f"Palabras: {thinking_analysis['words']:,}")
            
            if thinking_analysis['structure_info']:
                print("Estructura detectada:")
                for key, value in thinking_analysis['structure_info'].items():
                    print(f"  - {key}: {value}")
            
            # Guardar thinking content
            thinking_filename = os.path.join(output_dir, "thinking_content.md")
            save_content_to_file(book.thinking_content, thinking_filename, "Thinking content")
        else:
            print("\n❌ No hay thinking content disponible")
        
        # Crear archivo de metadatos
        metadata = {
            'book_info': {
                'id': book.id,
                'title': book.title,
                'genre': book.genre,
                'target_audience': book.target_audience,
                'tone': book.tone,
                'language': book.language,
                'status': book.status.value if book.status else None
            },
            'configuration': {
                'chapter_count': book.chapter_count,
                'page_count': book.page_count,
                'format_size': book.format_size,
                'line_spacing': book.line_spacing,
                'include_toc': book.include_toc,
                'include_introduction': book.include_introduction,
                'include_conclusion': book.include_conclusion,
                'writing_style': book.writing_style
            },
            'statistics': {
                'final_pages': book.final_pages,
                'final_words': book.final_words,
                'prompt_tokens': book.prompt_tokens,
                'completion_tokens': book.completion_tokens,
                'thinking_tokens': book.thinking_tokens,
                'total_tokens': book.total_tokens,
                'estimated_cost': float(book.estimated_cost) if book.estimated_cost else 0
            },
            'timestamps': {
                'created_at': book.created_at.isoformat() if book.created_at else None,
                'started_at': book.started_at.isoformat() if book.started_at else None,
                'completed_at': book.completed_at.isoformat() if book.completed_at else None
            },
            'files': {
                'file_paths': book.file_paths,
                'available_formats': book.file_formats
            },
            'content_analysis': {
                'main_content': analyze_content_type(book.content) if book.content else None,
                'thinking_content': analyze_content_type(book.thinking_content) if book.thinking_content else None
            }
        }
        
        metadata_filename = os.path.join(output_dir, "metadata.json")
        save_content_to_file(
            json.dumps(metadata, indent=2, ensure_ascii=False), 
            metadata_filename, 
            "Metadatos del libro"
        )
        
        # Crear README con información sobre los archivos extraídos
        readme_content = f"""# Contenido Extraído del Libro ID 34

## Información del Libro
- **Título**: {book.title}
- **Género**: {book.genre}
- **Audiencia**: {book.target_audience}
- **Tono**: {book.tone}
- **Idioma**: {book.language}
- **Estado**: {book.status.value if book.status else 'Unknown'}

## Estadísticas
- **Páginas finales**: {book.final_pages}
- **Palabras finales**: {book.final_words:,}
- **Tokens totales**: {book.total_tokens:,}
- **Costo estimado**: ${book.estimated_cost if book.estimated_cost else 0}

## Archivos Extraídos

### book_content.md
Contiene el contenido principal del libro en formato Markdown.
- Longitud: {len(book.content):,} caracteres
- Palabras: {len(book.content.split()):,}
- Líneas: {len(book.content.splitlines()):,}

### thinking_content.md
{f"Contiene el contenido de 'thinking' del modelo AI (si está disponible)." if book.thinking_content else "No disponible - el libro no tiene thinking content."}
{f"- Longitud: {len(book.thinking_content):,} caracteres" if book.thinking_content else ""}
{f"- Palabras: {len(book.thinking_content.split()):,}" if book.thinking_content else ""}

### metadata.json
Contiene todos los metadatos del libro incluyendo configuración, estadísticas y análisis de contenido.

## Estructura del Contenido

El libro está estructurado en formato Markdown con:
- Tabla de contenidos
- Introducción
- 10 capítulos principales
- Múltiples secciones con ejemplos de código
- Conclusión

## Formatos Disponibles

Los siguientes archivos han sido generados por el sistema:
{chr(10).join([f"- {fmt.upper()}: {path}" for fmt, path in (book.file_paths or {}).items()])}

## Fecha de Extracción
{metadata['timestamps']['created_at']}
"""
        
        readme_filename = os.path.join(output_dir, "README.md")
        save_content_to_file(readme_content, readme_filename, "README con información")
        
        print("\n" + "=" * 80)
        print("✅ EXTRACCIÓN COMPLETADA")
        print("=" * 80)
        print(f"📁 Todos los archivos guardados en: {output_dir}/")
        print(f"📊 Archivos creados:")
        for filename in os.listdir(output_dir):
            filepath = os.path.join(output_dir, filename)
            size_mb = os.path.getsize(filepath) / 1024 / 1024
            print(f"   - {filename} ({size_mb:.2f} MB)")
        
        print(f"\n📋 Resumen:")
        print(f"   - Contenido principal: {'✅' if book.content else '❌'}")
        print(f"   - Thinking content: {'✅' if book.thinking_content else '❌'}")
        print(f"   - Metadatos: ✅")
        print(f"   - README: ✅")


if __name__ == "__main__":
    main()