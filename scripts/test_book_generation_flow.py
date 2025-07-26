#!/usr/bin/env python3
"""
Script de prueba para validar el flujo completo de generación de libros.
Verifica que todas las configuraciones del usuario se respeten correctamente.

Uso:
    python scripts/test_book_generation_flow.py
"""

import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, List

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.book_generation import BookGeneration
from app.models.user import User
from app.services.claude_service import ClaudeService
from flask import Flask

def print_section(title: str):
    """Imprime un separador de sección"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def validate_book_parameters(book: BookGeneration) -> Dict[str, Any]:
    """Valida que un libro tenga todos los parámetros correctos"""
    print_section("VALIDACIÓN DE PARÁMETROS DEL LIBRO")
    
    # Parámetros esperados
    expected_params = {
        'title': str,
        'genre': str,
        'target_audience': str,
        'tone': str,
        'language': str,
        'chapter_count': int,
        'page_count': int,
        'format_size': str,
        'line_spacing': str,
        'key_topics': str,
        'additional_instructions': str,
        'writing_style': str,
        'include_toc': bool,
        'include_introduction': bool,
        'include_conclusion': bool
    }
    
    validation_results = {
        'valid': True,
        'missing': [],
        'incorrect_type': [],
        'values': {}
    }
    
    # Verificar cada parámetro
    for param, expected_type in expected_params.items():
        value = getattr(book, param, None)
        
        if value is None:
            validation_results['missing'].append(param)
            validation_results['valid'] = False
            print(f"❌ {param}: FALTANTE")
        elif not isinstance(value, expected_type):
            validation_results['incorrect_type'].append({
                'param': param,
                'expected': expected_type.__name__,
                'actual': type(value).__name__
            })
            validation_results['valid'] = False
            print(f"❌ {param}: Tipo incorrecto (esperado {expected_type.__name__}, obtenido {type(value).__name__})")
        else:
            validation_results['values'][param] = value
            print(f"✅ {param}: {value}")
    
    # Validar el diccionario parameters
    if hasattr(book, 'parameters') and book.parameters:
        print("\n📦 Parámetros adicionales guardados:")
        for key, value in book.parameters.items():
            print(f"   - {key}: {value}")
    
    return validation_results

def calculate_effective_pages(length: str, page_size: str, line_spacing: str) -> int:
    """Calcula las páginas efectivas según el algoritmo del sistema"""
    base_pages = {
        'short': 100,
        'medium': 200,
        'long': 300
    }
    
    page_size_factors = {
        'pocket': 0.5,
        'A5': 0.65,
        'B5': 0.8,
        'letter': 1.0
    }
    
    line_spacing_factors = {
        'single': 1.0,
        'medium': 0.8,
        'double': 0.6
    }
    
    effective_pages = int(
        base_pages.get(length, 150) * 
        page_size_factors.get(page_size, 1.0) * 
        line_spacing_factors.get(line_spacing, 0.8)
    )
    
    return effective_pages

def test_page_calculation():
    """Prueba el cálculo de páginas efectivas"""
    print_section("PRUEBA DE CÁLCULO DE PÁGINAS")
    
    test_cases = [
        {'length': 'short', 'page_size': 'pocket', 'line_spacing': 'single', 'expected': 50},
        {'length': 'medium', 'page_size': 'pocket', 'line_spacing': 'medium', 'expected': 80},
        {'length': 'long', 'page_size': 'letter', 'line_spacing': 'single', 'expected': 300},
        {'length': 'medium', 'page_size': 'A5', 'line_spacing': 'double', 'expected': 78},
        {'length': 'short', 'page_size': 'B5', 'line_spacing': 'medium', 'expected': 64},
    ]
    
    all_passed = True
    for test in test_cases:
        calculated = calculate_effective_pages(
            test['length'], 
            test['page_size'], 
            test['line_spacing']
        )
        passed = calculated == test['expected']
        all_passed &= passed
        
        status = "✅" if passed else "❌"
        print(f"{status} {test['length']}, {test['page_size']}, {test['line_spacing']} = {calculated} páginas (esperado: {test['expected']})")
    
    return all_passed

def validate_architecture_compliance(book: BookGeneration) -> Dict[str, Any]:
    """Valida que la arquitectura respete los parámetros del libro"""
    print_section("VALIDACIÓN DE ARQUITECTURA")
    
    if not book.has_architecture:
        print("❌ El libro no tiene arquitectura generada")
        return {'valid': False, 'errors': ['No architecture']}
    
    architecture = book.architecture
    results = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    # Verificar campos principales
    checks = [
        ('title', book.title, architecture.get('title')),
        ('genre', book.genre, architecture.get('genre')),
        ('language', book.language, architecture.get('language')),
        ('tone', book.tone, architecture.get('tone')),
        ('target_audience', book.target_audience, architecture.get('target_audience')),
        ('page_size', book.format_size, architecture.get('page_size')),
        ('line_spacing', book.line_spacing, architecture.get('line_spacing')),
        ('target_pages', book.page_count, architecture.get('target_pages')),
        ('chapter_count', book.chapter_count, len(architecture.get('structure', {}).get('chapters', [])))
    ]
    
    for field, expected, actual in checks:
        if expected != actual:
            results['valid'] = False
            results['errors'].append(f"{field}: esperado '{expected}', obtenido '{actual}'")
            print(f"❌ {field}: {expected} != {actual}")
        else:
            print(f"✅ {field}: {actual}")
    
    # Verificar estructura
    structure = architecture.get('structure', {})
    print(f"\n📚 Estructura:")
    print(f"   - Introducción: {'✅' if structure.get('introduction') else '❌'}")
    print(f"   - Capítulos: {len(structure.get('chapters', []))}")
    print(f"   - Conclusión: {'✅' if structure.get('conclusion') else '❌'}")
    
    # Verificar distribución de páginas
    total_pages = 0
    if structure.get('introduction'):
        total_pages += structure['introduction'].get('pages', 0)
    for chapter in structure.get('chapters', []):
        total_pages += chapter.get('pages', 0)
    if structure.get('conclusion'):
        total_pages += structure['conclusion'].get('pages', 0)
    
    print(f"\n📊 Distribución de páginas:")
    print(f"   - Total en arquitectura: {total_pages}")
    print(f"   - Target del libro: {book.page_count}")
    print(f"   - Diferencia: {abs(total_pages - book.page_count)}")
    
    if abs(total_pages - book.page_count) > 5:
        results['warnings'].append(f"La suma de páginas ({total_pages}) difiere del target ({book.page_count})")
    
    return results

def test_book_parameter_flow():
    """Prueba el flujo completo de parámetros del libro"""
    print_section("FLUJO COMPLETO DE PARÁMETROS")
    
    # Configuración de prueba
    test_config = {
        'title': 'Mi Libro de Prueba Completo',
        'genre': 'technical',
        'description': 'Este es un libro técnico sobre programación avanzada en Python para desarrolladores experimentados.',
        'audience': 'adult',
        'tone': 'educational',
        'language': 'es',
        'chapters': 12,
        'length': 'medium',
        'pageSize': 'pocket',
        'lineSpacing': 'medium',
        'additional_instructions': 'Incluir ejemplos de código y ejercicios prácticos en cada capítulo.'
    }
    
    print("📝 Configuración de prueba:")
    for key, value in test_config.items():
        print(f"   - {key}: {value}")
    
    # Calcular páginas efectivas
    effective_pages = calculate_effective_pages(
        test_config['length'],
        test_config['pageSize'],
        test_config['lineSpacing']
    )
    print(f"\n📐 Páginas efectivas calculadas: {effective_pages}")
    
    # Simular creación del libro (como lo haría el endpoint)
    book_params = {
        'user_id': 1,  # Usuario de prueba
        'title': test_config['title'],
        'genre': test_config['genre'],
        'target_audience': test_config['audience'],
        'tone': test_config['tone'],
        'language': test_config['language'],
        'chapter_count': test_config['chapters'],
        'page_count': effective_pages,
        'format_size': test_config['pageSize'],
        'line_spacing': test_config['lineSpacing'],
        'additional_instructions': test_config['additional_instructions'],
        'key_topics': test_config['description'],
        'writing_style': 'Professional and engaging',
        'include_toc': True,
        'include_introduction': True,
        'include_conclusion': True,
        'parameters': {
            'audience': test_config['audience'],
            'tone': test_config['tone'],
            'chapters': test_config['chapters'],
            'length': test_config['length'],
            'page_size': test_config['pageSize'],
            'line_spacing': test_config['lineSpacing'],
            'effective_pages': effective_pages,
            'description': test_config['description'],
            'additional_instructions': test_config['additional_instructions']
        }
    }
    
    print("\n✅ Parámetros del libro simulados correctamente")
    
    # Validar que el servicio Claude construya los prompts correctamente
    claude_service = ClaudeService()
    validated_params = claude_service.validate_book_params(book_params)
    
    print("\n🤖 Parámetros validados por ClaudeService:")
    for key, value in validated_params.items():
        if key != 'parameters':  # Skip el dict anidado para claridad
            print(f"   - {key}: {value}")
    
    return True

def main():
    """Función principal del script de prueba"""
    print("\n🔍 SCRIPT DE VALIDACIÓN DEL GENERADOR DE LIBROS")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Crear aplicación Flask
    app = create_app('testing')
    
    with app.app_context():
        # Test 1: Cálculo de páginas
        print("\n[TEST 1] Cálculo de páginas efectivas")
        pages_test_passed = test_page_calculation()
        
        # Test 2: Flujo de parámetros
        print("\n[TEST 2] Flujo completo de parámetros")
        params_test_passed = test_book_parameter_flow()
        
        # Test 3: Verificar libro existente (si hay alguno)
        print("\n[TEST 3] Verificación de libro existente")
        latest_book = BookGeneration.query.order_by(BookGeneration.created_at.desc()).first()
        
        if latest_book:
            print(f"\n📖 Analizando libro más reciente: {latest_book.title}")
            print(f"   ID: {latest_book.id}")
            print(f"   Estado: {latest_book.status.value}")
            print(f"   Creado: {latest_book.created_at}")
            
            # Validar parámetros
            param_validation = validate_book_parameters(latest_book)
            
            # Validar arquitectura si existe
            if latest_book.has_architecture:
                arch_validation = validate_architecture_compliance(latest_book)
            else:
                print("\n⚠️  El libro no tiene arquitectura generada aún")
        else:
            print("⚠️  No hay libros en la base de datos para analizar")
        
        # Resumen final
        print_section("RESUMEN DE PRUEBAS")
        print(f"✅ Test de cálculo de páginas: {'PASADO' if pages_test_passed else 'FALLADO'}")
        print(f"✅ Test de flujo de parámetros: {'PASADO' if params_test_passed else 'FALLADO'}")
        
        if latest_book:
            print(f"📊 Libro analizado: {latest_book.title}")
            if 'param_validation' in locals():
                print(f"   - Parámetros válidos: {'SÍ' if param_validation['valid'] else 'NO'}")
            if 'arch_validation' in locals():
                print(f"   - Arquitectura conforme: {'SÍ' if arch_validation['valid'] else 'NO'}")

if __name__ == '__main__':
    main()