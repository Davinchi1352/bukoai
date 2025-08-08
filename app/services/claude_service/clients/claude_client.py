"""
Claude API Client with Circuit Breaker

Cliente especializado para API de Claude con circuit breaker integrado.
Encapsula la lógica de conexión y manejo de errores.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, AsyncIterator
import httpx
from anthropic import AsyncAnthropic, APIError, APIConnectionError, RateLimitError

from .circuit_breaker import CircuitBreaker
from ..config.claude_config import ClaudeConfig

logger = logging.getLogger(__name__)


class ClaudeClient:
    """
    Cliente especializado para API de Claude con circuit breaker integrado.
    
    Encapsula la creación del cliente Anthropic y el manejo de errores
    que estaba distribuido en ClaudeService original.
    """
    
    def __init__(self, config: ClaudeConfig):
        """
        Inicializa el cliente Claude.
        
        Args:
            config: Configuración de Claude
        """
        self.config = config
        
        # Validar configuración
        self.config.validate()
        
        # Crear circuit breaker
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=config.circuit_failure_threshold,
            timeout=config.circuit_timeout,
            name="claude_api"
        )
        
        # Configurar HTTP client (extraído de claude_service.py líneas 49-61)
        http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=config.http_connect_timeout,
                read=config.http_read_timeout,
                write=config.http_write_timeout,
                pool=config.http_pool_timeout
            )
        )
        
        # Crear cliente Anthropic (extraído de claude_service.py líneas 63-66)
        self.client = AsyncAnthropic(
            api_key=config.api_key,
            http_client=http_client
        )
        
        logger.info("Claude client initialized", 
                   extra={
                       "model": config.model,
                       "circuit_breaker": str(self.circuit_breaker)
                   })
    
    async def create_message(self, messages: list, **kwargs) -> Dict[str, Any]:
        """
        Crea un mensaje usando la API de Claude con circuit breaker.
        
        Args:
            messages: Lista de mensajes para Claude
            **kwargs: Parámetros adicionales (max_tokens, temperature, etc.)
        
        Returns:
            Respuesta de Claude
            
        Raises:
            Exception: Si circuit breaker está abierto o hay errores API
        """
        
        async def _api_call():
            """Función interna para llamada API."""
            # Preparar parámetros por defecto
            api_params = {
                'model': self.config.model,
                'messages': messages,
                'max_tokens': kwargs.get('max_tokens', self.config.max_tokens),
                'temperature': kwargs.get('temperature', self.config.temperature),
            }
            
            # Agregar parámetros adicionales si se proporcionan
            for key in ['system', 'stream', 'thinking_budget']:
                if key in kwargs:
                    api_params[key] = kwargs[key]
            
            logger.debug("Claude API call", 
                        extra={
                            "model": api_params['model'],
                            "max_tokens": api_params['max_tokens'],
                            "message_count": len(messages)
                        })
            
            # Realizar llamada API
            response = await self.client.messages.create(**api_params)
            
            logger.debug("Claude API response received",
                        extra={"response_type": type(response).__name__})
            
            return response
        
        # Ejecutar con circuit breaker protection
        return await self._execute_with_circuit_breaker(_api_call)
    
    async def create_message_stream(self, messages: list, **kwargs) -> AsyncIterator[Any]:
        """
        Crea un mensaje con streaming usando circuit breaker.
        
        Args:
            messages: Lista de mensajes para Claude
            **kwargs: Parámetros adicionales
            
        Yields:
            Chunks de respuesta de Claude
        """
        
        async def _stream_call():
            """Función interna para streaming API."""
            api_params = {
                'model': self.config.model,
                'messages': messages,
                'max_tokens': kwargs.get('max_tokens', self.config.max_tokens),
                'temperature': kwargs.get('temperature', self.config.temperature),
                'stream': True
            }
            
            # Agregar parámetros adicionales
            for key in ['system', 'thinking_budget']:
                if key in kwargs:
                    api_params[key] = kwargs[key]
            
            logger.debug("Claude streaming API call",
                        extra={
                            "model": api_params['model'],
                            "max_tokens": api_params['max_tokens']
                        })
            
            # Crear stream
            stream = await self.client.messages.create(**api_params)
            return stream
        
        # Obtener stream con circuit breaker
        stream = await self._execute_with_circuit_breaker(_stream_call)
        
        # Yield chunks con manejo de errores
        try:
            async for chunk in stream:
                yield chunk
        except Exception as e:
            # Registrar error en circuit breaker
            self.circuit_breaker.record_failure(e)
            raise
        
        # Registrar éxito después de streaming completo
        self.circuit_breaker.record_success()
    
    async def _execute_with_circuit_breaker(self, func):
        """
        Ejecuta una función con protección de circuit breaker.
        
        Args:
            func: Función async a ejecutar
            
        Returns:
            Resultado de la función
        """
        # Verificar circuit breaker
        if self.circuit_breaker.is_open():
            error_msg = f"Claude API circuit breaker is open. Timeout: {self.circuit_breaker.timeout}s"
            logger.warning("claude_api_call_blocked", 
                         extra={"circuit_breaker_state": self.circuit_breaker.get_state().value})
            raise Exception(error_msg)
        
        try:
            # Ejecutar función
            result = await func()
            
            # Registrar éxito
            self.circuit_breaker.record_success()
            
            return result
            
        except (APIError, APIConnectionError, RateLimitError, asyncio.TimeoutError) as e:
            # Errores específicos de API que deben contar para circuit breaker
            logger.error("Claude API error",
                        extra={
                            "error_type": type(e).__name__,
                            "error": str(e)
                        })
            
            # Registrar error en circuit breaker
            self.circuit_breaker.record_failure(e)
            
            raise
        
        except Exception as e:
            # Otros errores también cuentan
            logger.error("Unexpected error in Claude client",
                        extra={
                            "error_type": type(e).__name__,
                            "error": str(e)
                        })
            
            self.circuit_breaker.record_failure(e)
            raise
    
    def get_circuit_breaker_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del circuit breaker."""
        stats = self.circuit_breaker.get_stats()
        return {
            'state': self.circuit_breaker.get_state().value,
            'error_count': self.circuit_breaker.error_count,
            'failure_threshold': self.circuit_breaker.failure_threshold,
            'success_count': stats.success_count,
            'failure_count': stats.failure_count,
            'last_success_time': stats.last_success_time,
            'last_failure_time': stats.last_failure_time,
            'state_changes': stats.state_changes
        }
    
    def force_circuit_reset(self):
        """Fuerza el reset del circuit breaker (para recovery manual)."""
        self.circuit_breaker.force_close()
        logger.info("Claude client circuit breaker manually reset")
    
    def __str__(self) -> str:
        """String representation del cliente."""
        return f"ClaudeClient(model={self.config.model}, {self.circuit_breaker})"