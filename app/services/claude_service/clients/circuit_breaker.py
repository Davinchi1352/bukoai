"""
Circuit Breaker Implementation

Circuit breaker independiente para manejo robusto de errores en servicios externos.
Extraído de la lógica original de ClaudeService.
"""

import logging
from datetime import datetime, timezone
from typing import Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Estados del circuit breaker."""
    CLOSED = "closed"      # Funcionamiento normal
    OPEN = "open"          # Circuito abierto por errores
    HALF_OPEN = "half_open"  # Estado de prueba después de timeout


@dataclass
class CircuitBreakerStats:
    """Estadísticas del circuit breaker."""
    error_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    state_changes: int = 0


class CircuitBreaker:
    """
    Circuit Breaker independiente para manejo de errores.
    
    Implementa exactamente la misma lógica que el ClaudeService original
    (líneas 92-166) pero como componente independiente y reutilizable.
    """
    
    def __init__(self, 
                 failure_threshold: int = 5,
                 timeout: int = 300,
                 name: str = "circuit_breaker"):
        """
        Inicializa el circuit breaker.
        
        Args:
            failure_threshold: Número de errores para abrir circuito (default: 5, igual que original)
            timeout: Tiempo en segundos antes de probar reconexión (default: 300s = 5 min)
            name: Nombre del circuit breaker para logs
        """
        # Configuración extraída de claude_service.py líneas 92-95
        self.failure_threshold = failure_threshold  # self.max_errors = 5
        self.timeout = timeout                      # self.circuit_timeout = 300
        self.name = name
        
        # Estado interno (exacto al original)
        self.error_count = 0                      # self.error_count = 0
        self.circuit_open_time: Optional[float] = None  # self.circuit_open_time = None
        self.state = CircuitState.CLOSED
        
        # Estadísticas adicionales
        self.stats = CircuitBreakerStats()
        
        logger.info(f"CircuitBreaker '{name}' initialized", 
                   extra={"failure_threshold": failure_threshold, "timeout": timeout})
    
    def is_open(self) -> bool:
        """
        Verifica si el circuit breaker está abierto.
        
        Returns:
            True si está abierto (no permitir llamadas), False si está cerrado
        """
        if self.circuit_open_time is None:
            return False
            
        current_time = datetime.now(timezone.utc).timestamp()
        elapsed = current_time - self.circuit_open_time
        
        if elapsed < self.timeout:
            return True
        else:
            # Tiempo de timeout alcanzado, intentar resetear
            self._reset_circuit()
            return False
    
    def check_and_call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Ejecuta una función con protección de circuit breaker.
        
        Equivale a la verificación manual que hace ClaudeService con
        _check_circuit_breaker() antes de cada llamada API.
        
        Args:
            func: Función a ejecutar
            *args, **kwargs: Argumentos para la función
        
        Returns:
            Resultado de la función
        
        Raises:
            Exception: Si el circuit breaker está abierto
        """
        # Verificar estado (equivale a _check_circuit_breaker())
        if self.is_open():
            error_msg = f"Circuit breaker '{self.name}' abierto. Esperando {self.timeout}s"
            logger.warning("circuit_breaker_call_blocked", 
                         extra={"circuit_name": self.name, "timeout": self.timeout})
            raise Exception(error_msg)
        
        try:
            # Ejecutar función
            result = func(*args, **kwargs)
            
            # Registrar éxito (equivale a _handle_api_success())
            self.record_success()
            
            return result
            
        except Exception as e:
            # Registrar error (equivale a _handle_api_error())
            self.record_failure(e)
            raise
    
    def record_success(self):
        """
        Registra un éxito y resetea contadores si es necesario.
        
        Equivale exactamente a ClaudeService._handle_api_success() líneas 160-165.
        """
        if self.error_count > 0:
            logger.info("circuit_breaker_recovered", 
                       extra={
                           "circuit_name": self.name,
                           "previous_errors": self.error_count,
                           "state": self.state.value
                       })
            self.error_count = 0
        
        # Actualizar estadísticas
        self.stats.success_count += 1
        self.stats.last_success_time = datetime.now(timezone.utc).timestamp()
        
        # Asegurar que el circuito esté cerrado
        if self.state != CircuitState.CLOSED:
            self.state = CircuitState.CLOSED
            self.stats.state_changes += 1
    
    def record_failure(self, error: Exception):
        """
        Registra un fallo y actualiza el estado del circuit breaker.
        
        Equivale exactamente a ClaudeService._handle_api_error() líneas 146-158.
        
        Args:
            error: Excepción que causó el fallo
        """
        self.error_count += 1
        self.stats.failure_count += 1
        self.stats.last_failure_time = datetime.now(timezone.utc).timestamp()
        
        logger.error("circuit_breaker_api_error",
                    extra={
                        "circuit_name": self.name,
                        "error": str(error),
                        "error_count": self.error_count,
                        "max_errors": self.failure_threshold
                    })
        
        # Abrir circuito si se alcanza el threshold
        if self.error_count >= self.failure_threshold:
            self.circuit_open_time = datetime.now(timezone.utc).timestamp()
            self.state = CircuitState.OPEN
            self.stats.state_changes += 1
            
            logger.error("circuit_breaker_opened",
                        extra={
                            "circuit_name": self.name,
                            "error_count": self.error_count,
                            "timeout": self.timeout,
                            "state": self.state.value
                        })
    
    def _reset_circuit(self):
        """
        Resetea el circuit breaker después del timeout.
        
        Equivale a la lógica en ClaudeService._check_circuit_breaker() líneas 140-144.
        """
        self.circuit_open_time = None
        self.error_count = 0
        self.state = CircuitState.CLOSED
        self.stats.state_changes += 1
        
        logger.info("circuit_breaker_reset",
                   extra={
                       "circuit_name": self.name,
                       "after_timeout": self.timeout,
                       "state": self.state.value
                   })
    
    def force_open(self):
        """Fuerza la apertura del circuito (útil para testing)."""
        self.circuit_open_time = datetime.now(timezone.utc).timestamp()
        self.state = CircuitState.OPEN
        self.stats.state_changes += 1
        
        logger.warning("circuit_breaker_force_opened",
                      extra={"circuit_name": self.name, "state": self.state.value})
    
    def force_close(self):
        """Fuerza el cierre del circuito (útil para testing/recovery manual)."""
        self._reset_circuit()
        
        logger.info("circuit_breaker_force_closed",
                   extra={"circuit_name": self.name, "state": self.state.value})
    
    def get_stats(self) -> CircuitBreakerStats:
        """Retorna estadísticas del circuit breaker."""
        return self.stats
    
    def get_state(self) -> CircuitState:
        """Retorna el estado actual del circuit breaker."""
        return self.state
    
    def __str__(self) -> str:
        """String representation del circuit breaker."""
        return (f"CircuitBreaker(name='{self.name}', state={self.state.value}, "
               f"errors={self.error_count}/{self.failure_threshold}, "
               f"timeout={self.timeout}s)")
    
    def __repr__(self) -> str:
        """Detailed representation del circuit breaker."""
        return (f"CircuitBreaker(name='{self.name}', state={self.state.value}, "
               f"error_count={self.error_count}, failure_threshold={self.failure_threshold}, "
               f"timeout={self.timeout}, circuit_open_time={self.circuit_open_time})")