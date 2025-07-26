#!/usr/bin/env python3
"""
Script para corregir la arquitectura del libro ID 52
"""

import sys
import os
import json
import re

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.book_generation import BookGeneration

def fix_architecture():
    """Corrige la arquitectura procesando raw_content"""
    app = create_app('development')
    
    with app.app_context():
        book = db.session.get(BookGeneration, 52)
        if not book or not book.architecture:
            print('❌ Libro o arquitectura no encontrada')
            return
        
        print('🔄 Procesando arquitectura para corregir estructura...')
        
        arch_data = json.loads(book.architecture) if isinstance(book.architecture, str) else book.architecture
        
        if 'raw_content' in arch_data and 'structure' not in arch_data:
            raw_content = arch_data['raw_content']
            print('📝 Arquitectura está en raw_content, procesando...')
            
            # Extraer JSON usando regex
            json_pattern = r'```json\s*([\s\S]*?)\s*```'
            json_match = re.search(json_pattern, raw_content, re.IGNORECASE)
            
            if json_match:
                try:
                    extracted_json = json_match.group(1).strip()
                    parsed = json.loads(extracted_json)
                    
                    # Verificar si tiene wrapper book_architecture
                    if isinstance(parsed, dict) and 'book_architecture' in parsed:
                        corrected_arch = parsed['book_architecture']
                        print('✅ Encontrada arquitectura en wrapper book_architecture')
                    else:
                        corrected_arch = parsed
                        print('✅ Arquitectura extraída directamente')
                    
                    # Verificar que tenga capítulos
                    chapters = corrected_arch.get('structure', {}).get('chapters', [])
                    print(f'📚 Capítulos encontrados: {len(chapters)}')
                    
                    if len(chapters) > 0:
                        # Actualizar la arquitectura con la versión corregida
                        book.architecture = json.dumps(corrected_arch, ensure_ascii=False)
                        db.session.commit()
                        print('✅ Arquitectura actualizada con capítulos correctos')
                        print(f'📖 Primer capítulo: {chapters[0].get("title", "Sin título")}')
                        return True
                    else:
                        print('❌ No se encontraron capítulos en la arquitectura extraída')
                        
                except Exception as e:
                    print(f'❌ Error procesando JSON: {e}')
            else:
                print('❌ No se encontró bloque JSON en raw_content')
        else:
            print('✅ Arquitectura ya está en formato correcto')
            return True
    
    return False

if __name__ == '__main__':
    if fix_architecture():
        print('\n✅ Arquitectura corregida exitosamente')
    else:
        print('\n❌ No se pudo corregir la arquitectura')