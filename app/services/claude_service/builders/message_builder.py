"""
Message Builder

Builder utilitario para construcción de mensajes genéricos para Claude API.
Facilita la creación consistente de messages y system prompts.
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class MessageBuilder:
    """
    Builder utilitario para construcción de mensajes para Claude API.
    
    Proporciona métodos helper para crear estructuras de mensajes consistentes
    y manejar patrones comunes de construcción de prompts.
    """
    
    def __init__(self):
        """Inicializa el builder de mensajes."""
        logger.info("MessageBuilder initialized")
    
    def create_standard_message_structure(self, system_prompt: str, 
                                        user_prompt: str, 
                                        context_messages: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Crea la estructura estándar de mensajes para Claude API.
        
        Args:
            system_prompt: Prompt del sistema
            user_prompt: Prompt del usuario
            context_messages: Mensajes de contexto adicionales (opcional)
            
        Returns:
            Estructura de mensaje estándar
        """
        messages = []
        
        # Agregar mensajes de contexto si existen
        if context_messages:
            messages.extend(context_messages)
        
        # Agregar mensaje principal del usuario
        messages.append({
            "role": "user",
            "content": user_prompt
        })
        
        return {
            "system": system_prompt,
            "messages": messages
        }
    
    def build_system_prompt_with_sections(self, sections: List[Dict[str, str]]) -> str:
        """
        Construye un system prompt estructurado por secciones.
        
        Args:
            sections: Lista de secciones con 'title' y 'content'
            
        Returns:
            System prompt estructurado
        """
        prompt_parts = []
        
        for section in sections:
            title = section.get('title', 'Sección')
            content = section.get('content', '')
            
            if content:
                # Formatear como sección con título
                prompt_parts.append(f"## {title.upper()}\n\n{content}")
        
        return "\n\n".join(prompt_parts)
    
    def build_user_prompt_with_data(self, template: str, data: Dict[str, Any]) -> str:
        """
        Construye un user prompt usando un template y datos.
        
        Args:
            template: Template del prompt con placeholders {key}
            data: Datos para rellenar el template
            
        Returns:
            User prompt con datos aplicados
        """
        try:
            return template.format(**data)
        except KeyError as e:
            logger.warning(f"Missing template key: {e}")
            # Retornar template original si hay errores
            return template
    
    def add_parameter_section(self, base_prompt: str, params: Dict[str, Any], 
                            section_title: str = "PARÁMETROS") -> str:
        """
        Agrega una sección de parámetros a un prompt existente.
        
        Args:
            base_prompt: Prompt base
            params: Parámetros a agregar
            section_title: Título de la sección
            
        Returns:
            Prompt con sección de parámetros agregada
        """
        param_lines = [f"**{section_title}:**"]
        
        for key, value in params.items():
            if value is not None:
                # Formatear key de manera legible
                readable_key = key.replace('_', ' ').title()
                param_lines.append(f"- {readable_key}: {value}")
        
        param_section = "\n".join(param_lines)
        
        return f"{base_prompt}\n\n{param_section}"
    
    def create_list_section(self, items: List[str], title: str, 
                          bullet_style: str = "-") -> str:
        """
        Crea una sección formateada con lista de elementos.
        
        Args:
            items: Lista de elementos
            title: Título de la sección
            bullet_style: Estilo de viñeta ("-", "*", "•", etc.)
            
        Returns:
            Sección formateada con lista
        """
        if not items:
            return f"**{title}**: Sin elementos definidos."
        
        section_lines = [f"**{title}:**"]
        section_lines.extend([f"{bullet_style} {item}" for item in items])
        
        return "\n".join(section_lines)
    
    def format_json_instruction(self, json_structure: Dict[str, Any], 
                              description: str = "Responde con este formato JSON") -> str:
        """
        Formatea instrucciones para respuestas en JSON.
        
        Args:
            json_structure: Estructura JSON de ejemplo
            description: Descripción de la instrucción
            
        Returns:
            Instrucción formateada para JSON
        """
        # Convertir estructura a string legible
        import json
        json_example = json.dumps(json_structure, indent=2, ensure_ascii=False)
        
        return f"""{description}:

```json
{json_example}
```

IMPORTANTE: Responde ÚNICAMENTE con JSON válido, sin markdown ni comentarios adicionales."""
    
    def create_context_summary(self, context_data: Dict[str, Any], 
                             max_length: int = 500) -> str:
        """
        Crea un resumen de contexto para incluir en prompts.
        
        Args:
            context_data: Datos de contexto
            max_length: Longitud máxima del resumen
            
        Returns:
            Resumen de contexto formateado
        """
        summary_parts = []
        
        # Procesar elementos clave del contexto
        key_elements = ['title', 'genre', 'target_pages', 'main_theme']
        
        for key in key_elements:
            if key in context_data:
                readable_key = key.replace('_', ' ').title()
                value = context_data[key]
                summary_parts.append(f"{readable_key}: {value}")
        
        # Agregar elementos adicionales si hay espacio
        summary_text = " | ".join(summary_parts)
        
        if len(summary_text) > max_length:
            # Truncar y agregar indicador
            summary_text = summary_text[:max_length-3] + "..."
        
        return f"[Contexto: {summary_text}]" if summary_text else ""
    
    def validate_message_structure(self, message_structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida que la estructura de mensaje esté bien formada.
        
        Args:
            message_structure: Estructura de mensaje a validar
            
        Returns:
            Resultado de la validación
        """
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Validar campos requeridos
        if 'system' not in message_structure:
            validation['errors'].append("Falta campo 'system'")
            validation['is_valid'] = False
        
        if 'messages' not in message_structure:
            validation['errors'].append("Falta campo 'messages'")
            validation['is_valid'] = False
        
        # Validar contenido
        system_prompt = message_structure.get('system', '')
        if not system_prompt or len(system_prompt.strip()) < 50:
            validation['warnings'].append("System prompt muy corto")
        
        messages = message_structure.get('messages', [])
        if not messages:
            validation['warnings'].append("No hay mensajes de usuario")
        
        # Validar formato de mensajes
        for i, message in enumerate(messages):
            if not isinstance(message, dict):
                validation['errors'].append(f"Mensaje {i} no es un diccionario")
                validation['is_valid'] = False
                continue
            
            if 'role' not in message:
                validation['errors'].append(f"Mensaje {i} sin campo 'role'")
                validation['is_valid'] = False
            
            if 'content' not in message:
                validation['errors'].append(f"Mensaje {i} sin campo 'content'")
                validation['is_valid'] = False
            
            # Validar roles válidos
            valid_roles = ['user', 'assistant', 'system']
            if message.get('role') not in valid_roles:
                validation['warnings'].append(f"Mensaje {i} tiene rol no estándar: {message.get('role')}")
        
        return validation
    
    def estimate_token_count(self, text: str) -> int:
        """
        Estima el número de tokens en un texto.
        
        Estimación aproximada: ~4 caracteres por token en promedio.
        
        Args:
            text: Texto a evaluar
            
        Returns:
            Estimación de tokens
        """
        if not text:
            return 0
        
        # Estimación simple: ~4 caracteres por token
        return len(text) // 4
    
    def optimize_prompt_length(self, prompt: str, max_tokens: int = 8000) -> str:
        """
        Optimiza la longitud de un prompt para ajustarse a límites de tokens.
        
        Args:
            prompt: Prompt original
            max_tokens: Límite máximo de tokens
            
        Returns:
            Prompt optimizado
        """
        estimated_tokens = self.estimate_token_count(prompt)
        
        if estimated_tokens <= max_tokens:
            return prompt
        
        # Calcular longitud objetivo (con margen de seguridad)
        target_length = int((max_tokens * 4) * 0.9)  # 90% del límite
        
        if len(prompt) <= target_length:
            return prompt
        
        # Truncar manteniendo estructura
        truncated = prompt[:target_length]
        
        # Buscar último punto o salto de línea para corte limpio
        last_period = truncated.rfind('.')
        last_newline = truncated.rfind('\n')
        
        cut_point = max(last_period, last_newline)
        
        if cut_point > target_length * 0.8:  # Si el corte es razonable
            return truncated[:cut_point + 1] + "\n\n[...contenido truncado por límite de tokens...]"
        else:
            return truncated + "\n\n[...contenido truncado por límite de tokens...]"
    
    def __str__(self) -> str:
        """String representation del builder."""
        return "MessageBuilder(generic_message_utilities)"