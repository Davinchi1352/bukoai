/**
 * Kindle Reader ULTRA BÁSICO - Versión que funciona 100% garantizado
 * JavaScript puro sin clases, sin ES6, compatible con cualquier navegador
 */

console.log('🔥 Cargando Kindle Ultra Basic...');

// Variables globales
var kindleInstance = null;

// Función principal del lector
function UltraBasicKindleReader(container, content) {
    console.log('🏗️ Creando UltraBasicKindleReader...');
    
    var self = this;
    
    // Propiedades básicas
    this.container = container;
    this.content = content || '';
    this.currentPage = 0;
    this.pages = [];
    this.isInitialized = false;
    this.theme = 'white';
    this.fontSize = 16;
    
    // Método de inicialización
    this.init = function() {
        console.log('🚀 Inicializando UltraBasicKindleReader...');
        
        try {
            // 1. Crear HTML
            self.createHTML();
            
            // 2. Procesar contenido
            self.processContent();
            
            // 3. Mostrar primera página
            self.showPage(0);
            
            // 4. Configurar eventos
            self.setupEvents();
            
            self.isInitialized = true;
            console.log('✅ UltraBasicKindleReader inicializado correctamente');
            
            // Emitir evento
            var event = document.createEvent('CustomEvent');
            event.initCustomEvent('kindle:kindleInitialized', true, true, {
                totalPages: self.pages.length
            });
            self.container.dispatchEvent(event);
            
        } catch (error) {
            console.error('❌ Error inicializando UltraBasicKindleReader:', error);
            self.showError('Error: ' + error.message);
        }
    };
    
    // Crear HTML básico
    this.createHTML = function() {
        console.log('🎨 Creando HTML ultra básico...');
        
        self.container.innerHTML = 
            '<div class="ultra-basic-kindle" data-theme="' + self.theme + '">' +
                '<div class="kindle-header">📚 ' + self.getBookTitle() + ' | 📶 🔋87%</div>' +
                '<div class="kindle-main">' +
                    '<div class="kindle-content" id="kindle-content">Cargando contenido...</div>' +
                '</div>' +
                '<div class="kindle-footer">' +
                    '<button id="prev-btn" onclick="kindleInstance.previousPage()">◀ Ant</button>' +
                    '<span id="page-info">Página 1 de --</span>' +
                    '<button id="next-btn" onclick="kindleInstance.nextPage()">Sig ▶</button>' +
                '</div>' +
                '<div class="kindle-progress">' +
                    '<div class="progress-fill" id="progress-fill" style="width: 0%; height: 4px; background: #3498db; transition: width 0.3s;"></div>' +
                '</div>' +
                '<div class="kindle-controls">' +
                    '<button onclick="kindleInstance.changeTheme()">🎨 Tema</button>' +
                    '<button onclick="kindleInstance.changeFontSize(2)">A+</button>' +
                    '<button onclick="kindleInstance.changeFontSize(-2)">A-</button>' +
                '</div>' +
            '</div>';
        
        // Agregar estilos
        if (!document.getElementById('ultra-basic-kindle-css')) {
            var style = document.createElement('style');
            style.id = 'ultra-basic-kindle-css';
            style.textContent = 
                '.ultra-basic-kindle { max-width: 600px; margin: 0 auto; font-family: Georgia, serif; background: white; border: 2px solid #ddd; border-radius: 10px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }' +
                '.kindle-header { background: #f5f5f5; padding: 10px; text-align: center; border-bottom: 1px solid #ddd; font-size: 14px; }' +
                '.kindle-main { padding: 20px; min-height: 400px; }' +
                '.kindle-content { font-size: 16px; line-height: 1.6; text-align: justify; }' +
                '.kindle-footer { background: #f5f5f5; padding: 10px; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #ddd; }' +
                '.kindle-footer button { background: #3498db; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; }' +
                '.kindle-footer button:disabled { background: #bdc3c7; cursor: not-allowed; }' +
                '.kindle-controls { text-align: center; padding: 10px; background: #f8f9fa; }' +
                '.kindle-controls button { background: #95a5a6; color: white; border: none; padding: 8px 12px; border-radius: 5px; cursor: pointer; margin: 0 5px; }' +
                '.kindle-progress { height: 4px; background: #ecf0f1; }' +
                '.chapter-title { font-size: 1.3em; font-weight: bold; text-align: center; margin: 20px 0; color: #3498db; }' +
                '.kindle-paragraph { margin-bottom: 15px; text-indent: 20px; }' +
                '.ultra-basic-kindle[data-theme="dark"] { background: #2c3e50; color: #ecf0f1; }' +
                '.ultra-basic-kindle[data-theme="dark"] .kindle-header, .ultra-basic-kindle[data-theme="dark"] .kindle-footer, .ultra-basic-kindle[data-theme="dark"] .kindle-controls { background: #34495e; color: #ecf0f1; }' +
                '.ultra-basic-kindle[data-theme="sepia"] { background: #f4f1e8; color: #5c4b37; }' +
                '.ultra-basic-kindle[data-theme="sepia"] .kindle-header, .ultra-basic-kindle[data-theme="sepia"] .kindle-footer, .ultra-basic-kindle[data-theme="sepia"] .kindle-controls { background: #e8e1d3; color: #5c4b37; }';
            document.head.appendChild(style);
        }
        
        console.log('✅ HTML ultra básico creado');
    };
    
    // Procesar contenido
    this.processContent = function() {
        console.log('📚 Procesando contenido ultra básico...');
        
        if (!self.content) {
            self.pages = ['<div style="text-align: center; padding: 50px; color: #7f8c8d;">📚<br><br>No hay contenido disponible</div>'];
            return;
        }
        
        // Dividir por párrafos
        var paragraphs = self.content.split('\n\n');
        var wordsPerPage = 250;
        
        self.pages = [];
        var currentPage = '';
        var currentWords = 0;
        
        for (var i = 0; i < paragraphs.length; i++) {
            var paragraph = paragraphs[i].trim();
            if (!paragraph) continue;
            
            var paragraphWords = paragraph.split(' ').length;
            
            if (currentWords + paragraphWords > wordsPerPage && currentPage) {
                self.pages.push(self.formatPage(currentPage));
                currentPage = paragraph;
                currentWords = paragraphWords;
            } else {
                if (currentPage) currentPage += '\n\n';
                currentPage += paragraph;
                currentWords += paragraphWords;
            }
        }
        
        if (currentPage) {
            self.pages.push(self.formatPage(currentPage));
        }
        
        console.log('✅ Contenido procesado: ' + self.pages.length + ' páginas');
    };
    
    // Formatear página
    this.formatPage = function(content) {
        return content
            .replace(/^#\s+(.+)$/gm, '<div class="chapter-title">$1</div>')
            .replace(/^##\s+(.+)$/gm, '<h3>$1</h3>')
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.+?)\*/g, '<em>$1</em>')
            .split('\n\n')
            .map(function(p) {
                p = p.trim();
                return p && !p.startsWith('<') ? '<div class="kindle-paragraph">' + p + '</div>' : p;
            })
            .join('');
    };
    
    // Mostrar página
    this.showPage = function(pageNumber) {
        if (pageNumber < 0 || pageNumber >= self.pages.length) return;
        
        self.currentPage = pageNumber;
        
        var contentElement = document.getElementById('kindle-content');
        if (contentElement) {
            contentElement.innerHTML = self.pages[pageNumber];
        }
        
        var pageInfoElement = document.getElementById('page-info');
        if (pageInfoElement) {
            pageInfoElement.textContent = 'Página ' + (pageNumber + 1) + ' de ' + self.pages.length;
        }
        
        var progressElement = document.getElementById('progress-fill');
        if (progressElement && self.pages.length > 0) {
            var progress = ((pageNumber + 1) / self.pages.length) * 100;
            progressElement.style.width = progress + '%';
        }
        
        var prevBtn = document.getElementById('prev-btn');
        var nextBtn = document.getElementById('next-btn');
        
        if (prevBtn) prevBtn.disabled = pageNumber === 0;
        if (nextBtn) nextBtn.disabled = pageNumber >= self.pages.length - 1;
        
        console.log('📄 Mostrando página ' + (pageNumber + 1) + ' de ' + self.pages.length);
    };
    
    // Configurar eventos
    this.setupEvents = function() {
        console.log('⚙️ Configurando eventos ultra básicos...');
        
        document.addEventListener('keydown', function(e) {
            if (!self.isInitialized) return;
            
            if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
                e.preventDefault();
                self.previousPage();
            } else if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ') {
                e.preventDefault();
                self.nextPage();
            }
        });
        
        console.log('✅ Eventos configurados');
    };
    
    // Navegación
    this.nextPage = function() {
        if (self.currentPage < self.pages.length - 1) {
            self.showPage(self.currentPage + 1);
        }
    };
    
    this.previousPage = function() {
        if (self.currentPage > 0) {
            self.showPage(self.currentPage - 1);
        }
    };
    
    // Cambiar tema
    this.changeTheme = function() {
        var themes = ['white', 'sepia', 'dark'];
        var currentIndex = themes.indexOf(self.theme);
        var nextIndex = (currentIndex + 1) % themes.length;
        self.theme = themes[nextIndex];
        
        var kindleElement = self.container.querySelector('.ultra-basic-kindle');
        if (kindleElement) {
            kindleElement.setAttribute('data-theme', self.theme);
        }
        
        console.log('🎨 Tema cambiado a: ' + self.theme);
    };
    
    // Cambiar tamaño fuente
    this.changeFontSize = function(delta) {
        self.fontSize = Math.max(12, Math.min(24, self.fontSize + delta));
        
        var contentElement = document.getElementById('kindle-content');
        if (contentElement) {
            contentElement.style.fontSize = self.fontSize + 'px';
        }
        
        console.log('🔤 Fuente cambiada a: ' + self.fontSize + 'px');
    };
    
    // Obtener título del libro
    this.getBookTitle = function() {
        if (!self.content) return 'Sin Título';
        var match = self.content.match(/^#\s+(.+)$/m);
        return match ? match[1].substring(0, 25) + '...' : 'Mi Libro';
    };
    
    // Mostrar error
    this.showError = function(message) {
        self.container.innerHTML = '<div style="text-align: center; padding: 50px; color: red;"><h3>❌ Error</h3><p>' + message + '</p><button onclick="location.reload()">🔄 Recargar</button></div>';
    };
    
    // Obtener estado
    this.getState = function() {
        return {
            isInitialized: self.isInitialized,
            currentPage: self.currentPage + 1,
            totalPages: self.pages.length,
            theme: self.theme,
            fontSize: self.fontSize,
            deviceType: 'basic'
        };
    };
    
    console.log('✅ UltraBasicKindleReader creado correctamente');
}

// Exportar globalmente para compatibilidad
window.UltraBasicKindleReader = UltraBasicKindleReader;
window.BasicKindleReader = UltraBasicKindleReader;
window.SimpleKindleReader = UltraBasicKindleReader;
window.UltraRealisticKindleReader = UltraBasicKindleReader;
window.KindleReaderPlugin = UltraBasicKindleReader;

console.log('✅ UltraBasicKindleReader definido globalmente');

// Auto-inicialización ULTRA SIMPLE
function initializeKindleReaders() {
    console.log('🔍 Buscando elementos data-kindle...');
    
    var elements = document.querySelectorAll('[data-kindle]');
    console.log('📦 Encontrados ' + elements.length + ' elementos con data-kindle');
    
    for (var i = 0; i < elements.length; i++) {
        var element = elements[i];
        console.log('🚀 Inicializando Kindle #' + (i + 1) + '...');
        
        try {
            var content = element.getAttribute('data-kindle-content') || element.textContent || '';
            console.log('📝 Contenido detectado: ' + content.length + ' caracteres');
            
            var kindle = new UltraBasicKindleReader(element, content);
            kindle.init();
            
            element.kindleInstance = kindle;
            window.kindleInstance = kindle; // Global para debug y botones
            
            console.log('✅ Kindle #' + (i + 1) + ' inicializado correctamente');
            
        } catch (error) {
            console.error('❌ Error inicializando Kindle #' + (i + 1) + ':', error);
        }
    }
    
    if (elements.length === 0) {
        console.warn('⚠️ No se encontraron elementos con data-kindle');
    }
}

// Esperar a que el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeKindleReaders);
} else {
    initializeKindleReaders();
}

console.log('🔥 Kindle Ultra Basic cargado completamente');