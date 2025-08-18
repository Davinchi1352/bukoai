"""
Generador Profesional de Documentos Aspose.Words
Sistema de última generación para la creación de documentos Word profesionales.

Características principales:
- Arquitectura modular con patrones factory
- Configuración dinámica y flexible
- Compatibilidad con cualquier tipo de libro
- Algoritmos avanzados de formato y layout
- Integración inteligente con Claude AI
"""

import os
import tempfile
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

# Configure globalization BEFORE importing Aspose.Words
os.environ['DOTNET_SYSTEM_GLOBALIZATION_INVARIANT'] = 'true'
os.environ['DOTNET_SYSTEM_GLOBALIZATION_USENLS'] = 'false'

# Global flag to track Aspose.Words availability
ASPOSE_WORDS_AVAILABLE = False
aspose_import_error = None

try:
    import aspose.words as aw
    from aspose.words import Document, DocumentBuilder, SaveFormat
    from aspose.words.drawing import RelativeHorizontalPosition, RelativeVerticalPosition
    from aspose.words.drawing import WrapType
    import aspose.pydrawing as drawing
    ASPOSE_WORDS_AVAILABLE = True
except Exception as e:
    aspose_import_error = str(e)
    # Create mock classes to prevent import errors
    class MockDocument:
        def __init__(self, *args, **kwargs):
            raise RuntimeError(f"Aspose.Words not available: {aspose_import_error}")
    
    class MockDocumentBuilder:
        def __init__(self, *args, **kwargs):
            raise RuntimeError(f"Aspose.Words not available: {aspose_import_error}")
    
    class MockSaveFormat:
        DOCX = "docx"
        PDF = "pdf"
    
    class MockDrawing:
        class Color:
            @staticmethod
            def from_argb(a, r, g, b):
                return f"Color(a={a}, r={r}, g={g}, b={b})"
    
    # Use mock classes
    aw = None
    Document = MockDocument
    DocumentBuilder = MockDocumentBuilder
    SaveFormat = MockSaveFormat
    drawing = MockDrawing
    RelativeHorizontalPosition = None
    RelativeVerticalPosition = None
    WrapType = None

from app.models.book_generation import BookGeneration
from app.services.intelligent_content_generator import (
    IntelligentContentGenerator, 
    ContentType, 
    ContentGenerationRequest,
    BookAnalysis
)

logger = logging.getLogger(__name__)


class PageFormat(Enum):
    """Formatos de página estándar para libros"""
    POCKET = "pocket"  # 4.25" x 6.87"
    MASS_MARKET = "mass_market"  # 4.25" x 7"
    TRADE_PAPERBACK = "trade_paperback"  # 6" x 9"
    HARDCOVER = "hardcover"  # 6.14" x 9.21"
    LARGE_FORMAT = "large_format"  # 8.5" x 11"
    SQUARE = "square"  # 8" x 8"
    CUSTOM = "custom"


class FontFamily(Enum):
    """Familias de fuentes profesionales"""
    TIMES_NEW_ROMAN = "Times New Roman"
    GARAMOND = "Garamond"
    GEORGIA = "Georgia"
    MINION_PRO = "Minion Pro"
    CRIMSON_PRO = "Crimson Text"
    LIBRE_BASKERVILLE = "Libre Baskerville"
    BOOK_ANTIQUA = "Book Antiqua"
    PALATINO = "Palatino Linotype"


@dataclass
class PageDimensions:
    """Dimensiones de página en puntos (1 inch = 72 points)"""
    width: float
    height: float
    margin_top: float = 72.0  # 1 inch
    margin_bottom: float = 72.0
    margin_left: float = 72.0
    margin_right: float = 72.0
    
    @classmethod
    def from_format(cls, page_format: PageFormat) -> 'PageDimensions':
        """Crea dimensiones basadas en formato estándar"""
        dimensions_map = {
            PageFormat.POCKET: cls(width=306, height=495),  # 4.25" x 6.87"
            PageFormat.MASS_MARKET: cls(width=306, height=504),  # 4.25" x 7"
            PageFormat.TRADE_PAPERBACK: cls(width=432, height=648),  # 6" x 9"
            PageFormat.HARDCOVER: cls(width=442, height=662),  # 6.14" x 9.21"
            PageFormat.LARGE_FORMAT: cls(width=612, height=792),  # 8.5" x 11"
            PageFormat.SQUARE: cls(width=576, height=576),  # 8" x 8"
        }
        return dimensions_map.get(page_format, cls(width=432, height=648))


@dataclass
class TypographySettings:
    """Configuración tipográfica profesional"""
    body_font_family: FontFamily = FontFamily.TIMES_NEW_ROMAN
    body_font_size: float = 11.0
    heading_font_family: FontFamily = FontFamily.TIMES_NEW_ROMAN
    heading_font_size: float = 16.0
    line_spacing: float = 1.2
    paragraph_spacing_before: float = 6.0
    paragraph_spacing_after: float = 6.0
    first_line_indent: float = 18.0  # 0.25 inch
    use_drop_caps: bool = True
    drop_cap_lines: int = 3
    chapter_title_size: float = 18.0
    use_small_caps_for_headers: bool = True
    justify_text: bool = True


@dataclass
class BookStructureSettings:
    """Configuración de estructura del libro"""
    include_cover_page: bool = True
    include_title_page: bool = True
    include_copyright_page: bool = True
    include_dedication: bool = True
    include_table_of_contents: bool = True
    include_prologue: bool = False
    include_epilogue: bool = False
    include_acknowledgments: bool = False
    include_about_author: bool = True
    include_bibliography: bool = False
    page_numbering_start: int = 1
    start_chapters_on_odd_page: bool = True
    use_headers_footers: bool = True


@dataclass
class ExportSettings:
    """Configuración de exportación"""
    format: SaveFormat = SaveFormat.DOCX
    include_bookmarks: bool = True
    optimize_for_print: bool = True
    embed_fonts: bool = False
    compress_images: bool = True
    quality_level: int = 85  # Para imágenes


@dataclass
class AsposeDocumentConfiguration:
    """Configuración completa del documento"""
    page_format: PageFormat = PageFormat.POCKET
    page_dimensions: Optional[PageDimensions] = None
    typography: TypographySettings = field(default_factory=TypographySettings)
    structure: BookStructureSettings = field(default_factory=BookStructureSettings)
    export: ExportSettings = field(default_factory=ExportSettings)
    author_name: str = ""
    custom_styles: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.page_dimensions is None:
            self.page_dimensions = PageDimensions.from_format(self.page_format)


class AsposeProfessionalGenerator:
    """
    Generador profesional de documentos Word usando Aspose.Words.
    
    Este servicio representa un sistema de última generación que:
    - Utiliza análisis inteligente de contenido
    - Aplica formato profesional dinámico
    - Soporta cualquier tipo de libro
    - Proporciona control granular sobre el diseño
    """
    
    def __init__(self):
        # Initialize content generator with proper error handling
        try:
            self.content_generator = IntelligentContentGenerator()
            self.content_generator_available = True
            logger.info("IntelligentContentGenerator initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing IntelligentContentGenerator: {str(e)}")
            self.content_generator = None
            self.content_generator_available = False
            logger.warning("Using fallback content generation mode")
        
        self.document = None
        self.builder = None
        self.config = None
        self.book_analysis = None
        self.aspose_available = ASPOSE_WORDS_AVAILABLE
        self.aspose_error = aspose_import_error
        
        if not self.aspose_available:
            logger.warning(f"Aspose.Words not available: {self.aspose_error}")
            logger.info("Professional document generation will use fallback mode")
        else:
            logger.info("Aspose.Words loaded successfully")
            # Inicializar Aspose.Words license si está disponible
            self._initialize_license()
    
    def generate_professional_document(
        self, 
        book: BookGeneration, 
        config: AsposeDocumentConfiguration,
        output_path: Optional[str] = None
    ) -> str:
        """
        Genera un documento Word profesional completo.
        
        Args:
            book: El libro a formatear
            config: Configuración del documento
            output_path: Ruta de salida opcional
        
        Returns:
            Ruta del archivo generado
        """
        try:
            logger.info(f"Iniciando generación profesional para: {book.title}")
            
            # Análizar contenido del libro
            self.book_analysis = self.content_generator.analyze_book_content(book)
            self.config = config
            
            # Crear documento nuevo
            self.document = Document()
            self.builder = DocumentBuilder(self.document)
            
            # Configurar página y estilos
            self._setup_document_structure()
            self._create_professional_styles()
            
            # Generar secciones del libro
            self._generate_document_sections(book)
            
            # Configurar numeración y navegación
            self._setup_page_numbering()
            self._create_bookmarks_and_navigation()
            
            # Guardar documento
            output_file = output_path or self._generate_output_filename(book)
            self.document.save(output_file)
            
            logger.info(f"Documento generado exitosamente: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error generando documento profesional: {str(e)}")
            raise
    
    def generate_preview_document(
        self, 
        book: BookGeneration, 
        config: AsposeDocumentConfiguration,
        max_pages: int = 10
    ) -> str:
        """
        Genera una vista previa limitada del documento para configuración en tiempo real.
        Si Aspose.Words no está disponible, usa un modo de fallback.
        """
        # Check if Aspose.Words is available
        if not self.aspose_available:
            logger.warning("Aspose.Words not available, using fallback preview generation")
            return self._generate_fallback_preview(book, config, max_pages)
        
        try:
            # Manejar tanto objetos AsposeDocumentConfiguration como diccionarios
            if isinstance(config, dict):
                # Si es un diccionario, convertir a objeto usando el mismo método que el endpoint
                from app.routes.professional_aspose import _build_aspose_config_from_request
                config = _build_aspose_config_from_request(config)
            
            # Configuración modificada para preview
            preview_config = AsposeDocumentConfiguration(
                page_format=config.page_format,
                page_dimensions=config.page_dimensions,
                typography=config.typography,
                structure=BookStructureSettings(
                    include_cover_page=True,
                    include_title_page=True,
                    include_table_of_contents=True,
                    include_dedication=config.structure.include_dedication,
                    include_prologue=False,  # Omitir para preview
                    include_epilogue=False,
                    include_acknowledgments=False,
                    include_about_author=False
                ),
                export=config.export,
                author_name=config.author_name
            )
            
            # Análizar contenido con fallback handling
            if self.content_generator_available and self.content_generator:
                self.book_analysis = self.content_generator.analyze_book_content(book)
            else:
                # Fallback mode: create basic book analysis
                self.book_analysis = self._create_fallback_book_analysis(book)
            self.config = preview_config
            
            # Crear documento de preview
            self.document = Document()
            self.builder = DocumentBuilder(self.document)
            
            # Configuración básica
            logger.info("Setting up document structure...")
            self._setup_document_structure()
            logger.info("Creating professional styles...")
            self._create_professional_styles()
            
            # Generar secciones principales para preview
            try:
                if preview_config.structure.include_cover_page:
                    logger.info("Creating cover page...")
                    self._create_cover_page(book)
                    self.builder.insert_break(aw.BreakType.PAGE_BREAK)
                
                if preview_config.structure.include_title_page:
                    logger.info("Creating title page...")
                    self._create_title_page(book)
                    self.builder.insert_break(aw.BreakType.PAGE_BREAK)
                
                if preview_config.structure.include_table_of_contents:
                    logger.info("Creating table of contents...")
                    self._create_table_of_contents(book)
                    self.builder.insert_break(aw.BreakType.PAGE_BREAK)
                
                if preview_config.structure.include_dedication:
                    logger.info("Creating dedication page...")
                    self._create_dedication_page(book)
                    self.builder.insert_break(aw.BreakType.PAGE_BREAK)
                
                # Agregar muestra del primer capítulo
                logger.info("Creating sample chapter...")
                self._create_sample_chapter(book, max_pages - 4)  # Reservar 4 páginas para preliminares
                
            except Exception as section_error:
                logger.error(f"Error in specific section creation: {str(section_error)}")
                logger.error(f"Error type: {type(section_error).__name__}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise
            
            # Guardar preview
            preview_file = self._generate_preview_filename(book)
            # Use proper SaveFormat - save() only needs the file path with correct extension
            self.document.save(preview_file)
            
            return preview_file
            
        except Exception as e:
            logger.error(f"Error generando preview: {str(e)}")
            raise
    
    def _configure_globalization(self):
        """
        Configura la globalización para Aspose.Words usando modo invariante.
        Usa modo invariante como estrategia principal para evitar problemas de ICU.
        """
        try:
            import os
            import sys
            
            logger.info("Configurando globalización para Aspose.Words...")
            
            # Usar modo invariante como estrategia principal
            # Esto evita todos los problemas relacionados con ICU
            os.environ['DOTNET_SYSTEM_GLOBALIZATION_INVARIANT'] = 'true'
            os.environ['DOTNET_SYSTEM_GLOBALIZATION_USENLS'] = 'false'
            
            logger.info("Globalization set to invariant mode - avoiding ICU dependencies")
            
            # Verificar que Aspose.Words puede inicializarse correctamente
            try:
                # Test básico de Aspose.Words para verificar funcionamiento
                logger.info("Testing Aspose.Words initialization...")
                test_doc = aw.Document()
                test_builder = aw.DocumentBuilder(test_doc)
                test_builder.write("Test initialization - invariant mode")
                
                # Verificar que podemos escribir texto básico
                test_content = test_doc.get_text()
                if "Test initialization" not in test_content:
                    raise Exception("Aspose.Words content generation test failed")
                
                # Cleanup del test
                del test_doc
                del test_builder
                
                logger.info("✅ Aspose.Words initialization successful in invariant mode")
                self.icu_available = False  # No usamos ICU pero funciona
                
            except Exception as aspose_error:
                logger.error(f"❌ Aspose.Words initialization failed: {aspose_error}")
                
                # Intentar configuración alternativa
                logger.info("Trying alternative configuration...")
                os.environ['DOTNET_SYSTEM_GLOBALIZATION_INVARIANT'] = 'true'
                os.environ['DOTNET_SYSTEM_NET_DISABLEIPV6'] = 'true'
                
                try:
                    # Re-test con configuración alternativa
                    test_doc2 = aw.Document()
                    test_builder2 = aw.DocumentBuilder(test_doc2)
                    test_builder2.write("Alternative test")
                    del test_doc2
                    del test_builder2
                    
                    logger.info("✅ Aspose.Words working with alternative configuration")
                    self.icu_available = False
                    
                except Exception as final_error:
                    logger.critical(f"❌ Cannot initialize Aspose.Words: {final_error}")
                    raise RuntimeError(f"Aspose.Words initialization failed completely: {final_error}")
            
            logger.info("🎯 Globalization configuration completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Critical error in globalization configuration: {e}")
            raise RuntimeError(f"Could not configure Aspose.Words globalization: {e}")

    def _initialize_license(self):
        """Inicializa la licencia de Aspose.Words si está disponible"""
        try:
            # Buscar archivo de licencia
            license_paths = [
                "/app/licenses/Aspose.Words.lic",
                "./licenses/Aspose.Words.lic",
                os.environ.get('ASPOSE_LICENSE_PATH', '')
            ]
            
            for license_path in license_paths:
                if license_path and os.path.exists(license_path):
                    license = aw.License()
                    license.set_license(license_path)
                    logger.info("Licencia Aspose.Words inicializada correctamente")
                    return
            
            logger.warning("Licencia Aspose.Words no encontrada - usando modo evaluación")
            
        except Exception as e:
            logger.warning(f"Error inicializando licencia Aspose.Words: {str(e)}")
    
    def _setup_document_structure(self):
        """Configura la estructura básica del documento"""
        # Configurar página
        page_setup = self.builder.page_setup
        dims = self.config.page_dimensions
        
        page_setup.page_width = dims.width
        page_setup.page_height = dims.height
        page_setup.top_margin = dims.margin_top
        page_setup.bottom_margin = dims.margin_bottom
        page_setup.left_margin = dims.margin_left
        page_setup.right_margin = dims.margin_right
        
        # Configurar orientación y calidad
        page_setup.orientation = aw.Orientation.PORTRAIT
        page_setup.paper_size = aw.PaperSize.CUSTOM
        
        # Configurar headers y footers si están habilitados
        if self.config.structure.use_headers_footers:
            self._setup_headers_footers()
    
    def _create_professional_styles(self):
        """Crea estilos profesionales para el documento"""
        styles = self.document.styles
        typo = self.config.typography
        
        # Estilo para texto del cuerpo
        body_style = styles.add(aw.StyleType.PARAGRAPH, "BookBody")
        body_font = body_style.font
        body_font.name = typo.body_font_family.value
        body_font.size = typo.body_font_size
        
        body_paragraph = body_style.paragraph_format
        body_paragraph.line_spacing_rule = aw.LineSpacingRule.MULTIPLE
        body_paragraph.line_spacing = typo.line_spacing
        body_paragraph.space_before = typo.paragraph_spacing_before
        body_paragraph.space_after = typo.paragraph_spacing_after
        body_paragraph.first_line_indent = typo.first_line_indent
        
        if typo.justify_text:
            body_paragraph.alignment = aw.ParagraphAlignment.JUSTIFY
        
        # Estilo para títulos de capítulo
        chapter_style = styles.add(aw.StyleType.PARAGRAPH, "ChapterTitle")
        chapter_font = chapter_style.font
        chapter_font.name = typo.heading_font_family.value
        chapter_font.size = typo.chapter_title_size
        chapter_font.bold = True
        
        chapter_paragraph = chapter_style.paragraph_format
        chapter_paragraph.alignment = aw.ParagraphAlignment.CENTER
        chapter_paragraph.space_before = 36.0  # 0.5 inch
        chapter_paragraph.space_after = 24.0   # 0.33 inch
        chapter_paragraph.keep_with_next = True
        
        if typo.use_small_caps_for_headers:
            chapter_font.small_caps = True
        
        # Estilo para encabezados de sección
        heading_style = styles.add(aw.StyleType.PARAGRAPH, "SectionHeading")
        heading_font = heading_style.font
        heading_font.name = typo.heading_font_family.value
        heading_font.size = typo.heading_font_size
        heading_font.bold = True
        
        heading_paragraph = heading_style.paragraph_format
        heading_paragraph.alignment = aw.ParagraphAlignment.CENTER
        heading_paragraph.space_before = 24.0
        heading_paragraph.space_after = 18.0
        heading_paragraph.keep_with_next = True
        
        # Estilo para tabla de contenidos
        toc_style = styles.add(aw.StyleType.PARAGRAPH, "TOCEntry")
        toc_font = toc_style.font
        toc_font.name = typo.body_font_family.value
        toc_font.size = typo.body_font_size - 1
        
        toc_paragraph = toc_style.paragraph_format
        toc_paragraph.space_after = 6.0
        toc_paragraph.left_indent = 18.0
        
        # Aplicar estilos personalizados si existen
        for style_name, style_config in self.config.custom_styles.items():
            self._apply_custom_style(style_name, style_config)
    
    def _generate_document_sections(self, book: BookGeneration):
        """Genera todas las secciones del documento según la configuración"""
        structure = self.config.structure
        
        # Portada
        if structure.include_cover_page:
            self._create_cover_page(book)
            self.builder.insert_break(aw.BreakType.PAGE_BREAK)
        
        # Página de título
        if structure.include_title_page:
            self._create_title_page(book)
            self.builder.insert_break(aw.BreakType.PAGE_BREAK)
        
        # Página de copyright
        if structure.include_copyright_page:
            self._create_copyright_page(book)
            self.builder.insert_break(aw.BreakType.PAGE_BREAK)
        
        # Dedicatoria
        if structure.include_dedication:
            self._create_dedication_page(book)
            self.builder.insert_break(aw.BreakType.PAGE_BREAK)
        
        # Tabla de contenidos
        if structure.include_table_of_contents:
            self._create_table_of_contents(book)
            self.builder.insert_break(aw.BreakType.PAGE_BREAK)
        
        # Prólogo
        if structure.include_prologue:
            self._create_prologue_page(book)
            self.builder.insert_break(aw.BreakType.PAGE_BREAK)
        
        # Contenido principal (capítulos)
        self._create_main_content(book)
        
        # Epílogo
        if structure.include_epilogue:
            self.builder.insert_break(aw.BreakType.PAGE_BREAK)
            self._create_epilogue_page(book)
        
        # Agradecimientos
        if structure.include_acknowledgments:
            self.builder.insert_break(aw.BreakType.PAGE_BREAK)
            self._create_acknowledgments_page(book)
        
        # Acerca del autor
        if structure.include_about_author:
            self.builder.insert_break(aw.BreakType.PAGE_BREAK)
            self._create_about_author_page(book)
        
        # Bibliografía
        if structure.include_bibliography:
            self.builder.insert_break(aw.BreakType.PAGE_BREAK)
            self._create_bibliography_page(book)
    
    def _create_cover_page(self, book: BookGeneration):
        """Crea la página de portada"""
        # Centrar contenido verticalmente
        self.builder.paragraph_format.alignment = aw.ParagraphAlignment.CENTER
        self.builder.paragraph_format.space_before = 144.0  # 2 inches from top
        
        # Título principal
        self.builder.font.name = self.config.typography.heading_font_family.value
        self.builder.font.size = 24.0
        self.builder.font.bold = True
        self.builder.font.color = drawing.Color.from_argb(255, 0, 0, 0)  # Black color
        
        self.builder.writeln(book.title.upper())
        
        # Subtítulo si existe
        if hasattr(book, 'subtitle') and book.subtitle:
            self.builder.paragraph_format.space_before = 18.0
            self.builder.font.size = 16.0
            self.builder.font.bold = False
            self.builder.writeln(book.subtitle)
        
        # Espacio antes del autor
        self.builder.paragraph_format.space_before = 72.0  # 1 inch
        
        # Nombre del autor
        author_name = self.config.author_name or "Generado con Claude AI"
        self.builder.font.size = 14.0
        self.builder.font.bold = False
        self.builder.writeln(f"Por {author_name}")
        
        # Resetear formato
        self._reset_paragraph_format()
    
    def _create_title_page(self, book: BookGeneration):
        """Crea la página de título oficial"""
        # Similar a portada pero con más detalles legales
        self.builder.paragraph_format.alignment = aw.ParagraphAlignment.CENTER
        self.builder.paragraph_format.space_before = 108.0  # 1.5 inches
        
        # Título
        self.builder.font.name = self.config.typography.heading_font_family.value
        self.builder.font.size = 22.0
        self.builder.font.bold = True
        
        self.builder.writeln(book.title)
        
        # Autor
        self.builder.paragraph_format.space_before = 36.0
        self.builder.font.size = 14.0
        self.builder.font.bold = False
        
        author_name = self.config.author_name or "Claude AI Assistant"
        self.builder.writeln(f"Por {author_name}")
        
        # Información de publicación (en la parte inferior)
        self.builder.paragraph_format.space_before = 200.0
        self.builder.font.size = 10.0
        self.builder.font.italic = True
        
        current_year = datetime.now().year
        self.builder.writeln(f"Primera Edición")
        self.builder.writeln(f"{current_year}")
        
        self._reset_paragraph_format()
    
    def _create_copyright_page(self, book: BookGeneration):
        """Crea la página de copyright"""
        self.builder.paragraph_format.alignment = aw.ParagraphAlignment.LEFT
        self.builder.font.name = self.config.typography.body_font_family.value
        self.builder.font.size = 9.0
        self.builder.font.bold = False
        self.builder.font.italic = False
        
        current_year = datetime.now().year
        author_name = self.config.author_name or "El Autor"
        
        copyright_text = f"""Copyright © {current_year} por {author_name}

Todos los derechos reservados. Ninguna parte de esta publicación puede ser reproducida, distribuida, o transmitida en cualquier forma o por cualquier medio, incluyendo fotocopiado, grabación, u otros métodos electrónicos o mecánicos, sin el permiso previo por escrito del editor, excepto en el caso de citas breves incorporadas en reseñas críticas y ciertos otros usos no comerciales permitidos por la ley de derechos de autor.

Para solicitudes de permisos, escriba al editor, dirigido "Departamento de Permisos".

Primera Edición: {current_year}

Este libro fue generado utilizando tecnología de inteligencia artificial Claude AI, desarrollada por Anthropic.

Impreso en [País de Impresión]

ISBN: [Número ISBN]

Clasificación de la Biblioteca del Congreso: [Número de Clasificación]"""
        
        for line in copyright_text.split('\n'):
            if line.strip():
                self.builder.writeln(line.strip())
            else:
                self.builder.writeln()
        
        self._reset_paragraph_format()
    
    def _create_dedication_page(self, book: BookGeneration):
        """Crea la página de dedicatoria"""
        # Generar dedicatoria inteligente con fallback
        if self.content_generator_available and self.content_generator:
            try:
                request = ContentGenerationRequest(
                    content_type=ContentType.DEDICATION,
                    book_analysis=self.book_analysis,
                    specific_requirements={}
                )
                dedication_text = self.content_generator.generate_content(request)
            except Exception as e:
                logger.warning(f"Error generating intelligent dedication: {e}")
                dedication_text = self._get_fallback_dedication(book)
        else:
            dedication_text = self._get_fallback_dedication(book)
        
        # Formatear dedicatoria
        self.builder.paragraph_format.alignment = aw.ParagraphAlignment.CENTER
        self.builder.paragraph_format.space_before = 144.0  # 2 inches from top
        
        self.builder.font.name = self.config.typography.body_font_family.value
        self.builder.font.size = 12.0
        self.builder.font.bold = False
        self.builder.font.italic = True
        
        self.builder.writeln(dedication_text)
        
        self._reset_paragraph_format()
    
    def _create_table_of_contents(self, book: BookGeneration):
        """Crea la tabla de contenidos"""
        # Título de la sección
        try:
            self.builder.paragraph_format.style_name = "Heading 1"
        except Exception as e:
            logger.warning(f"Error setting Heading 1 style: {e}")
            
        self.builder.writeln("TABLA DE CONTENIDOS")
        
        try:
            self.builder.paragraph_format.style_name = "Normal"
        except Exception as e:
            logger.warning(f"Error setting Normal style: {e}")
        
        # Generar tabla de contenidos inteligente con fallback
        if self.content_generator_available and self.content_generator:
            try:
                request = ContentGenerationRequest(
                    content_type=ContentType.CHAPTER_TITLES,
                    book_analysis=self.book_analysis,
                    specific_requirements={}
                )
                chapter_titles = self.content_generator.generate_content(request)
            except Exception as e:
                logger.warning(f"Error generating intelligent chapter titles: {e}")
                chapter_titles = self._get_fallback_chapter_titles(book)
        else:
            chapter_titles = self._get_fallback_chapter_titles(book)
        
        # Asegurar que tenemos una lista válida
        if not chapter_titles:
            chapter_titles = self._get_fallback_chapter_titles(book)
        
        # Si no es una lista, convertir a lista
        if isinstance(chapter_titles, str):
            chapter_titles = [title.strip() for title in chapter_titles.split('\n') if title.strip()]
        
        # Verificar que es una lista y tiene contenido
        if not isinstance(chapter_titles, list) or not chapter_titles:
            chapter_titles = self._get_fallback_chapter_titles(book)
        
        # Agregar prólogo si está incluido
        if self.config.structure.include_prologue:
            self.builder.writeln("Prólogo ........................... 1")
        
        # Agregar capítulos
        for i, title in enumerate(chapter_titles, 1):
            page_num = (i * 3) + 5  # Estimación simple de páginas
            self.builder.writeln(f"Capítulo {i}: {title} ........................... {page_num}")
        
        # Agregar secciones finales
        if self.config.structure.include_epilogue:
            final_page = len(chapter_titles) * 3 + 10
            self.builder.writeln(f"Epílogo ........................... {final_page}")
        
        if self.config.structure.include_about_author:
            final_page = len(chapter_titles) * 3 + 12
            self.builder.writeln(f"Acerca del Autor ........................... {final_page}")
        
        self._reset_paragraph_format()
    
    def _create_prologue_page(self, book: BookGeneration):
        """Crea la página de prólogo"""
        # Título
        self.builder.paragraph_format.style = self.document.styles["SectionHeading"]
        self.builder.writeln("PRÓLOGO")
        
        # Generar contenido del prólogo
        request = ContentGenerationRequest(
            content_type=ContentType.PROLOGUE,
            book_analysis=self.book_analysis,
            specific_requirements={}
        )
        
        prologue_text = self.content_generator.generate_content(request)
        
        # Formatear prólogo
        self._set_style_safely("BookBody", "Normal")
        
        # Agregar drop cap si está habilitado
        if self.config.typography.use_drop_caps:
            self._add_drop_cap(prologue_text[0])
            prologue_text = prologue_text[1:]
        
        self.builder.write(prologue_text)
        
        self._reset_paragraph_format()
    
    def _create_main_content(self, book: BookGeneration):
        """Crea el contenido principal del libro (capítulos)"""
        # Dividir contenido en capítulos usando análisis inteligente
        chapters = self.book_analysis.chapter_structure
        
        if not chapters:
            # Si no hay estructura de capítulos clara, dividir por longitud
            chapters = self._create_default_chapters(book.content)
        
        # Generar títulos inteligentes para capítulos con fallback
        if self.content_generator_available and self.content_generator:
            try:
                request = ContentGenerationRequest(
                    content_type=ContentType.CHAPTER_TITLES,
                    book_analysis=self.book_analysis,
                    specific_requirements={}
                )
                chapter_titles = self.content_generator.generate_content(request)
            except Exception as e:
                logger.warning(f"Error generating chapter titles for main content: {e}")
                chapter_titles = self._get_fallback_chapter_titles(book)
        else:
            chapter_titles = self._get_fallback_chapter_titles(book)
            
        # Verificar que tenemos una lista válida
        if not chapter_titles or not isinstance(chapter_titles, (list, str)):
            chapter_titles = self._get_fallback_chapter_titles(book)
            
        if isinstance(chapter_titles, str):
            chapter_titles = [title.strip() for title in chapter_titles.split('\n') if title.strip()]
            
        # Asegurar que tenemos al menos algunos títulos
        if not chapter_titles or not isinstance(chapter_titles, list):
            chapter_titles = self._get_fallback_chapter_titles(book)
        
        # Procesar cada capítulo
        for i, chapter in enumerate(chapters):
            if self.config.structure.start_chapters_on_odd_page:
                self._ensure_odd_page()
            else:
                self.builder.insert_break(aw.BreakType.PAGE_BREAK)
            
            # Título del capítulo
            self._set_style_safely("ChapterTitle", "Heading 1")
            
            chapter_title = chapter_titles[i] if i < len(chapter_titles) else f"Capítulo {i + 1}"
            self.builder.writeln(f"CAPÍTULO {i + 1}")
            self.builder.writeln(chapter_title.upper())
            
            # Contenido del capítulo
            self._set_style_safely("BookBody", "Normal")
            
            chapter_content = chapter.get('content', '') or self._extract_chapter_content(book.content, i, len(chapters))
            
            # Procesar párrafos
            paragraphs = chapter_content.split('\n\n')
            for j, paragraph in enumerate(paragraphs):
                paragraph = paragraph.strip()
                if not paragraph:
                    continue
                
                # Agregar drop cap al primer párrafo del capítulo
                if j == 0 and self.config.typography.use_drop_caps:
                    self._add_drop_cap(paragraph[0])
                    paragraph = paragraph[1:]
                
                self.builder.write(paragraph)
                self.builder.writeln()
                self.builder.writeln()
        
        self._reset_paragraph_format()
    
    def _create_sample_chapter(self, book: BookGeneration, max_pages: int = 5):
        """Crea una muestra del primer capítulo para preview"""
        # Título del capítulo
        try:
            # Use proper Aspose.Words method to get style
            chapter_style = self.document.styles.get_by_name("ChapterTitle")
            self.builder.paragraph_format.style = chapter_style
        except Exception as style_error:
            logger.warning(f"ChapterTitle style not found, using default: {style_error}")
            # Fallback to default heading style
            self.builder.paragraph_format.style_name = "Heading 1"
            
        self.builder.writeln("CAPÍTULO 1")
        self.builder.writeln("MUESTRA DEL CONTENIDO")
        
        # Contenido de muestra
        try:
            # Use proper Aspose.Words method to get style
            body_style = self.document.styles.get_by_name("BookBody")
            self.builder.paragraph_format.style = body_style
        except Exception as style_error:
            logger.warning(f"BookBody style not found, using default: {style_error}")
            # Fallback to normal style
            self.builder.paragraph_format.style_name = "Normal"
        
        try:
            # Verificar que tenemos contenido
            if not book.content or not isinstance(book.content, str):
                logger.warning("Book content is empty or not a string, using placeholder")
                sample_content = "Este es un contenido de ejemplo para el documento de vista previa."
            else:
                # Tomar primeras palabras del contenido
                logger.info(f"Processing book content, length: {len(book.content)} characters")
                words = book.content.split()
                logger.info(f"Split into {len(words)} words")
                
                sample_words = min(500 * max_pages, len(words))  # ~500 palabras por página
                logger.info(f"Taking {sample_words} words for sample")
                
                sample_content = ' '.join(words[:sample_words])
                logger.info(f"Sample content length: {len(sample_content)} characters")
        
            # Dividir en párrafos aproximados
            sentences = sample_content.split('.')
            logger.info(f"Split into {len(sentences)} sentences")
            current_paragraph = ""
            
            for i, sentence in enumerate(sentences):
                logger.debug(f"Processing sentence {i}: type={type(sentence)}, length={len(str(sentence))}")
                
                # Ensure sentence is a string
                if not isinstance(sentence, str):
                    logger.warning(f"Sentence {i} is not a string: {type(sentence)}, converting...")
                    sentence = str(sentence)
                
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                current_paragraph += sentence + ". "
                
                # Crear nuevo párrafo cada 3-4 oraciones
                if i % 3 == 0 and i > 0:
                    if i == 3 and self.config.typography.use_drop_caps:
                        if current_paragraph and len(current_paragraph) > 0:
                            self._add_drop_cap(current_paragraph[0])
                            current_paragraph = current_paragraph[1:]
                    
                    self.builder.write(current_paragraph.strip())
                    self.builder.writeln()
                    self.builder.writeln()
                    current_paragraph = ""
                    
        except Exception as sample_error:
            logger.error(f"Error in sample chapter creation: {str(sample_error)}")
            logger.error(f"Error type: {type(sample_error).__name__}")
            # Log the variables that might be causing issues
            logger.error(f"book.content type: {type(book.content) if hasattr(book, 'content') else 'No content attr'}")
            logger.error(f"max_pages: {max_pages}, type: {type(max_pages)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
        
        # Agregar párrafo final si queda contenido
        if current_paragraph.strip():
            self.builder.write(current_paragraph.strip())
            self.builder.writeln()
        
        # Indicador de preview
        self.builder.writeln()
        self.builder.paragraph_format.alignment = aw.ParagraphAlignment.CENTER
        self.builder.font.italic = True
        self.builder.font.size = 10.0
        self.builder.writeln("... [Vista previa - El contenido completo estará disponible en el documento final] ...")
        
        self._reset_paragraph_format()
    
    def _create_epilogue_page(self, book: BookGeneration):
        """Crea la página de epílogo"""
        self.builder.paragraph_format.style = self.document.styles["SectionHeading"]
        self.builder.writeln("EPÍLOGO")
        
        request = ContentGenerationRequest(
            content_type=ContentType.EPILOGUE,
            book_analysis=self.book_analysis,
            specific_requirements={}
        )
        
        epilogue_text = self.content_generator.generate_content(request)
        
        self.builder.paragraph_format.style = self.document.styles["BookBody"]
        self.builder.write(epilogue_text)
        
        self._reset_paragraph_format()
    
    def _create_acknowledgments_page(self, book: BookGeneration):
        """Crea la página de agradecimientos"""
        self.builder.paragraph_format.style = self.document.styles["SectionHeading"]
        self.builder.writeln("AGRADECIMIENTOS")
        
        request = ContentGenerationRequest(
            content_type=ContentType.ACKNOWLEDGMENTS,
            book_analysis=self.book_analysis,
            specific_requirements={}
        )
        
        acknowledgments_text = self.content_generator.generate_content(request)
        
        self.builder.paragraph_format.style = self.document.styles["BookBody"]
        self.builder.write(acknowledgments_text)
        
        self._reset_paragraph_format()
    
    def _create_about_author_page(self, book: BookGeneration):
        """Crea la página 'Acerca del Autor'"""
        self.builder.paragraph_format.style = self.document.styles["SectionHeading"]
        self.builder.writeln("ACERCA DEL AUTOR")
        
        author_info = {
            "name": self.config.author_name,
            "specialization": self.book_analysis.genre.value,
            "topics": ', '.join(self.book_analysis.main_themes)
        }
        
        request = ContentGenerationRequest(
            content_type=ContentType.ABOUT_AUTHOR,
            book_analysis=self.book_analysis,
            specific_requirements={},
            author_info=author_info
        )
        
        about_author_text = self.content_generator.generate_content(request)
        
        self.builder.paragraph_format.style = self.document.styles["BookBody"]
        self.builder.write(about_author_text)
        
        self._reset_paragraph_format()
    
    def _create_bibliography_page(self, book: BookGeneration):
        """Crea la página de bibliografía"""
        self.builder.paragraph_format.style = self.document.styles["SectionHeading"]
        self.builder.writeln("BIBLIOGRAFÍA")
        
        # Bibliografía básica para libros generados por IA
        self.builder.paragraph_format.style = self.document.styles["BookBody"]
        
        bibliography_text = """Este libro fue creado utilizando inteligencia artificial avanzada y técnicas de procesamiento de lenguaje natural. Las fuentes de información incluyen:

• Modelos de lenguaje entrenados en literatura académica y profesional
• Bases de conocimiento especializadas en el área temática
• Metodologías de generación de contenido asistida por IA
• Técnicas de análisis semántico y estructuración de información

Para más información sobre las tecnologías utilizadas en la creación de este contenido, consulte:

Anthropic. (2024). Claude AI: Advanced Language Model for Content Generation.
https://www.anthropic.com/claude

Tecnologías de formateo y presentación:
Aspose.Words for Python: Professional document generation and formatting.
https://products.aspose.com/words/python-net/"""
        
        self.builder.write(bibliography_text)
        
        self._reset_paragraph_format()
    
    # Métodos auxiliares de formato y configuración
    
    def _setup_headers_footers(self):
        """Configura encabezados y pies de página"""
        # Header para páginas pares
        self.builder.move_to_header_footer(aw.HeaderFooterType.HEADER_EVEN)
        self.builder.paragraph_format.alignment = aw.ParagraphAlignment.LEFT
        self.builder.font.size = 9.0
        self.builder.font.italic = True
        self.builder.write("TÍTULO DEL LIBRO")  # Se actualizará con el título real
        
        # Header para páginas impares (primary)
        self.builder.move_to_header_footer(aw.HeaderFooterType.HEADER_PRIMARY)
        self.builder.paragraph_format.alignment = aw.ParagraphAlignment.RIGHT
        self.builder.font.size = 9.0
        self.builder.font.italic = True
        self.builder.write("CAPÍTULO ACTUAL")  # Se actualizará dinámicamente
        
        # Footer con numeración
        self.builder.move_to_header_footer(aw.HeaderFooterType.FOOTER_PRIMARY)
        self.builder.paragraph_format.alignment = aw.ParagraphAlignment.CENTER
        self.builder.font.size = 10.0
        self.builder.font.italic = False
        self.builder.insert_field("PAGE", "")
        
        # Volver al cuerpo del documento
        self.builder.move_to_document_end()
    
    def _setup_page_numbering(self):
        """Configura la numeración de páginas"""
        if self.config.structure.page_numbering_start > 1:
            section = self.document.sections[0]
            section.page_setup.restart_page_numbering = True
            section.page_setup.page_starting_number = self.config.structure.page_numbering_start
    
    def _create_bookmarks_and_navigation(self):
        """Crea marcadores para navegación"""
        if not self.config.export.include_bookmarks:
            return
        
        # Los marcadores se crearían durante la creación de contenido
        # Este método podría agregar marcadores adicionales o índices
        pass
    
    def _add_drop_cap(self, first_char: str):
        """Agrega letra capital al inicio del párrafo"""
        if not self.config.typography.use_drop_caps or not first_char:
            return
        
        # Crear letra capital usando Aspose.Words
        self.builder.font.size = self.config.typography.body_font_size * 3
        self.builder.font.bold = True
        self.builder.write(first_char.upper())
        
        # Resetear formato para el resto del texto
        self.builder.font.size = self.config.typography.body_font_size
        self.builder.font.bold = False
    
    def _ensure_odd_page(self):
        """Asegura que el contenido inicie en página impar"""
        current_page = self.document.page_count
        if current_page % 2 == 0:  # Página par
            self.builder.insert_break(aw.BreakType.PAGE_BREAK)
        self.builder.insert_break(aw.BreakType.PAGE_BREAK)
    
    def _reset_paragraph_format(self):
        """Resetea el formato de párrafo a valores por defecto"""
        self.builder.paragraph_format.alignment = aw.ParagraphAlignment.LEFT
        self.builder.paragraph_format.space_before = 0
        self.builder.paragraph_format.space_after = 0
        self.builder.font.bold = False
        self.builder.font.italic = False
        self.builder.font.size = self.config.typography.body_font_size
        self.builder.font.name = self.config.typography.body_font_family.value
    
    def _apply_custom_style(self, style_name: str, style_config: Dict[str, Any]):
        """Aplica estilos personalizados definidos por el usuario"""
        try:
            style = self.document.styles.add(aw.StyleType.PARAGRAPH, style_name)
            
            # Aplicar configuraciones de fuente
            if 'font_name' in style_config:
                style.font.name = style_config['font_name']
            if 'font_size' in style_config:
                style.font.size = style_config['font_size']
            if 'bold' in style_config:
                style.font.bold = style_config['bold']
            if 'italic' in style_config:
                style.font.italic = style_config['italic']
            
            # Aplicar configuraciones de párrafo
            if 'alignment' in style_config:
                alignment_map = {
                    'left': aw.ParagraphAlignment.LEFT,
                    'center': aw.ParagraphAlignment.CENTER,
                    'right': aw.ParagraphAlignment.RIGHT,
                    'justify': aw.ParagraphAlignment.JUSTIFY
                }
                style.paragraph_format.alignment = alignment_map.get(
                    style_config['alignment'], aw.ParagraphAlignment.LEFT
                )
            
            if 'space_before' in style_config:
                style.paragraph_format.space_before = style_config['space_before']
            if 'space_after' in style_config:
                style.paragraph_format.space_after = style_config['space_after']
            
        except Exception as e:
            logger.warning(f"Error aplicando estilo personalizado {style_name}: {str(e)}")
    
    def _create_default_chapters(self, content: str, target_chapters: int = 10) -> List[Dict[str, Any]]:
        """Crea estructura de capítulos por defecto cuando no se detecta estructura clara"""
        words = content.split()
        words_per_chapter = len(words) // target_chapters
        
        chapters = []
        for i in range(target_chapters):
            start_idx = i * words_per_chapter
            end_idx = start_idx + words_per_chapter if i < target_chapters - 1 else len(words)
            
            chapter_content = ' '.join(words[start_idx:end_idx])
            chapters.append({
                'number': i + 1,
                'title': f"Capítulo {i + 1}",
                'content': chapter_content,
                'word_count': end_idx - start_idx
            })
        
        return chapters
    
    def _extract_chapter_content(self, content: str, chapter_index: int, total_chapters: int) -> str:
        """Extrae contenido para un capítulo específico"""
        words = content.split()
        words_per_chapter = len(words) // total_chapters
        
        start_idx = chapter_index * words_per_chapter
        end_idx = start_idx + words_per_chapter if chapter_index < total_chapters - 1 else len(words)
        
        return ' '.join(words[start_idx:end_idx])
    
    def _generate_output_filename(self, book: BookGeneration) -> str:
        """Genera nombre de archivo para el documento de salida"""
        safe_title = "".join(c for c in book.title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title.replace(' ', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return f"/tmp/professional_book_{safe_title}_{timestamp}.docx"
    
    def _generate_preview_filename(self, book: BookGeneration) -> str:
        """Genera nombre de archivo para preview"""
        safe_title = "".join(c for c in book.title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title.replace(' ', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return f"/tmp/preview_{safe_title}_{timestamp}.docx"
    
    def _generate_fallback_preview(
        self, 
        book: BookGeneration, 
        config: AsposeDocumentConfiguration,
        max_pages: int = 10
    ) -> str:
        """
        Genera una vista previa usando fallback cuando Aspose.Words no está disponible.
        Crea un archivo HTML simple como alternativa.
        """
        try:
            logger.info("Generating fallback preview (Aspose.Words not available)")
            
            # Generate simple HTML preview
            safe_title = "".join(c for c in book.title if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_title = safe_title.replace(' ', '_')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            preview_filename = f"/tmp/fallback_preview_{safe_title}_{timestamp}.html"
            
            # Create simple HTML content
            html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{book.title} - Vista Previa</title>
    <style>
        body {{
            font-family: 'Times New Roman', serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            background: #f9f9f9;
        }}
        .document {{
            background: white;
            padding: 40px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            margin: 20px 0;
        }}
        .cover-page {{
            text-align: center;
            page-break-after: always;
            margin-bottom: 40px;
        }}
        .title {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 60px 0;
            color: #333;
        }}
        .author {{
            font-size: 1.2em;
            margin: 20px 0;
            color: #666;
        }}
        .notice {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
            color: #856404;
        }}
        .content {{
            margin: 30px 0;
        }}
        h2 {{
            color: #333;
            border-bottom: 2px solid #ddd;
            padding-bottom: 5px;
        }}
        .chapter {{
            margin: 20px 0;
            padding: 15px;
            border-left: 4px solid #007bff;
            background: #f8f9fa;
        }}
    </style>
</head>
<body>
    <div class="document">
        <div class="cover-page">
            <h1 class="title">{book.title}</h1>
            <p class="author">Autor: {config.author_name or 'Autor No Especificado'}</p>
            
            <div class="notice">
                <strong>Vista Previa Simplificada</strong><br>
                Esta es una vista previa en modo fallback debido a limitaciones técnicas.<br>
                La versión final del documento tendrá formato profesional completo.
            </div>
        </div>
        
        <div class="content">
            <h2>Información del Documento</h2>
            <p><strong>Título:</strong> {book.title}</p>
            <p><strong>Estado:</strong> {book.status}</p>
            <p><strong>Configuración:</strong> {config.page_format.value}</p>
            <p><strong>Fuente:</strong> {config.typography.body_font_family.value}</p>
            <p><strong>Tamaño de fuente:</strong> {config.typography.body_font_size}pt</p>
            
            <h2>Contenido (Muestra)</h2>
            <div class="chapter">
"""
            
            # Add sample of book content (first 2000 characters)
            if book.content:
                sample_content = book.content[:2000]
                # Clean and format the content
                sample_content = sample_content.replace('\n\n', '</p><p>')
                sample_content = sample_content.replace('\n', '<br>')
                html_content += f"<p>{sample_content}</p>"
                
                if len(book.content) > 2000:
                    html_content += "<p><em>... (contenido continúa en el documento completo)</em></p>"
            else:
                html_content += "<p>Contenido no disponible para vista previa.</p>"
            
            html_content += """
            </div>
            
            <div class="notice">
                <strong>Nota:</strong> Esta vista previa está limitada debido a que el sistema de generación 
                profesional de documentos Aspose.Words no está disponible temporalmente. 
                Para obtener un documento Word profesional completo, contacte al administrador del sistema.
            </div>
        </div>
    </div>
</body>
</html>"""
            
            # Write the HTML file
            with open(preview_filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Fallback preview generated: {preview_filename}")
            return preview_filename
            
        except Exception as e:
            logger.error(f"Error generating fallback preview: {str(e)}")
            raise RuntimeError(f"Failed to generate fallback preview: {str(e)}")
    
    def _create_fallback_book_analysis(self, book: BookGeneration):
        """Crea análisis básico del libro cuando IntelligentContentGenerator no está disponible"""
        # Import here to avoid circular imports
        from app.services.intelligent_content_generator import BookAnalysis, BookGenre
        
        # Basic heuristic analysis based on title and content
        title_lower = book.title.lower()
        content_sample = book.content[:1000].lower() if book.content else ""
        
        # Simple genre detection
        genre = BookGenre.NON_FICTION  # Default
        if any(word in title_lower for word in ['mystery', 'detective', 'crime']):
            genre = BookGenre.MYSTERY
        elif any(word in title_lower for word in ['romance', 'love', 'heart']):
            genre = BookGenre.ROMANCE
        elif any(word in title_lower for word in ['sci-fi', 'science', 'future', 'space']):
            genre = BookGenre.SCIENCE_FICTION
        elif any(word in title_lower for word in ['fantasy', 'magic', 'wizard', 'dragon']):
            genre = BookGenre.FANTASY
        elif any(word in content_sample for word in ['learn', 'study', 'lesson', 'chapter']):
            genre = BookGenre.EDUCATIONAL
        
        return BookAnalysis(
            genre=genre,
            main_themes=["general content", "narrative", "information"],
            tone="neutral",
            target_audience="adults",
            language_style="narrative",
            key_concepts=["content", "information", "narrative"],
            chapter_structure=[],
            estimated_reading_level="intermediate",
            cultural_context="general"
        )
    
    def _get_fallback_dedication(self, book: BookGeneration) -> str:
        """Genera una dedicatoria simple cuando el generador inteligente no está disponible"""
        dedications = [
            "A todos aquellos que buscan el conocimiento y la sabiduría.",
            "Con gratitud a quienes inspiraron este trabajo.",
            "Dedicado a los lectores que encuentran valor en estas páginas.",
            "Para aquellos que ven la belleza en las palabras escritas.",
            "Con esperanza de que este contenido sea de utilidad."
        ]
        
        import random
        return random.choice(dedications)
    
    def _get_fallback_chapter_titles(self, book: BookGeneration) -> List[str]:
        """Genera títulos de capítulos básicos cuando el generador inteligente no está disponible"""
        # Análisis simple del contenido para determinar número de capítulos
        if not book.content:
            return ["Capítulo 1: Introducción", "Capítulo 2: Desarrollo", "Capítulo 3: Conclusión"]
        
        word_count = len(book.content.split())
        estimated_chapters = max(3, min(12, word_count // 2000))  # 1 capítulo por cada 2000 palabras, mín 3, máx 12
        
        # Títulos genéricos pero apropiados
        chapter_titles = []
        for i in range(1, estimated_chapters + 1):
            if i == 1:
                chapter_titles.append("Introducción")
            elif i == estimated_chapters:
                chapter_titles.append("Conclusiones")
            else:
                chapter_titles.append(f"Desarrollo - Parte {i - 1}")
        
        return chapter_titles
    
    def _get_style_safely(self, style_name: str):
        """Método auxiliar para acceder a estilos de forma segura"""
        try:
            # Try to get the style by name using proper Aspose.Words method
            return self.document.styles.get_by_name(style_name)
        except Exception as e:
            logger.warning(f"Style '{style_name}' not found: {e}")
            # Return None so calling code can handle fallback
            return None
    
    def _set_style_safely(self, style_name: str, fallback_style_name: str = "Normal"):
        """Método auxiliar para establecer estilos de forma segura"""
        try:
            style = self._get_style_safely(style_name)
            if style:
                self.builder.paragraph_format.style = style
            else:
                # Use style name fallback
                self.builder.paragraph_format.style_name = fallback_style_name
        except Exception as e:
            logger.warning(f"Error setting style '{style_name}': {e}, using {fallback_style_name}")
            try:
                self.builder.paragraph_format.style_name = fallback_style_name
            except Exception as fallback_error:
                logger.error(f"Even fallback style failed: {fallback_error}")