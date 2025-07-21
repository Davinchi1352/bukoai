"""
Configuración avanzada de logging para Buko AI.
"""
import os
import logging
import logging.handlers
from typing import Dict, Any
from pythonjsonlogger import jsonlogger


class LogConfig:
    """
    Configurador avanzado de logging con rotation y formatos estructurados.
    """
    
    @staticmethod
    def setup_logging(app):
        """
        Configura el sistema de logging completo para la aplicación.
        """
        # Crear directorio de logs si no existe
        log_dir = app.config.get('LOG_DIR', 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Configurar nivel de logging
        log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper())
        
        # Limpiar handlers existentes
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        
        # Configurar formatters
        formatters = LogConfig._get_formatters()
        
        # Configurar handlers
        handlers = LogConfig._get_handlers(app, formatters, log_dir)
        
        # Aplicar configuración al logger principal
        app.logger.setLevel(log_level)
        root_logger.setLevel(log_level)
        
        for handler in handlers:
            app.logger.addHandler(handler)
            root_logger.addHandler(handler)
        
        # Configurar loggers específicos
        LogConfig._configure_specific_loggers(log_level)
        
        # Log de inicio
        app.logger.info(f"Logging configurado - Nivel: {app.config.get('LOG_LEVEL', 'INFO')}")
    
    @staticmethod
    def _get_formatters() -> Dict[str, logging.Formatter]:
        """Obtiene los formatters configurados."""
        formatters = {}
        
        # Formatter estándar para desarrollo
        formatters['standard'] = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s '
            '[%(filename)s:%(lineno)d]',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Formatter detallado para archivos
        formatters['detailed'] = logging.Formatter(
            '%(asctime)s [%(levelname)-8s] %(name)-20s: %(message)s '
            '[%(pathname)s:%(lineno)d] (%(funcName)s)',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Formatter JSON para logs estructurados
        formatters['json'] = jsonlogger.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%dT%H:%M:%S'
        )
        
        # Formatter simple para consola
        formatters['simple'] = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        
        return formatters
    
    @staticmethod
    def _get_handlers(app, formatters: Dict[str, logging.Formatter], 
                     log_dir: str) -> list:
        """Obtiene los handlers configurados."""
        handlers = []
        log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper())
        
        # Handler para consola (desarrollo)
        if app.config.get('LOG_TO_STDOUT', True):
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            console_handler.setFormatter(formatters['standard'])
            handlers.append(console_handler)
        
        # Handler para archivo principal con rotation
        main_file_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(log_dir, 'buko-ai.log'),
            maxBytes=50 * 1024 * 1024,  # 50MB
            backupCount=10,
            encoding='utf-8'
        )
        main_file_handler.setLevel(log_level)
        main_file_handler.setFormatter(formatters['detailed'])
        handlers.append(main_file_handler)
        
        # Handler para errores
        error_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(log_dir, 'errors.log'),
            maxBytes=25 * 1024 * 1024,  # 25MB
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatters['detailed'])
        handlers.append(error_handler)
        
        # Handler para logs estructurados (JSON)
        json_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(log_dir, 'structured.jsonl'),
            maxBytes=100 * 1024 * 1024,  # 100MB
            backupCount=15,
            encoding='utf-8'
        )
        json_handler.setLevel(logging.INFO)
        json_handler.setFormatter(formatters['json'])
        handlers.append(json_handler)
        
        # Handler para métricas de performance
        performance_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(log_dir, 'performance.log'),
            maxBytes=25 * 1024 * 1024,  # 25MB
            backupCount=7,
            encoding='utf-8'
        )
        performance_handler.setLevel(logging.INFO)
        performance_handler.setFormatter(formatters['json'])
        
        # Filtro para logs de performance
        performance_filter = logging.Filter('performance')
        performance_handler.addFilter(performance_filter)
        handlers.append(performance_handler)
        
        # Handler para seguridad
        security_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(log_dir, 'security.log'),
            maxBytes=25 * 1024 * 1024,  # 25MB
            backupCount=10,
            encoding='utf-8'
        )
        security_handler.setLevel(logging.WARNING)
        security_handler.setFormatter(formatters['detailed'])
        
        # Filtro para logs de seguridad
        security_filter = logging.Filter('security')
        security_handler.addFilter(security_filter)
        handlers.append(security_handler)
        
        # Handler para eventos de negocio
        business_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(log_dir, 'business.log'),
            maxBytes=50 * 1024 * 1024,  # 50MB
            backupCount=12,
            encoding='utf-8'
        )
        business_handler.setLevel(logging.INFO)
        business_handler.setFormatter(formatters['json'])
        
        # Filtro para logs de negocio
        business_filter = logging.Filter('business')
        business_handler.addFilter(business_filter)
        handlers.append(business_handler)
        
        # Handler para Syslog (producción)
        if not app.debug and app.config.get('SYSLOG_ENABLED', False):
            syslog_handler = logging.handlers.SysLogHandler(
                address=app.config.get('SYSLOG_ADDRESS', '/dev/log')
            )
            syslog_handler.setLevel(logging.WARNING)
            syslog_handler.setFormatter(formatters['json'])
            handlers.append(syslog_handler)
        
        # Handler para email (errores críticos)
        if not app.debug and app.config.get('ERROR_EMAIL_ENABLED', False):
            mail_handler = logging.handlers.SMTPHandler(
                mailhost=app.config.get('MAIL_SERVER'),
                fromaddr=app.config.get('ERROR_EMAIL_FROM'),
                toaddrs=app.config.get('ERROR_EMAIL_TO', []),
                subject='Buko AI - Error Crítico',
                credentials=(
                    app.config.get('MAIL_USERNAME'),
                    app.config.get('MAIL_PASSWORD')
                ) if app.config.get('MAIL_USERNAME') else None,
                secure=() if app.config.get('MAIL_USE_TLS') else None
            )
            mail_handler.setLevel(logging.CRITICAL)
            mail_handler.setFormatter(formatters['detailed'])
            handlers.append(mail_handler)
        
        return handlers
    
    @staticmethod
    def _configure_specific_loggers(log_level: int):
        """Configura loggers específicos de librerías externas."""
        # SQLAlchemy
        logging.getLogger('sqlalchemy.engine').setLevel(
            logging.INFO if log_level <= logging.DEBUG else logging.WARNING
        )
        logging.getLogger('sqlalchemy.dialects').setLevel(logging.WARNING)
        logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
        logging.getLogger('sqlalchemy.orm').setLevel(logging.WARNING)
        
        # Celery
        logging.getLogger('celery').setLevel(logging.INFO)
        logging.getLogger('celery.task').setLevel(logging.INFO)
        logging.getLogger('celery.worker').setLevel(logging.INFO)
        
        # Redis
        logging.getLogger('redis').setLevel(logging.WARNING)
        
        # Flask
        logging.getLogger('flask').setLevel(logging.INFO)
        logging.getLogger('werkzeug').setLevel(
            logging.INFO if log_level <= logging.DEBUG else logging.WARNING
        )
        
        # Requests
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        
        # Anthropic
        logging.getLogger('anthropic').setLevel(logging.INFO)
        
        # SocketIO
        logging.getLogger('socketio').setLevel(logging.WARNING)
        logging.getLogger('engineio').setLevel(logging.WARNING)


class LogMetrics:
    """
    Recolector de métricas de logging.
    """
    
    def __init__(self):
        self.metrics = {
            'total_logs': 0,
            'errors': 0,
            'warnings': 0,
            'info': 0,
            'debug': 0,
            'critical': 0
        }
    
    def increment(self, level: str):
        """Incrementa contador de logs por nivel."""
        self.metrics['total_logs'] += 1
        level_key = level.lower()
        if level_key in self.metrics:
            self.metrics[level_key] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas actuales."""
        return self.metrics.copy()
    
    def reset(self):
        """Resetea todas las métricas."""
        for key in self.metrics:
            self.metrics[key] = 0


class LogAnalyzer:
    """
    Analizador de logs para detectar patrones y problemas.
    """
    
    @staticmethod
    def analyze_error_patterns(log_file: str, hours: int = 24) -> Dict[str, Any]:
        """
        Analiza patrones de errores en las últimas horas.
        
        Args:
            log_file: Ruta del archivo de log
            hours: Número de horas hacia atrás a analizar
            
        Returns:
            Diccionario con análisis de patrones
        """
        try:
            import re
            from datetime import datetime, timedelta
            from collections import defaultdict
            
            if not os.path.exists(log_file):
                return {'error': 'Log file not found'}
            
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            error_patterns = defaultdict(int)
            error_messages = []
            
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        # Buscar timestamp
                        timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                        if timestamp_match:
                            timestamp_str = timestamp_match.group(1)
                            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                            
                            if timestamp >= cutoff_time and 'ERROR' in line:
                                # Extraer mensaje de error
                                error_msg = line.split('ERROR')[1].strip() if 'ERROR' in line else line
                                error_messages.append(error_msg[:200])  # Primeros 200 chars
                                
                                # Categorizar errores
                                if 'Database' in error_msg or 'SQLAlchemy' in error_msg:
                                    error_patterns['database'] += 1
                                elif 'Redis' in error_msg or 'Cache' in error_msg:
                                    error_patterns['cache'] += 1
                                elif 'Celery' in error_msg or 'Task' in error_msg:
                                    error_patterns['celery'] += 1
                                elif 'HTTP' in error_msg or '404' in error_msg or '500' in error_msg:
                                    error_patterns['http'] += 1
                                elif 'Auth' in error_msg or 'Permission' in error_msg:
                                    error_patterns['auth'] += 1
                                else:
                                    error_patterns['other'] += 1
                                    
                    except Exception:
                        continue
            
            return {
                'total_errors': sum(error_patterns.values()),
                'error_categories': dict(error_patterns),
                'recent_errors': error_messages[-10:],  # Últimos 10 errores
                'analysis_period_hours': hours
            }
            
        except Exception as e:
            return {'error': f'Failed to analyze logs: {str(e)}'}
    
    @staticmethod
    def get_log_stats(log_dir: str) -> Dict[str, Any]:
        """
        Obtiene estadísticas generales de logs.
        
        Args:
            log_dir: Directorio de logs
            
        Returns:
            Diccionario con estadísticas
        """
        try:
            stats = {
                'log_files': [],
                'total_size_mb': 0,
                'oldest_log': None,
                'newest_log': None
            }
            
            if not os.path.exists(log_dir):
                return stats
            
            for filename in os.listdir(log_dir):
                file_path = os.path.join(log_dir, filename)
                if os.path.isfile(file_path) and filename.endswith('.log'):
                    file_stat = os.stat(file_path)
                    file_info = {
                        'name': filename,
                        'size_mb': round(file_stat.st_size / (1024 * 1024), 2),
                        'modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                    }
                    stats['log_files'].append(file_info)
                    stats['total_size_mb'] += file_info['size_mb']
                    
                    # Actualizar fechas
                    if not stats['oldest_log'] or file_stat.st_mtime < stats['oldest_log']:
                        stats['oldest_log'] = file_stat.st_mtime
                    if not stats['newest_log'] or file_stat.st_mtime > stats['newest_log']:
                        stats['newest_log'] = file_stat.st_mtime
            
            # Convertir timestamps a ISO
            if stats['oldest_log']:
                stats['oldest_log'] = datetime.fromtimestamp(stats['oldest_log']).isoformat()
            if stats['newest_log']:
                stats['newest_log'] = datetime.fromtimestamp(stats['newest_log']).isoformat()
            
            stats['total_size_mb'] = round(stats['total_size_mb'], 2)
            return stats
            
        except Exception as e:
            return {'error': f'Failed to get log stats: {str(e)}'}


# Instancia global de métricas
log_metrics = LogMetrics()