"""
Regeneration Builder

Builder especializado para construcción de prompts de regeneración de arquitecturas.
Extraído de ClaudeService original - responsabilidad única.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class RegenerationBuilder:
    """
    Builder especializado para prompts de regeneración de arquitecturas.
    
    Extrae la lógica de construcción de prompts de regeneración que estaba en ClaudeService
    (líneas 1153-1417 con métodos helper).
    """
    
    def __init__(self):
        """Inicializa el builder de regeneración."""
        logger.info("RegenerationBuilder initialized")
    
    def build_regeneration_messages(self, book_params: Dict[str, Any], 
                                   current_architecture: Dict[str, Any], 
                                   feedback_what: str, feedback_how: str) -> Dict[str, Any]:
        """
        Construye los mensajes para regeneración de arquitectura.
        
        Extraído de ClaudeService._build_regeneration_messages() líneas 1153-1175.
        
        Args:
            book_params: Parámetros originales del libro
            current_architecture: Arquitectura actual a regenerar
            feedback_what: Qué cambiar específicamente
            feedback_how: Cómo hacer los cambios
            
        Returns:
            Diccionario con system prompt y messages
        """
        return {
            "system": self.build_regeneration_system_prompt(),
            "messages": [
                {
                    "role": "user", 
                    "content": self.build_regeneration_user_prompt(
                        book_params, current_architecture, feedback_what, feedback_how
                    )
                }
            ]
        }
    
    def build_regeneration_system_prompt(self) -> str:
        """
        Construye el system prompt para regeneración de arquitectura.
        
        Extraído de ClaudeService._build_regeneration_system_prompt() líneas 1176-1304.
        
        Returns:
            System prompt para regeneración
        """
        return """Eres un arquitecto experto de libros especializado en perfeccionar y regenerar estructuras de libros basándote en feedback específico del usuario.

Tu trabajo es tomar una arquitectura existente y mejorarla según las indicaciones precisas del usuario, manteniendo lo que funciona y cambiando solo lo que se solicita.

## INSTRUCCIONES CRÍTICAS:

### 1. FORMATO DE RESPUESTA OBLIGATORIO
Debes responder EXACTAMENTE con este formato JSON válido (sin markdown, sin comentarios):

{
  "title": "Título definitivo del libro", 
  "genre": "género_específico",
  "target_audience": "audiencia_objetivo",
  "target_pages": número_páginas_estimadas,
  "estimated_words": número_palabras_estimadas,
  "tone": "tono_narrativo",
  "perspective": "perspectiva_narrativa",
  "chapters": [
    {
      "number": 1,
      "title": "Título del capítulo",
      "summary": "Resumen detallado de lo que sucede en el capítulo",
      "key_points": ["punto_clave_1", "punto_clave_2"],
      "estimated_pages": páginas_estimadas,
      "character_focus": ["personaje_principal", "personaje_secundario"]
    }
  ],
  "characters": [
    {
      "name": "Nombre del personaje",
      "role": "protagonista/antagonista/secundario",
      "description": "Descripción física y psicológica detallada",
      "background": "Historia personal y motivaciones",
      "arc": "Evolución del personaje a través de la historia",
      "relationships": "Relaciones con otros personajes"
    }
  ],
  "setting": {
    "time": "época_temporal", 
    "location": "ubicación_geográfica",
    "world_description": "Descripción detallada del mundo/ambiente",
    "atmosphere": "Atmósfera y mood general"
  },
  "themes": ["tema_principal", "tema_secundario"],
  "plot_structure": {
    "exposition": "Planteamiento inicial",
    "rising_action": "Desarrollo y complicaciones", 
    "climax": "Punto álgido de la historia",
    "falling_action": "Resolución de conflictos",
    "resolution": "Desenlace final"
  },
  "special_elements": [
    {
      "type": "prólogo/epílogo/dedicatoria",
      "title": "título_elemento",
      "description": "qué_incluye"
    }
  ]
}

### 2. PRINCIPIOS DE REGENERACIÓN:
- **Conservación inteligente**: Mantén lo que funciona de la arquitectura actual
- **Cambios específicos**: Implementa exactamente lo que el usuario solicita
- **Coherencia global**: Asegúrate de que todos los cambios mantengan la coherencia narrativa
- **Mejora continua**: Si detectas oportunidades de mejora que no contradigan el feedback, inclúyelas
- **Balance narrativo**: Mantén proporciones adecuadas entre capítulos y desarrollo de personajes

### 3. ANÁLISIS DEL FEEDBACK:
- **QUÉ cambiar**: Identifica exactamente los elementos específicos a modificar
- **CÓMO cambiar**: Implementa los métodos y enfoques sugeridos por el usuario
- **IMPACTO**: Considera cómo los cambios afectan el resto de la narrativa
- **COHERENCIA**: Ajusta otros elementos que puedan verse afectados por los cambios

### 4. CALIDAD MANTENIDA:
- La arquitectura regenerada debe mantener o superar la calidad de la original
- Estructura narrativa sólida con desarrollo coherente
- Personajes bien desarrollados con arcos satisfactorios
- Temas profundos y relevantes para el género
- Pacing apropiado y distribución equilibrada de contenido

### 5. VALIDACIÓN:
- Todos los cambios solicitados están implementados
- La coherencia narrativa se mantiene
- El número de páginas objetivo se respeta
- La calidad general de la arquitectura es profesional

Recuerda: Estás perfeccionando una arquitectura existente, no creando una nueva desde cero. Mantén la esencia de lo que funciona y mejora específicamente lo que se solicita."""
    
    def build_regeneration_user_prompt(self, book_params: Dict[str, Any], 
                                     current_architecture: Dict[str, Any], 
                                     feedback_what: str, feedback_how: str) -> str:
        """
        Construye el user prompt para regeneración de arquitectura.
        
        Extraído de ClaudeService._build_regeneration_user_prompt() líneas 1305-1417.
        
        Args:
            book_params: Parámetros originales del libro
            current_architecture: Arquitectura actual
            feedback_what: Qué cambiar
            feedback_how: Cómo cambiarlo
            
        Returns:
            User prompt para regeneración
        """
        # Extraer información básica
        current_title = current_architecture.get('title', book_params.get('title', 'Sin título'))
        current_genre = current_architecture.get('genre', book_params.get('genre', 'ficción'))
        target_pages = current_architecture.get('target_pages', book_params.get('target_pages', 150))
        
        # Preparar resumen de la arquitectura actual
        current_summary = self._summarize_current_architecture(current_architecture)
        
        # Preparar feedback estructurado
        feedback_section = self._format_feedback_section(feedback_what, feedback_how)
        
        prompt = f"""Regenera y mejora la siguiente arquitectura de libro según el feedback específico del usuario:

**INFORMACIÓN DEL LIBRO:**
- Título actual: "{current_title}"
- Género: {current_genre}
- Páginas objetivo: {target_pages}

**ARQUITECTURA ACTUAL:**
{current_summary}

**FEEDBACK DEL USUARIO:**
{feedback_section}

**INSTRUCCIONES ESPECÍFICAS:**

1. **Analizar el feedback**: Identifica exactamente qué elementos cambiar y cómo
2. **Mantener lo bueno**: Conserva los aspectos de la arquitectura que funcionan bien
3. **Implementar cambios**: Aplica específicamente las modificaciones solicitadas
4. **Validar coherencia**: Asegúrate de que todos los cambios mantengan la coherencia narrativa
5. **Optimizar estructura**: Aprovecha la regeneración para perfeccionar la estructura general

**CALIDAD REQUERIDA:**
- Arquitectura profesional que incorpore completamente el feedback
- Coherencia narrativa mantenida o mejorada
- Desarrollo de personajes consistente con los cambios
- Estructura balanceada para {target_pages} páginas
- Mejoras en los aspectos específicamente solicitados

Responde ÚNICAMENTE con el JSON de la arquitectura regenerada, sin explicaciones adicionales."""

        return prompt
    
    def _summarize_current_architecture(self, architecture: Dict[str, Any]) -> str:
        """
        Crea un resumen estructurado de la arquitectura actual.
        
        Args:
            architecture: Arquitectura actual a resumir
            
        Returns:
            Resumen formateado de la arquitectura
        """
        summary_parts = []
        
        # Información básica
        if architecture.get('title'):
            summary_parts.append(f"**Título**: {architecture['title']}")
        if architecture.get('genre'):
            summary_parts.append(f"**Género**: {architecture['genre']}")
        if architecture.get('target_pages'):
            summary_parts.append(f"**Páginas**: {architecture['target_pages']}")
        
        # Capítulos
        chapters = architecture.get('chapters', [])
        if chapters:
            summary_parts.append(f"\n**Capítulos ({len(chapters)} total):**")
            for i, chapter in enumerate(chapters[:5]):  # Mostrar solo primeros 5
                chapter_title = chapter.get('title', f'Capítulo {i+1}')
                chapter_summary = chapter.get('summary', 'Sin resumen')
                summary_parts.append(f"- {chapter_title}: {chapter_summary[:100]}...")
            
            if len(chapters) > 5:
                summary_parts.append(f"- ... y {len(chapters) - 5} capítulos más")
        
        # Personajes
        characters = architecture.get('characters', [])
        if characters:
            summary_parts.append(f"\n**Personajes ({len(characters)} total):**")
            for character in characters[:3]:  # Mostrar solo primeros 3
                name = character.get('name', 'Sin nombre')
                role = character.get('role', 'sin rol')
                desc = character.get('description', 'sin descripción')
                summary_parts.append(f"- {name} ({role}): {desc[:80]}...")
            
            if len(characters) > 3:
                summary_parts.append(f"- ... y {len(characters) - 3} personajes más")
        
        # Temas y configuración
        themes = architecture.get('themes', [])
        if themes:
            summary_parts.append(f"\n**Temas**: {', '.join(themes)}")
        
        setting = architecture.get('setting', {})
        if setting:
            setting_desc = []
            if setting.get('time'):
                setting_desc.append(f"Tiempo: {setting['time']}")
            if setting.get('location'):
                setting_desc.append(f"Lugar: {setting['location']}")
            if setting_desc:
                summary_parts.append(f"\n**Configuración**: {', '.join(setting_desc)}")
        
        return "\n".join(summary_parts)
    
    def _format_feedback_section(self, feedback_what: str, feedback_how: str) -> str:
        """
        Formatea la sección de feedback de manera estructurada.
        
        Args:
            feedback_what: Qué cambiar
            feedback_how: Cómo cambiarlo
            
        Returns:
            Feedback formateado
        """
        feedback_parts = []
        
        if feedback_what and feedback_what.strip():
            feedback_parts.append(f"**QUÉ cambiar:**\n{feedback_what.strip()}")
        
        if feedback_how and feedback_how.strip():
            feedback_parts.append(f"**CÓMO cambiar:**\n{feedback_how.strip()}")
        
        return "\n\n".join(feedback_parts) if feedback_parts else "Sin feedback específico proporcionado."
    
    def validate_regeneration_result(self, original_architecture: Dict[str, Any], 
                                   regenerated_architecture: Dict[str, Any], 
                                   feedback_what: str, feedback_how: str) -> Dict[str, Any]:
        """
        Valida que la arquitectura regenerada cumpla con los requisitos.
        
        Args:
            original_architecture: Arquitectura original
            regenerated_architecture: Arquitectura regenerada
            feedback_what: Feedback sobre qué cambiar
            feedback_how: Feedback sobre cómo cambiar
            
        Returns:
            Resultado de la validación con score y observaciones
        """
        validation_results = {
            'valid': True,
            'score': 0.0,
            'issues': [],
            'improvements': []
        }
        
        # Validaciones básicas
        required_fields = ['title', 'genre', 'chapters', 'characters']
        for field in required_fields:
            if field not in regenerated_architecture:
                validation_results['issues'].append(f"Campo requerido faltante: {field}")
                validation_results['valid'] = False
        
        # Validar que hay capítulos
        chapters = regenerated_architecture.get('chapters', [])
        if len(chapters) == 0:
            validation_results['issues'].append("No se encontraron capítulos en la arquitectura")
            validation_results['valid'] = False
        elif len(chapters) < 5:
            validation_results['issues'].append(f"Pocos capítulos: {len(chapters)} (mínimo recomendado: 5)")
        
        # Validar personajes
        characters = regenerated_architecture.get('characters', [])
        if len(characters) == 0:
            validation_results['issues'].append("No se encontraron personajes en la arquitectura")
            validation_results['valid'] = False
        
        # Calcular score básico
        if validation_results['valid']:
            validation_results['score'] = 0.8  # Base score
            
            # Bonus por completitud
            if len(chapters) >= 10:
                validation_results['score'] += 0.1
            if len(characters) >= 3:
                validation_results['score'] += 0.1
            
            validation_results['score'] = min(1.0, validation_results['score'])
        
        return validation_results
    
    def __str__(self) -> str:
        """String representation del builder."""
        return "RegenerationBuilder(regeneration_prompts)"