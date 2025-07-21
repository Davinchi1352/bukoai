#!/usr/bin/env python3
"""
Script para exportar y mostrar el contenido completo del libro con ID 34
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


def extract_chapters_from_markdown(content: str) -> list:
    """Extrae capítulos de contenido Markdown"""
    lines = content.splitlines()
    chapters = []
    current_chapter = None
    current_content = []
    
    for line in lines:
        # Detectar headers de nivel 1 (capítulos principales)
        header_match = re.match(r'^#\s+(.+)', line)
        if header_match:
            # Guardar capítulo anterior si existe
            if current_chapter:
                current_chapter['content'] = '\n'.join(current_content).strip()
                chapters.append(current_chapter)
            
            # Iniciar nuevo capítulo
            current_chapter = {
                'title': header_match.group(1).strip(),
                'content': ''
            }
            current_content = []
        else:
            # Agregar línea al contenido actual
            if current_chapter:
                current_content.append(line)
    
    # Agregar último capítulo
    if current_chapter:
        current_chapter['content'] = '\n'.join(current_content).strip()
        chapters.append(current_chapter)
    
    return chapters


def extract_sections_from_content(content: str) -> Dict[str, Any]:
    """Extrae secciones importantes del contenido"""
    sections = {
        'table_of_contents': '',
        'introduction': '',
        'chapters': [],
        'conclusion': '',
        'full_structure': []
    }
    
    lines = content.splitlines()
    current_section = None
    current_content = []
    
    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        
        # Detectar tabla de contenidos
        if 'tabla de contenidos' in line_lower or 'table of contents' in line_lower:
            current_section = 'toc'
            current_content = [line]
            continue
        
        # Detectar introducción
        if line_lower.startswith('# introducción') or line_lower.startswith('## introducción'):
            if current_section == 'toc':
                sections['table_of_contents'] = '\n'.join(current_content)
            current_section = 'introduction'
            current_content = [line]
            continue
        
        # Detectar capítulos
        if re.match(r'^#\s+(capítulo|chapter)\s+\d+', line, re.IGNORECASE):
            if current_section == 'introduction':
                sections['introduction'] = '\n'.join(current_content)
            current_section = 'chapter'
            current_content = [line]
            continue
        
        # Detectar conclusión
        if line_lower.startswith('# conclusión') or line_lower.startswith('## conclusión'):
            current_section = 'conclusion'
            current_content = [line]
            continue
        
        # Agregar línea al contenido actual
        if current_section:
            current_content.append(line)
        
        # Registrar estructura general
        if line.startswith('#'):
            level = len(line.split()[0])
            title = line.strip('#').strip()
            sections['full_structure'].append({
                'level': level,
                'title': title,
                'line': i + 1
            })
    
    # Procesar último contenido
    if current_section == 'conclusion':
        sections['conclusion'] = '\n'.join(current_content)
    
    return sections


def format_content_sample(content: str, max_length: int = 2000) -> str:
    """Formatea una muestra del contenido para visualización"""
    if len(content) <= max_length:
        return content
    
    # Truncar en la última línea completa
    truncated = content[:max_length]
    last_newline = truncated.rfind('\n')
    if last_newline > 0:
        truncated = truncated[:last_newline]
    
    return truncated + f"\n\n[... contenido truncado - {len(content) - len(truncated)} caracteres restantes ...]"


def main():
    """Función principal"""
    print("📖 Exportando contenido completo del libro con ID 34...")
    
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
        print(f"📝 Contenido disponible: {'Sí' if book.content else 'No'}")
        print(f"🧠 Thinking content disponible: {'Sí' if book.thinking_content else 'No'}")
        print()
        
        if not book.content:
            print("❌ El libro no tiene contenido disponible para analizar")
            return
        
        # Análisis general del contenido
        print("=" * 100)
        print("📊 RESUMEN GENERAL DEL CONTENIDO")
        print("=" * 100)
        print(f"Longitud total: {len(book.content):,} caracteres")
        print(f"Número de palabras: {len(book.content.split()):,}")
        print(f"Número de líneas: {len(book.content.splitlines()):,}")
        print()
        
        # Extraer secciones
        sections = extract_sections_from_content(book.content)
        
        # Mostrar estructura completa
        print("=" * 100)
        print("📋 ESTRUCTURA COMPLETA DEL DOCUMENTO")
        print("=" * 100)
        if sections['full_structure']:
            for item in sections['full_structure']:
                indent = "  " * (item['level'] - 1)
                print(f"{indent}{'#' * item['level']} {item['title']} (línea {item['line']})")
        print()
        
        # Mostrar tabla de contenidos
        if sections['table_of_contents']:
            print("=" * 100)
            print("📚 TABLA DE CONTENIDOS")
            print("=" * 100)
            print(format_content_sample(sections['table_of_contents'], 1500))
            print()
        
        # Mostrar introducción
        if sections['introduction']:
            print("=" * 100)
            print("🎯 INTRODUCCIÓN")
            print("=" * 100)
            print(format_content_sample(sections['introduction'], 2000))
            print()
        
        # Extraer y mostrar capítulos
        chapters = extract_chapters_from_markdown(book.content)
        
        if chapters:
            print("=" * 100)
            print(f"📖 CAPÍTULOS DETECTADOS ({len(chapters)} en total)")
            print("=" * 100)
            
            for i, chapter in enumerate(chapters[:5]):  # Mostrar solo los primeros 5 capítulos completos
                print(f"\n📄 CAPÍTULO {i+1}: {chapter['title']}")
                print("-" * 80)
                if chapter['content']:
                    content_sample = format_content_sample(chapter['content'], 1500)
                    print(content_sample)
                else:
                    print("(Sin contenido disponible)")
                print("-" * 80)
            
            if len(chapters) > 5:
                print(f"\n... y {len(chapters) - 5} capítulos adicionales")
                print("\nÍndice de capítulos restantes:")
                for i, chapter in enumerate(chapters[5:], 6):
                    print(f"  {i}. {chapter['title']} ({len(chapter['content'])} caracteres)")
        
        # Mostrar conclusión
        if sections['conclusion']:
            print("\n" + "=" * 100)
            print("🎯 CONCLUSIÓN")
            print("=" * 100)
            print(format_content_sample(sections['conclusion'], 2000))
            print()
        
        # Análisis de formateo Markdown
        print("=" * 100)
        print("🎨 ELEMENTOS DE FORMATEO MARKDOWN")
        print("=" * 100)
        
        # Buscar elementos específicos
        formatting_stats = {
            'headers': len(re.findall(r'^#+\s+', book.content, re.MULTILINE)),
            'bold_text': len(re.findall(r'\*\*[^*]+\*\*', book.content)),
            'italic_text': len(re.findall(r'\*[^*]+\*', book.content)),
            'code_blocks': len(re.findall(r'```[\s\S]*?```', book.content)),
            'inline_code': len(re.findall(r'`[^`]+`', book.content)),
            'bullet_lists': len(re.findall(r'^\s*[\*\-\+]\s+', book.content, re.MULTILINE)),
            'numbered_lists': len(re.findall(r'^\s*\d+\.\s+', book.content, re.MULTILINE)),
            'horizontal_rules': len(re.findall(r'^---+$', book.content, re.MULTILINE)),
            'links': len(re.findall(r'\[([^\]]+)\]\(([^)]+)\)', book.content)),
        }
        
        for element, count in formatting_stats.items():
            print(f"{element.replace('_', ' ').title()}: {count}")
        
        # Mostrar algunos ejemplos de código si existen
        code_blocks = re.findall(r'```([\s\S]*?)```', book.content)
        if code_blocks:
            print(f"\n🔍 EJEMPLOS DE CÓDIGO ENCONTRADOS ({len(code_blocks)} bloques):")
            for i, code in enumerate(code_blocks[:3]):  # Mostrar solo los primeros 3
                print(f"\n--- Bloque de código {i+1} ---")
                print(code.strip()[:500] + "..." if len(code) > 500 else code.strip())
        
        # Información de archivos generados
        print("\n" + "=" * 100)
        print("📁 ARCHIVOS GENERADOS")
        print("=" * 100)
        if book.file_paths:
            for format_type, path in book.file_paths.items():
                # Verificar si el archivo existe
                full_path = os.path.join(os.path.dirname(__file__), path)
                exists = os.path.exists(full_path)
                size_info = ""
                if exists:
                    size = os.path.getsize(full_path)
                    size_mb = size / (1024 * 1024)
                    size_info = f" ({size_mb:.2f} MB)"
                
                print(f"{format_type.upper()}: {path}{size_info} {'✅' if exists else '❌'}")
        else:
            print("No hay archivos generados disponibles")
        
        print("\n" + "=" * 100)
        print("✅ EXPORTACIÓN COMPLETADA")
        print("=" * 100)
        print(f"Total de contenido analizado: {len(book.content):,} caracteres")
        print(f"Capítulos estructurados: {len(chapters) if chapters else 0}")
        print(f"Elementos de formateo detectados: {sum(formatting_stats.values())}")


if __name__ == "__main__":
    main()