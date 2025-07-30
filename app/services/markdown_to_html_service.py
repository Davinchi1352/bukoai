"""
Professional Markdown to HTML Conversion Service
Convierte contenido Markdown a HTML estructurado profesional para ebooks comerciales.
"""

import re
import html
import uuid
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import markdown
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from markdown.postprocessors import Postprocessor
from bs4 import BeautifulSoup
import json


class HTMLElementType(Enum):
    """Tipos de elementos HTML para estructura semántica."""
    BOOK_TITLE = "book-title"
    CHAPTER = "chapter"
    CHAPTER_TITLE = "chapter-title"
    SECTION = "section"
    SUBSECTION = "subsection"
    PARAGRAPH = "paragraph"
    EXPRESSION = "expression"
    PHONETIC = "phonetic"
    TRANSLATION = "translation"
    USAGE = "usage"
    EXAMPLE = "example"
    LIST = "list"
    LIST_ITEM = "list-item"
    EMPHASIS = "emphasis"
    STRONG = "strong"
    BLOCKQUOTE = "blockquote"
    CODE = "code"
    SEPARATOR = "separator"
    TABLE_OF_CONTENTS = "toc"
    INDEX_ENTRY = "index-entry"
    FOOTNOTE = "footnote"
    CROSS_REFERENCE = "cross-ref"


@dataclass
class HTMLElement:
    """Elemento HTML estructurado con metadatos."""
    id: str
    type: HTMLElementType
    content: str
    attributes: Dict[str, str]
    children: List['HTMLElement']
    metadata: Dict[str, Any]
    
    def to_html(self) -> str:
        """Convierte el elemento a HTML."""
        tag = self._get_tag_name()
        attrs = self._build_attributes()
        
        if self.children:
            children_html = "".join([child.to_html() for child in self.children])
            return f"<{tag}{attrs}>{self.content}{children_html}</{tag}>"
        elif tag in ["hr", "br"]:
            return f"<{tag}{attrs} />"
        else:
            return f"<{tag}{attrs}>{self.content}</{tag}>"
    
    def _get_tag_name(self) -> str:
        """Obtiene el nombre de la etiqueta HTML según el tipo."""
        tag_mapping = {
            HTMLElementType.BOOK_TITLE: "h1",
            HTMLElementType.CHAPTER: "section",
            HTMLElementType.CHAPTER_TITLE: "h2",
            HTMLElementType.SECTION: "h3",
            HTMLElementType.SUBSECTION: "h4",
            HTMLElementType.PARAGRAPH: "p",
            HTMLElementType.EXPRESSION: "div",
            HTMLElementType.PHONETIC: "span",
            HTMLElementType.TRANSLATION: "div",
            HTMLElementType.USAGE: "div",
            HTMLElementType.EXAMPLE: "div",
            HTMLElementType.LIST: "ul",
            HTMLElementType.LIST_ITEM: "li",
            HTMLElementType.EMPHASIS: "em",
            HTMLElementType.STRONG: "strong",
            HTMLElementType.BLOCKQUOTE: "blockquote",
            HTMLElementType.CODE: "code",
            HTMLElementType.SEPARATOR: "hr",
            HTMLElementType.TABLE_OF_CONTENTS: "nav",
            HTMLElementType.INDEX_ENTRY: "span",
            HTMLElementType.FOOTNOTE: "aside",
            HTMLElementType.CROSS_REFERENCE: "a"
        }
        return tag_mapping.get(self.type, "div")
    
    def _build_attributes(self) -> str:
        """Construye la cadena de atributos HTML."""
        attrs = []
        
        # ID único
        attrs.append(f'id="{self.id}"')
        
        # Clases CSS
        classes = [f"ebook-{self.type.value}"]
        if "class" in self.attributes:
            classes.append(self.attributes["class"])
        attrs.append(f'class="{" ".join(classes)}"')
        
        # Data attributes para metadatos
        if self.metadata:
            attrs.append(f"data-metadata='{json.dumps(self.metadata)}'")
        
        # Otros atributos
        for key, value in self.attributes.items():
            if key != "class":
                attrs.append(f'{key}="{html.escape(str(value))}"')
        
        return " " + " ".join(attrs) if attrs else ""


@dataclass
class BookStructure:
    """Estructura completa del libro en HTML."""
    title: str
    author: str
    language: str
    elements: List[HTMLElement]
    toc: List[Dict[str, Any]]
    index: Dict[str, List[str]]
    metadata: Dict[str, Any]
    
    def to_html_document(self) -> str:
        """Genera el documento HTML completo."""
        html_parts = [
            '<!DOCTYPE html>',
            '<html lang="' + self.language + '">',
            '<head>',
            '<meta charset="UTF-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
            '<title>' + html.escape(self.title) + '</title>',
            '<meta name="author" content="' + html.escape(self.author) + '">',
            '<link rel="stylesheet" href="/static/css/ebook-professional.css">',
            self._generate_metadata_tags(),
            '</head>',
            '<body class="ebook-body">',
            '<div class="ebook-container">',
            self._generate_toc_html(),
            '<main class="ebook-content">'
        ]
        
        # Agregar elementos del libro
        for element in self.elements:
            html_parts.append(element.to_html())
        
        html_parts.extend([
            '</main>',
            self._generate_index_html(),
            '</div>',
            '<script src="/static/js/ebook-navigation.js"></script>',
            '</body>',
            '</html>'
        ])
        
        return "\n".join(html_parts)
    
    def to_html_content(self) -> str:
        """Genera solo el contenido HTML sin el documento completo (para embedding)."""
        html_parts = [
            self._generate_toc_html(),
            '<div class="ebook-content">'
        ]
        
        # Agregar elementos del libro
        for element in self.elements:
            html_parts.append(element.to_html())
        
        html_parts.extend([
            '</div>',
            self._generate_index_html()
        ])
        
        return "\n".join(html_parts)
    
    def _generate_metadata_tags(self) -> str:
        """Genera etiquetas meta para el documento."""
        tags = []
        for key, value in self.metadata.items():
            if isinstance(value, str):
                tags.append(f'<meta name="{key}" content="{html.escape(value)}">')
        return "\n".join(tags)
    
    def _generate_toc_html(self) -> str:
        """Genera el HTML para la tabla de contenidos."""
        if not self.toc:
            return ""
        
        html_parts = [
            '<nav class="ebook-toc" id="table-of-contents">',
            '<h2>Tabla de Contenidos</h2>',
            '<ol class="toc-list">'
        ]
        
        for item in self.toc:
            html_parts.append(self._generate_toc_item(item))
        
        html_parts.extend(['</ol>', '</nav>'])
        return "\n".join(html_parts)
    
    def _generate_toc_item(self, item: Dict[str, Any]) -> str:
        """Genera un elemento de la tabla de contenidos."""
        html = f'<li><a href="#{item["id"]}">{html.escape(item["title"])}</a>'
        if item.get("children"):
            html += '<ol class="toc-sublist">'
            for child in item["children"]:
                html += self._generate_toc_item(child)
            html += '</ol>'
        html += '</li>'
        return html
    
    def _generate_index_html(self) -> str:
        """Genera el HTML para el índice."""
        if not self.index:
            return ""
        
        html_parts = [
            '<div class="ebook-index" id="book-index">',
            '<h2>Índice</h2>',
            '<div class="index-entries">'
        ]
        
        for term, locations in sorted(self.index.items()):
            html_parts.append(
                f'<div class="index-entry">'
                f'<span class="index-term">{html.escape(term)}</span>'
                f'<span class="index-locations">{", ".join(locations)}</span>'
                f'</div>'
            )
        
        html_parts.extend(['</div>', '</div>'])
        return "\n".join(html_parts)


class MarkdownToHTMLConverter:
    """Convertidor profesional de Markdown a HTML estructurado."""
    
    def __init__(self):
        self.element_counter = 0
        self.toc_entries = []
        self.index_terms = {}
        self.footnotes = []
        self.current_chapter = None
        self.current_section = None
        
    def convert(self, markdown_content: str, book_title: str = "", 
                author: str = "", language: str = "es") -> BookStructure:
        """Convierte contenido Markdown a estructura HTML profesional."""
        
        # Pre-procesar el markdown
        processed_content = self._preprocess_markdown(markdown_content)
        
        # Parsear elementos
        elements = self._parse_markdown_to_elements(processed_content)
        
        # Post-procesar elementos
        elements = self._postprocess_elements(elements)
        
        # Generar tabla de contenidos
        toc = self._generate_table_of_contents(elements)
        
        # Extraer términos para el índice
        index = self._extract_index_terms(elements)
        
        # Metadata del libro
        metadata = {
            "generator": "Buko AI Professional Formatter",
            "format_version": "1.0",
            "creation_date": str(uuid.uuid4())[:8]
        }
        
        return BookStructure(
            title=book_title or self._extract_title(elements),
            author=author,
            language=language,
            elements=elements,
            toc=toc,
            index=index,
            metadata=metadata
        )
    
    def _preprocess_markdown(self, content: str) -> str:
        """Pre-procesa el contenido markdown para normalización."""
        # Normalizar saltos de línea
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        # Asegurar espacios después de # en encabezados
        content = re.sub(r'^(#{1,6})([^# ])', r'\1 \2', content, flags=re.MULTILINE)
        
        # Normalizar listas
        content = re.sub(r'^(\s*)[*+-]\s+', r'\1- ', content, flags=re.MULTILINE)
        
        return content
    
    def _parse_markdown_to_elements(self, content: str) -> List[HTMLElement]:
        """Parsea el contenido markdown a elementos HTML estructurados."""
        elements = []
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].rstrip()
            
            # Título principal del libro
            if line.startswith('# ') and not line.startswith('# CAPÍTULO'):
                elements.append(self._create_book_title(line[2:]))
                i += 1
                continue
            
            # Capítulo
            if line.startswith('# CAPÍTULO') or line.startswith('# Capítulo'):
                chapter_elem, skip = self._create_chapter(lines, i)
                elements.append(chapter_elem)
                i += skip
                continue
            
            # Título de capítulo
            if line.startswith('## '):
                elements.append(self._create_chapter_title(line[3:]))
                i += 1
                continue
            
            # Sección
            if line.startswith('### '):
                elements.append(self._create_section(line[4:]))
                i += 1
                continue
            
            # Subsección
            if line.startswith('#### '):
                elements.append(self._create_subsection(line[5:]))
                i += 1
                continue
            
            # Expresión numerada
            if re.match(r'^\*\*\d+\.\s+.*\*\*$', line):
                elements.append(self._create_expression(line))
                i += 1
                continue
            
            # Transcripción fonética
            if re.match(r'^\*\[.*\]\*$', line):
                elements.append(self._create_phonetic(line))
                i += 1
                continue
            
            # Traducción, uso, ejemplo
            if line.startswith('**Traducción'):
                elements.append(self._create_translation(line))
                i += 1
                continue
            
            if line.startswith('**Uso:'):
                elements.append(self._create_usage(line))
                i += 1
                continue
            
            if line.startswith('**Ejemplo:'):
                elements.append(self._create_example(line))
                i += 1
                continue
            
            # Lista
            if line.strip().startswith('- '):
                list_elem, skip = self._create_list(lines, i)
                elements.append(list_elem)
                i += skip
                continue
            
            # Separador
            if line.strip() in ['---', '***', '___']:
                elements.append(self._create_separator())
                i += 1
                continue
            
            # Párrafo
            if line.strip():
                para_elem, skip = self._create_paragraph(lines, i)
                elements.append(para_elem)
                i += skip
                continue
            
            i += 1
        
        return elements
    
    def _create_book_title(self, title: str) -> HTMLElement:
        """Crea elemento de título del libro."""
        self.element_counter += 1
        elem_id = f"book-title-{self.element_counter}"
        
        return HTMLElement(
            id=elem_id,
            type=HTMLElementType.BOOK_TITLE,
            content=html.escape(title),
            attributes={"data-level": "1"},
            children=[],
            metadata={"original_text": title}
        )
    
    def _create_chapter(self, lines: List[str], start_idx: int) -> Tuple[HTMLElement, int]:
        """Crea elemento de capítulo con su contenido."""
        self.element_counter += 1
        chapter_id = f"chapter-{self.element_counter}"
        
        # Extraer título del capítulo
        chapter_line = lines[start_idx]
        chapter_match = re.match(r'^#\s+(CAPÍTULO|Capítulo)\s+(\d+)', chapter_line)
        chapter_num = chapter_match.group(2) if chapter_match else str(self.element_counter)
        
        self.current_chapter = chapter_num
        
        # Crear elemento de capítulo
        chapter_elem = HTMLElement(
            id=chapter_id,
            type=HTMLElementType.CHAPTER,
            content="",
            attributes={
                "data-chapter-number": chapter_num,
                "class": "chapter-container"
            },
            children=[],
            metadata={"chapter_number": int(chapter_num)}
        )
        
        # Agregar título del capítulo
        title_elem = HTMLElement(
            id=f"{chapter_id}-title",
            type=HTMLElementType.CHAPTER_TITLE,
            content=html.escape(chapter_line[2:]),
            attributes={"data-level": "2"},
            children=[],
            metadata={"chapter_number": int(chapter_num)}
        )
        
        chapter_elem.children.append(title_elem)
        
        # Agregar a TOC
        self.toc_entries.append({
            "id": chapter_id,
            "title": chapter_line[2:],
            "level": 1,
            "children": []
        })
        
        return chapter_elem, 1
    
    def _create_chapter_title(self, title: str) -> HTMLElement:
        """Crea elemento de título de capítulo."""
        self.element_counter += 1
        elem_id = f"chapter-title-{self.element_counter}"
        
        elem = HTMLElement(
            id=elem_id,
            type=HTMLElementType.CHAPTER_TITLE,
            content=html.escape(title),
            attributes={"data-level": "2"},
            children=[],
            metadata={
                "chapter": self.current_chapter,
                "original_text": title
            }
        )
        
        # Agregar a TOC si hay un capítulo actual
        if self.toc_entries and self.current_chapter:
            self.toc_entries[-1]["children"].append({
                "id": elem_id,
                "title": title,
                "level": 2
            })
        
        return elem
    
    def _create_section(self, title: str) -> HTMLElement:
        """Crea elemento de sección."""
        self.element_counter += 1
        self.current_section = self.element_counter
        elem_id = f"section-{self.element_counter}"
        
        return HTMLElement(
            id=elem_id,
            type=HTMLElementType.SECTION,
            content=html.escape(title),
            attributes={"data-level": "3"},
            children=[],
            metadata={
                "chapter": self.current_chapter,
                "section_number": self.current_section
            }
        )
    
    def _create_subsection(self, title: str) -> HTMLElement:
        """Crea elemento de subsección."""
        self.element_counter += 1
        elem_id = f"subsection-{self.element_counter}"
        
        return HTMLElement(
            id=elem_id,
            type=HTMLElementType.SUBSECTION,
            content=html.escape(title),
            attributes={"data-level": "4"},
            children=[],
            metadata={
                "chapter": self.current_chapter,
                "section": self.current_section
            }
        )
    
    def _create_expression(self, line: str) -> HTMLElement:
        """Crea elemento de expresión numerada."""
        self.element_counter += 1
        elem_id = f"expression-{self.element_counter}"
        
        # Extraer número y contenido
        match = re.match(r'^\*\*(\d+)\.\s+(.*?)\*\*$', line)
        if match:
            expr_num = match.group(1)
            expr_text = match.group(2)
            
            # Agregar al índice
            self._add_to_index(expr_text, elem_id)
            
            return HTMLElement(
                id=elem_id,
                type=HTMLElementType.EXPRESSION,
                content=f'<span class="expr-number">{expr_num}.</span> '
                        f'<span class="expr-text">{html.escape(expr_text)}</span>',
                attributes={
                    "data-expression-number": expr_num,
                    "class": "numbered-expression"
                },
                children=[],
                metadata={
                    "expression_number": int(expr_num),
                    "expression_text": expr_text,
                    "chapter": self.current_chapter
                }
            )
        
        return self._create_paragraph([line], 0)[0]
    
    def _create_phonetic(self, line: str) -> HTMLElement:
        """Crea elemento de transcripción fonética."""
        self.element_counter += 1
        elem_id = f"phonetic-{self.element_counter}"
        
        # Extraer contenido fonético
        match = re.match(r'^\*\[(.*?)\]\*$', line)
        phonetic_text = match.group(1) if match else line
        
        return HTMLElement(
            id=elem_id,
            type=HTMLElementType.PHONETIC,
            content=html.escape(phonetic_text),
            attributes={
                "class": "phonetic-transcription",
                "aria-label": "Transcripción fonética"
            },
            children=[],
            metadata={"phonetic_text": phonetic_text}
        )
    
    def _create_translation(self, line: str) -> HTMLElement:
        """Crea elemento de traducción."""
        self.element_counter += 1
        elem_id = f"translation-{self.element_counter}"
        
        # Determinar tipo de traducción
        is_literal = "literal" in line.lower()
        translation_type = "literal" if is_literal else "contextual"
        
        # Extraer texto de traducción
        content = re.sub(r'^\*\*.*?:\*\*\s*', '', line)
        
        return HTMLElement(
            id=elem_id,
            type=HTMLElementType.TRANSLATION,
            content=f'<span class="translation-label">'
                    f'{"Traducción literal" if is_literal else "Traducción contextual"}:</span> '
                    f'<span class="translation-text">{html.escape(content)}</span>',
            attributes={
                "class": f"translation-{translation_type}",
                "data-translation-type": translation_type
            },
            children=[],
            metadata={"translation_type": translation_type}
        )
    
    def _create_usage(self, line: str) -> HTMLElement:
        """Crea elemento de uso."""
        self.element_counter += 1
        elem_id = f"usage-{self.element_counter}"
        
        content = re.sub(r'^\*\*Uso:\*\*\s*', '', line)
        
        return HTMLElement(
            id=elem_id,
            type=HTMLElementType.USAGE,
            content=f'<span class="usage-label">Uso:</span> '
                    f'<span class="usage-text">{html.escape(content)}</span>',
            attributes={"class": "usage-description"},
            children=[],
            metadata={"usage_text": content}
        )
    
    def _create_example(self, line: str) -> HTMLElement:
        """Crea elemento de ejemplo."""
        self.element_counter += 1
        elem_id = f"example-{self.element_counter}"
        
        content = re.sub(r'^\*\*Ejemplo:\*\*\s*', '', line)
        
        return HTMLElement(
            id=elem_id,
            type=HTMLElementType.EXAMPLE,
            content=f'<span class="example-label">Ejemplo:</span> '
                    f'<span class="example-text">{html.escape(content)}</span>',
            attributes={"class": "example-sentence"},
            children=[],
            metadata={"example_text": content}
        )
    
    def _create_list(self, lines: List[str], start_idx: int) -> Tuple[HTMLElement, int]:
        """Crea elemento de lista."""
        self.element_counter += 1
        list_id = f"list-{self.element_counter}"
        
        list_elem = HTMLElement(
            id=list_id,
            type=HTMLElementType.LIST,
            content="",
            attributes={"class": "content-list"},
            children=[],
            metadata={"item_count": 0}
        )
        
        i = start_idx
        while i < len(lines) and lines[i].strip().startswith('- '):
            item_content = lines[i].strip()[2:]
            self.element_counter += 1
            
            item_elem = HTMLElement(
                id=f"list-item-{self.element_counter}",
                type=HTMLElementType.LIST_ITEM,
                content=self._process_inline_markdown(item_content),
                attributes={},
                children=[],
                metadata={"list_id": list_id}
            )
            
            list_elem.children.append(item_elem)
            list_elem.metadata["item_count"] += 1
            i += 1
        
        return list_elem, i - start_idx
    
    def _create_separator(self) -> HTMLElement:
        """Crea elemento separador."""
        self.element_counter += 1
        
        return HTMLElement(
            id=f"separator-{self.element_counter}",
            type=HTMLElementType.SEPARATOR,
            content="",
            attributes={"class": "content-separator"},
            children=[],
            metadata={}
        )
    
    def _create_paragraph(self, lines: List[str], start_idx: int) -> Tuple[HTMLElement, int]:
        """Crea elemento de párrafo."""
        self.element_counter += 1
        para_id = f"paragraph-{self.element_counter}"
        
        # Recolectar líneas del párrafo
        para_lines = []
        i = start_idx
        while i < len(lines) and lines[i].strip() and not self._is_block_element(lines[i]):
            para_lines.append(lines[i].strip())
            i += 1
        
        content = " ".join(para_lines)
        processed_content = self._process_inline_markdown(content)
        
        return HTMLElement(
            id=para_id,
            type=HTMLElementType.PARAGRAPH,
            content=processed_content,
            attributes={"class": "content-paragraph"},
            children=[],
            metadata={
                "word_count": len(content.split()),
                "has_emphasis": "*" in content and "**" not in content,
                "has_strong": "**" in content
            }
        ), i - start_idx
    
    def _is_block_element(self, line: str) -> bool:
        """Verifica si una línea es un elemento de bloque."""
        patterns = [
            r'^#{1,6}\s+',  # Encabezados
            r'^\*\*\d+\.\s+.*\*\*$',  # Expresiones numeradas
            r'^\*\[.*\]\*$',  # Transcripciones fonéticas
            r'^\*\*(?:Traducción|Uso|Ejemplo):',  # Elementos especiales
            r'^[-*+]\s+',  # Listas
            r'^(---|___|[*]{3})$',  # Separadores
        ]
        
        return any(re.match(pattern, line.strip()) for pattern in patterns)
    
    def _process_inline_markdown(self, text: str) -> str:
        """Procesa markdown inline (negrita, cursiva, etc.)."""
        # Negrita
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        
        # Cursiva (evitar conflicto con negrita)
        text = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'<em>\1</em>', text)
        
        # Código inline
        text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
        
        # Enlaces
        text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)
        
        # Escapar HTML restante
        return text
    
    def _postprocess_elements(self, elements: List[HTMLElement]) -> List[HTMLElement]:
        """Post-procesa elementos para mejoras adicionales."""
        processed = []
        
        for i, elem in enumerate(elements):
            # Agrupar elementos relacionados
            if elem.type == HTMLElementType.EXPRESSION:
                # Buscar elementos relacionados que siguen
                group = [elem]
                j = i + 1
                while j < len(elements) and elements[j].type in [
                    HTMLElementType.PHONETIC,
                    HTMLElementType.TRANSLATION,
                    HTMLElementType.USAGE,
                    HTMLElementType.EXAMPLE
                ]:
                    group.append(elements[j])
                    j += 1
                
                # Crear contenedor para el grupo
                if len(group) > 1:
                    self.element_counter += 1
                    container = HTMLElement(
                        id=f"expression-group-{self.element_counter}",
                        type=HTMLElementType.EXPRESSION,
                        content="",
                        attributes={"class": "expression-container"},
                        children=group,
                        metadata={"expression_count": len(group)}
                    )
                    processed.append(container)
                    # Saltar elementos agrupados
                    elements[i:j] = [None] * (j - i)
                else:
                    processed.append(elem)
            elif elem is not None:
                processed.append(elem)
        
        return processed
    
    def _generate_table_of_contents(self, elements: List[HTMLElement]) -> List[Dict[str, Any]]:
        """Genera la tabla de contenidos desde los elementos."""
        # Ya se construye durante el parsing
        return self.toc_entries
    
    def _extract_index_terms(self, elements: List[HTMLElement]) -> Dict[str, List[str]]:
        """Extrae términos para el índice."""
        return self.index_terms
    
    def _add_to_index(self, term: str, location_id: str) -> None:
        """Agrega un término al índice."""
        if term not in self.index_terms:
            self.index_terms[term] = []
        self.index_terms[term].append(location_id)
    
    def _extract_title(self, elements: List[HTMLElement]) -> str:
        """Extrae el título del libro de los elementos."""
        for elem in elements:
            if elem.type == HTMLElementType.BOOK_TITLE:
                return elem.content.replace('<strong>', '').replace('</strong>', '')
        return "Libro sin título"


# Función de utilidad para conversión directa
def convert_markdown_to_professional_html(markdown_content: str, 
                                         book_title: str = "",
                                         author: str = "",
                                         language: str = "es") -> str:
    """Función de utilidad para conversión directa de Markdown a HTML profesional."""
    converter = MarkdownToHTMLConverter()
    book_structure = converter.convert(markdown_content, book_title, author, language)
    return book_structure.to_html_document()


# Función para extraer solo el contenido principal (sin documento completo)
def convert_markdown_to_content_html(markdown_content: str) -> str:
    """Convierte Markdown a HTML del contenido principal solamente."""
    converter = MarkdownToHTMLConverter()
    book_structure = converter.convert(markdown_content)
    
    html_parts = []
    for element in book_structure.elements:
        html_parts.append(element.to_html())
    
    return "\n".join(html_parts)