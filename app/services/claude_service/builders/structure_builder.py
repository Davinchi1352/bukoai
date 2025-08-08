"""
Structure Builder

Builder especializado para construcción de estructuras de libros.
Extraído de ClaudeService original - responsabilidad única.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class StructureBuilder:
    """
    Builder especializado para construcción de estructuras de libros.
    
    Extrae la lógica de construcción de estructuras que estaba en ClaudeService
    (líneas 2960+ con métodos helper).
    """
    
    def __init__(self):
        """Inicializa el builder de estructura."""
        logger.info("StructureBuilder initialized")
    
    def build_complete_book_structure(self, approved_architecture: Dict[str, Any]) -> str:
        """
        Construye la estructura completa del libro en formato texto.
        
        Extraído de ClaudeService._build_complete_book_structure() líneas 2960+.
        
        Args:
            approved_architecture: Arquitectura aprobada del libro
            
        Returns:
            Estructura del libro en formato texto
        """
        structure_parts = []
        
        # Información básica del libro
        structure_parts.append("=== ESTRUCTURA DEL LIBRO ===\n")
        
        if approved_architecture.get('title'):
            structure_parts.append(f"**Título**: {approved_architecture['title']}")
        
        if approved_architecture.get('genre'):
            structure_parts.append(f"**Género**: {approved_architecture['genre']}")
        
        if approved_architecture.get('target_pages'):
            structure_parts.append(f"**Páginas objetivo**: {approved_architecture['target_pages']}")
        
        if approved_architecture.get('estimated_words'):
            structure_parts.append(f"**Palabras estimadas**: {approved_architecture['estimated_words']:,}")
        
        # Temas principales
        themes = approved_architecture.get('themes', [])
        if themes:
            structure_parts.append(f"**Temas**: {', '.join(themes)}")
        
        structure_parts.append("")  # Línea en blanco
        
        # Estructura de capítulos
        chapters = self._get_chapters_from_architecture(approved_architecture)
        if chapters:
            structure_parts.append("=== CAPÍTULOS ===\n")
            for chapter in chapters:
                chapter_text = self._format_chapter_info(chapter)
                structure_parts.append(chapter_text)
                structure_parts.append("")  # Separador
        
        # Personajes principales
        characters = approved_architecture.get('characters', [])
        if characters:
            structure_parts.append("=== PERSONAJES ===\n")
            character_text = self.format_characters_for_prompt(characters)
            structure_parts.append(character_text)
            structure_parts.append("")
        
        # Configuración (setting)
        setting = approved_architecture.get('setting', {})
        if setting:
            structure_parts.append("=== CONFIGURACIÓN ===\n")
            setting_text = self._format_setting_info(setting)
            structure_parts.append(setting_text)
            structure_parts.append("")
        
        # Elementos especiales
        special_elements = approved_architecture.get('special_elements', [])
        if special_elements:
            structure_parts.append("=== ELEMENTOS ESPECIALES ===\n")
            special_text = self.format_special_sections_for_prompt(special_elements)
            structure_parts.append(special_text)
            structure_parts.append("")
        
        # Estructura narrativa
        plot_structure = approved_architecture.get('plot_structure', {})
        if plot_structure:
            structure_parts.append("=== ESTRUCTURA NARRATIVA ===\n")
            plot_text = self._format_plot_structure(plot_structure)
            structure_parts.append(plot_text)
        
        return "\n".join(structure_parts)
    
    def format_characters_for_prompt(self, characters: List[Dict[str, Any]]) -> str:
        """
        Formatea los personajes para incluir en prompts.
        
        Extraído de ClaudeService._format_characters_for_prompt() líneas 3016+.
        
        Args:
            characters: Lista de personajes
            
        Returns:
            Personajes formateados para prompt
        """
        if not characters:
            return "Sin personajes definidos."
        
        character_texts = []
        
        for character in characters:
            char_parts = []
            
            # Nombre y rol
            name = character.get('name', 'Sin nombre')
            role = character.get('role', 'sin rol definido')
            char_parts.append(f"**{name}** ({role.title()})")
            
            # Descripción
            description = character.get('description', '')
            if description:
                char_parts.append(f"  Descripción: {description}")
            
            # Background
            background = character.get('background', '')
            if background:
                char_parts.append(f"  Historia: {background}")
            
            # Arco del personaje
            arc = character.get('arc', '')
            if arc:
                char_parts.append(f"  Desarrollo: {arc}")
            
            # Relaciones
            relationships = character.get('relationships', '')
            if relationships:
                char_parts.append(f"  Relaciones: {relationships}")
            
            character_texts.append("\n".join(char_parts))
        
        return "\n\n".join(character_texts)
    
    def format_special_sections_for_prompt(self, special_sections: List[Dict[str, Any]]) -> str:
        """
        Formatea las secciones especiales para incluir en prompts.
        
        Extraído de ClaudeService._format_special_sections_for_prompt() líneas 3033+.
        
        Args:
            special_sections: Lista de secciones especiales
            
        Returns:
            Secciones especiales formateadas
        """
        if not special_sections:
            return "Sin secciones especiales definidas."
        
        section_texts = []
        
        for section in special_sections:
            section_parts = []
            
            # Tipo y título
            section_type = section.get('type', 'sección especial')
            title = section.get('title', f'Sin título ({section_type})')
            section_parts.append(f"**{title}** ({section_type.title()})")
            
            # Descripción
            description = section.get('description', '')
            if description:
                section_parts.append(f"  {description}")
            
            section_texts.append("\n".join(section_parts))
        
        return "\n\n".join(section_texts)
    
    def _get_chapters_from_architecture(self, architecture: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extrae los capítulos de la arquitectura en formato compatible.
        
        Args:
            architecture: Arquitectura del libro
            
        Returns:
            Lista de capítulos
        """
        # Compatible con ambos formatos
        chapters = []
        
        if architecture.get('structure', {}).get('chapters'):
            # Formato: architecture.structure.chapters
            chapters = architecture['structure']['chapters']
        elif architecture.get('chapters'):
            # Formato: architecture.chapters (nuevo formato)
            chapters = architecture['chapters']
        
        return chapters
    
    def _format_chapter_info(self, chapter: Dict[str, Any]) -> str:
        """
        Formatea la información de un capítulo individual.
        
        Args:
            chapter: Información del capítulo
            
        Returns:
            Información del capítulo formateada
        """
        chapter_parts = []
        
        # Número y título
        number = chapter.get('number', 'N/A')
        title = chapter.get('title', 'Sin título')
        chapter_parts.append(f"**Capítulo {number}: {title}**")
        
        # Resumen
        summary = chapter.get('summary', '')
        if summary:
            chapter_parts.append(f"  Resumen: {summary}")
        
        # Puntos clave
        key_points = chapter.get('key_points', [])
        if key_points:
            points_text = ', '.join(key_points)
            chapter_parts.append(f"  Puntos clave: {points_text}")
        
        # Páginas estimadas
        estimated_pages = chapter.get('estimated_pages', 0)
        if estimated_pages:
            chapter_parts.append(f"  Páginas estimadas: {estimated_pages}")
        
        # Personajes en foco
        character_focus = chapter.get('character_focus', [])
        if character_focus:
            focus_text = ', '.join(character_focus)
            chapter_parts.append(f"  Personajes principales: {focus_text}")
        
        return "\n".join(chapter_parts)
    
    def _format_setting_info(self, setting: Dict[str, Any]) -> str:
        """
        Formatea la información del setting.
        
        Args:
            setting: Información del setting
            
        Returns:
            Setting formateado
        """
        setting_parts = []
        
        # Tiempo
        time_period = setting.get('time', '')
        if time_period:
            setting_parts.append(f"**Época**: {time_period}")
        
        # Ubicación
        location = setting.get('location', '')
        if location:
            setting_parts.append(f"**Ubicación**: {location}")
        
        # Descripción del mundo
        world_desc = setting.get('world_description', '')
        if world_desc:
            setting_parts.append(f"**Descripción del mundo**: {world_desc}")
        
        # Atmósfera
        atmosphere = setting.get('atmosphere', '')
        if atmosphere:
            setting_parts.append(f"**Atmósfera**: {atmosphere}")
        
        return "\n".join(setting_parts) if setting_parts else "Sin configuración específica definida."
    
    def _format_plot_structure(self, plot_structure: Dict[str, Any]) -> str:
        """
        Formatea la estructura narrativa.
        
        Args:
            plot_structure: Estructura de la trama
            
        Returns:
            Estructura narrativa formateada
        """
        plot_parts = []
        
        # Elementos de la estructura clásica
        structure_elements = [
            ('exposition', 'Exposición'),
            ('rising_action', 'Desarrollo'),
            ('climax', 'Clímax'),
            ('falling_action', 'Resolución'),
            ('resolution', 'Desenlace')
        ]
        
        for key, label in structure_elements:
            value = plot_structure.get(key, '')
            if value:
                plot_parts.append(f"**{label}**: {value}")
        
        return "\n".join(plot_parts) if plot_parts else "Sin estructura narrativa específica definida."
    
    def build_chapter_navigation(self, chapters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Construye un índice de navegación entre capítulos.
        
        Args:
            chapters: Lista de capítulos
            
        Returns:
            Estructura de navegación
        """
        navigation = {
            'total_chapters': len(chapters),
            'chapter_index': {},
            'page_distribution': {}
        }
        
        current_page = 1
        
        for i, chapter in enumerate(chapters):
            chapter_num = chapter.get('number', i + 1)
            chapter_title = chapter.get('title', f'Capítulo {chapter_num}')
            estimated_pages = chapter.get('estimated_pages', 10)
            
            navigation['chapter_index'][chapter_num] = {
                'title': chapter_title,
                'start_page': current_page,
                'end_page': current_page + estimated_pages - 1,
                'page_count': estimated_pages
            }
            
            navigation['page_distribution'][chapter_num] = estimated_pages
            current_page += estimated_pages
        
        navigation['total_pages'] = current_page - 1
        
        return navigation
    
    def validate_structure_completeness(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida que la estructura esté completa y bien formada.
        
        Args:
            structure: Estructura a validar
            
        Returns:
            Resultado de la validación
        """
        validation = {
            'is_complete': True,
            'missing_elements': [],
            'warnings': [],
            'score': 0.0
        }
        
        # Elementos requeridos
        required_elements = ['title', 'genre', 'chapters', 'characters']
        
        for element in required_elements:
            if element not in structure or not structure[element]:
                validation['missing_elements'].append(element)
                validation['is_complete'] = False
        
        # Validaciones específicas
        chapters = structure.get('chapters', [])
        if len(chapters) < 5:
            validation['warnings'].append(f"Pocos capítulos: {len(chapters)} (recomendado: 8+)")
        
        characters = structure.get('characters', [])
        if len(characters) < 2:
            validation['warnings'].append(f"Pocos personajes: {len(characters)} (recomendado: 3+)")
        
        # Calcular score
        if validation['is_complete']:
            base_score = 0.7
            bonus = 0
            
            if len(chapters) >= 8:
                bonus += 0.1
            if len(characters) >= 3:
                bonus += 0.1
            if structure.get('setting'):
                bonus += 0.05
            if structure.get('themes'):
                bonus += 0.05
            
            validation['score'] = min(1.0, base_score + bonus)
        
        return validation
    
    def __str__(self) -> str:
        """String representation del builder."""
        return "StructureBuilder(book_structure_formatting)"