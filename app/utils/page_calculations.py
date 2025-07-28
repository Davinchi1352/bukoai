"""
Utilidades centralizadas para cálculos de páginas y palabras.
"""

def get_words_per_page(page_size: str, line_spacing: str) -> int:
    """
    Retorna la cantidad de palabras por página basado en formato y espaciado.
    
    ESTOS VALORES DEBEN SER CONSISTENTES EN TODO EL SISTEMA.
    """
    words_per_page_matrix = {
        # Valores conservadores pero realistas
        ('pocket', 'single'): 280,   ('pocket', 'medium'): 240,   ('pocket', 'double'): 180,
        ('A5', 'single'): 350,       ('A5', 'medium'): 300,       ('A5', 'double'): 220,
        ('B5', 'single'): 420,       ('B5', 'medium'): 360,       ('B5', 'double'): 270,
        ('letter', 'single'): 500,   ('letter', 'medium'): 420,   ('letter', 'double'): 320,
    }
    
    return words_per_page_matrix.get((page_size, line_spacing), 300)  # Default


def calculate_pages_from_words(word_count: int, page_size: str, line_spacing: str) -> int:
    """
    Calcula páginas reales basado en formato específico.
    """
    words_per_page = get_words_per_page(page_size, line_spacing)
    return max(1, word_count // words_per_page) if word_count > 0 else 0


def calculate_target_words(target_pages: int, page_size: str, line_spacing: str) -> int:
    """
    Calcula palabras necesarias para alcanzar páginas target.
    """
    words_per_page = get_words_per_page(page_size, line_spacing)
    return target_pages * words_per_page