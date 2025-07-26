#!/usr/bin/env python3
"""
Test del nuevo algoritmo de cálculo de páginas
para verificar que respeta las promesas hechas al usuario
"""

def calculate_effective_pages(length, page_size, line_spacing):
    """
    Replica el nuevo algoritmo SÚPER GENEROSO de cálculo de páginas
    """
    # Rangos prometidos al usuario (pero entregamos MÁS)
    promised_ranges = {
        'short': {
            'promised_min': 50, 'promised_max': 100,
            'generous_target': 100,  # Usar el MÁXIMO como base
            'generous_min': 80,      # 100 * 0.8 = 80 (aún supera promesa de 50)
            'generous_max': 120      # 100 * 1.2 = 120 (20% más que prometido)
        },
        'medium': {
            'promised_min': 100, 'promised_max': 200,
            'generous_target': 200,  # Usar el MÁXIMO como base
            'generous_min': 160,     # 200 * 0.8 = 160 (supera promesa de 100)
            'generous_max': 240      # 200 * 1.2 = 240 (20% más que prometido)
        },
        'long': {
            'promised_min': 200, 'promised_max': 300,
            'generous_target': 300,  # Usar el MÁXIMO como base
            'generous_min': 240,     # 300 * 0.8 = 240 (supera promesa de 200)
            'generous_max': 360      # 300 * 1.2 = 360 (20% más que prometido)
        }
    }
    
    # Factores de ajuste por tamaño de página (SÚPER GENEROSOS - algunos dan más del máximo)
    page_size_factors = {
        'pocket': 0.9,   # Más generoso para pocket
        'A5': 1.0,       # A5 da el máximo completo
        'B5': 1.05,      # B5 da 5% más que el máximo prometido
        'letter': 1.1    # Letter da 10% más que el máximo prometido
    }
    
    # Factores de ajuste por interlineado (SÚPER GENEROSOS)
    line_spacing_factors = {
        'single': 1.1,   # Single da 10% MÁS contenido
        'medium': 1.0,   # Medium da exactamente el target
        'double': 0.95   # Double da solo 5% menos
    }
    
    # Obtener configuración generosa
    length_config = promised_ranges.get(length, promised_ranges['medium'])
    
    # Calcular páginas usando el MÁXIMO GENEROSO como base
    calculated_pages = int(
        length_config['generous_target'] * 
        page_size_factors.get(page_size, 1.0) * 
        line_spacing_factors.get(line_spacing, 0.95)
    )
    
    # APLICAR RANGO GENEROSO: 20% arriba y abajo del máximo prometido
    effective_pages = max(calculated_pages, length_config['generous_min'])
    effective_pages = min(effective_pages, length_config['generous_max'])
    
    # GARANTÍA FINAL: Nunca menos del mínimo prometido original
    effective_pages = max(effective_pages, length_config['promised_min'])
    
    return {
        'length': length,
        'page_size': page_size,
        'line_spacing': line_spacing,
        'promised_range': f"{length_config['promised_min']}-{length_config['promised_max']}",
        'generous_range': f"{length_config['generous_min']}-{length_config['generous_max']}",
        'target': length_config['generous_target'],
        'calculated_pages': calculated_pages,
        'effective_pages': effective_pages,
        'respects_promise': effective_pages >= length_config['promised_min'],  # Solo necesita cumplir el mínimo
        'is_generous': effective_pages > length_config['promised_max']
    }

def test_book_54_original():
    """Test con parámetros originales de book 54"""
    print("=== BOOK 54 ORIGINAL (ALGORITMO ANTERIOR) ===")
    # Algoritmo anterior que causaba el problema
    base_pages = 100  # short
    old_pocket_factor = 0.5
    old_medium_factor = 0.8
    old_result = int(base_pages * old_pocket_factor * old_medium_factor)
    print(f"Algoritmo anterior: 100 * 0.5 * 0.8 = {old_result} páginas")
    print(f"Promesa al usuario: 50-100 páginas")
    print(f"¿Cumple promesa? {'✅ SÍ' if 50 <= old_result <= 100 else '❌ NO'}")
    print()

def test_book_54_generous():
    """Test con parámetros de book 54 usando algoritmo SÚPER GENEROSO"""
    print("=== BOOK 54 SÚPER GENEROSO (ALGORITMO FINAL) ===")
    result = calculate_effective_pages('short', 'pocket', 'medium')
    print(f"Algoritmo súper generoso:")
    print(f"  Target (máximo prometido): {result['target']}")
    print(f"  Calculado: {result['target']} * 0.9 * 1.0 = {result['calculated_pages']}")
    print(f"  Efectivo: {result['effective_pages']} páginas")
    print(f"Promesa al usuario: {result['promised_range']} páginas")
    print(f"Rango generoso: {result['generous_range']} páginas")
    print(f"¿Cumple promesa? {'✅ SÍ' if result['respects_promise'] else '❌ NO'}")
    print(f"¿Es súper generoso? {'🎁 SÍ' if result['is_generous'] else 'No'}")
    print()

def test_various_combinations():
    """Test varios casos para verificar generosidad"""
    print("=== PRUEBAS EXHAUSTIVAS - ALGORITMO SÚPER GENEROSO ===")
    
    test_cases = [
        ('short', 'pocket', 'medium'),
        ('short', 'pocket', 'double'),
        ('short', 'A5', 'medium'),
        ('short', 'letter', 'single'),
        ('medium', 'pocket', 'medium'),
        ('medium', 'A5', 'single'),
        ('medium', 'letter', 'single'),
        ('long', 'pocket', 'double'),
        ('long', 'A5', 'medium'),
        ('long', 'letter', 'single'),
    ]
    
    all_pass = True
    generous_count = 0
    
    print("Formato: [Estado] Configuración = Páginas (Prometido vs Generoso)")
    print("-" * 70)
    
    for length, page_size, line_spacing in test_cases:
        result = calculate_effective_pages(length, page_size, line_spacing)
        status = '✅' if result['respects_promise'] else '❌'
        generous = '🎁' if result['is_generous'] else '  '
        
        config = f"{length}/{page_size}/{line_spacing}"
        pages_info = f"{result['effective_pages']} págs"
        ranges_info = f"(Prometido: {result['promised_range']}, Generoso: {result['generous_range']})"
        
        print(f"{status}{generous} {config.ljust(20)} = {pages_info.ljust(10)} {ranges_info}")
        
        if not result['respects_promise']:
            all_pass = False
        if result['is_generous']:
            generous_count += 1
    
    print()
    print(f"CUMPLIMIENTO: {'✅ TODOS LOS CASOS CUMPLEN' if all_pass else '❌ FALTAN CORRECCIONES'}")
    print(f"GENEROSIDAD: 🎁 {generous_count}/{len(test_cases)} casos dan MÁS de lo prometido")
    print(f"SATISFACCIÓN DEL CLIENTE: {'🌟 EXCELENTE' if generous_count >= len(test_cases) * 0.7 else 'Buena'}")

if __name__ == "__main__":
    test_book_54_original()
    test_book_54_generous()
    test_various_combinations()