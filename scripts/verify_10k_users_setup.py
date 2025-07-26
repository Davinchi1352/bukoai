#!/usr/bin/env python3
"""
Script de verificación para sistema optimizado para 10,000 usuarios.
Verifica configuración, conectividad y rendimiento básico.
"""

import asyncio
import time
import json
import psutil
import redis
import httpx
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
import sys
import os

# Agregar path de la aplicación
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class SystemVerification:
    """Verificador del sistema para 10K usuarios."""
    
    def __init__(self):
        self.results = []
        self.errors = []
        self.start_time = time.time()
    
    def log_result(self, test_name: str, status: str, details: Dict[str, Any] = None):
        """Registra resultado de una verificación."""
        result = {
            'test': test_name,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        self.results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")
        if details:
            for key, value in details.items():
                print(f"   {key}: {value}")
    
    def log_error(self, test_name: str, error: str):
        """Registra un error."""
        self.errors.append({'test': test_name, 'error': error})
        self.log_result(test_name, "FAIL", {'error': error})
    
    async def verify_database_config(self):
        """Verifica configuración de base de datos para 10K usuarios."""
        try:
            from app import create_app, db
            app = create_app()
            
            with app.app_context():
                # Verificar configuración del pool
                engine = db.engine
                pool = engine.pool
                
                pool_size = getattr(pool, 'size', lambda: 0)()
                max_overflow = getattr(pool, 'overflow', lambda: 0)()
                
                # Verificaciones
                checks = {
                    'pool_size': pool_size,
                    'max_overflow': max_overflow,
                    'total_connections': pool_size + max_overflow,
                    'pool_recycle': engine.pool._recycle,
                    'pool_timeout': engine.pool._timeout
                }
                
                # Validar configuración
                is_optimal = (
                    pool_size >= 15 and  # Mínimo 15 conexiones base
                    max_overflow >= 20 and  # Mínimo 20 overflow
                    (pool_size + max_overflow) >= 35  # Total >= 35
                )
                
                status = "PASS" if is_optimal else "WARN"
                self.log_result("Database Pool Configuration", status, checks)
                
                # Test conexión
                result = db.session.execute(db.text("SELECT 1")).scalar()
                self.log_result("Database Connectivity", "PASS", {'test_query': result})
                
        except Exception as e:
            self.log_error("Database Configuration", str(e))
    
    async def verify_redis_config(self):
        """Verifica configuración de Redis para alta concurrencia."""
        try:
            # Test Redis Celery
            redis_celery = redis.from_url("redis://localhost:6380/0", 
                                        socket_connect_timeout=5,
                                        socket_timeout=5)
            redis_celery.ping()
            
            # Test Redis Cache
            redis_cache = redis.from_url("redis://localhost:6380/1",
                                       socket_connect_timeout=5,
                                       socket_timeout=5)
            redis_cache.ping()
            
            # Verificar configuración
            info = redis_celery.info()
            memory_usage = info.get('used_memory_human', 'unknown')
            max_clients = info.get('maxclients', 0)
            connected_clients = info.get('connected_clients', 0)
            
            details = {
                'memory_usage': memory_usage,
                'max_clients': max_clients,
                'connected_clients': connected_clients,
                'celery_connectivity': True,
                'cache_connectivity': True
            }
            
            status = "PASS" if max_clients >= 1000 else "WARN"
            self.log_result("Redis Configuration", status, details)
            
        except Exception as e:
            self.log_error("Redis Configuration", str(e))
    
    async def verify_celery_config(self):
        """Verifica configuración de Celery para 10K usuarios."""
        try:
            from app import create_app
            app = create_app()
            
            # Verificar configuración
            celery_config = {
                'worker_concurrency': app.config.get('CELERY_WORKER_CONCURRENCY', 1),
                'soft_time_limit': app.config.get('CELERY_TASK_SOFT_TIME_LIMIT', 0),
                'hard_time_limit': app.config.get('CELERY_TASK_TIME_LIMIT', 0),
                'prefetch_multiplier': app.config.get('CELERY_WORKER_PREFETCH_MULTIPLIER', 1),
                'max_tasks_per_child': app.config.get('CELERY_WORKER_MAX_TASKS_PER_CHILD', 0),
                'max_memory_per_child': app.config.get('CELERY_WORKER_MAX_MEMORY_PER_CHILD', 0)
            }
            
            # Validar configuración óptima
            is_optimal = (
                celery_config['worker_concurrency'] >= 4 and
                celery_config['soft_time_limit'] >= 3600 and  # Al menos 1 hora
                celery_config['prefetch_multiplier'] >= 2
            )
            
            status = "PASS" if is_optimal else "WARN"
            self.log_result("Celery Configuration", status, celery_config)
            
        except Exception as e:
            self.log_error("Celery Configuration", str(e))
    
    async def verify_claude_service_config(self):
        """Verifica configuración del servicio Claude para alta calidad."""
        try:
            from app.services.claude_service import ClaudeService
            
            service = ClaudeService()
            
            config = {
                'model': service.model,
                'max_tokens': service.max_tokens,
                'thinking_budget': service.thinking_budget,
                'architecture_timeout': service.architecture_timeout,
                'chunk_timeout': service.chunk_timeout,
                'progress_check_interval': service.progress_check_interval,
                'max_errors': service.max_errors,
                'circuit_timeout': service.circuit_timeout
            }
            
            # Validar configuración para calidad + eficiencia
            is_optimal = (
                service.max_tokens >= 32000 and  # Suficiente para calidad
                service.thinking_budget >= 10000 and  # Suficiente thinking
                service.architecture_timeout >= 1200 and  # Al menos 20 min
                service.chunk_timeout >= 1800  # Al menos 30 min
            )
            
            status = "PASS" if is_optimal else "WARN"
            self.log_result("Claude Service Configuration", status, config)
            
        except Exception as e:
            self.log_error("Claude Service Configuration", str(e))
    
    async def verify_websocket_config(self):
        """Verifica configuración de WebSocket para 10K usuarios."""
        try:
            from app import create_app
            app = create_app()
            
            ws_config = {
                'ping_timeout': app.config.get('SOCKETIO_PING_TIMEOUT', 60),
                'ping_interval': app.config.get('SOCKETIO_PING_INTERVAL', 25),
                'max_http_buffer_size': app.config.get('SOCKETIO_MAX_HTTP_BUFFER_SIZE', 100000),
                'async_mode': app.config.get('SOCKETIO_ASYNC_MODE', 'threading'),
                'cors_allowed_origins': app.config.get('SOCKETIO_CORS_ALLOWED_ORIGINS', '*'),
                'allow_upgrades': app.config.get('SOCKETIO_ALLOW_UPGRADES', True)
            }
            
            # Validar configuración
            is_optimal = (
                ws_config['ping_timeout'] >= 60 and  # Al menos 1 minuto
                ws_config['max_http_buffer_size'] >= 50000  # Al menos 50KB
            )
            
            status = "PASS" if is_optimal else "WARN"
            self.log_result("WebSocket Configuration", status, ws_config)
            
        except Exception as e:
            self.log_error("WebSocket Configuration", str(e))
    
    async def verify_system_resources(self):
        """Verifica recursos del sistema."""
        try:
            # CPU y memoria
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Conexiones de red
            connections = len(psutil.net_connections())
            
            resources = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': round(memory.available / (1024**3), 2),
                'disk_percent': disk.percent,
                'disk_free_gb': round(disk.free / (1024**3), 2),
                'network_connections': connections,
                'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else 'N/A'
            }
            
            # Verificar si el sistema está saludable
            is_healthy = (
                cpu_percent < 80 and
                memory.percent < 80 and
                disk.percent < 85 and
                memory.available > 2 * (1024**3)  # Al menos 2GB disponible
            )
            
            status = "PASS" if is_healthy else "WARN"
            self.log_result("System Resources", status, resources)
            
        except Exception as e:
            self.log_error("System Resources", str(e))
    
    async def verify_monitoring_system(self):
        """Verifica sistema de monitoreo y logging."""
        try:
            from app.utils.structured_logging import (
                book_generation_monitor, performance_logger,
                track_book_generation_start, track_generation_complete
            )
            
            # Test logging estructurado
            test_book_id = 99999
            test_user_id = 1
            test_params = {
                'page_count': 100,
                'chapter_count': 10,
                'language': 'es',
                'genre': 'test'
            }
            
            # Test tracking functions
            track_book_generation_start(test_book_id, test_user_id, 'test', test_params)
            track_generation_complete(test_book_id, test_user_id, 'completed', 100, 25000, 50000)
            
            monitoring_features = {
                'structured_logging': True,
                'book_generation_monitor': True,
                'performance_logger': True,
                'tracking_functions': True,
                'test_tracking_successful': True
            }
            
            self.log_result("Monitoring System", "PASS", monitoring_features)
            
        except Exception as e:
            self.log_error("Monitoring System", str(e))
    
    async def verify_docker_environment(self):
        """Verifica entorno Docker."""
        try:
            # Verificar variables de entorno críticas
            env_vars = {
                'ANTHROPIC_API_KEY': 'CONFIGURED' if os.getenv('ANTHROPIC_API_KEY') else 'MISSING',
                'DATABASE_URL': 'CONFIGURED' if os.getenv('DATABASE_URL') else 'MISSING',
                'REDIS_URL': 'CONFIGURED' if os.getenv('REDIS_URL') else 'MISSING',
                'FLASK_ENV': os.getenv('FLASK_ENV', 'production'),
                'CELERY_WORKER_CONCURRENCY': os.getenv('CELERY_WORKER_CONCURRENCY', 'default'),
                'DB_POOL_SIZE': os.getenv('DB_POOL_SIZE', 'default')
            }
            
            # Verificar archivos críticos
            critical_files = [
                'docker-compose.yml',
                'Dockerfile',
                'requirements.txt',
                'app/__init__.py',
                'config/base.py'
            ]
            
            file_status = {}
            for file_path in critical_files:
                full_path = Path(__file__).parent.parent / file_path
                file_status[file_path] = 'EXISTS' if full_path.exists() else 'MISSING'
            
            details = {
                'environment_variables': env_vars,
                'critical_files': file_status
            }
            
            # Verificar que las configuraciones críticas están presentes
            critical_missing = [k for k, v in env_vars.items() 
                              if k in ['ANTHROPIC_API_KEY', 'DATABASE_URL'] and v == 'MISSING']
            
            status = "PASS" if not critical_missing else "FAIL"
            self.log_result("Docker Environment", status, details)
            
        except Exception as e:
            self.log_error("Docker Environment", str(e))
    
    async def run_all_verifications(self):
        """Ejecuta todas las verificaciones."""
        print("🚀 Iniciando verificación del sistema para 10,000 usuarios...")
        print("=" * 60)
        
        verifications = [
            self.verify_docker_environment,
            self.verify_database_config,
            self.verify_redis_config,
            self.verify_celery_config,
            self.verify_claude_service_config,
            self.verify_websocket_config,
            self.verify_system_resources,
            self.verify_monitoring_system
        ]
        
        for verification in verifications:
            try:
                await verification()
            except Exception as e:
                test_name = verification.__name__.replace('verify_', '').replace('_', ' ').title()
                self.log_error(test_name, f"Verification failed: {str(e)}")
        
        # Resumen final
        self.print_summary()
    
    def print_summary(self):
        """Imprime resumen de verificaciones."""
        total_tests = len(self.results)
        passed = len([r for r in self.results if r['status'] == 'PASS'])
        warnings = len([r for r in self.results if r['status'] == 'WARN'])
        failed = len([r for r in self.results if r['status'] == 'FAIL'])
        
        duration = time.time() - self.start_time
        
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE VERIFICACIÓN")
        print("=" * 60)
        print(f"⏱️  Duración: {duration:.2f} segundos")
        print(f"📈 Total de tests: {total_tests}")
        print(f"✅ Exitosos: {passed}")
        print(f"⚠️  Advertencias: {warnings}")
        print(f"❌ Fallados: {failed}")
        
        if failed == 0 and warnings == 0:
            print("\n🎉 ¡Sistema completamente optimizado para 10,000 usuarios!")
        elif failed == 0:
            print("\n👍 Sistema funcionando bien, revisar advertencias para optimización.")
        else:
            print("\n🔧 Sistema necesita correcciones antes de manejar 10,000 usuarios.")
        
        # Guardar resultados
        self.save_results()
    
    def save_results(self):
        """Guarda resultados en archivo JSON."""
        results_file = Path(__file__).parent.parent / 'verification_results.json'
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': time.time() - self.start_time,
            'total_tests': len(self.results),
            'passed': len([r for r in self.results if r['status'] == 'PASS']),
            'warnings': len([r for r in self.results if r['status'] == 'WARN']),
            'failed': len([r for r in self.results if r['status'] == 'FAIL']),
            'results': self.results,
            'errors': self.errors
        }
        
        with open(results_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📄 Resultados guardados en: {results_file}")

async def main():
    """Función principal."""
    verifier = SystemVerification()
    await verifier.run_all_verifications()

if __name__ == "__main__":
    asyncio.run(main())