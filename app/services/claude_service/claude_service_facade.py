"""
Claude Service Facade

Facade unificado que integra todos los componentes extraídos del refactoring.
Proporciona la misma interfaz pública que el ClaudeService original manteniendo
compatibilidad completa.
"""

import logging
from typing import Dict, Any

# Importar todos los componentes extraídos
from .config.claude_config import ClaudeConfig
from .clients.claude_client import ClaudeClient
from .generators.architecture_generator import ArchitectureGenerator
from .generators.content_generator import ContentGenerator
from .builders.regeneration_builder import RegenerationBuilder
from .builders.structure_builder import StructureBuilder
from .builders.message_builder import MessageBuilder

logger = logging.getLogger(__name__)


class MockClaudeClient:
    """Cliente mock para testing sin API key real."""
    
    def __init__(self, config):
        self.config = config
        # Mock circuit breaker
        from .clients.circuit_breaker import CircuitBreaker, CircuitState
        self.circuit_breaker = CircuitBreaker(name="mock_circuit")
        # Mock client
        self.client = MockAnthropicClient()
    
    async def create_message(self, **kwargs):
        """Mock create message."""
        return MockResponse("Mock response content")
    
    def get_circuit_breaker_stats(self):
        """Mock circuit breaker stats."""
        return {
            'state': 'closed',
            'error_count': 0,
            'failure_threshold': 5,
            'success_count': 0,
            'failure_count': 0
        }
    
    def force_circuit_reset(self):
        """Mock circuit reset."""
        pass

class MockAnthropicClient:
    """Mock Anthropic client for testing."""
    
    class messages:
        @staticmethod
        async def create(**kwargs):
            return MockResponse("Mock architecture or content")
        
        @staticmethod
        def stream(**kwargs):
            async def mock_stream():
                yield MockStreamEvent("Mock chunk 1")
                yield MockStreamEvent("Mock chunk 2")
            return mock_stream()

class MockResponse:
    """Mock response from Claude API."""
    
    def __init__(self, text_content):
        self.content = [MockContent(text_content)]

class MockContent:
    """Mock content object."""
    
    def __init__(self, text):
        self.text = text

class MockStreamEvent:
    """Mock stream event."""
    
    def __init__(self, text):
        self.type = "content_block_delta"
        self.delta = MockDelta(text)

class MockDelta:
    """Mock delta object."""
    
    def __init__(self, text):
        self.text = text


class ClaudeServiceFacade:
    """
    Facade unificado para el servicio Claude refactorizado.
    
    Integra todos los componentes extraídos y proporciona la misma interfaz
    pública que el ClaudeService original, manteniendo compatibilidad completa.
    
    Componentes integrados:
    - ClaudeConfig: Configuración centralizada
    - ClaudeClient: Cliente con circuit breaker
    - ArchitectureGenerator: Generación de arquitecturas
    - ContentGenerator: Generación multi-chunk de contenido
    - RegenerationBuilder: Builder para regeneración
    - StructureBuilder: Builder para estructuras
    - MessageBuilder: Builder de mensajes genéricos
    """
    
    def __init__(self, testing_mode: bool = False):
        """
        Inicializa el facade con todos los componentes.
        
        Mantiene la misma inicialización que el ClaudeService original
        pero usando los componentes extraídos.
        
        Args:
            testing_mode: Si True, no requiere API key para testing
        """
        # Configuración centralizada (Phase 1)
        self.config = ClaudeConfig()
        
        # En modo testing, no requerir API key
        if testing_mode:
            self.config.validate(require_api_key=False)
            # Crear un cliente mock para testing
            self.claude_client = MockClaudeClient(self.config)
        else:
            # Cliente con circuit breaker (Phase 2) 
            self.claude_client = ClaudeClient(self.config)
        
        # Generadores especializados (Phase 3)
        self.architecture_generator = ArchitectureGenerator(self.config, self.claude_client)
        self.content_generator = ContentGenerator(self.config, self.claude_client)
        
        # Builders especializados (Phase 4)
        self.regeneration_builder = RegenerationBuilder()
        self.structure_builder = StructureBuilder()
        self.message_builder = MessageBuilder()
        
        # Configuraciones compatibles con el original
        self.model = self.config.model
        self.max_tokens = self.config.max_tokens
        self.temperature = self.config.temperature
        self.thinking_budget = self.config.thinking_budget
        self.architecture_timeout = self.config.architecture_timeout
        self.chunk_timeout = self.config.chunk_timeout
        self.max_chunks = self.config.max_chunks
        self.chunk_overlap = self.config.chunk_overlap
        self.progress_check_interval = getattr(self.config, 'progress_check_interval', 10)
        
        # Cliente Anthropic para compatibilidad
        self.client = self.claude_client.client
        
        logger.info("ClaudeServiceFacade initialized", 
                   extra={
                       "model": self.config.model,
                       "components": [
                           "ClaudeConfig", "ClaudeClient", "ArchitectureGenerator",
                           "ContentGenerator", "RegenerationBuilder", "StructureBuilder",
                           "MessageBuilder"
                       ]
                   })
    
    # =========================================
    # ARCHITECTURE GENERATION METHODS
    # =========================================
    
    async def generate_book_architecture(self, book_id: int, book_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera únicamente la arquitectura del libro.
        
        Delegación completa al ArchitectureGenerator.
        
        Args:
            book_id: ID del libro
            book_params: Parámetros del libro
            
        Returns:
            Resultado con la arquitectura generada
        """
        return await self.architecture_generator.generate_book_architecture(book_id, book_params)
    
    async def regenerate_book_architecture(self, book_id: int, book_params: Dict[str, Any], 
                                         current_architecture: Dict[str, Any], 
                                         feedback_what: str, feedback_how: str) -> Dict[str, Any]:
        """
        Regenera una arquitectura existente basada en feedback.
        
        Usa el RegenerationBuilder + ArchitectureGenerator.
        
        Args:
            book_id: ID del libro
            book_params: Parámetros del libro
            current_architecture: Arquitectura actual
            feedback_what: Qué cambiar
            feedback_how: Cómo cambiar
            
        Returns:
            Resultado con la arquitectura regenerada
        """
        try:
            # Construir mensajes de regeneración usando el builder especializado
            regeneration_messages = self.regeneration_builder.build_regeneration_messages(
                book_params, current_architecture, feedback_what, feedback_how
            )
            
            # Usar el cliente Claude para generar
            system_prompt = regeneration_messages["system"]
            messages = regeneration_messages["messages"]
            
            # Configurar parámetros específicos para regeneración
            api_params = {
                'model': self.config.model,
                'max_tokens': self.config.max_tokens,
                'temperature': self.config.temperature,
                'system': system_prompt,
                'messages': messages,
                'thinking': {
                    'type': 'enabled',
                    'budget_tokens': self.config.thinking_budget
                }
            }
            
            # Realizar llamada API con circuit breaker
            response = await self.claude_client.create_message(**api_params)
            
            # Extraer contenido
            if hasattr(response, 'content') and response.content:
                content = response.content[0].text if hasattr(response.content[0], 'text') else str(response.content[0])
            else:
                content = str(response)
            
            # Validar resultado usando el builder
            validation = self.regeneration_builder.validate_regeneration_result(
                current_architecture, {}, feedback_what, feedback_how  # Simplified validation
            )
            
            logger.info("architecture_regeneration_completed",
                       book_id=book_id,
                       content_length=len(content),
                       validation_score=validation.get('score', 0))
            
            return {
                'success': True,
                'architecture': content,
                'validation': validation,
                'feedback_applied': {
                    'what': feedback_what,
                    'how': feedback_how
                }
            }
            
        except Exception as e:
            error_msg = f"Error regenerando arquitectura: {str(e)}"
            logger.error("architecture_regeneration_error",
                        book_id=book_id,
                        error=str(e),
                        error_type=type(e).__name__)
            
            return {
                'success': False,
                'error': error_msg,
                'error_type': type(e).__name__
            }
    
    # =========================================
    # CONTENT GENERATION METHODS
    # =========================================
    
    async def generate_book_from_architecture_multichunk(self, book_id: int, 
                                                       book_params: Dict[str, Any], 
                                                       approved_architecture: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera el contenido completo del libro usando multi-chunk.
        
        Delegación completa al ContentGenerator.
        
        Args:
            book_id: ID del libro
            book_params: Parámetros del libro
            approved_architecture: Arquitectura aprobada
            
        Returns:
            Resultado de la generación completa
        """
        return await self.content_generator.generate_book_from_architecture_multichunk(
            book_id, book_params, approved_architecture
        )
    
    async def regenerate_chapter_content(self, chapter_content: str, 
                                       feedback: Dict[str, str], 
                                       book=None) -> Dict[str, Any]:
        """
        Regenera el contenido de un capítulo específico.
        
        Implementación simplificada usando MessageBuilder.
        
        Args:
            chapter_content: Contenido actual del capítulo
            feedback: Feedback para la regeneración
            book: Información del libro (opcional)
            
        Returns:
            Resultado de la regeneración del capítulo
        """
        try:
            # Construir prompt usando MessageBuilder
            system_sections = [
                {
                    'title': 'Rol',
                    'content': 'Eres un editor experto especializado en mejorar contenido de libros.'
                },
                {
                    'title': 'Tarea',
                    'content': 'Regenera el contenido del capítulo basándote en el feedback proporcionado.'
                }
            ]
            
            system_prompt = self.message_builder.build_system_prompt_with_sections(system_sections)
            
            # Construir user prompt
            user_prompt = f"""Regenera el siguiente contenido de capítulo basándote en el feedback:

**CONTENIDO ACTUAL:**
{chapter_content}

**FEEDBACK:**
{feedback}

Mantén el estilo y tono, pero implementa las mejoras solicitadas."""
            
            # Crear estructura de mensaje
            message_structure = self.message_builder.create_standard_message_structure(
                system_prompt, user_prompt
            )
            
            # Validar mensaje
            validation = self.message_builder.validate_message_structure(message_structure)
            if not validation['is_valid']:
                raise Exception(f"Estructura de mensaje inválida: {validation['errors']}")
            
            # Generar contenido
            response = await self.claude_client.create_message(
                messages=message_structure['messages'],
                system=message_structure['system']
            )
            
            # Extraer contenido
            if hasattr(response, 'content') and response.content:
                regenerated_content = response.content[0].text if hasattr(response.content[0], 'text') else str(response.content[0])
            else:
                regenerated_content = str(response)
            
            return {
                'success': True,
                'content': regenerated_content,
                'original_length': len(chapter_content),
                'new_length': len(regenerated_content),
                'feedback_applied': feedback
            }
            
        except Exception as e:
            error_msg = f"Error regenerando capítulo: {str(e)}"
            logger.error("chapter_regeneration_error",
                        error=str(e),
                        error_type=type(e).__name__)
            
            return {
                'success': False,
                'error': error_msg,
                'error_type': type(e).__name__
            }
    
    # =========================================
    # UTILITY METHODS
    # =========================================
    
    def validate_book_params(self, book_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida parámetros de libro usando StructureBuilder.
        
        Args:
            book_params: Parámetros del libro a validar
            
        Returns:
            Resultado de la validación
        """
        try:
            # Usar StructureBuilder para validar completitud
            validation = self.structure_builder.validate_structure_completeness(book_params)
            
            # Agregar validaciones específicas de parámetros
            required_params = ['title', 'genre', 'target_pages']
            missing_params = []
            
            for param in required_params:
                if param not in book_params or not book_params[param]:
                    missing_params.append(param)
            
            if missing_params:
                validation['missing_elements'].extend(missing_params)
                validation['is_complete'] = False
            
            return validation
            
        except Exception as e:
            logger.error("book_params_validation_error", error=str(e))
            return {
                'is_complete': False,
                'missing_elements': ['validation_error'],
                'warnings': [str(e)],
                'score': 0.0
            }
    
    def estimate_generation_time(self, book_params: Dict[str, Any]) -> int:
        """
        Estima tiempo de generación basado en parámetros del libro.
        
        Args:
            book_params: Parámetros del libro
            
        Returns:
            Tiempo estimado en segundos
        """
        target_pages = book_params.get('target_pages', 150)
        
        # Estimación basada en páginas y configuración actual
        base_time_per_page = 2  # segundos por página
        chunk_overhead = self.max_chunks * 30  # overhead por chunk
        
        estimated_time = (target_pages * base_time_per_page) + chunk_overhead
        
        return min(estimated_time, 3600)  # Máximo 1 hora
    
    # =========================================
    # CIRCUIT BREAKER MANAGEMENT
    # =========================================
    
    def get_circuit_breaker_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del circuit breaker."""
        return self.claude_client.get_circuit_breaker_stats()
    
    def force_circuit_reset(self):
        """Fuerza el reset del circuit breaker."""
        self.claude_client.force_circuit_reset()
    
    # =========================================
    # COMPATIBILITY METHODS
    # =========================================
    
    def _check_circuit_breaker(self):
        """Método de compatibilidad - verificación manejada por ClaudeClient."""
        pass  # Circuit breaker es manejado automáticamente por ClaudeClient
    
    def _handle_api_error(self, error: Exception):
        """Método de compatibilidad - manejo de errores en ClaudeClient."""
        self.claude_client.circuit_breaker.record_failure(error)
    
    def _handle_api_success(self):
        """Método de compatibilidad - registro de éxito en ClaudeClient.""" 
        self.claude_client.circuit_breaker.record_success()
    
    def _update_progress(self, book_id: int, operation: str, details: str = None):
        """Método de compatibilidad - delegado a generators."""
        # Los generators manejan su propio progreso
        pass
    
    def _get_optimized_tokens(self, content_type: str) -> int:
        """Obtiene tokens optimizados para un tipo de contenido."""
        return self.config.token_config.get_limit(content_type)
    
    def _get_optimized_thinking_budget(self, content_type: str) -> int:
        """Obtiene presupuesto de thinking optimizado."""
        return self.config.thinking_budget
    
    def estimate_thinking_tokens(self, thinking_content) -> int:
        """Estima tokens de thinking usando MessageBuilder."""
        if not thinking_content:
            return 0
        
        content_str = str(thinking_content)
        return self.message_builder.estimate_token_count(content_str)
    
    # =========================================
    # STRING REPRESENTATION
    # =========================================
    
    def __str__(self) -> str:
        """String representation del facade."""
        return (f"ClaudeServiceFacade(model={self.config.model}, "
                f"components=7, circuit_state={self.claude_client.circuit_breaker.get_state().value})")
    
    def __repr__(self) -> str:
        """Detailed representation del facade."""
        components = [
            "ClaudeConfig", "ClaudeClient", "ArchitectureGenerator",
            "ContentGenerator", "RegenerationBuilder", "StructureBuilder", "MessageBuilder"
        ]
        return (f"ClaudeServiceFacade(model='{self.config.model}', "
                f"max_tokens={self.config.max_tokens}, "
                f"components={components})")