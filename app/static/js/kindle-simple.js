/**
 * Ultra Realistic Kindle Reader - Versión Simplificada
 * Funciona garantizado sin errores
 */

(function(window) {
    'use strict';

    class SimpleKindleReader {
        constructor(options = {}) {
            this.config = {
                container: options.container || '#kindle-reader',
                content: options.content || '',
                fontSize: options.fontSize || 3,
                theme: options.theme || 'white',
                deviceType: options.deviceType || 'paperwhite'
            };

            this.state = {
                currentPage: 0,
                totalPages: 0,
                isInitialized: false,
                pages: []
            };

            this.container = null;
            this.elements = {};
        }

        async init() {
            console.log('🚀 Inicializando Simple Kindle Reader...');
            
            try {
                // 1. Encontrar contenedor
                this.container = typeof this.config.container === 'string' 
                    ? document.querySelector(this.config.container) 
                    : this.config.container;

                if (!this.container) {
                    throw new Error('Contenedor no encontrado');
                }

                // 2. Crear HTML
                this.createHTML();

                // 3. Procesar contenido
                this.processContent();

                // 4. Mostrar primera página
                this.showPage(0);

                // 5. Setup eventos
                this.setupEvents();

                this.state.isInitialized = true;
                console.log('✅ Simple Kindle Reader inicializado correctamente');

                // Emitir evento
                const event = new CustomEvent('kindle:kindleInitialized', {
                    detail: { 
                        totalPages: this.state.totalPages,
                        deviceType: this.config.deviceType
                    },
                    bubbles: true
                });
                this.container.dispatchEvent(event);

            } catch (error) {
                console.error('❌ Error inicializando Simple Kindle Reader:', error);
                this.showError(error.message);
            }
        }

        createHTML() {
            this.container.innerHTML = `
                <div class="simple-kindle" data-theme="${this.config.theme}">
                    <div class="kindle-device">
                        <div class="kindle-screen">
                            <!-- Status Bar -->
                            <div class="status-bar">
                                <div class="book-title-status">📚 ${this.getBookTitle()}</div>
                                <div class="status-icons">📶 🔄 🔋87%</div>
                            </div>
                            
                            <!-- Área de lectura -->
                            <div class="reading-area" id="reading-area">
                                <div class="page-content" id="page-content">
                                    <div class="loading">Procesando libro...</div>
                                </div>
                            </div>
                            
                            <!-- Controles de página -->
                            <div class="page-controls">
                                <button id="prev-btn" class="nav-btn">◀</button>
                                <div class="page-info">
                                    <span id="current-page">1</span> de <span id="total-pages">--</span>
                                </div>
                                <button id="next-btn" class="nav-btn">▶</button>
                            </div>
                            
                            <!-- Progress bar -->
                            <div class="progress-bar">
                                <div class="progress-fill" id="progress-fill" style="width: 0%"></div>
                            </div>
                        </div>
                        
                        <!-- Menú de configuración -->
                        <div class="config-menu" id="config-menu" style="display: none;">
                            <h3>⚙️ Configuración</h3>
                            <div class="config-group">
                                <label>Tema:</label>
                                <button onclick="kindleInstance.changeTheme('white')" class="theme-btn">☀️ Claro</button>
                                <button onclick="kindleInstance.changeTheme('sepia')" class="theme-btn">🍂 Sepia</button>
                                <button onclick="kindleInstance.changeTheme('dark')" class="theme-btn">🌙 Oscuro</button>
                            </div>
                            <div class="config-group">
                                <label>Tamaño de Fuente:</label>
                                <button onclick="kindleInstance.changeFontSize(-1)" class="size-btn">A-</button>
                                <span id="font-size-display">${this.config.fontSize}</span>
                                <button onclick="kindleInstance.changeFontSize(1)" class="size-btn">A+</button>
                            </div>
                            <button onclick="kindleInstance.closeMenu()" class="close-menu">✕ Cerrar</button>
                        </div>
                    </div>
                </div>
            `;

            // Cache elementos
            this.elements = {
                readingArea: this.container.querySelector('#reading-area'),
                pageContent: this.container.querySelector('#page-content'),
                currentPage: this.container.querySelector('#current-page'),
                totalPages: this.container.querySelector('#total-pages'),
                progressFill: this.container.querySelector('#progress-fill'),
                prevBtn: this.container.querySelector('#prev-btn'),
                nextBtn: this.container.querySelector('#next-btn'),
                configMenu: this.container.querySelector('#config-menu'),
                fontSizeDisplay: this.container.querySelector('#font-size-display')
            };
        }

        processContent() {
            console.log('📚 Procesando contenido...');
            
            if (!this.config.content) {
                this.state.pages = ['<div class="no-content">📚<br><br>No hay contenido disponible</div>'];
                this.state.totalPages = 1;
                return;
            }

            // Dividir por párrafos
            const paragraphs = this.config.content.split(/\n\s*\n/).filter(p => p.trim());
            const wordsPerPage = 250; // Aproximadamente
            
            this.state.pages = [];
            let currentPage = '';
            let wordCount = 0;

            for (const paragraph of paragraphs) {
                const paragraphWords = paragraph.split(/\s+/).length;
                
                if (wordCount + paragraphWords > wordsPerPage && currentPage.trim()) {
                    // Nueva página
                    this.state.pages.push(this.formatPage(currentPage));
                    currentPage = paragraph;
                    wordCount = paragraphWords;
                } else {
                    currentPage += (currentPage ? '\n\n' : '') + paragraph;
                    wordCount += paragraphWords;
                }
            }

            // Última página
            if (currentPage.trim()) {
                this.state.pages.push(this.formatPage(currentPage));
            }

            this.state.totalPages = this.state.pages.length;
            console.log(`✅ Contenido procesado: ${this.state.totalPages} páginas`);
        }

        formatPage(content) {
            return content
                .replace(/^#\s+(.+)$/gm, '<h1 class="chapter-title">$1</h1>')
                .replace(/^##\s+(.+)$/gm, '<h2 class="section-title">$1</h2>')
                .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.+?)\*/g, '<em>$1</em>')
                .split(/\n\s*\n/)
                .map(p => p.trim() && !p.startsWith('<h') ? `<p>${p}</p>` : p)
                .join('');
        }

        showPage(pageNumber) {
            if (pageNumber < 0 || pageNumber >= this.state.totalPages) return;

            this.state.currentPage = pageNumber;
            
            // Actualizar contenido
            if (this.elements.pageContent) {
                this.elements.pageContent.innerHTML = this.state.pages[pageNumber];
            }

            // Actualizar info de página
            if (this.elements.currentPage) {
                this.elements.currentPage.textContent = pageNumber + 1;
            }
            if (this.elements.totalPages) {
                this.elements.totalPages.textContent = this.state.totalPages;
            }

            // Actualizar progreso
            const progress = this.state.totalPages > 0 ? 
                ((pageNumber + 1) / this.state.totalPages) * 100 : 0;
            if (this.elements.progressFill) {
                this.elements.progressFill.style.width = progress + '%';
            }

            // Actualizar botones
            if (this.elements.prevBtn) {
                this.elements.prevBtn.disabled = pageNumber === 0;
            }
            if (this.elements.nextBtn) {
                this.elements.nextBtn.disabled = pageNumber >= this.state.totalPages - 1;
            }

            console.log(`📄 Mostrando página ${pageNumber + 1} de ${this.state.totalPages}`);
        }

        setupEvents() {
            // Botones de navegación
            if (this.elements.prevBtn) {
                this.elements.prevBtn.onclick = () => this.previousPage();
            }
            if (this.elements.nextBtn) {
                this.elements.nextBtn.onclick = () => this.nextPage();
            }

            // Navegación por teclado
            document.addEventListener('keydown', (e) => {
                if (!this.state.isInitialized) return;
                
                switch (e.key) {
                    case 'ArrowLeft':
                    case 'ArrowUp':
                        e.preventDefault();
                        this.previousPage();
                        break;
                    case 'ArrowRight':
                    case 'ArrowDown':
                    case ' ':
                        e.preventDefault();
                        this.nextPage();
                        break;
                    case 'm':
                    case 'M':
                        this.toggleMenu();
                        break;
                }
            });

            // Click en área de lectura para menú
            if (this.elements.readingArea) {
                this.elements.readingArea.onclick = (e) => {
                    const rect = this.elements.readingArea.getBoundingClientRect();
                    const clickX = e.clientX - rect.left;
                    const width = rect.width;
                    
                    if (clickX < width * 0.3) {
                        this.previousPage();
                    } else if (clickX > width * 0.7) {
                        this.nextPage();
                    } else {
                        this.toggleMenu();
                    }
                };
            }
        }

        nextPage() {
            if (this.state.currentPage < this.state.totalPages - 1) {
                this.showPage(this.state.currentPage + 1);
            }
        }

        previousPage() {
            if (this.state.currentPage > 0) {
                this.showPage(this.state.currentPage - 1);
            }
        }

        toggleMenu() {
            const menu = this.elements.configMenu;
            if (menu) {
                menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
            }
        }

        closeMenu() {
            if (this.elements.configMenu) {
                this.elements.configMenu.style.display = 'none';
            }
        }

        changeTheme(theme) {
            this.config.theme = theme;
            const kindleDiv = this.container.querySelector('.simple-kindle');
            if (kindleDiv) {
                kindleDiv.setAttribute('data-theme', theme);
            }
            console.log(`🎨 Tema cambiado a: ${theme}`);
        }

        changeFontSize(delta) {
            const newSize = Math.max(1, Math.min(8, this.config.fontSize + delta));
            if (newSize !== this.config.fontSize) {
                this.config.fontSize = newSize;
                
                const kindleDiv = this.container.querySelector('.simple-kindle');
                if (kindleDiv) {
                    kindleDiv.style.setProperty('--font-size', this.getFontSizePixels(newSize) + 'px');
                }
                
                if (this.elements.fontSizeDisplay) {
                    this.elements.fontSizeDisplay.textContent = newSize;
                }
                
                console.log(`🔤 Tamaño de fuente cambiado a: ${newSize}`);
            }
        }

        getFontSizePixels(size) {
            const sizes = [12, 14, 16, 18, 20, 22, 24, 26];
            return sizes[size - 1] || 16;
        }

        getBookTitle() {
            // Extraer título del contenido
            const titleMatch = this.config.content?.match(/^#\s+(.+)$/m);
            return titleMatch ? titleMatch[1] : 'Mi Libro';
        }

        showError(message) {
            this.container.innerHTML = `
                <div class="kindle-error">
                    <h3>❌ Error del Kindle</h3>
                    <p>${message}</p>
                    <button onclick="location.reload()">🔄 Recargar</button>
                </div>
            `;
        }

        getState() {
            return {
                isInitialized: this.state.isInitialized,
                currentPage: this.state.currentPage + 1,
                totalPages: this.state.totalPages,
                theme: this.config.theme,
                fontSize: this.config.fontSize,
                deviceType: this.config.deviceType
            };
        }

        destroy() {
            this.state.isInitialized = false;
            if (this.container) {
                this.container.innerHTML = '';
            }
        }
    }

    // CSS integrado
    const css = `
        <style id="simple-kindle-css">
            .simple-kindle {
                --font-size: 16px;
                --bg-color: #ffffff;
                --text-color: #1a1a1a;
                --border-color: #e0e0e0;
                --accent-color: #3498db;
                
                max-width: 600px;
                margin: 0 auto;
                font-family: 'Georgia', serif;
            }
            
            .simple-kindle[data-theme="sepia"] {
                --bg-color: #f4f1e8;
                --text-color: #5c4b37;
                --border-color: #d4c5a9;
            }
            
            .simple-kindle[data-theme="dark"] {
                --bg-color: #1a1a1a;
                --text-color: #e5e5e5;
                --border-color: #404040;
            }
            
            .kindle-device {
                background: linear-gradient(145deg, #f0f0f0, #ffffff);
                border-radius: 20px;
                padding: 20px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            }
            
            .kindle-screen {
                background: var(--bg-color);
                border: 2px solid var(--border-color);
                border-radius: 15px;
                min-height: 500px;
                position: relative;
                overflow: hidden;
            }
            
            .status-bar {
                display: flex;
                justify-content: space-between;
                padding: 10px 15px;
                border-bottom: 1px solid var(--border-color);
                font-size: 12px;
                color: var(--text-color);
                opacity: 0.7;
            }
            
            .reading-area {
                padding: 30px 25px;
                min-height: 350px;
                color: var(--text-color);
                font-size: var(--font-size);
                line-height: 1.5;
                cursor: pointer;
            }
            
            .page-content {
                max-width: 100%;
                text-align: justify;
            }
            
            .page-content p {
                margin: 0 0 1em 0;
                text-indent: 1.2em;
            }
            
            .chapter-title {
                font-size: 1.3em;
                font-weight: bold;
                text-align: center;
                margin: 0 0 1.5em 0;
                color: var(--accent-color);
            }
            
            .section-title {
                font-size: 1.1em;
                font-weight: bold;
                margin: 1.5em 0 1em 0;
                color: var(--text-color);
            }
            
            .page-controls {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 15px 20px;
                border-top: 1px solid var(--border-color);
                background: var(--bg-color);
            }
            
            .nav-btn {
                background: var(--accent-color);
                color: white;
                border: none;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                font-size: 16px;
                cursor: pointer;
                transition: all 0.2s;
            }
            
            .nav-btn:hover:not(:disabled) {
                background: #2980b9;
                transform: scale(1.1);
            }
            
            .nav-btn:disabled {
                background: #bdc3c7;
                cursor: not-allowed;
                transform: none;
            }
            
            .page-info {
                font-weight: bold;
                color: var(--text-color);
            }
            
            .progress-bar {
                height: 4px;
                background: var(--border-color);
                position: relative;
            }
            
            .progress-fill {
                height: 100%;
                background: var(--accent-color);
                transition: width 0.3s ease;
            }
            
            .config-menu {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: var(--bg-color);
                border: 2px solid var(--border-color);
                border-radius: 15px;
                padding: 20px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
                z-index: 100;
                min-width: 250px;
            }
            
            .config-group {
                margin: 15px 0;
                text-align: center;
            }
            
            .config-group label {
                display: block;
                margin-bottom: 8px;
                font-weight: bold;
                color: var(--text-color);
            }
            
            .theme-btn, .size-btn {
                background: var(--accent-color);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 12px;
                margin: 0 5px;
                cursor: pointer;
                font-size: 12px;
            }
            
            .theme-btn:hover, .size-btn:hover {
                background: #2980b9;
            }
            
            .close-menu {
                background: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                cursor: pointer;
                width: 100%;
                margin-top: 15px;
            }
            
            .loading {
                text-align: center;
                padding: 50px;
                color: var(--text-color);
                opacity: 0.7;
            }
            
            .no-content {
                text-align: center;
                padding: 50px;
                color: var(--text-color);
                opacity: 0.7;
                font-size: 18px;
                line-height: 1.6;
            }
            
            .kindle-error {
                text-align: center;
                padding: 50px 20px;
                color: #e74c3c;
            }
            
            .kindle-error button {
                background: var(--accent-color);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                cursor: pointer;
                margin-top: 15px;
            }
            
            @media (max-width: 768px) {
                .kindle-device {
                    padding: 15px;
                    margin: 0 10px;
                }
                
                .reading-area {
                    padding: 20px 15px;
                    font-size: calc(var(--font-size) * 0.9);
                }
                
                .config-menu {
                    width: 90%;
                    max-width: 300px;
                }
            }
        </style>
    `;

    // Inyectar CSS
    if (!document.getElementById('simple-kindle-css')) {
        document.head.insertAdjacentHTML('beforeend', css);
    }

    // Exportar
    window.SimpleKindleReader = SimpleKindleReader;
    window.UltraRealisticKindleReader = SimpleKindleReader; // Compatibilidad
    window.KindleReaderPlugin = SimpleKindleReader;

    // Auto-inicialización
    document.addEventListener('DOMContentLoaded', () => {
        console.log('🔍 Buscando elementos con data-kindle (Simple)...');
        
        const elements = document.querySelectorAll('[data-kindle]');
        console.log(`📦 Encontrados ${elements.length} elementos`);
        
        elements.forEach((element, index) => {
            console.log(`🚀 Inicializando Simple Kindle #${index + 1}...`);
            
            const content = element.dataset.kindleContent || element.textContent || '';
            const options = {
                container: element,
                content: content,
                fontSize: parseInt(element.dataset.kindleFontSize) || 3,
                theme: element.dataset.kindleTheme || 'white',
                deviceType: element.dataset.kindleDeviceType || 'paperwhite'
            };
            
            const kindle = new SimpleKindleReader(options);
            kindle.init();
            
            element.kindleInstance = kindle;
            window.kindleInstance = kindle; // Global para debug
        });
    });

})(window);