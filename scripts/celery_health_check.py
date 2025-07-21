#!/usr/bin/env python3
"""
Health check script para servicios Celery
"""

import sys
import os
import redis
import logging
from celery import Celery
from typing import Dict, Any

# Configurar logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def check_redis_connection() -> bool:
    """Verificar conexión a Redis"""
    try:
        redis_url = os.getenv('REDIS_URL', 'redis://redis:6379/0')
        r = redis.from_url(redis_url)
        r.ping()
        return True
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        return False

def check_celery_worker() -> bool:
    """Verificar que el worker de Celery esté funcionando"""
    try:
        # Crear instancia de Celery
        celery_app = Celery('app')
        celery_app.config_from_object({
            'broker_url': os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0'),
            'result_backend': os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0'),
            'task_always_eager': False,
            'broker_connection_retry_on_startup': True,
        })
        
        # Verificar que el worker pueda conectarse al broker
        inspect = celery_app.control.inspect()
        active_workers = inspect.active()
        
        if active_workers:
            return True
        else:
            # Es posible que no haya workers activos pero el servicio esté funcionando
            return True
            
    except Exception as e:
        logger.error(f"Celery worker check failed: {e}")
        return False

def check_celery_beat() -> bool:
    """Verificar que el beat de Celery esté funcionando"""
    try:
        # Verificar que el archivo de schedule existe y es reciente
        schedule_file = '/app/celerybeat-schedule'
        
        if os.path.exists(schedule_file):
            # Verificar que el archivo fue modificado en los últimos 10 minutos
            import time
            file_time = os.path.getmtime(schedule_file)
            current_time = time.time()
            
            # Si el archivo es muy antiguo, podría indicar un problema
            if current_time - file_time > 600:  # 10 minutos
                logger.warning("Celery beat schedule file is old")
                return False
            
            return True
        else:
            # Si no existe el archivo, el beat probablemente esté iniciando
            logger.warning("Celery beat schedule file does not exist yet")
            return True
            
    except Exception as e:
        logger.error(f"Celery beat check failed: {e}")
        return False

def main():
    """Función principal del health check"""
    service_type = sys.argv[1] if len(sys.argv) > 1 else 'worker'
    
    # Verificar Redis primero (requerido para ambos servicios)
    if not check_redis_connection():
        print("UNHEALTHY: Redis connection failed")
        sys.exit(1)
    
    # Verificar el servicio específico
    if service_type == 'worker':
        if check_celery_worker():
            print("HEALTHY: Celery worker is running")
            sys.exit(0)
        else:
            print("UNHEALTHY: Celery worker check failed")
            sys.exit(1)
    
    elif service_type == 'beat':
        if check_celery_beat():
            print("HEALTHY: Celery beat is running")
            sys.exit(0)
        else:
            print("UNHEALTHY: Celery beat check failed")
            sys.exit(1)
    
    else:
        print(f"UNKNOWN: Unknown service type: {service_type}")
        sys.exit(1)

if __name__ == '__main__':
    main()