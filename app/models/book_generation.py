"""
Modelo de Generación de Libros para Buko AI
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Enum as SQLEnum, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from .base import BaseModel, db


class BookStatus(enum.Enum):
    """Estados de generación de libros"""
    QUEUED = "QUEUED"
    ARCHITECTURE_REVIEW = "ARCHITECTURE_REVIEW"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class BookFormat(enum.Enum):
    """Formatos de libro"""
    PDF = "pdf"
    EPUB = "epub"
    DOCX = "docx"
    TXT = "txt"


class BookGeneration(BaseModel):
    """Modelo para generación de libros"""
    
    __tablename__ = "book_generations"
    
    # Relación con usuario
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="books")
    
    # Información básica del libro
    title = Column(String(500), nullable=False)
    genre = Column(String(100), nullable=True)
    target_audience = Column(String(200), nullable=True)
    tone = Column(String(100), nullable=True)
    key_topics = Column(Text, nullable=True)
    chapter_count = Column(Integer, default=10, nullable=False)
    page_count = Column(Integer, default=50, nullable=False)
    format_size = Column(String(20), default="pocket", nullable=False)
    line_spacing = Column(String(20), default="medium", nullable=False)
    language = Column(String(5), default="es", nullable=False)
    additional_instructions = Column(Text, nullable=True)
    
    # Configuración de estructura
    include_toc = Column(Boolean, default=True, nullable=False)
    include_introduction = Column(Boolean, default=True, nullable=False)
    include_conclusion = Column(Boolean, default=True, nullable=False)
    writing_style = Column(String(200), nullable=True)
    
    # Parámetros completos (JSON)
    parameters = Column(JSON, nullable=True)
    
    # Contenido generado
    content = Column(Text, nullable=True)
    content_html = Column(Text, nullable=True)  # Contenido en HTML estructurado para formateo profesional
    thinking_content = Column(Text, nullable=True)
    thinking_length = Column(Integer, default=0, nullable=False)
    
    # Arquitectura del libro (para flujo de dos etapas)
    architecture = Column(JSON, nullable=True)
    architecture_approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Feedback de regeneración de arquitectura (para estadísticas)
    regeneration_feedback_what = Column(Text, nullable=True)  # Lo que no le gustó
    regeneration_feedback_how = Column(Text, nullable=True)   # Qué quiere cambiar
    regeneration_history = Column(JSON, nullable=True)        # Historial de regeneraciones
    regeneration_count = Column(Integer, default=0, nullable=False)  # Número de regeneraciones
    
    # Estado del procesamiento
    status = Column(SQLEnum(BookStatus), default=BookStatus.QUEUED, nullable=False)
    task_id = Column(String(255), nullable=True, index=True)
    queue_position = Column(Integer, nullable=True)
    priority = Column(Integer, default=0, nullable=False)
    
    # Métricas de tokens
    prompt_tokens = Column(Integer, default=0, nullable=False)
    completion_tokens = Column(Integer, default=0, nullable=False)
    thinking_tokens = Column(Integer, default=0, nullable=False)
    total_tokens = Column(Integer, default=0, nullable=False)
    estimated_cost = Column(DECIMAL(10, 4), default=0.0000, nullable=False)
    
    # Estadísticas de streaming
    streaming_stats = Column(JSON, nullable=True)
    
    # Resultado final
    final_pages = Column(Integer, nullable=True)
    final_words = Column(Integer, nullable=True)
    file_paths = Column(JSON, nullable=True)
    cover_url = Column(String(500), nullable=True)
    
    # Manejo de errores
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    
    # Timestamps de procesamiento
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones
    downloads = relationship("BookDownload", back_populates="book", cascade="all, delete-orphan")
    
    def __init__(self, **kwargs):
        """Inicializa una nueva generación de libro"""
        super().__init__(**kwargs)
        
        # Construir parámetros completos
        if not self.parameters:
            self.parameters = self._build_parameters()
    
    def _build_parameters(self) -> Dict[str, Any]:
        """Construye los parámetros completos del libro"""
        return {
            "title": self.title,
            "genre": self.genre,
            "target_audience": self.target_audience,
            "tone": self.tone,
            "key_topics": self.key_topics,
            "chapter_count": self.chapter_count,
            "page_count": self.page_count,
            "page_size": self.format_size,  # Mapear format_size a page_size para Claude
            "line_spacing": self.line_spacing,  # Incluir line_spacing faltante
            "language": self.language,
            "additional_instructions": self.additional_instructions,
            "include_toc": self.include_toc,
            "include_introduction": self.include_introduction,
            "include_conclusion": self.include_conclusion,
            "writing_style": self.writing_style,
        }
    
    @property
    def is_completed(self) -> bool:
        """Verifica si la generación está completada"""
        return self.status == BookStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Verifica si la generación falló"""
        return self.status == BookStatus.FAILED
    
    @property
    def is_processing(self) -> bool:
        """Verifica si está siendo procesado"""
        return self.status == BookStatus.PROCESSING
    
    @property
    def is_queued(self) -> bool:
        """Verifica si está en cola"""
        return self.status == BookStatus.QUEUED
    
    @property
    def is_architecture_review(self) -> bool:
        """Verifica si está esperando revisión de arquitectura"""
        return self.status == BookStatus.ARCHITECTURE_REVIEW
    
    @property
    def has_architecture(self) -> bool:
        """Verifica si tiene arquitectura generada"""
        return self.architecture is not None
    
    @property
    def is_architecture_approved(self) -> bool:
        """Verifica si la arquitectura fue aprobada"""
        return self.architecture_approved_at is not None
    
    @property
    def can_retry(self) -> bool:
        """Verifica si puede reintentarse"""
        return self.retry_count < self.max_retries and self.is_failed
    
    @property
    def processing_time(self) -> Optional[float]:
        """Retorna el tiempo de procesamiento en segundos"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    @property
    def estimated_reading_time(self) -> Optional[int]:
        """Retorna el tiempo estimado de lectura en minutos"""
        if self.final_words:
            # Promedio de 200 palabras por minuto
            return max(1, self.final_words // 200)
        return None
    
    @property
    def file_formats(self) -> List[str]:
        """Retorna los formatos de archivo disponibles"""
        if self.file_paths:
            return list(self.file_paths.keys())
        return []
    
    def start_processing(self) -> None:
        """Marca el libro como en procesamiento"""
        self.status = BookStatus.PROCESSING
        self.started_at = datetime.now(timezone.utc)
        db.session.commit()
    
    def mark_completed(self, content: str, final_stats: Dict[str, Any]) -> None:
        """Marca el libro como completado"""
        self.status = BookStatus.COMPLETED
        self.content = content  # Mantener para compatibilidad
        self.content_html = content  # El contenido ya viene en HTML estructurado
        self.completed_at = datetime.now(timezone.utc)
        
        # Actualizar estadísticas finales
        if final_stats:
            self.final_pages = final_stats.get("estimated_pages")
            self.final_words = final_stats.get("estimated_words")
            self.streaming_stats = final_stats
            
            # Actualizar número real de capítulos si está disponible
            if final_stats.get("chapters"):
                self.chapter_count = final_stats.get("chapters")
        
        db.session.commit()
    
    def mark_failed(self, error_message: str) -> None:
        """Marca el libro como fallido"""
        self.status = BookStatus.FAILED
        self.error_message = error_message
        self.completed_at = datetime.utcnow()
        db.session.commit()
    
    def retry_generation(self) -> None:
        """Reintenta la generación"""
        if self.can_retry:
            self.retry_count += 1
            self.status = BookStatus.QUEUED
            self.error_message = None
            self.started_at = None
            self.completed_at = None
            db.session.commit()
    
    def cancel_generation(self) -> None:
        """Cancela la generación"""
        self.status = BookStatus.CANCELLED
        self.completed_at = datetime.utcnow()
        db.session.commit()
    
    def mark_architecture_review(self, architecture: Dict[str, Any]) -> None:
        """Marca el libro como esperando revisión de arquitectura"""
        self.status = BookStatus.ARCHITECTURE_REVIEW
        self.architecture = architecture
        self.completed_at = None  # Reset completed_at
        db.session.commit()
    
    def approve_architecture(self, updated_architecture: Optional[Dict[str, Any]] = None) -> None:
        """Aprueba la arquitectura y marca para generación completa"""
        if updated_architecture:
            self.architecture = updated_architecture
        self.architecture_approved_at = datetime.now(timezone.utc)
        self.status = BookStatus.QUEUED  # Volver a cola para generación completa
        
        # Convertir contenido markdown existente a HTML si existe
        if self.content and not self.content_html:
            from app.services.markdown_to_html_service import convert_markdown_to_content_html
            try:
                self.content_html = convert_markdown_to_content_html(self.content)
            except Exception as e:
                # Log error pero no fallar la aprobación
                print(f"Error converting markdown to HTML: {e}")
        
        db.session.commit()
    
    def add_regeneration_feedback(self, feedback_what: str, feedback_how: str, current_architecture: Dict[str, Any]) -> None:
        """Agrega feedback de regeneración al historial"""
        self.regeneration_feedback_what = feedback_what
        self.regeneration_feedback_how = feedback_how
        self.regeneration_count += 1
        
        # Inicializar historial si no existe
        if not self.regeneration_history:
            self.regeneration_history = []
        
        # Agregar entrada al historial
        regeneration_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "feedback_what": feedback_what,
            "feedback_how": feedback_how,
            "previous_architecture": current_architecture,
            "regeneration_number": self.regeneration_count
        }
        self.regeneration_history.append(regeneration_entry)
        
        # Limitar historial a las últimas 10 regeneraciones para evitar que crezca demasiado
        if len(self.regeneration_history) > 10:
            self.regeneration_history = self.regeneration_history[-10:]
        
        db.session.commit()
    
    def get_regeneration_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de regeneración para análisis"""
        return {
            "regeneration_count": self.regeneration_count,
            "has_regenerations": self.regeneration_count > 0,
            "last_feedback_what": self.regeneration_feedback_what,
            "last_feedback_how": self.regeneration_feedback_how,
            "regeneration_history_count": len(self.regeneration_history) if self.regeneration_history else 0,
            "most_common_feedback_themes": self._analyze_feedback_themes() if self.regeneration_history else []
        }
    
    def _analyze_feedback_themes(self) -> List[str]:
        """Analiza los temas más comunes en el feedback de regeneración"""
        if not self.regeneration_history:
            return []
        
        # Palabras clave comunes en feedback de arquitectura
        themes_keywords = {
            "characters": ["personaje", "character", "protagonista", "mentor"],
            "structure": ["estructura", "structure", "capítulo", "chapter", "organización"],
            "content": ["contenido", "content", "tema", "topic", "información"],
            "tone": ["tono", "tone", "estilo", "style", "enfoque", "approach"],
            "length": ["largo", "length", "páginas", "pages", "extenso", "corto"]
        }
        
        feedback_texts = []
        for entry in self.regeneration_history:
            feedback_texts.extend([entry.get("feedback_what", ""), entry.get("feedback_how", "")])
        
        combined_feedback = " ".join(feedback_texts).lower()
        
        themes_found = []
        for theme, keywords in themes_keywords.items():
            if any(keyword in combined_feedback for keyword in keywords):
                themes_found.append(theme)
        
        return themes_found[:3]  # Retornar máximo 3 temas principales
    
    def update_queue_position(self, position: int) -> None:
        """Actualiza la posición en cola"""
        self.queue_position = position
        db.session.commit()
    
    def update_tokens(self, prompt_tokens: int, completion_tokens: int, thinking_tokens: int = 0) -> None:
        """Actualiza las métricas de tokens ACUMULANDO todas las fases (arquitectura + regeneración + generación)"""
        # ACUMULAR tokens de todas las fases en lugar de sobrescribir
        self.prompt_tokens = (self.prompt_tokens or 0) + prompt_tokens
        self.completion_tokens = (self.completion_tokens or 0) + completion_tokens
        self.thinking_tokens = (self.thinking_tokens or 0) + thinking_tokens
        self.total_tokens = self.prompt_tokens + self.completion_tokens + self.thinking_tokens
        
        # Calcular costo estimado total (precios Claude Sonnet 4)
        input_cost = (self.prompt_tokens / 1000) * 0.015
        output_cost = (self.completion_tokens / 1000) * 0.075
        thinking_cost = (self.thinking_tokens / 1000) * 0.015
        self.estimated_cost = round(input_cost + output_cost + thinking_cost, 4)
        
        db.session.commit()
    
    def update_file_paths(self, file_paths: Dict[str, str]) -> None:
        """Actualiza las rutas de archivos generados"""
        self.file_paths = file_paths
        db.session.commit()
    
    def get_file_path(self, format_type: str) -> Optional[str]:
        """Retorna la ruta del archivo en el formato especificado"""
        if self.file_paths:
            return self.file_paths.get(format_type)
        return None
    
    def get_download_url(self, format_type: str) -> Optional[str]:
        """Retorna la URL de descarga para el formato especificado"""
        file_path = self.get_file_path(format_type)
        if file_path:
            return f"/api/books/{self.uuid}/download/{format_type}"
        return None
    
    def get_progress_info(self) -> Dict[str, Any]:
        """Retorna información de progreso"""
        return {
            "id": self.id,
            "uuid": str(self.uuid),
            "title": self.title,
            "status": self.status.value,
            "queue_position": self.queue_position,
            "progress": self._calculate_progress(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "estimated_completion": self._estimate_completion_time(),
            "error_message": self.error_message,
            "can_retry": self.can_retry,
        }
    
    def _calculate_progress(self) -> int:
        """Calcula el progreso porcentual dinámico basado en tiempo transcurrido"""
        if self.status == BookStatus.COMPLETED:
            return 100
        elif self.status == BookStatus.FAILED:
            return -1
        elif self.status == BookStatus.QUEUED:
            return 0
        elif self.status == BookStatus.ARCHITECTURE_REVIEW:
            return 25  # Arquitectura generada, esperando aprobación
        elif self.status == BookStatus.PROCESSING:
            # Progreso dinámico basado en tiempo transcurrido
            if not self.started_at:
                return 5  # Recién iniciado
            
            elapsed_minutes = (datetime.now(timezone.utc) - self.started_at).total_seconds() / 60
            estimated_total_minutes = self.page_count * 0.5  # ~30 segundos por página
            
            # Progreso base de 10% + progreso por tiempo transcurrido
            time_progress = min(80, (elapsed_minutes / estimated_total_minutes) * 80)
            return max(10, min(90, 10 + int(time_progress)))
        return 0
    
    def _estimate_completion_time(self) -> Optional[str]:
        """Estima el tiempo de finalización"""
        if self.status == BookStatus.COMPLETED:
            return None
        
        # Estimación basada en páginas (ejemplo: 30 segundos por página)
        estimated_seconds = self.page_count * 30
        
        if self.queue_position:
            # Agregar tiempo de cola
            estimated_seconds += self.queue_position * 60
        
        estimated_completion = datetime.utcnow() + timedelta(seconds=estimated_seconds)
        return estimated_completion.isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario"""
        base_dict = super().to_dict()
        base_dict.update({
            "user_email": self.user.email if self.user else None,
            "is_completed": self.is_completed,
            "is_failed": self.is_failed,
            "is_processing": self.is_processing,
            "processing_time": self.processing_time,
            "estimated_reading_time": self.estimated_reading_time,
            "file_formats": self.file_formats,
            "download_urls": {
                fmt: self.get_download_url(fmt) for fmt in self.file_formats
            },
        })
        return base_dict
    
    @classmethod
    def get_by_user(cls, user_id: int) -> List['BookGeneration']:
        """Retorna libros de un usuario"""
        return cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def find_by_uuid(cls, uuid_str: str) -> Optional['BookGeneration']:
        """Busca un libro por UUID"""
        return cls.query.filter_by(uuid=uuid_str).first()
    
    @classmethod
    def get_queued_books(cls) -> List['BookGeneration']:
        """Retorna libros en cola ordenados por prioridad"""
        return cls.query.filter_by(status=BookStatus.QUEUED).order_by(
            cls.priority.desc(), cls.created_at.asc()
        ).all()
    
    @classmethod
    def get_processing_books(cls) -> List['BookGeneration']:
        """Retorna libros en procesamiento"""
        return cls.query.filter_by(status=BookStatus.PROCESSING).all()
    
    @classmethod
    def get_completed_books(cls) -> List['BookGeneration']:
        """Retorna libros completados"""
        return cls.query.filter_by(status=BookStatus.COMPLETED).all()
    
    @classmethod
    def get_failed_books(cls) -> List['BookGeneration']:
        """Retorna libros fallidos"""
        return cls.query.filter_by(status=BookStatus.FAILED).all()
    
    @classmethod
    def get_architecture_review_books(cls) -> List['BookGeneration']:
        """Retorna libros esperando revisión de arquitectura"""
        return cls.query.filter_by(status=BookStatus.ARCHITECTURE_REVIEW).all()
    
    @classmethod
    def get_statistics(cls) -> Dict[str, Any]:
        """Retorna estadísticas globales"""
        total = cls.query.count()
        completed = cls.query.filter_by(status=BookStatus.COMPLETED).count()
        failed = cls.query.filter_by(status=BookStatus.FAILED).count()
        processing = cls.query.filter_by(status=BookStatus.PROCESSING).count()
        queued = cls.query.filter_by(status=BookStatus.QUEUED).count()
        architecture_review = cls.query.filter_by(status=BookStatus.ARCHITECTURE_REVIEW).count()
        
        return {
            "total_books": total,
            "completed_books": completed,
            "failed_books": failed,
            "processing_books": processing,
            "queued_books": queued,
            "architecture_review_books": architecture_review,
            "success_rate": (completed / total * 100) if total > 0 else 0,
            "average_processing_time": cls._calculate_average_processing_time(),
        }
    
    @classmethod
    def _calculate_average_processing_time(cls) -> Optional[float]:
        """Calcula el tiempo promedio de procesamiento"""
        completed_books = cls.query.filter(
            cls.status == BookStatus.COMPLETED,
            cls.started_at.isnot(None),
            cls.completed_at.isnot(None)
        ).all()
        
        if not completed_books:
            return None
        
        total_time = sum(
            (book.completed_at - book.started_at).total_seconds()
            for book in completed_books
        )
        
        return total_time / len(completed_books)
    
    def get_cover_gradient(self) -> str:
        """Genera un gradiente de color para la portada basado en el género"""
        gradients = {
            'fiction': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'non_fiction': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            'children': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            'poetry': 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
            'technical': 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
            'self_help': 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
            'biography': 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
            'history': 'linear-gradient(135deg, #ffd89b 0%, #19547b 100%)',
            'science_fiction': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'romance': 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)',
            'mystery': 'linear-gradient(135deg, #434343 0%, #000000 100%)',
            'fantasy': 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
        }
        return gradients.get(self.genre, 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)')
    
    def get_estimated_pages(self) -> int:
        """Retorna el número estimado de páginas"""
        if self.final_pages:
            return self.final_pages
        
        # Estimación basada en palabras (250 palabras por página)
        if self.final_words:
            return max(1, self.final_words // 250)
        
        # Estimación basada en capítulos (15 páginas por capítulo)
        return self.chapter_count * 15
    
    def get_word_count(self) -> int:
        """Retorna el número de palabras"""
        if self.final_words:
            return self.final_words
        
        # Estimación basada en contenido
        if self.content:
            return len(self.content.split())
        
        # Estimación basada en capítulos (3000 palabras por capítulo)
        return self.chapter_count * 3000
    
    def get_chapter_count(self) -> int:
        """Retorna el número de capítulos"""
        if self.content_data and isinstance(self.content_data, dict):
            chapters = self.content_data.get('chapters', [])
            if chapters:
                return len(chapters)
        
        return self.chapter_count or 10
    
    def get_reading_time(self) -> int:
        """Retorna el tiempo de lectura en minutos"""
        if self.estimated_reading_time:
            return self.estimated_reading_time
        
        # Estimación basada en palabras (200 palabras por minuto)
        word_count = self.get_word_count()
        return max(1, word_count // 200)
    
    @property
    def content_data(self) -> Optional[Dict[str, Any]]:
        """Retorna el contenido estructurado como diccionario"""
        if self.content:
            try:
                # Si el contenido es JSON, parsearlo
                import json
                return json.loads(self.content)
            except:
                # Si no es JSON, estructurar el contenido como un solo capítulo
                return {
                    'chapters': [
                        {
                            'title': 'Contenido Principal',
                            'content': self.content
                        }
                    ]
                }
        return None
    
    @property
    def progress(self) -> int:
        """Retorna el progreso como un número entero"""
        return self._calculate_progress()
    
    @property
    def current_step(self) -> str:
        """Retorna el paso actual de procesamiento con detalles dinámicos"""
        if self.status == BookStatus.QUEUED:
            if self.is_architecture_approved:
                return "En cola para generación completa del libro"
            if self.queue_position:
                return f"En cola de procesamiento (posición {self.queue_position})"
            return "En cola de procesamiento"
        elif self.status == BookStatus.ARCHITECTURE_REVIEW:
            return "Arquitectura del libro generada - Esperando tu aprobación"
        elif self.status == BookStatus.PROCESSING:
            if not self.started_at:
                return "Iniciando generación con Claude AI..."
            
            elapsed_minutes = (datetime.now(timezone.utc) - self.started_at).total_seconds() / 60
            estimated_total_minutes = self.page_count * 0.5  # Misma lógica que _calculate_progress()
            progress_percentage = min(90, max(10, 10 + int((elapsed_minutes / estimated_total_minutes) * 80)))
            
            # Mensajes basados en progreso real en lugar de tiempo fijo
            if progress_percentage < 15:
                return "Conectando con Claude AI y analizando tu solicitud..."
            elif progress_percentage < 30:
                return f"Claude está pensando profundamente en tu libro... ({int(elapsed_minutes)} min, {progress_percentage}%)"
            elif progress_percentage < 50:
                return f"Generando contenido... ({int(elapsed_minutes)} min, {progress_percentage}%)"
            elif progress_percentage < 75:
                return f"Escribiendo capítulos... ({int(elapsed_minutes)} min, {progress_percentage}%)"
            else:
                return f"Finalizando generación... ({int(elapsed_minutes)} min, {progress_percentage}%)"
        elif self.status == BookStatus.COMPLETED:
            return "Generación completada exitosamente"
        elif self.status == BookStatus.FAILED:
            return f"Error en la generación: {self.error_message or 'Error desconocido'}"
        else:
            return "Estado desconocido"
    
    def __repr__(self) -> str:
        return f"<BookGeneration {self.title} by {self.user.email if self.user else 'Unknown'}>"