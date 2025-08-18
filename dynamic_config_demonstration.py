#!/usr/bin/env python3
"""
DEMOSTRACIÓN DEL SISTEMA DE CONFIGURACIÓN DINÁMICO

Este script demuestra cómo el nuevo sistema reemplaza los 50+ valores 
hardcodeados con configuración dinámica adaptada a cada usuario.

Ejecutar desde: /home/davinchi/bukoai/
    python dynamic_config_demonstration.py
"""

import sys
import os
sys.path.insert(0, '.')

from app.services.claude_service.config.dynamic_config import (
    UserConfiguration, 
    DynamicConfigurationBuilder,
    create_dynamic_configuration_from_user_form
)

def demo_old_vs_new_system():
    """Demuestra las diferencias entre sistema hardcodeado vs dinámico."""
    
    print("🎯 DEMOSTRACIÓN: SISTEMA DINÁMICO vs HARDCODES")
    print("=" * 80)
    print()
    
    print("📋 PROBLEMA ANTERIOR - VALORES HARDCODEADOS (No escalables):")
    print("-" * 60)
    print("• max_tokens: 28000                    (Para TODOS los libros)")
    print("• thinking_budget: 45000               (Para TODOS los libros)")
    print("• chunk_timeout: 3600                  (Para TODOS los libros)")  
    print("• max_chunks: 7                       (Para TODOS los libros)")
    print("• target_pages: 150                   (Para TODOS los libros)")
    print("• min_chapters: 8                     (Para TODOS los libros)")
    print("• max_chapters: 25                    (Para TODOS los libros)")
    print("• Y 40+ valores más... 🤯")
    print()
    
    # Crear diferentes configuraciones de usuario
    test_cases = [
        {
            'name': '📚 LIBRO CORTO INFANTIL',
            'config': {
                'title': 'Las Aventuras del Ratón Pérez',
                'genre': 'infantil', 
                'language': 'es',
                'description': 'Un cuento mágico para niños',
                'audience': 'children',
                'tone': 'playful',
                'chapters': 6,
                'length': 'short',      # 50-100 páginas
                'pageSize': 'pocket',   # Pequeño como Kindle
                'lineSpacing': 'medium' # Lectura cómoda
            }
        },
        {
            'name': '📖 NOVELA ADULTA MEDIA',
            'config': {
                'title': 'El Misterio del Lago Dorado',
                'genre': 'ficcion',
                'language': 'es', 
                'description': 'Una novela de suspense envolvente',
                'audience': 'adult',
                'tone': 'suspenseful',
                'chapters': 15,
                'length': 'medium',     # 100-200 páginas
                'pageSize': 'A5',       # Estándar
                'lineSpacing': 'single' # Más texto por página
            }
        },
        {
            'name': '📚 LIBRO TÉCNICO LARGO',
            'config': {
                'title': 'Inteligencia Artificial Avanzada',
                'genre': 'academico',
                'language': 'es',
                'description': 'Guía completa de IA para profesionales',
                'audience': 'adult', 
                'tone': 'professional',
                'chapters': 25,
                'length': 'long',       # 200-300 páginas
                'pageSize': 'letter',   # Más contenido
                'lineSpacing': 'medium' # Legibilidad técnica
            }
        }
    ]
    
    print("✨ SOLUCIÓN NUEVA - CONFIGURACIÓN DINÁMICA (Escalable):")
    print("-" * 60)
    
    for test_case in test_cases:
        print(f"\n{test_case['name']}:")
        print(f"  Usuario selecciona: {test_case['config']['chapters']} capítulos, "
              f"{test_case['config']['length']}, {test_case['config']['pageSize']}, "
              f"audiencia {test_case['config']['audience']}")
        
        # Generar configuración dinámica
        dynamic_config = create_dynamic_configuration_from_user_form(test_case['config'])
        
        print(f"  🎯 Sistema adapta automáticamente:")
        print(f"     • target_pages: {dynamic_config.target_pages}")
        print(f"     • max_tokens: {dynamic_config.max_tokens:,}")
        print(f"     • thinking_budget: {dynamic_config.thinking_budget:,}")
        print(f"     • chunk_timeout: {dynamic_config.chunk_timeout}s")
        print(f"     • max_chunks: {dynamic_config.max_chunks}")
        print(f"     • words_per_page: {dynamic_config.words_per_page}")
        print(f"     • total_target_words: {dynamic_config.total_target_words:,}")
        print(f"     • architecture_timeout: {dynamic_config.architecture_timeout}s")
    
    print()
    print("🎊 RESULTADO:")
    print("=" * 80)
    print("✅ ANTES: 1 configuración hardcodeada para TODOS los usuarios")
    print("✅ AHORA: Configuración OPTIMIZADA para cada libro específico")
    print("✅ ESCALABILIDAD: Funciona para miles de usuarios con diferentes necesidades")
    print("✅ CALIDAD: Cada libro recibe la configuración ÓPTIMA para su tipo")
    print()


def demo_token_optimization():
    """Demuestra la optimización de tokens dinámicos."""
    
    print("🧠 DEMOSTRACIÓN: OPTIMIZACIÓN DE TOKENS DINÁMICOS")
    print("=" * 80)
    print()
    
    # Libro corto vs largo
    short_book = create_dynamic_configuration_from_user_form({
        'title': 'Cuento Corto',
        'genre': 'infantil',
        'language': 'es',
        'description': 'Un cuento simple',
        'audience': 'children',
        'tone': 'simple',
        'chapters': 5,
        'length': 'short',
        'pageSize': 'pocket',
        'lineSpacing': 'medium'
    })
    
    long_book = create_dynamic_configuration_from_user_form({
        'title': 'Tratado Académico',
        'genre': 'academico',
        'language': 'es',
        'description': 'Investigación académica profunda',
        'audience': 'adult',
        'tone': 'academic',
        'chapters': 20,
        'length': 'long',
        'pageSize': 'letter',
        'lineSpacing': 'single'
    })
    
    print("📚 LIBRO CORTO INFANTIL:")
    print(f"  • Páginas objetivo: {short_book.target_pages}")
    print(f"  • Max tokens: {short_book.max_tokens:,}")
    print(f"  • Thinking budget: {short_book.thinking_budget:,}")
    print(f"  • Arquitectura timeout: {short_book.architecture_timeout}s")
    print(f"  • Chunk timeout: {short_book.chunk_timeout}s")
    print()
    
    print("📖 LIBRO LARGO ACADÉMICO:")
    print(f"  • Páginas objetivo: {long_book.target_pages}")
    print(f"  • Max tokens: {long_book.max_tokens:,}")
    print(f"  • Thinking budget: {long_book.thinking_budget:,}")
    print(f"  • Arquitectura timeout: {long_book.architecture_timeout}s")
    print(f"  • Chunk timeout: {long_book.chunk_timeout}s")
    print()
    
    # Calcular ahorro/optimización
    token_ratio = long_book.max_tokens / short_book.max_tokens
    time_ratio = long_book.chunk_timeout / short_book.chunk_timeout
    
    print("📊 OPTIMIZACIÓN INTELIGENTE:")
    print(f"  • Tokens optimizados: {token_ratio:.1f}x más para libro complejo")
    print(f"  • Timeouts adaptados: {time_ratio:.1f}x más tiempo para libro largo")
    print(f"  • Resultado: CADA libro recibe exactamente lo que necesita")
    print()


def demo_scalability():
    """Demuestra la escalabilidad del sistema."""
    
    print("🚀 DEMOSTRACIÓN: ESCALABILIDAD PARA MILES DE USUARIOS")
    print("=" * 80)
    print()
    
    print("🌍 DIFERENTES USUARIOS, DIFERENTES NECESIDADES:")
    print("-" * 50)
    
    user_scenarios = [
        ("🇪🇸 Escritor español", "novela", "adult", "medium", "A5"),
        ("🇺🇸 Profesor americano", "academico", "adult", "long", "letter"), 
        ("🇫🇷 Autora francesa", "infantil", "children", "short", "pocket"),
        ("🇩🇪 Investigador alemán", "tecnico", "adult", "long", "B5"),
        ("🇮🇹 Blogger italiana", "biografia", "adult", "medium", "A5"),
    ]
    
    print("Usuario                    | Target Pages | Max Tokens | Chunks | Timeout")
    print("-" * 75)
    
    for user, genre, audience, length, page_size in user_scenarios:
        config = create_dynamic_configuration_from_user_form({
            'title': f'Libro de {user}',
            'genre': genre,
            'language': 'es',
            'description': 'Libro personalizado',
            'audience': audience,
            'tone': 'professional',
            'chapters': 12,
            'length': length,
            'pageSize': page_size,
            'lineSpacing': 'medium'
        })
        
        print(f"{user:<25} | {config.target_pages:>11} | {config.max_tokens:>10,} | {config.max_chunks:>6} | {config.chunk_timeout:>7}s")
    
    print()
    print("✨ CADA USUARIO RECIBE CONFIGURACIÓN ÓPTIMA PARA SU LIBRO ESPECÍFICO")
    print("🎯 SISTEMA ESCALA AUTOMÁTICAMENTE SIN INTERVENCIÓN MANUAL")
    print()


def demo_configuration_mapping():
    """Demuestra el mapeo de configuración completo."""
    
    print("🔧 DEMOSTRACIÓN: MAPEO COMPLETO DE CONFIGURACIÓN")
    print("=" * 80)
    print()
    
    print("📝 DEL FORMULARIO DEL USUARIO A LA CONFIGURACIÓN DEL SISTEMA:")
    print("-" * 70)
    
    # Ejemplo de configuración completa
    user_form_data = {
        'title': 'Mi Libro Personalizado',
        'genre': 'ficcion',
        'language': 'es',
        'description': 'Una historia fascinante',
        'audience': 'adult',
        'tone': 'dramatic',
        'chapters': 12,
        'length': 'medium',
        'pageSize': 'A5',
        'lineSpacing': 'medium',
        'additional_instructions': 'Incluir elementos de suspense'
    }
    
    config = create_dynamic_configuration_from_user_form(user_form_data)
    
    print("🎯 ENTRADA (Formulario del Usuario):")
    for key, value in user_form_data.items():
        print(f"  {key}: {value}")
    
    print()
    print("⚙️ SALIDA (Configuración del Sistema):")
    print(f"  target_pages: {config.target_pages}")
    print(f"  words_per_page: {config.words_per_page}")
    print(f"  total_target_words: {config.total_target_words:,}")
    print(f"  max_tokens: {config.max_tokens:,}")
    print(f"  thinking_budget: {config.thinking_budget:,}")
    print(f"  architecture_timeout: {config.architecture_timeout}s")
    print(f"  chunk_timeout: {config.chunk_timeout}s")
    print(f"  thinking_timeout: {config.thinking_timeout}s")
    print(f"  max_chunks: {config.max_chunks}")
    print(f"  chunk_overlap: {config.chunk_overlap}")
    print(f"  pages_per_chunk: {config.pages_per_chunk}")
    print()
    
    print("🧠 TOKEN LIMITS DINÁMICOS:")
    for content_type, tokens in config.token_limits.items():
        print(f"  {content_type}: {tokens:,} tokens")
    
    print()
    print("📊 UMBRALES DE CALIDAD DINÁMICOS:")
    for threshold, value in config.quality_thresholds.items():
        print(f"  {threshold}: {value}")
    
    print()
    print("🎉 RESULTADO: ¡50+ valores configurados automáticamente!")
    print()


if __name__ == "__main__":
    print("🎯 SISTEMA DE CONFIGURACIÓN DINÁMICO - BUKO AI")
    print("Eliminación de 50+ hardcodes para escalabilidad masiva")
    print("=" * 80)
    print()
    
    demo_old_vs_new_system()
    print("\n" + "="*80 + "\n")
    
    demo_token_optimization()
    print("\n" + "="*80 + "\n")
    
    demo_scalability()
    print("\n" + "="*80 + "\n")
    
    demo_configuration_mapping()
    
    print("🏁 CONCLUSIÓN:")
    print("=" * 80)
    print("✅ ELIMINADOS: 50+ valores hardcodeados")
    print("✅ IMPLEMENTADO: Sistema de configuración dinámico y escalable")
    print("✅ RESULTADO: Cada usuario recibe configuración óptima para su libro")
    print("✅ ESCALABILIDAD: Sistema preparado para miles de usuarios simultáneos")
    print("🎊 SISTEMA LISTO PARA PRODUCCIÓN MASIVA")
    print()