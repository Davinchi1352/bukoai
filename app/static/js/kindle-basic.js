/**
 * Kindle Reader Básico - Versión Ultra Simplificada
 * Funciona en cualquier navegador sin errores
 */

console.log('🔥 Cargando Kindle Basic...');

// Definir clase básica
function BasicKindleReader(options) {
    console.log('🏗️ Creando BasicKindleReader con opciones:', options);
    
    this.container = options.container;
    this.content = options.content || '';
    this.currentPage = 0;
    this.pages = [];
    this.isInitialized = false;
    
    console.log('✅ BasicKindleReader creado correctamente');
}

// Método init
BasicKindleReader.prototype.init = function() {
    console.log('🚀 Inicializando BasicKindleReader...');
    
    try {
        // Crear HTML básico
        this.createBasicHTML();
        
        // Procesar contenido
        this.processBasicContent();
        
        // Mostrar primera página
        this.showPage(0);
        
        // Configurar eventos básicos
        this.setupBasicEvents();
        
        this.isInitialized = true;
        console.log('✅ BasicKindleReader inicializado correctamente');
        
        // Emitir evento
        var event = new CustomEvent('kindle:kindleInitialized', {
            detail: { totalPages: this.pages.length },
            bubbles: true
        });
        this.container.dispatchEvent(event);
        
    } catch (error) {
        console.error('❌ Error inicializando BasicKindleReader:', error);
        this.showError('Error: ' + error.message);
    }
};

// Crear HTML básico
BasicKindleReader.prototype.createBasicHTML = function() {
    console.log('🎨 Creando HTML básico...');
    
    this.container.innerHTML = `
        <div class="basic-kindle">
            <div class="kindle-frame">
                <div class="kindle-header">
                    📚 ${this.getBookTitle()} | 📶 🔋87%
                </div>
                <div class="kindle-content" id="kindle-content">
                    <div class="loading">Procesando contenido...</div>
                </div>
                <div class="kindle-footer">
                    <button id="prev-btn" onclick="kindleInstance.previousPage()">◀ Anterior</button>
                    <span id="page-info">Página 1 de --</span>
                    <button id="next-btn" onclick="kindleInstance.nextPage()">Siguiente ▶</button>
                </div>
                <div class="kindle-progress">
                    <div class="progress-bar" id="progress-bar" style="width: 0%"></div>
                </div>
            </div>
            <div class="kindle-controls">
                <button onclick="kindleInstance.changeTheme()">🎨 Cambiar Tema</button>
                <button onclick="kindleInstance.changeFontSize(1)">A+</button>
                <button onclick="kindleInstance.changeFontSize(-1)">A-</button>
            </div>
        </div>
        
        <style>
        .basic-kindle {
            max-width: 600px;
            margin: 0 auto;
            font-family: Georgia, serif;
        }
        .kindle-frame {
            background: white;
            border: 2px solid #ddd;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .kindle-header {
            background: #f5f5f5;
            padding: 10px;
            text-align: center;
            border-bottom: 1px solid #ddd;
            font-size: 14px;
        }
        .kindle-content {
            padding: 20px;
            min-height: 400px;
            font-size: 16px;
            line-height: 1.5;
            text-align: justify;
        }
        .kindle-footer {
            background: #f5f5f5;
            padding: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid #ddd;
        }
        .kindle-footer button {
            background: #3498db;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 5px;
            cursor: pointer;
        }
        .kindle-footer button:disabled {
            background: #bdc3c7;
            cursor: not-allowed;
        }
        .kindle-progress {
            height: 4px;
            background: #ecf0f1;
        }
        .progress-bar {
            height: 100%;
            background: #3498db;
            transition: width 0.3s ease;
        }
        .kindle-controls {
            text-align: center;
            margin-top: 15px;
        }
        .kindle-controls button {
            background: #95a5a6;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 5px;
            cursor: pointer;
            margin: 0 5px;
        }
        .loading {
            text-align: center;
            padding: 50px;
            color: #7f8c8d;
        }
        .basic-kindle[data-theme="dark"] .kindle-frame {
            background: #2c3e50;
            color: #ecf0f1;
        }
        .basic-kindle[data-theme="dark"] .kindle-content {
            background: #2c3e50;
            color: #ecf0f1;
        }
        .basic-kindle[data-theme="sepia"] .kindle-frame {
            background: #f4f1e8;
            color: #5c4b37;
        }
        .basic-kindle[data-theme="sepia"] .kindle-content {
            background: #f4f1e8;
            color: #5c4b37;
        }
        .chapter-title {
            font-size: 1.3em;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
            color: #3498db;
        }
        .kindle-paragraph {
            margin-bottom: 15px;
            text-indent: 20px;
        }
        </style>
    `;
    
    console.log('✅ HTML básico creado');
};

// Procesar contenido básico
BasicKindleReader.prototype.processBasicContent = function() {
    console.log('📚 Procesando contenido básico...');
    
    if (!this.content) {
        this.pages = ['<div class="no-content">📚 No hay contenido disponible</div>'];
        return;
    }
    
    // Dividir en párrafos
    var paragraphs = this.content.split(/\n\s*\n/).filter(function(p) { 
        return p.trim(); 
    });
    
    this.pages = [];
    var currentPage = '';
    var wordsPerPage = 300;
    var currentWordCount = 0;
    
    for (var i = 0; i < paragraphs.length; i++) {
        var paragraph = paragraphs[i];
        var paragraphWords = paragraph.split(/\s+/).length;
        
        if (currentWordCount + paragraphWords > wordsPerPage && currentPage.trim()) {
            this.pages.push(this.formatPage(currentPage));
            currentPage = paragraph;
            currentWordCount = paragraphWords;
        } else {
            currentPage += (currentPage ? '\n\n' : '') + paragraph;
            currentWordCount += paragraphWords;
        }
    }
    
    // Última página
    if (currentPage.trim()) {
        this.pages.push(this.formatPage(currentPage));
    }
    
    console.log('✅ Contenido procesado: ' + this.pages.length + ' páginas');
};

// Formatear página
BasicKindleReader.prototype.formatPage = function(content) {
    return content
        .replace(/^#\s+(.+)$/gm, '<div class="chapter-title">$1</div>')
        .replace(/^##\s+(.+)$/gm, '<h3>$1</h3>')
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        .split(/\n\s*\n/)
        .map(function(p) {
            return p.trim() && !p.startsWith('<') ? '<div class="kindle-paragraph">' + p + '</div>' : p;
        })
        .join('');
};

// Mostrar página
BasicKindleReader.prototype.showPage = function(pageNumber) {
    if (pageNumber < 0 || pageNumber >= this.pages.length) return;
    
    this.currentPage = pageNumber;
    
    var contentElement = document.getElementById('kindle-content');
    if (contentElement) {
        contentElement.innerHTML = this.pages[pageNumber];
    }
    
    var pageInfoElement = document.getElementById('page-info');
    if (pageInfoElement) {
        pageInfoElement.textContent = 'Página ' + (pageNumber + 1) + ' de ' + this.pages.length;
    }
    
    var progressElement = document.getElementById('progress-bar');
    if (progressElement && this.pages.length > 0) {
        var progress = ((pageNumber + 1) / this.pages.length) * 100;
        progressElement.style.width = progress + '%';
    }
    
    var prevBtn = document.getElementById('prev-btn');
    var nextBtn = document.getElementById('next-btn');
    
    if (prevBtn) prevBtn.disabled = pageNumber === 0;
    if (nextBtn) nextBtn.disabled = pageNumber >= this.pages.length - 1;
    
    console.log('📄 Mostrando página ' + (pageNumber + 1) + ' de ' + this.pages.length);
};

// Configurar eventos básicos
BasicKindleReader.prototype.setupBasicEvents = function() {
    console.log('⚙️ Configurando eventos básicos...');
    
    var self = this;
    
    document.addEventListener('keydown', function(e) {
        if (!self.isInitialized) return;
        
        switch(e.key) {
            case 'ArrowLeft':
            case 'ArrowUp':
                e.preventDefault();
                self.previousPage();
                break;
            case 'ArrowRight':
            case 'ArrowDown':
            case ' ':
                e.preventDefault();
                self.nextPage();
                break;
        }
    });
    
    console.log('✅ Eventos configurados');
};

// Navegación
BasicKindleReader.prototype.nextPage = function() {
    if (this.currentPage < this.pages.length - 1) {
        this.showPage(this.currentPage + 1);
    }
};

BasicKindleReader.prototype.previousPage = function() {
    if (this.currentPage > 0) {
        this.showPage(this.currentPage - 1);
    }
};

// Cambiar tema
BasicKindleReader.prototype.changeTheme = function() {
    var themes = ['white', 'sepia', 'dark'];
    var currentTheme = this.theme || 'white';
    var currentIndex = themes.indexOf(currentTheme);
    var nextIndex = (currentIndex + 1) % themes.length;
    var nextTheme = themes[nextIndex];
    
    this.theme = nextTheme;
    var kindleElement = this.container.querySelector('.basic-kindle');
    if (kindleElement) {
        kindleElement.setAttribute('data-theme', nextTheme);
    }
    
    console.log('🎨 Tema cambiado a: ' + nextTheme);
};

// Cambiar tamaño fuente
BasicKindleReader.prototype.changeFontSize = function(delta) {
    this.fontSize = (this.fontSize || 16) + delta;
    if (this.fontSize < 12) this.fontSize = 12;
    if (this.fontSize > 24) this.fontSize = 24;
    
    var contentElement = document.getElementById('kindle-content');
    if (contentElement) {
        contentElement.style.fontSize = this.fontSize + 'px';
    }
    
    console.log('🔤 Fuente cambiada a: ' + this.fontSize + 'px');
};

// Obtener título del libro
BasicKindleReader.prototype.getBookTitle = function() {
    if (!this.content) return 'Sin Título';
    var match = this.content.match(/^#\s+(.+)$/m);
    return match ? match[1].substring(0, 30) + '...' : 'Mi Libro';
};

// Mostrar error
BasicKindleReader.prototype.showError = function(message) {
    this.container.innerHTML = '<div style="text-align: center; padding: 50px; color: red;"><h3>❌ Error</h3><p>' + message + '</p><button onclick="location.reload()">🔄 Recargar</button></div>';
};

// Obtener estado
BasicKindleReader.prototype.getState = function() {
    return {
        isInitialized: this.isInitialized,
        currentPage: this.currentPage + 1,
        totalPages: this.pages.length,
        theme: this.theme || 'white',
        fontSize: this.fontSize || 16
    };
};

// Exportar globalmente
window.BasicKindleReader = BasicKindleReader;
window.SimpleKindleReader = BasicKindleReader; // Compatibilidad
window.UltraRealisticKindleReader = BasicKindleReader; // Compatibilidad
window.KindleReaderPlugin = BasicKindleReader; // Compatibilidad

console.log('✅ BasicKindleReader definido globalmente');

// Auto-inicialización
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔍 DOM cargado, buscando elementos data-kindle...');
    
    var elements = document.querySelectorAll('[data-kindle]');
    console.log('📦 Encontrados ' + elements.length + ' elementos con data-kindle');
    
    for (var i = 0; i < elements.length; i++) {
        var element = elements[i];
        console.log('🚀 Inicializando Kindle #' + (i + 1) + '...');
        
        try {
            var content = element.getAttribute('data-kindle-content') || element.textContent || '';
            console.log('📝 Contenido detectado: ' + content.length + ' caracteres');
            
            var options = {
                container: element,
                content: content
            };
            
            var kindle = new BasicKindleReader(options);
            kindle.init();
            
            element.kindleInstance = kindle;
            window.kindleInstance = kindle; // Global para debug
            
            console.log('✅ Kindle #' + (i + 1) + ' inicializado correctamente');
            
        } catch (error) {
            console.error('❌ Error inicializando Kindle #' + (i + 1) + ':', error);
        }
    }
    
    if (elements.length === 0) {
        console.warn('⚠️ No se encontraron elementos con data-kindle');
    }
});

console.log('🔥 Kindle Basic cargado completamente');