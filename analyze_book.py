#!/usr/bin/env python3
"""
Script para analizar el libro con ID 34 y mostrar su estructura de contenido
"""

import os
import sys
import json
import re
from typing import Dict, Any, Optional

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from main import create_app
from app.models import db, BookGeneration, BookStatus


def analyze_content_structure(content: str) -> Dict[str, Any]:
    """Analiza la estructura del contenido de un libro"""
    if not content:
        return {"error": "No content available"}
    
    analysis = {
        "content_type": "unknown",
        "length": len(content),
        "word_count": len(content.split()),
        "line_count": len(content.splitlines()),
        "structure": {},
        "formatting_elements": {},
        "sample_content": content[:1000] + "..." if len(content) > 1000 else content
    }
    
    # Detectar si es JSON
    try:
        json_data = json.loads(content)
        analysis["content_type"] = "json"
        analysis["structure"] = analyze_json_structure(json_data)
        return analysis
    except json.JSONDecodeError:
        pass
    
    # Detectar si es Markdown
    markdown_patterns = [
        r'^#{1,6}\s+',  # Headers
        r'^\*\s+',      # Bullet points
        r'^\d+\.\s+',   # Numbered lists
        r'\*\*.*?\*\*', # Bold text
        r'\*.*?\*',     # Italic text
        r'```',         # Code blocks
    ]
    
    markdown_count = 0
    for pattern in markdown_patterns:
        if re.search(pattern, content, re.MULTILINE):
            markdown_count += 1
    
    if markdown_count >= 2:
        analysis["content_type"] = "markdown"
        analysis["structure"] = analyze_markdown_structure(content)
        analysis["formatting_elements"] = analyze_markdown_formatting(content)
    else:
        analysis["content_type"] = "plain_text"
        analysis["structure"] = analyze_plain_text_structure(content)
    
    return analysis


def analyze_json_structure(json_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analiza la estructura de contenido JSON"""
    structure = {
        "type": "json_structured",
        "keys": list(json_data.keys()) if isinstance(json_data, dict) else [],
        "chapters": [],
        "sections": []
    }
    
    if isinstance(json_data, dict):
        # Buscar capítulos
        if "chapters" in json_data:
            chapters = json_data["chapters"]
            if isinstance(chapters, list):
                structure["chapter_count"] = len(chapters)
                for i, chapter in enumerate(chapters):
                    if isinstance(chapter, dict):
                        chapter_info = {
                            "index": i,
                            "title": chapter.get("title", f"Chapter {i+1}"),
                            "content_length": len(str(chapter.get("content", "")))
                        }
                        structure["chapters"].append(chapter_info)
        
        # Buscar otras secciones
        for key, value in json_data.items():
            if key != "chapters" and isinstance(value, (str, list, dict)):
                structure["sections"].append({
                    "key": key,
                    "type": type(value).__name__,
                    "length": len(str(value)) if isinstance(value, str) else len(value) if isinstance(value, list) else len(value.keys()) if isinstance(value, dict) else 0
                })
    
    return structure


def analyze_markdown_structure(content: str) -> Dict[str, Any]:
    """Analiza la estructura de contenido Markdown"""
    lines = content.splitlines()
    structure = {
        "type": "markdown",
        "headers": [],
        "chapters": [],
        "sections": []
    }
    
    current_chapter = None
    current_section = None
    
    for i, line in enumerate(lines):
        # Detectar headers
        header_match = re.match(r'^(#{1,6})\s+(.+)', line)
        if header_match:
            level = len(header_match.group(1))
            title = header_match.group(2).strip()
            
            header_info = {
                "level": level,
                "title": title,
                "line_number": i + 1
            }
            structure["headers"].append(header_info)
            
            # Si es un header de nivel 1, considerarlo como capítulo
            if level == 1:
                if current_chapter:
                    structure["chapters"].append(current_chapter)
                current_chapter = {
                    "title": title,
                    "line_start": i + 1,
                    "sections": []
                }
            # Si es un header de nivel 2-3, considerarlo como sección
            elif level <= 3 and current_chapter:
                section_info = {
                    "title": title,
                    "level": level,
                    "line_number": i + 1
                }
                current_chapter["sections"].append(section_info)
    
    # Agregar el último capítulo si existe
    if current_chapter:
        structure["chapters"].append(current_chapter)
    
    structure["chapter_count"] = len(structure["chapters"])
    structure["header_count"] = len(structure["headers"])
    
    return structure


def analyze_markdown_formatting(content: str) -> Dict[str, Any]:
    """Analiza elementos de formateo en Markdown"""
    formatting = {}
    
    # Buscar elementos de formateo
    patterns = {
        "bold": r'\*\*(.+?)\*\*',
        "italic": r'\*(.+?)\*',
        "code_inline": r'`(.+?)`',
        "code_blocks": r'```[\s\S]*?```',
        "links": r'\[(.+?)\]\((.+?)\)',
        "images": r'!\[(.+?)\]\((.+?)\)',
        "bullet_lists": r'^\s*[\*\-\+]\s+',
        "numbered_lists": r'^\s*\d+\.\s+',
        "blockquotes": r'^\s*>\s+',
        "horizontal_rules": r'^[-_*]{3,}$'
    }
    
    for element, pattern in patterns.items():
        matches = re.findall(pattern, content, re.MULTILINE)
        formatting[element] = {
            "count": len(matches),
            "examples": matches[:3] if matches else []  # Primeros 3 ejemplos
        }
    
    return formatting


def analyze_plain_text_structure(content: str) -> Dict[str, Any]:
    """Analiza la estructura de texto plano"""
    lines = content.splitlines()
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    
    structure = {
        "type": "plain_text",
        "paragraph_count": len(paragraphs),
        "average_paragraph_length": sum(len(p) for p in paragraphs) / len(paragraphs) if paragraphs else 0,
        "longest_paragraph": max(len(p) for p in paragraphs) if paragraphs else 0,
        "shortest_paragraph": min(len(p) for p in paragraphs) if paragraphs else 0
    }
    
    # Intentar detectar capítulos por patrones comunes
    chapter_patterns = [
        r'^Capítulo\s+\d+',
        r'^CAPÍTULO\s+\d+',
        r'^Chapter\s+\d+',
        r'^\d+\.\s*[A-Z]',
        r'^[A-Z]{2,}\s*$'  # Líneas en mayúsculas (posibles títulos)
    ]
    
    potential_chapters = []
    for i, line in enumerate(lines):
        for pattern in chapter_patterns:
            if re.match(pattern, line.strip()):
                potential_chapters.append({
                    "line_number": i + 1,
                    "text": line.strip(),
                    "pattern": pattern
                })
                break
    
    structure["potential_chapters"] = potential_chapters
    structure["potential_chapter_count"] = len(potential_chapters)
    
    return structure


def get_book_statistics(book: BookGeneration) -> Dict[str, Any]:
    """Obtiene estadísticas del libro"""
    stats = {
        "basic_info": {
            "id": book.id,
            "title": book.title,
            "genre": book.genre,
            "target_audience": book.target_audience,
            "tone": book.tone,
            "language": book.language,
            "status": book.status.value if book.status else None
        },
        "configuration": {
            "chapter_count": book.chapter_count,
            "page_count": book.page_count,
            "format_size": book.format_size,
            "line_spacing": book.line_spacing,
            "include_toc": book.include_toc,
            "include_introduction": book.include_introduction,
            "include_conclusion": book.include_conclusion,
            "writing_style": book.writing_style
        },
        "final_stats": {
            "final_pages": book.final_pages,
            "final_words": book.final_words,
            "estimated_reading_time": book.estimated_reading_time
        },
        "tokens": {
            "prompt_tokens": book.prompt_tokens,
            "completion_tokens": book.completion_tokens,
            "thinking_tokens": book.thinking_tokens,
            "total_tokens": book.total_tokens,
            "estimated_cost": float(book.estimated_cost) if book.estimated_cost else 0
        },
        "timestamps": {
            "created_at": book.created_at.isoformat() if book.created_at else None,
            "started_at": book.started_at.isoformat() if book.started_at else None,
            "completed_at": book.completed_at.isoformat() if book.completed_at else None,
            "processing_time": book.processing_time
        },
        "files": {
            "file_paths": book.file_paths,
            "cover_url": book.cover_url,
            "available_formats": book.file_formats
        }
    }
    
    return stats


def main():
    """Función principal"""
    print("🔍 Analizando libro con ID 34...")
    
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
        
        # Obtener estadísticas básicas
        stats = get_book_statistics(book)
        
        print("=" * 80)
        print("📖 INFORMACIÓN BÁSICA DEL LIBRO")
        print("=" * 80)
        for key, value in stats["basic_info"].items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        
        print("\n" + "=" * 80)
        print("⚙️  CONFIGURACIÓN")
        print("=" * 80)
        for key, value in stats["configuration"].items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        
        print("\n" + "=" * 80)
        print("📈 ESTADÍSTICAS FINALES")
        print("=" * 80)
        for key, value in stats["final_stats"].items():
            if value is not None:
                print(f"{key.replace('_', ' ').title()}: {value}")
        
        print("\n" + "=" * 80)
        print("🎯 TOKENS Y COSTOS")
        print("=" * 80)
        for key, value in stats["tokens"].items():
            print(f"{key.replace('_', ' ').title()}: {value:,}" if isinstance(value, int) else f"{key.replace('_', ' ').title()}: {value}")
        
        print("\n" + "=" * 80)
        print("📁 ARCHIVOS")
        print("=" * 80)
        print(f"Formatos disponibles: {stats['files']['available_formats']}")
        if stats['files']['file_paths']:
            print("Rutas de archivos:")
            for format_type, path in stats['files']['file_paths'].items():
                print(f"  - {format_type.upper()}: {path}")
        
        # Analizar contenido principal
        if book.content:
            print("\n" + "=" * 80)
            print("📝 ANÁLISIS DEL CONTENIDO PRINCIPAL")
            print("=" * 80)
            content_analysis = analyze_content_structure(book.content)
            
            print(f"Tipo de contenido: {content_analysis['content_type']}")
            print(f"Longitud total: {content_analysis['length']:,} caracteres")
            print(f"Palabras: {content_analysis['word_count']:,}")
            print(f"Líneas: {content_analysis['line_count']:,}")
            
            if content_analysis["structure"]:
                print("\n📋 Estructura:")
                structure = content_analysis["structure"]
                if structure.get("type") == "json_structured":
                    print(f"  - Tipo: JSON estructurado")
                    print(f"  - Claves principales: {structure.get('keys', [])}")
                    if structure.get("chapters"):
                        print(f"  - Capítulos encontrados: {len(structure['chapters'])}")
                        for chapter in structure["chapters"][:5]:  # Mostrar solo los primeros 5
                            print(f"    * {chapter['title']} ({chapter['content_length']} caracteres)")
                
                elif structure.get("type") == "markdown":
                    print(f"  - Tipo: Markdown")
                    print(f"  - Headers totales: {structure.get('header_count', 0)}")
                    print(f"  - Capítulos detectados: {structure.get('chapter_count', 0)}")
                    if structure.get("chapters"):
                        print("  - Lista de capítulos:")
                        for chapter in structure["chapters"][:5]:  # Mostrar solo los primeros 5
                            sections_count = len(chapter.get("sections", []))
                            print(f"    * {chapter['title']} ({sections_count} secciones)")
                
                elif structure.get("type") == "plain_text":
                    print(f"  - Tipo: Texto plano")
                    print(f"  - Párrafos: {structure.get('paragraph_count', 0)}")
                    print(f"  - Promedio por párrafo: {structure.get('average_paragraph_length', 0):.1f} caracteres")
                    if structure.get("potential_chapters"):
                        print(f"  - Posibles capítulos detectados: {len(structure['potential_chapters'])}")
            
            # Mostrar elementos de formateo si es Markdown
            if content_analysis.get("formatting_elements"):
                print("\n🎨 Elementos de formateo encontrados:")
                for element, data in content_analysis["formatting_elements"].items():
                    if data["count"] > 0:
                        print(f"  - {element.replace('_', ' ').title()}: {data['count']}")
            
            print("\n📄 Muestra del contenido (primeros 1000 caracteres):")
            print("-" * 80)
            print(content_analysis["sample_content"])
            print("-" * 80)
        
        # Analizar thinking_content si está disponible
        if book.thinking_content:
            print("\n" + "=" * 80)
            print("🧠 ANÁLISIS DEL THINKING CONTENT")
            print("=" * 80)
            thinking_analysis = analyze_content_structure(book.thinking_content)
            
            print(f"Tipo de contenido: {thinking_analysis['content_type']}")
            print(f"Longitud total: {thinking_analysis['length']:,} caracteres")
            print(f"Palabras: {thinking_analysis['word_count']:,}")
            print(f"Líneas: {thinking_analysis['line_count']:,}")
            
            print("\n📄 Muestra del thinking content (primeros 1000 caracteres):")
            print("-" * 80)
            print(thinking_analysis["sample_content"])
            print("-" * 80)
        else:
            print("\n❌ No hay thinking_content disponible para este libro")
        
        print("\n" + "=" * 80)
        print("✅ ANÁLISIS COMPLETADO")
        print("=" * 80)


if __name__ == "__main__":
    main()