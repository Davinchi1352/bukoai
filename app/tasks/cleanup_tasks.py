"""
Tareas de Celery para limpieza y mantenimiento.
"""
import logging
import os
import shutil
from datetime import datetime, timedelta
from app import celery, db
from app.models.system_log import SystemLog
from app.models.book_generation import BookGeneration, BookStatus
from app.models.user import User
from app.utils.logging import log_system_event

logger = logging.getLogger(__name__)


@celery.task
def cleanup_old_logs():
    """
    Limpia logs del sistema anteriores a 30 días.
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        # Contar logs a eliminar
        logs_to_delete = SystemLog.query.filter(
            SystemLog.created_at < cutoff_date
        ).count()
        
        # Eliminar logs antiguos
        deleted_count = SystemLog.query.filter(
            SystemLog.created_at < cutoff_date
        ).delete()
        
        db.session.commit()
        
        # Log del evento de limpieza
        log_system_event(
            action="logs_cleanup",
            details={
                "cutoff_date": cutoff_date.isoformat(),
                "deleted_count": deleted_count
            }
        )
        
        logger.info(f"Limpieza de logs completada: {deleted_count} logs eliminados")
        return {'status': 'completed', 'deleted_count': deleted_count}
        
    except Exception as exc:
        logger.error(f"Error en limpieza de logs: {str(exc)}")
        return {'status': 'failed', 'error': str(exc)}


@celery.task
def cleanup_old_files():
    """
    Limpia archivos de libros generados anteriores a 7 días.
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        
        # Buscar generaciones de libros antiguas completadas
        old_books = BookGeneration.query.filter(
            BookGeneration.created_at < cutoff_date,
            BookGeneration.status == BookStatus.COMPLETED,
            BookGeneration.file_paths.isnot(None)
        ).all()
        
        deleted_files = 0
        freed_space = 0
        
        for book in old_books:
            if book.file_paths:
                for format_type, file_path in book.file_paths.items():
                    if file_path and os.path.exists(file_path):
                        try:
                            # Obtener tamaño del archivo antes de eliminarlo
                            file_size = os.path.getsize(file_path)
                            
                            # Eliminar archivo
                            os.remove(file_path)
                            deleted_files += 1
                            freed_space += file_size
                            
                            logger.debug(f"Archivo eliminado: {file_path}")
                            
                        except Exception as file_exc:
                            logger.warning(f"No se pudo eliminar archivo {file_path}: {str(file_exc)}")
                
                # Limpiar rutas de archivos en la base de datos
                book.file_paths = None
        
        db.session.commit()
        
        # Convertir bytes a MB
        freed_space_mb = freed_space / (1024 * 1024)
        
        # Log del evento de limpieza
        log_system_event(
            action="files_cleanup",
            details={
                "cutoff_date": cutoff_date.isoformat(),
                "deleted_files": deleted_files,
                "freed_space_mb": round(freed_space_mb, 2),
                "books_processed": len(old_books)
            }
        )
        
        logger.info(f"Limpieza de archivos completada: {deleted_files} archivos eliminados, {freed_space_mb:.2f} MB liberados")
        return {
            'status': 'completed',
            'deleted_files': deleted_files,
            'freed_space_mb': round(freed_space_mb, 2),
            'books_processed': len(old_books)
        }
        
    except Exception as exc:
        logger.error(f"Error en limpieza de archivos: {str(exc)}")
        return {'status': 'failed', 'error': str(exc)}


@celery.task
def cleanup_failed_generations():
    """
    Limpia generaciones de libros fallidas anteriores a 24 horas.
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(hours=24)
        
        # Buscar generaciones fallidas antiguas
        failed_books = BookGeneration.query.filter(
            BookGeneration.created_at < cutoff_date,
            BookGeneration.status == BookStatus.FAILED
        ).all()
        
        deleted_count = 0
        for book in failed_books:
            # Limpiar archivos parciales si existen
            if book.file_paths:
                for format_type, file_path in book.file_paths.items():
                    if file_path and os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                        except Exception:
                            pass
            
            # Eliminar registro de la base de datos
            db.session.delete(book)
            deleted_count += 1
        
        db.session.commit()
        
        # Log del evento
        log_system_event(
            action="failed_generations_cleanup",
            details={
                "cutoff_date": cutoff_date.isoformat(),
                "deleted_count": deleted_count
            }
        )
        
        logger.info(f"Limpieza de generaciones fallidas completada: {deleted_count} registros eliminados")
        return {'status': 'completed', 'deleted_count': deleted_count}
        
    except Exception as exc:
        logger.error(f"Error en limpieza de generaciones fallidas: {str(exc)}")
        return {'status': 'failed', 'error': str(exc)}


@celery.task
def cleanup_temp_files():
    """
    Limpia archivos temporales del sistema.
    """
    try:
        temp_dirs = [
            '/tmp/buko_ai',
            './tmp',
            './temp'
        ]
        
        total_deleted = 0
        total_freed = 0
        
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                try:
                    # Calcular espacio antes de eliminar
                    dir_size = get_directory_size(temp_dir)
                    
                    # Eliminar contenido del directorio
                    for filename in os.listdir(temp_dir):
                        file_path = os.path.join(temp_dir, filename)
                        if os.path.isfile(file_path):
                            # Solo eliminar archivos más antiguos de 1 hora
                            file_age = datetime.utcnow() - datetime.fromtimestamp(os.path.getctime(file_path))
                            if file_age > timedelta(hours=1):
                                os.remove(file_path)
                                total_deleted += 1
                        elif os.path.isdir(file_path):
                            # Eliminar directorios vacíos
                            try:
                                os.rmdir(file_path)
                            except OSError:
                                pass  # Directorio no vacío
                    
                    # Calcular espacio liberado
                    new_dir_size = get_directory_size(temp_dir)
                    total_freed += (dir_size - new_dir_size)
                    
                except Exception as dir_exc:
                    logger.warning(f"Error limpiando directorio {temp_dir}: {str(dir_exc)}")
        
        freed_mb = total_freed / (1024 * 1024)
        
        # Log del evento
        log_system_event(
            action="temp_files_cleanup",
            details={
                "deleted_files": total_deleted,
                "freed_space_mb": round(freed_mb, 2)
            }
        )
        
        logger.info(f"Limpieza de archivos temporales completada: {total_deleted} archivos, {freed_mb:.2f} MB liberados")
        return {
            'status': 'completed',
            'deleted_files': total_deleted,
            'freed_space_mb': round(freed_mb, 2)
        }
        
    except Exception as exc:
        logger.error(f"Error en limpieza de archivos temporales: {str(exc)}")
        return {'status': 'failed', 'error': str(exc)}


@celery.task
def cleanup_inactive_users():
    """
    Marca como inactivos usuarios que no han iniciado sesión en 90 días.
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        
        # Buscar usuarios inactivos
        inactive_users = User.query.filter(
            User.last_login < cutoff_date,
            User.status == 'ACTIVE'
        ).all()
        
        marked_inactive = 0
        for user in inactive_users:
            # Solo marcar como inactivos usuarios gratuitos
            if user.subscription_type.value == 'FREE':
                user.status = 'INACTIVE'
                marked_inactive += 1
                
                # Log del evento
                log_system_event(
                    user_id=user.id,
                    action="user_marked_inactive",
                    details={
                        "last_login": user.last_login.isoformat() if user.last_login else None,
                        "days_inactive": (datetime.utcnow() - user.last_login).days if user.last_login else None
                    }
                )
        
        db.session.commit()
        
        logger.info(f"Usuarios marcados como inactivos: {marked_inactive}")
        return {'status': 'completed', 'marked_inactive': marked_inactive}
        
    except Exception as exc:
        logger.error(f"Error marcando usuarios inactivos: {str(exc)}")
        return {'status': 'failed', 'error': str(exc)}


@celery.task
def database_maintenance():
    """
    Ejecuta tareas de mantenimiento de la base de datos.
    """
    try:
        # Recopilar estadísticas de la base de datos
        from sqlalchemy import text
        
        stats = {}
        
        # Estadísticas de tablas
        result = db.session.execute(text("""
            SELECT schemaname, tablename, n_tup_ins, n_tup_upd, n_tup_del, n_live_tup, n_dead_tup
            FROM pg_stat_user_tables
            WHERE schemaname = 'public'
        """))
        
        stats['tables'] = []
        for row in result:
            stats['tables'].append({
                'table': row[1],
                'inserts': row[2],
                'updates': row[3],
                'deletes': row[4],
                'live_tuples': row[5],
                'dead_tuples': row[6]
            })
        
        # Tamaño de la base de datos
        result = db.session.execute(text("""
            SELECT pg_size_pretty(pg_database_size(current_database())) as db_size
        """))
        stats['database_size'] = result.fetchone()[0]
        
        # Log de estadísticas
        log_system_event(
            action="database_maintenance",
            details=stats
        )
        
        logger.info(f"Mantenimiento de base de datos completado")
        return {'status': 'completed', 'stats': stats}
        
    except Exception as exc:
        logger.error(f"Error en mantenimiento de base de datos: {str(exc)}")
        return {'status': 'failed', 'error': str(exc)}


def get_directory_size(path):
    """
    Calcula el tamaño total de un directorio en bytes.
    """
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
    except Exception:
        pass
    return total_size