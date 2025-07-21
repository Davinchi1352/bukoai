"""
Modelo para plantillas de email
"""
from typing import Dict, Any, Optional, List
from sqlalchemy import Column, String, Text, Boolean, JSON
from jinja2 import Template
from app.models.base import BaseModel


class EmailTemplate(BaseModel):
    """Modelo de plantillas de email"""
    
    __tablename__ = "email_templates"
    
    # Información de la plantilla
    name = Column(String(100), unique=True, nullable=False)
    subject = Column(String(255), nullable=False)
    html_content = Column(Text, nullable=False)
    text_content = Column(Text, nullable=True)
    
    # Variables disponibles
    variables = Column(JSON, nullable=True)
    
    # Configuración
    language = Column(String(5), default="es", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    def render_subject(self, variables: Dict[str, Any]) -> str:
        """Renderiza el asunto de la plantilla con las variables"""
        subject_template = Template(self.subject)
        return subject_template.render(**variables)
    
    def render_html_content(self, variables: Dict[str, Any]) -> str:
        """Renderiza el contenido HTML de la plantilla con las variables"""
        html_template = Template(self.html_content)
        return html_template.render(**variables)
    
    def render_text_content(self, variables: Dict[str, Any]) -> str:
        """Renderiza el contenido de texto de la plantilla con las variables"""
        if not self.text_content:
            return ""
        text_template = Template(self.text_content)
        return text_template.render(**variables)
    
    def render_template(self, variables: Dict[str, Any]) -> Dict[str, str]:
        """Renderiza la plantilla con las variables"""
        return {
            "subject": self.render_subject(variables),
            "html_content": self.render_html_content(variables),
            "text_content": self.render_text_content(variables)
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario"""
        base_dict = super().to_dict()
        base_dict.update({
            "is_active": self.is_active,
            "language": self.language,
        })
        return base_dict
    
    @classmethod
    def get_by_name(cls, name: str, language: str = "es") -> Optional['EmailTemplate']:
        """Busca una plantilla por nombre e idioma"""
        return cls.query.filter_by(name=name, language=language, is_active=True).first()
    
    @classmethod
    def get_active_templates(cls) -> List['EmailTemplate']:
        """Retorna plantillas activas"""
        return cls.query.filter_by(is_active=True).all()
    
    def __repr__(self) -> str:
        return f"<EmailTemplate {self.name} - {self.language}>"