/**
 * Ultra Realistic Kindle Reader Plugin - Reingeniería Completa 2024
 * Simula perfectamente la experiencia real de un Kindle Paperwhite
 * 
 * @version 2.0.0
 * @author BukoAI Team
 * @license MIT
 */

(function(global) {
    'use strict';

    class UltraRealisticKindleReader {
        constructor(options = {}) {
            // Configuración avanzada del Kindle realista
            this.config = {
                container: options.container || '#kindle-reader',
                content: options.content || '',
                
                // Configuraciones de texto realistas como Kindle
                fontSize: options.fontSize || 3, // Escala Kindle (1-8)
                lineHeight: options.lineHeight || 1.35, // Espaciado Kindle
                margins: options.margins || 2, // Márgenes Kindle (0-3)
                fontFamily: options.fontFamily || 'Bookerly', // Fuente por defecto Kindle
                
                // Temas realistas
                theme: options.theme || 'white',
                brightness: options.brightness || 8, // Brillo (1-24)
                warmth: options.warmth || 10, // Luz cálida (1-24)
                
                // Configuraciones de página
                orientation: options.orientation || 'portrait',
                pageNumbers: options.pageNumbers !== false,
                timeDisplay: options.timeDisplay !== false,
                batteryDisplay: options.batteryDisplay !== false,
                progressBar: options.progressBar !== false,
                
                // Funciones avanzadas
                annotations: options.annotations !== false,
                bookmarks: options.bookmarks !== false,
                dictionary: options.dictionary !== false,
                search: options.search !== false,
                
                // Simulación de hardware
                deviceType: options.deviceType || 'paperwhite',
                screenSize: options.screenSize || 'large', // compact, large, oasis
                hasPhysicalButtons: options.hasPhysicalButtons || false,
                
                // Efectos realistas
                eInkEffect: options.eInkEffect !== false,
                pageFlipAnimation: options.pageFlipAnimation !== false,
                typingEffect: options.typingEffect || false,
                
                ...options
            };

            // Estado completo del Kindle
            this.state = {
                // Navegación
                currentPage: 0,
                totalPages: 0,
                currentChapter: 0,
                totalChapters: 0,
                
                // Sistema
                isInitialized: false,
                isTransitioning: false,
                isLoading: false,
                isMenuOpen: false,
                
                // Pantalla
                screenWidth: 0,
                screenHeight: 0,
                dpi: 300, // DPI real de Kindle Paperwhite
                
                // Libro
                bookTitle: '',
                bookAuthor: '',
                bookProgress: 0,
                readingTime: 0,
                wordsPerMinute: 250,
                
                // Interacción
                lastTap: 0,
                selectionMode: false,
                selectedText: '',
                
                // Configuraciones activas
                activeFont: 'Bookerly',
                activeFontSize: 3,
                activeTheme: 'white',
                activeBrightness: 8,
                
                // Simulación de estado
                batteryLevel: 87,
                wifiStatus: true,
                syncStatus: true,
                currentTime: new Date()
            };

            // Estructura de contenido avanzada
            this.book = {
                pages: [],
                chapters: [],
                tableOfContents: [],
                bookmarks: [],
                annotations: [],
                highlights: [],
                notes: [],
                vocabulary: []
            };
            
            // Referencias DOM organizadas
            this.elements = {};
            
            // Cache de renders para performance
            this.renderCache = new Map();
            
            // Timers para simulaciones
            this.timers = {
                clock: null,
                battery: null,
                eInk: null,
                sync: null
            };
            
            // Event listeners registrados
            this.eventListeners = [];
            
            // Índice de búsqueda
            this.searchIndex = new Map();

            // Bind de métodos principales
            this.bindMethods();
        }
        
        bindMethods() {
            const methods = [
                'init', 'destroy', 'nextPage', 'previousPage', 'goToPage',
                'handleResize', 'handleKeyPress', 'handleTouch', 'handleTap',
                'openMenu', 'closeMenu', 'toggleBookmark', 'addHighlight',
                'showDefinition', 'updateClock', 'simulateBattery'
            ];
            
            methods.forEach(method => {
                if (this[method]) {
                    this[method] = this[method].bind(this);
                }
            });
        }

        /**
         * Inicialización completa del Kindle realista
         */
        async init() {
            try {
                console.log('🚀 Inicializando Ultra Realistic Kindle Reader v2.0...');
                
                this.state.isLoading = true;
                
                // 1. Verificar y preparar contenedor
                await this.setupContainer();
                
                // 2. Crear interfaz realista del Kindle
                await this.createRealisticInterface();
                
                // 3. Inyectar estilos avanzados
                await this.injectAdvancedCSS();
                
                // 4. Cache de elementos DOM
                this.cacheAllElements();
                
                // 5. Medir pantalla como Kindle real
                this.measureKindleScreen();
                
                // 6. Procesar contenido con algoritmos avanzados
                await this.processBookContent();
                
                // 7. Configurar eventos y gestos
                this.setupAdvancedEvents();
                
                // 8. Iniciar simulaciones realistas
                this.startRealisticSimulations();
                
                // 9. Mostrar primera página con efecto e-ink
                await this.displayFirstPage();
                
                // 10. Finalizar inicialización
                this.state.isInitialized = true;
                this.state.isLoading = false;
                
                console.log('✅ Ultra Realistic Kindle inicializado:');
                console.log(`   📚 ${this.book.pages.length} páginas procesadas`);
                console.log(`   📖 ${this.book.chapters.length} capítulos detectados`);
                console.log(`   ⚡ Simulación ${this.config.deviceType} activa`);
                
                // Emitir evento de inicialización completa
                this.emit('kindleInitialized', {
                    totalPages: this.book.pages.length,
                    totalChapters: this.book.chapters.length,
                    deviceType: this.config.deviceType,
                    screenSize: this.config.screenSize
                });
                
            } catch (error) {
                console.error('❌ Error inicializando Ultra Realistic Kindle:', error);
                this.showCriticalError(error.message);
            }
        }

        /**
         * Configurar contenedor con validaciones avanzadas
         */
        async setupContainer() {
            if (typeof this.config.container === 'string') {
                this.container = document.querySelector(this.config.container);
            } else {
                this.container = this.config.container;
            }
            
            if (!this.container) {
                throw new Error(`Contenedor Kindle no encontrado: ${this.config.container}`);
            }
            
            // Preparar contenedor
            this.container.classList.add('ultra-realistic-kindle-container');
            this.container.setAttribute('data-kindle-version', '2.0');
            this.container.setAttribute('data-device-type', this.config.deviceType);
            
            // Detectar capacidades del dispositivo
            this.detectDeviceCapabilities();
        }
        
        /**
         * Detectar capacidades del dispositivo usuario
         */
        detectDeviceCapabilities() {
            const capabilities = {
                touchSupport: 'ontouchstart' in window,
                devicePixelRatio: window.devicePixelRatio || 1,
                screenSize: {
                    width: window.screen.width,
                    height: window.screen.height
                },
                isMobile: /Mobi|Android/i.test(navigator.userAgent),
                isTablet: /iPad|Android.*Tablet/i.test(navigator.userAgent),
                prefersDark: window.matchMedia('(prefers-color-scheme: dark)').matches
            };
            
            this.deviceCapabilities = capabilities;
            console.log('🔍 Capacidades detectadas:', capabilities);
        }

        /**
         * Crear interfaz ultra realista del Kindle
         */
        async createRealisticInterface() {
            console.log('🎨 Creando interfaz ultra realista...');
            
            this.container.innerHTML = `
                <div class="ultra-realistic-kindle" 
                     data-device="${this.config.deviceType}"
                     data-screen="${this.config.screenSize}"
                     data-theme="${this.config.theme}"
                     data-orientation="${this.config.orientation}">
                     
                    <!-- Marco físico del Kindle -->
                    <div class="kindle-frame">
                        <!-- Pantalla E-ink realista -->
                        <div class="kindle-screen">
                            <!-- Status bar superior -->
                            <div class="kindle-statusbar">
                                <div class="statusbar-left">
                                    <span class="book-title" id="status-book-title">Mi Biblioteca</span>
                                </div>
                                <div class="statusbar-right">
                                    <span class="wifi-icon" id="wifi-status">📶</span>
                                    <span class="sync-icon" id="sync-status">🔄</span>
                                    <span class="battery-icon" id="battery-status">🔋</span>
                                    <span class="battery-level" id="battery-level">87%</span>
                                </div>
                            </div>
                            
                            <!-- Área principal de lectura -->
                            <div class="kindle-reading-area">
                                <!-- Contenido del libro -->
                                <div class="book-content" id="book-content">
                                    <div class="page-text" id="page-text">
                                        <div class="loading-animation">
                                            <div class="kindle-loading-text">Cargando libro...</div>
                                            <div class="kindle-progress-dots">
                                                <span></span><span></span><span></span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- Zonas táctiles invisibles -->
                                <div class="touch-zones">
                                    <div class="touch-zone touch-left" data-action="prev-page"></div>
                                    <div class="touch-zone touch-center" data-action="menu"></div>
                                    <div class="touch-zone touch-right" data-action="next-page"></div>
                                </div>
                            </div>
                            
                            <!-- Barra de progreso de lectura -->
                            <div class="reading-progress-area">
                                <div class="progress-bar-container">
                                    <div class="progress-bar" id="reading-progress">
                                        <div class="progress-fill" id="progress-fill"></div>
                                    </div>
                                </div>
                                
                                <!-- Información de página y tiempo -->
                                <div class="page-info">
                                    <div class="page-info-left">
                                        <span class="current-page" id="current-page">1</span>
                                        <span class="page-separator"> de </span>
                                        <span class="total-pages" id="total-pages">--</span>
                                    </div>
                                    <div class="page-info-center">
                                        <span class="chapter-info" id="chapter-info"></span>
                                    </div>
                                    <div class="page-info-right">
                                        <span class="reading-time" id="reading-time"></span>
                                        <span class="current-time" id="current-time"></span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Botones físicos (para modelos que los tienen) -->
                        <div class="physical-buttons" style="display: ${this.config.hasPhysicalButtons ? 'flex' : 'none'}">
                            <button class="physical-btn btn-prev" id="physical-prev">
                                <span class="btn-icon">◀</span>
                            </button>
                            <button class="physical-btn btn-next" id="physical-next">
                                <span class="btn-icon">▶</span>
                            </button>
                        </div>
                    </div>
                    
                    <!-- Menú principal (overlay) -->
                    <div class="kindle-main-menu" id="main-menu">
                        <div class="menu-header">
                            <h3>Configuración de Lectura</h3>
                            <button class="menu-close" id="menu-close">✕</button>
                        </div>
                        
                        <div class="menu-content">
                            <!-- Controles de fuente -->
                            <div class="menu-section font-controls">
                                <h4>Texto</h4>
                                <div class="font-family-selector">
                                    <button class="font-btn active" data-font="Bookerly">Bookerly</button>
                                    <button class="font-btn" data-font="OpenDyslexic">OpenDyslexic</button>
                                    <button class="font-btn" data-font="Caecilia">Caecilia</button>
                                    <button class="font-btn" data-font="Ember">Ember</button>
                                </div>
                                
                                <div class="font-size-slider">
                                    <label>Tamaño</label>
                                    <div class="size-controls">
                                        <button class="size-btn" id="font-decrease">A-</button>
                                        <div class="size-indicator" id="font-size-indicator">
                                            <span class="size-dot" data-size="1"></span>
                                            <span class="size-dot" data-size="2"></span>
                                            <span class="size-dot active" data-size="3"></span>
                                            <span class="size-dot" data-size="4"></span>
                                            <span class="size-dot" data-size="5"></span>
                                            <span class="size-dot" data-size="6"></span>
                                            <span class="size-dot" data-size="7"></span>
                                            <span class="size-dot" data-size="8"></span>
                                        </div>
                                        <button class="size-btn" id="font-increase">A+</button>
                                    </div>
                                </div>
                                
                                <div class="text-options">
                                    <div class="option-row">
                                        <label>Espaciado</label>
                                        <div class="spacing-controls">
                                            <button class="spacing-btn" data-spacing="0">○</button>
                                            <button class="spacing-btn active" data-spacing="1">○</button>
                                            <button class="spacing-btn" data-spacing="2">○</button>
                                            <button class="spacing-btn" data-spacing="3">○</button>
                                        </div>
                                    </div>
                                    
                                    <div class="option-row">
                                        <label>Márgenes</label>
                                        <div class="margin-controls">
                                            <button class="margin-btn" data-margin="0">□</button>
                                            <button class="margin-btn active" data-margin="1">□</button>
                                            <button class="margin-btn" data-margin="2">□</button>
                                            <button class="margin-btn" data-margin="3">□</button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Controles de tema y brillo -->
                            <div class="menu-section theme-controls">
                                <h4>Pantalla</h4>
                                <div class="theme-selector">
                                    <button class="theme-option active" data-theme="white">
                                        <div class="theme-preview theme-white"></div>
                                        <span>Blanco</span>
                                    </button>
                                    <button class="theme-option" data-theme="sepia">
                                        <div class="theme-preview theme-sepia"></div>
                                        <span>Sepia</span>
                                    </button>
                                    <button class="theme-option" data-theme="dark">
                                        <div class="theme-preview theme-dark"></div>
                                        <span>Negro</span>
                                    </button>
                                </div>
                                
                                <div class="brightness-control">
                                    <label>Brillo</label>
                                    <div class="brightness-slider">
                                        <span class="brightness-icon">☀️</span>
                                        <input type="range" id="brightness-range" min="1" max="24" value="8">
                                        <span class="brightness-value" id="brightness-value">8</span>
                                    </div>
                                </div>
                                
                                <div class="warmth-control">
                                    <label>Luz Cálida</label>
                                    <div class="warmth-slider">
                                        <span class="warmth-icon">🔆</span>
                                        <input type="range" id="warmth-range" min="1" max="24" value="10">
                                        <span class="warmth-value" id="warmth-value">10</span>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Navegación y opciones -->
                            <div class="menu-section navigation-controls">
                                <h4>Navegación</h4>
                                <div class="nav-buttons">
                                    <button class="nav-btn" id="go-to-page">
                                        <span class="nav-icon">📄</span>
                                        <span>Ir a página</span>
                                    </button>
                                    <button class="nav-btn" id="table-of-contents">
                                        <span class="nav-icon">📚</span>
                                        <span>Índice</span>
                                    </button>
                                    <button class="nav-btn" id="bookmarks">
                                        <span class="nav-icon">🔖</span>
                                        <span>Marcadores</span>
                                    </button>
                                    <button class="nav-btn" id="search-book">
                                        <span class="nav-icon">🔍</span>
                                        <span>Buscar</span>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Efectos e-ink -->
                    <div class="kindle-eink-overlay" id="eink-overlay"></div>
                </div>
            `;
        }

        /**
         * Cache completo de elementos DOM
         */
        cacheAllElements() {
            const kindle = this.container.querySelector('.ultra-realistic-kindle');
            
            this.elements = {
                // Elementos principales
                kindle: kindle,
                frame: kindle.querySelector('.kindle-frame'),
                screen: kindle.querySelector('.kindle-screen'),
                
                // Status bar
                statusBar: kindle.querySelector('.kindle-statusbar'),
                bookTitle: kindle.querySelector('#status-book-title'),
                wifiStatus: kindle.querySelector('#wifi-status'),
                syncStatus: kindle.querySelector('#sync-status'),
                batteryStatus: kindle.querySelector('#battery-status'),
                batteryLevel: kindle.querySelector('#battery-level'),
                
                // Área de lectura
                readingArea: kindle.querySelector('.kindle-reading-area'),
                bookContent: kindle.querySelector('#book-content'),
                pageText: kindle.querySelector('#page-text'),
                
                // Zonas táctiles
                touchZones: {
                    left: kindle.querySelector('.touch-left'),
                    center: kindle.querySelector('.touch-center'),
                    right: kindle.querySelector('.touch-right')
                },
                
                // Progreso e información
                progressArea: kindle.querySelector('.reading-progress-area'),
                progressBar: kindle.querySelector('#reading-progress'),
                progressFill: kindle.querySelector('#progress-fill'),
                currentPage: kindle.querySelector('#current-page'),
                totalPages: kindle.querySelector('#total-pages'),
                chapterInfo: kindle.querySelector('#chapter-info'),
                readingTime: kindle.querySelector('#reading-time'),
                currentTime: kindle.querySelector('#current-time'),
                
                // Menú principal
                mainMenu: kindle.querySelector('#main-menu'),
                menuClose: kindle.querySelector('#menu-close'),
                
                // Controles de fuente
                fontButtons: kindle.querySelectorAll('.font-btn'),
                fontDecrease: kindle.querySelector('#font-decrease'),
                fontIncrease: kindle.querySelector('#font-increase'),
                fontSizeIndicator: kindle.querySelector('#font-size-indicator'),
                sizeDots: kindle.querySelectorAll('.size-dot'),
                
                // Controles de espaciado y márgenes
                spacingButtons: kindle.querySelectorAll('.spacing-btn'),
                marginButtons: kindle.querySelectorAll('.margin-btn'),
                
                // Controles de tema
                themeOptions: kindle.querySelectorAll('.theme-option'),
                brightnessRange: kindle.querySelector('#brightness-range'),
                brightnessValue: kindle.querySelector('#brightness-value'),
                warmthRange: kindle.querySelector('#warmth-range'),
                warmthValue: kindle.querySelector('#warmth-value'),
                
                // Navegación
                goToPageBtn: kindle.querySelector('#go-to-page'),
                tocBtn: kindle.querySelector('#table-of-contents'),
                bookmarksBtn: kindle.querySelector('#bookmarks'),
                searchBtn: kindle.querySelector('#search-book'),
                
                // Efectos
                einkOverlay: kindle.querySelector('#eink-overlay')
            };
            
            console.log('📦 Elementos DOM cacheados:', Object.keys(this.elements).length);
        }

        /**
         * Medir pantalla como Kindle real
         */
        measureKindleScreen() {
            const screenElement = this.elements.screen;
            if (!screenElement) return;

            // Obtener dimensiones reales de la pantalla Kindle
            const rect = screenElement.getBoundingClientRect();
            const styles = window.getComputedStyle(screenElement);
            
            // Calcular área de lectura efectiva
            const padding = {
                left: parseFloat(styles.paddingLeft) || 0,
                right: parseFloat(styles.paddingRight) || 0,
                top: parseFloat(styles.paddingTop) || 0,
                bottom: parseFloat(styles.paddingBottom) || 0
            };

            // Dimensiones de la pantalla Kindle
            this.state.screenWidth = rect.width;
            this.state.screenHeight = rect.height;
            
            // Área efectiva para texto (descontando status bar, progress bar, etc.)
            this.state.textAreaWidth = rect.width - padding.left - padding.right;
            this.state.textAreaHeight = rect.height - padding.top - padding.bottom - 80; // Status bar y progress
            
            // Simular características del e-ink
            this.state.pixelDensity = this.state.dpi;
            this.state.refreshRate = 85; // ms para simular e-ink refresh
            
            // Calcular dimensiones basadas en dispositivo
            const deviceSpecs = this.getDeviceSpecs();
            this.state.physicalWidth = deviceSpecs.width;
            this.state.physicalHeight = deviceSpecs.height;

            console.log('📐 Pantalla Kindle medida:', {
                screen: `${this.state.screenWidth}x${this.state.screenHeight}`,
                textArea: `${this.state.textAreaWidth}x${this.state.textAreaHeight}`,
                device: this.config.deviceType,
                dpi: this.state.dpi
            });
        }
        
        /**
         * Obtener especificaciones del dispositivo Kindle
         */
        getDeviceSpecs() {
            const specs = {
                'paperwhite': {
                    width: 1072, height: 1448, // píxeles reales Kindle Paperwhite
                    physicalWidth: 6.9, physicalHeight: 4.6 // pulgadas
                },
                'oasis': {
                    width: 1264, height: 1680,
                    physicalWidth: 6.3, physicalHeight: 4.3
                },
                'basic': {
                    width: 800, height: 600,
                    physicalWidth: 6.0, physicalHeight: 4.3
                }
            };
            
            return specs[this.config.deviceType] || specs['paperwhite'];
        }

        /**
         * Procesar contenido del libro con algoritmos avanzados
         */
        async processBookContent() {
            console.log('📚 Procesando contenido del libro con algoritmos avanzados...');
            
            if (!this.config.content) {
                console.warn('⚠️ No hay contenido para procesar');
                this.book.pages = [{
                    content: '<div class="no-content">📚<br><br>No hay contenido disponible<br><br>Selecciona otro libro</div>',
                    type: 'empty',
                    pageNumber: 1
                }];
                return;
            }

            // 1. Analizar estructura del libro
            await this.analyzeBookStructure();
            
            // 2. Detectar capítulos y secciones
            await this.detectChaptersAndSections();
            
            // 3. Procesar tabla de contenidos
            await this.generateTableOfContents();
            
            // 4. Crear paginación inteligente tipo Kindle
            await this.createKindleStylePagination();
            
            // 5. Generar índices de búsqueda
            await this.buildSearchIndex();
            
            console.log('✅ Libro procesado completamente:');
            console.log(`   📄 ${this.book.pages.length} páginas`);
            console.log(`   📖 ${this.book.chapters.length} capítulos`);
            console.log(`   🗂️ ${this.book.tableOfContents.length} entradas en índice`);
        }

        /**
         * Analizar estructura del libro
         */
        async analyzeBookStructure() {
            const content = this.config.content;
            
            // Extraer metadatos del libro
            const titleMatch = content.match(/^#\s+(.+)$/m);
            this.state.bookTitle = titleMatch ? titleMatch[1] : 'Libro sin título';
            
            // Detectar autor si está presente
            const authorMatch = content.match(/autor[:\s]*([^\n]+)/i);
            this.state.bookAuthor = authorMatch ? authorMatch[1].trim() : 'Autor desconocido';
            
            // Calcular estadísticas básicas
            this.book.totalWords = content.split(/\s+/).length;
            this.book.totalCharacters = content.length;
            this.book.estimatedReadingTime = Math.ceil(this.book.totalWords / this.state.wordsPerMinute);
            
            // Actualizar status bar
            if (this.elements.bookTitle) {
                this.elements.bookTitle.textContent = this.state.bookTitle;
            }
            
            console.log('📊 Estructura del libro:', {
                title: this.state.bookTitle,
                author: this.state.bookAuthor,
                words: this.book.totalWords,
                estimatedTime: `${this.book.estimatedReadingTime} min`
            });
        }

        /**
         * Detectar capítulos y secciones
         */
        async detectChaptersAndSections() {
            const content = this.config.content;
            this.book.chapters = [];
            
            // Patrones para detectar capítulos
            const chapterPatterns = [
                /^#{1,2}\s+(.+)$/gm, // Markdown headers
                /^capítulo\s+\d+[:\s]*(.+)$/gmi, // Capítulo X: Título
                /^\d+\.\s+(.+)$/gm, // 1. Título
                /^[A-ZÁÉÍÓÚ]{2,}[^a-z]*$/gm // TÍTULOS EN MAYÚSCULAS
            ];
            
            let chapterIndex = 0;
            let currentPosition = 0;
            
            for (const pattern of chapterPatterns) {
                let match;
                const matches = [];
                
                while ((match = pattern.exec(content)) !== null) {
                    matches.push({
                        title: match[1] || match[0],
                        position: match.index,
                        fullMatch: match[0]
                    });
                }
                
                // Procesar matches encontrados
                for (let i = 0; i < matches.length; i++) {
                    const current = matches[i];
                    const next = matches[i + 1];
                    
                    const chapterContent = content.substring(
                        current.position,
                        next ? next.position : content.length
                    );
                    
                    this.book.chapters.push({
                        id: `chapter-${chapterIndex}`,
                        title: current.title.trim(),
                        content: chapterContent,
                        startPosition: current.position,
                        endPosition: next ? next.position : content.length,
                        wordCount: chapterContent.split(/\s+/).length,
                        estimatedPages: Math.ceil(chapterContent.split(/\s+/).length / 250),
                        chapterNumber: chapterIndex + 1
                    });
                    
                    chapterIndex++;
                }
                
                if (matches.length > 0) break; // Usar el primer patrón que encuentre capítulos
            }
            
            // Si no se detectaron capítulos, crear uno genérico
            if (this.book.chapters.length === 0) {
                this.book.chapters.push({
                    id: 'chapter-0',
                    title: 'Contenido principal',
                    content: content,
                    startPosition: 0,
                    endPosition: content.length,
                    wordCount: this.book.totalWords,
                    estimatedPages: Math.ceil(this.book.totalWords / 250),
                    chapterNumber: 1
                });
            }
            
            this.state.totalChapters = this.book.chapters.length;
        }

        /**
         * Generar tabla de contenidos
         */
        async generateTableOfContents() {
            this.book.tableOfContents = [];
            
            for (let i = 0; i < this.book.chapters.length; i++) {
                const chapter = this.book.chapters[i];
                this.book.tableOfContents.push({
                    id: chapter.id,
                    title: chapter.title,
                    chapterNumber: i + 1,
                    pageNumber: null, // Se calculará después de la paginación
                    level: 1
                });
            }
        }

        /**
         * Crear paginación estilo Kindle
         */
        async createKindleStylePagination() {
            this.book.pages = [];
            
            // Calcular caracteres por página basado en configuración
            const pageLayout = this.calculatePageLayout();
            
            let pageNumber = 1;
            let globalPosition = 0;
            
            for (const chapter of this.book.chapters) {
                const chapterStartPage = pageNumber;
                const chapterPages = this.paginateChapterContent(chapter, pageLayout, pageNumber);
                
                // Actualizar número de página de inicio del capítulo en TOC
                const tocEntry = this.book.tableOfContents.find(t => t.id === chapter.id);
                if (tocEntry) {
                    tocEntry.pageNumber = chapterStartPage;
                }
                
                this.book.pages.push(...chapterPages);
                pageNumber += chapterPages.length;
            }
            
            this.state.totalPages = this.book.pages.length;
            
            // Actualizar elementos DOM
            if (this.elements.totalPages) {
                this.elements.totalPages.textContent = this.state.totalPages;
            }
        }

        /**
         * Calcular layout de página tipo Kindle
         */
        calculatePageLayout() {
            const fontSize = this.getFontSizeInPixels();
            const lineHeight = fontSize * 1.35; // Factor Kindle
            const margins = this.getMarginsInPixels();
            
            const effectiveWidth = this.state.textAreaWidth - (margins.left + margins.right);
            const effectiveHeight = this.state.textAreaHeight - (margins.top + margins.bottom);
            
            // Cálculos basados en fuente Bookerly
            const avgCharWidth = fontSize * 0.55; // Factor específico para Bookerly
            const charsPerLine = Math.floor(effectiveWidth / avgCharWidth);
            const linesPerPage = Math.floor(effectiveHeight / lineHeight);
            
            return {
                charsPerLine: Math.max(30, charsPerLine),
                linesPerPage: Math.max(10, linesPerPage),
                wordsPerPage: Math.max(100, Math.floor(charsPerLine * linesPerPage / 5.5)),
                effectiveWidth,
                effectiveHeight,
                fontSize,
                lineHeight,
                margins
            };
        }

        /**
         * Paginar contenido de capítulo
         */
        paginateChapterContent(chapter, layout, startPageNumber) {
            const pages = [];
            const paragraphs = chapter.content.split(/\n\s*\n/).filter(p => p.trim());
            
            let currentPageContent = '';
            let currentWordCount = 0;
            let pageNumber = startPageNumber;
            
            for (const paragraph of paragraphs) {
                const paragraphWords = paragraph.trim().split(/\s+/).length;
                const testContent = currentPageContent + (currentPageContent ? '\n\n' : '') + paragraph;
                const testWordCount = testContent.trim().split(/\s+/).length;
                
                if (testWordCount <= layout.wordsPerPage && this.fitsInKindlePage(testContent, layout)) {
                    currentPageContent = testContent;
                    currentWordCount = testWordCount;
                } else {
                    // Crear nueva página
                    if (currentPageContent.trim()) {
                        pages.push(this.createKindlePage(
                            currentPageContent,
                            pageNumber,
                            chapter,
                            layout
                        ));
                        pageNumber++;
                    }
                    
                    // Manejar párrafos muy largos
                    if (paragraphWords > layout.wordsPerPage) {
                        const splitParagraphs = this.splitLongParagraph(paragraph, layout);
                        for (const splitPart of splitParagraphs) {
                            pages.push(this.createKindlePage(
                                splitPart,
                                pageNumber,
                                chapter,
                                layout
                            ));
                            pageNumber++;
                        }
                        currentPageContent = '';
                        currentWordCount = 0;
                    } else {
                        currentPageContent = paragraph;
                        currentWordCount = paragraphWords;
                    }
                }
            }
            
            // Agregar última página
            if (currentPageContent.trim()) {
                pages.push(this.createKindlePage(
                    currentPageContent,
                    pageNumber,
                    chapter,
                    layout
                ));
            }
            
            return pages;
        }

        /**
         * Crear página estilo Kindle
         */
        createKindlePage(content, pageNumber, chapter, layout) {
            // Formatear contenido con estilos Kindle
            const formattedContent = this.formatKindleContent(content);
            
            return {
                id: `page-${pageNumber}`,
                content: formattedContent,
                rawContent: content,
                pageNumber: pageNumber,
                chapter: chapter,
                wordCount: content.trim().split(/\s+/).length,
                estimatedReadingTime: Math.ceil(content.trim().split(/\s+/).length / this.state.wordsPerMinute),
                type: 'text'
            };
        }

        /**
         * Formatear contenido estilo Kindle
         */
        formatKindleContent(content) {
            return content
                // Procesar encabezados
                .replace(/^#{1,2}\s+(.+)$/gm, '<h2 class="kindle-chapter-title">$1</h2>')
                // Procesar negritas
                .replace(/\*\*(.+?)\*\*/g, '<strong class="kindle-bold">$1</strong>')
                // Procesar cursivas
                .replace(/\*(.+?)\*/g, '<em class="kindle-italic">$1</em>')
                // Procesar párrafos
                .split(/\n\s*\n/)
                .map(paragraph => {
                    if (paragraph.trim() && !paragraph.startsWith('<h2')) {
                        return `<p class="kindle-paragraph">${paragraph.trim()}</p>`;
                    }
                    return paragraph;
                })
                .join('');
        }

        /**
         * Verificar si contenido cabe en página Kindle
         */
        fitsInKindlePage(content, layout) {
            const words = content.trim().split(/\s+/).length;
            const lines = Math.ceil(words / (layout.charsPerLine / 5.5));
            return lines <= layout.linesPerPage && words <= layout.wordsPerPage;
        }

        /**
         * Dividir párrafo largo
         */
        splitLongParagraph(paragraph, layout) {
            const sentences = paragraph.split(/([.!?]+\s)/).filter(s => s.trim());
            const parts = [];
            const maxWordsPerPart = Math.floor(layout.wordsPerPage * 0.9);
            
            let currentPart = '';
            let currentWords = 0;
            
            for (const sentence of sentences) {
                const sentenceWords = sentence.trim().split(/\s+/).length;
                
                if (currentWords + sentenceWords <= maxWordsPerPart) {
                    currentPart += sentence;
                    currentWords += sentenceWords;
                } else {
                    if (currentPart.trim()) {
                        parts.push(currentPart.trim());
                    }
                    currentPart = sentence;
                    currentWords = sentenceWords;
                }
            }
            
            if (currentPart.trim()) {
                parts.push(currentPart.trim());
            }
            
            return parts.length > 0 ? parts : [paragraph];
        }

        /**
         * Construir índice de búsqueda
         */
        async buildSearchIndex() {
            this.searchIndex = new Map();
            
            for (let i = 0; i < this.book.pages.length; i++) {
                const page = this.book.pages[i];
                const words = page.rawContent.toLowerCase().split(/\s+/);
                
                words.forEach((word, wordIndex) => {
                    const cleanWord = word.replace(/[^\w]/g, '');
                    if (cleanWord.length > 2) {
                        if (!this.searchIndex.has(cleanWord)) {
                            this.searchIndex.set(cleanWord, []);
                        }
                        this.searchIndex.get(cleanWord).push({
                            pageNumber: i + 1,
                            wordIndex: wordIndex,
                            context: words.slice(Math.max(0, wordIndex - 5), wordIndex + 6).join(' ')
                        });
                    }
                });
            }
            
            console.log(`🔍 Índice de búsqueda construido: ${this.searchIndex.size} palabras únicas`);
        }

        /**
         * Obtener tamaño de fuente en píxeles
         */
        getFontSizeInPixels() {
            const fontSizes = [12, 14, 16, 18, 20, 22, 24, 26]; // Escala Kindle
            return fontSizes[this.config.fontSize - 1] || 16;
        }
        
        /**
         * Obtener márgenes en píxeles
         */
        getMarginsInPixels() {
            const marginSets = [
                { top: 20, right: 15, bottom: 20, left: 15 }, // Pequeño
                { top: 25, right: 20, bottom: 25, left: 20 }, // Medio
                { top: 30, right: 25, bottom: 30, left: 25 }, // Grande
                { top: 35, right: 30, bottom: 35, left: 30 }  // Extra grande
            ];
            return marginSets[this.config.margins] || marginSets[1];
        }

        /**
         * Configurar eventos avanzados
         */
        setupAdvancedEvents() {
            console.log('⚙️ Configurando eventos avanzados...');
            
            // Eventos de navegación táctil
            this.setupTouchNavigation();
            
            // Eventos de teclado
            this.setupKeyboardNavigation();
            
            // Eventos de menú
            this.setupMenuEvents();
            
            // Eventos de configuración
            this.setupSettingsEvents();
            
            // Resize handler
            this.addEventListener(window, 'resize', this.debounce(this.handleResize, 300));
        }
        
        /**
         * Agregar event listener con tracking
         */
        addEventListener(element, event, handler) {
            element.addEventListener(event, handler);
            this.eventListeners.push({ element, event, handler });
        }

        /**
         * Configurar navegación táctil
         */
        setupTouchNavigation() {
            if (!this.deviceCapabilities.touchSupport) return;
            
            // Zonas táctiles
            this.addEventListener(this.elements.touchZones.left, 'click', this.previousPage);
            this.addEventListener(this.elements.touchZones.right, 'click', this.nextPage);
            this.addEventListener(this.elements.touchZones.center, 'click', this.openMenu);
            
            // Gestos de deslizamiento
            let startX = 0;
            let startTime = 0;
            
            this.addEventListener(this.elements.screen, 'touchstart', (e) => {
                startX = e.touches[0].clientX;
                startTime = Date.now();
            });
            
            this.addEventListener(this.elements.screen, 'touchend', (e) => {
                const endX = e.changedTouches[0].clientX;
                const endTime = Date.now();
                const deltaX = endX - startX;
                const deltaTime = endTime - startTime;
                
                if (Math.abs(deltaX) > 50 && deltaTime < 300) {
                    if (deltaX < 0) {
                        this.nextPage();
                    } else {
                        this.previousPage();
                    }
                }
            });
        }

        /**
         * Configurar navegación por teclado
         */
        setupKeyboardNavigation() {
            this.addEventListener(document, 'keydown', (e) => {
                if (!this.state.isInitialized || this.state.isMenuOpen) return;
                
                switch (e.key) {
                    case 'ArrowLeft':
                    case 'ArrowUp':
                    case 'PageUp':
                        e.preventDefault();
                        this.previousPage();
                        break;
                        
                    case 'ArrowRight':
                    case 'ArrowDown':
                    case 'PageDown':
                    case ' ':
                        e.preventDefault();
                        this.nextPage();
                        break;
                        
                    case 'Home':
                        e.preventDefault();
                        this.goToPage(0);
                        break;
                        
                    case 'End':
                        e.preventDefault();
                        this.goToPage(this.state.totalPages - 1);
                        break;
                        
                    case 'Escape':
                        this.closeAllPanels();
                        break;
                        
                    case 'm':
                    case 'M':
                        this.toggleMenu();
                        break;
                }
            });
        }

        /**
         * Configurar eventos de menú
         */
        setupMenuEvents() {
            this.addEventListener(this.elements.menuClose, 'click', this.closeMenu);
        }

        /**
         * Configurar eventos de configuración
         */
        setupSettingsEvents() {
            // Controles de fuente
            this.addEventListener(this.elements.fontDecrease, 'click', () => this.changeFontSize(-1));
            this.addEventListener(this.elements.fontIncrease, 'click', () => this.changeFontSize(1));
            
            // Controles de tema
            this.elements.themeOptions.forEach(btn => {
                this.addEventListener(btn, 'click', () => this.changeTheme(btn.dataset.theme));
            });
            
            // Sliders de brillo y luz cálida
            this.addEventListener(this.elements.brightnessRange, 'input', (e) => {
                this.changeBrightness(parseInt(e.target.value));
            });
            
            this.addEventListener(this.elements.warmthRange, 'input', (e) => {
                this.changeWarmth(parseInt(e.target.value));
            });
        }

        /**
         * Iniciar simulaciones realistas
         */
        startRealisticSimulations() {
            console.log('⚡ Iniciando simulaciones realistas...');
            
            // Actualizar reloj
            this.timers.clock = setInterval(this.updateClock, 60000); // Cada minuto
            this.updateClock(); // Inicial
            
            // Simular batería
            this.timers.battery = setInterval(this.simulateBattery, 300000); // Cada 5 minutos
            
            // Simular sincronización
            this.timers.sync = setInterval(this.simulateSync, 600000); // Cada 10 minutos
            
            // Efecto e-ink en transiciones
            this.setupEInkEffect();
        }
        
        /**
         * Detener simulaciones
         */
        stopRealisticSimulations() {
            Object.keys(this.timers).forEach(key => {
                if (this.timers[key]) {
                    clearInterval(this.timers[key]);
                    this.timers[key] = null;
                }
            });
        }

        /**
         * Actualizar reloj
         */
        updateClock() {
            this.state.currentTime = new Date();
            if (this.elements.currentTime) {
                this.elements.currentTime.textContent = this.state.currentTime.toLocaleTimeString('es-ES', { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                });
            }
        }

        /**
         * Simular batería
         */
        simulateBattery() {
            // Disminuir batería gradualmente
            if (Math.random() < 0.3) { // 30% de probabilidad cada 5 min
                this.state.batteryLevel = Math.max(5, this.state.batteryLevel - 1);
                if (this.elements.batteryLevel) {
                    this.elements.batteryLevel.textContent = `${this.state.batteryLevel}%`;
                }
            }
        }

        /**
         * Simular sincronización
         */
        simulateSync() {
            if (this.elements.syncStatus) {
                this.elements.syncStatus.style.opacity = '0.5';
                setTimeout(() => {
                    if (this.elements.syncStatus) {
                        this.elements.syncStatus.style.opacity = '1';
                    }
                }, 2000);
            }
        }

        /**
         * Configurar efecto e-ink
         */
        setupEInkEffect() {
            if (!this.config.eInkEffect) return;
            
            this.eInkOverlay = this.elements.einkOverlay;
        }

        /**
         * Mostrar primera página
         */
        async displayFirstPage() {
            await this.goToPage(0);
            console.log('📄 Primera página mostrada');
        }

        /**
         * Navegar a página siguiente
         */
        async nextPage() {
            if (this.state.currentPage < this.state.totalPages - 1 && !this.state.isTransitioning) {
                await this.goToPage(this.state.currentPage + 1, 'next');
            }
        }

        /**
         * Navegar a página anterior
         */
        async previousPage() {
            if (this.state.currentPage > 0 && !this.state.isTransitioning) {
                await this.goToPage(this.state.currentPage - 1, 'prev');
            }
        }

        /**
         * Ir a página específica
         */
        async goToPage(pageNumber, direction = 'next') {
            if (pageNumber < 0 || pageNumber >= this.state.totalPages || this.state.isTransitioning) {
                return;
            }
            
            this.state.isTransitioning = true;
            
            // Efecto e-ink
            if (this.config.eInkEffect) {
                await this.showEInkEffect();
            }
            
            // Actualizar página
            this.state.currentPage = pageNumber;
            
            // Encontrar capítulo actual
            const currentPageData = this.book.pages[pageNumber];
            if (currentPageData && currentPageData.chapter) {
                this.state.currentChapter = this.book.chapters.findIndex(ch => ch.id === currentPageData.chapter.id);
            }
            
            // Actualizar display
            this.updateKindleDisplay();
            
            // Actualizar progreso
            this.updateReadingProgress();
            
            this.state.isTransitioning = false;
            
            // Emitir evento
            this.emit('pageChanged', {
                currentPage: pageNumber + 1,
                totalPages: this.state.totalPages,
                direction: direction,
                chapter: currentPageData?.chapter?.title
            });
        }

        /**
         * Actualizar display del Kindle
         */
        updateKindleDisplay() {
            const currentPageData = this.book.pages[this.state.currentPage];
            if (!currentPageData) return;
            
            // Actualizar contenido
            if (this.elements.pageText) {
                this.elements.pageText.innerHTML = currentPageData.content;
            }
            
            // Actualizar números de página
            if (this.elements.currentPage) {
                this.elements.currentPage.textContent = this.state.currentPage + 1;
            }
            
            // Actualizar información de capítulo
            if (this.elements.chapterInfo && currentPageData.chapter) {
                this.elements.chapterInfo.textContent = currentPageData.chapter.title;
            }
            
            // Actualizar tiempo de lectura
            if (this.elements.readingTime) {
                this.elements.readingTime.textContent = `${currentPageData.estimatedReadingTime} min`;
            }
        }

        /**
         * Actualizar progreso de lectura
         */
        updateReadingProgress() {
            const progress = (this.state.currentPage / Math.max(1, this.state.totalPages - 1)) * 100;
            this.state.bookProgress = Math.round(progress);
            
            if (this.elements.progressFill) {
                this.elements.progressFill.style.width = `${progress}%`;
            }
        }

        /**
         * Mostrar efecto e-ink
         */
        async showEInkEffect() {
            if (!this.eInkOverlay) return;
            
            return new Promise(resolve => {
                this.eInkOverlay.classList.add('active');
                setTimeout(() => {
                    this.eInkOverlay.classList.remove('active');
                    resolve();
                }, this.state.refreshRate);
            });
        }

        /**
         * Abrir/cerrar menú
         */
        toggleMenu() {
            if (this.state.isMenuOpen) {
                this.closeMenu();
            } else {
                this.openMenu();
            }
        }

        /**
         * Abrir menú
         */
        openMenu() {
            this.state.isMenuOpen = true;
            this.elements.mainMenu.classList.add('visible');
            this.emit('menuOpened');
        }

        /**
         * Cerrar menú
         */
        closeMenu() {
            this.state.isMenuOpen = false;
            this.elements.mainMenu.classList.remove('visible');
            this.emit('menuClosed');
        }

        /**
         * Cerrar todos los paneles
         */
        closeAllPanels() {
            this.closeMenu();
        }

        /**
         * Cambiar tamaño de fuente
         */
        changeFontSize(delta) {
            const newSize = Math.max(1, Math.min(8, this.config.fontSize + delta));
            if (newSize !== this.config.fontSize) {
                this.config.fontSize = newSize;
                this.state.activeFontSize = newSize;
                this.updateFontSizeDisplay();
                this.reprocessAndRefresh();
                this.emit('fontSizeChanged', { fontSize: newSize });
            }
        }

        /**
         * Actualizar display de tamaño de fuente
         */
        updateFontSizeDisplay() {
            this.elements.sizeDots.forEach((dot, index) => {
                dot.classList.toggle('active', index + 1 === this.config.fontSize);
            });
            
            // Aplicar tamaño a la pantalla
            const fontSize = this.getFontSizeInPixels();
            this.elements.kindle.style.setProperty('--kindle-font-size', `${fontSize}px`);
        }

        /**
         * Cambiar tema
         */
        changeTheme(theme) {
            if (this.config.theme !== theme) {
                this.config.theme = theme;
                this.state.activeTheme = theme;
                this.elements.kindle.setAttribute('data-theme', theme);
                
                this.elements.themeOptions.forEach(option => {
                    option.classList.toggle('active', option.dataset.theme === theme);
                });
                
                this.emit('themeChanged', { theme });
            }
        }

        /**
         * Cambiar brillo
         */
        changeBrightness(brightness) {
            this.config.brightness = brightness;
            this.state.activeBrightness = brightness;
            this.elements.brightnessValue.textContent = brightness;
            this.elements.kindle.style.setProperty('--kindle-brightness', brightness / 24);
            this.emit('brightnessChanged', { brightness });
        }

        /**
         * Cambiar luz cálida
         */
        changeWarmth(warmth) {
            this.config.warmth = warmth;
            this.elements.warmthValue.textContent = warmth;
            this.elements.kindle.style.setProperty('--kindle-warmth', warmth / 24);
            this.emit('warmthChanged', { warmth });
        }

        /**
         * Reprocesar y refrescar
         */
        async reprocessAndRefresh() {
            const currentPage = this.state.currentPage;
            await this.createKindleStylePagination();
            const newPage = Math.min(currentPage, this.state.totalPages - 1);
            await this.goToPage(newPage);
        }

        /**
         * Manejar resize de ventana
         */
        handleResize() {
            if (!this.state.isInitialized) return;
            
            console.log('🔄 Recalculando por resize...');
            
            // Guardar posición actual
            const currentProgress = this.state.totalPages > 0 ? this.state.currentPage / this.state.totalPages : 0;
            
            // Remedir y recalcular
            this.measureKindleScreen();
            this.reprocessAndRefresh();
            
            // Restaurar posición aproximada
            const newPage = Math.min(
                Math.floor(currentProgress * this.state.totalPages),
                this.state.totalPages - 1
            );
            
            this.goToPage(newPage);
        }

        /**
         * Mostrar error crítico
         */
        showCriticalError(message) {
            this.container.innerHTML = `
                <div class="kindle-critical-error">
                    <div class="error-icon">⚠️</div>
                    <h3>Error del Sistema Kindle</h3>
                    <p>${message}</p>
                    <button onclick="location.reload()" class="error-reload-btn">
                        Reiniciar Sistema
                    </button>
                </div>
            `;
        }

        /**
         * Obtener estado completo del Kindle
         */
        getState() {
            const currentPageData = this.book.pages[this.state.currentPage];
            
            return {
                // Estado básico
                isInitialized: this.state.isInitialized,
                isLoading: this.state.isLoading,
                
                // Navegación
                currentPage: this.state.currentPage + 1, // Display 1-based
                totalPages: this.state.totalPages,
                currentChapter: this.state.currentChapter + 1,
                totalChapters: this.state.totalChapters,
                
                // Libro
                bookTitle: this.state.bookTitle,
                bookAuthor: this.state.bookAuthor,
                bookProgress: Math.round((this.state.currentPage / Math.max(1, this.state.totalPages - 1)) * 100),
                
                // Página actual
                currentPageData: currentPageData ? {
                    content: currentPageData.content,
                    chapter: currentPageData.chapter?.title,
                    wordCount: currentPageData.wordCount,
                    readingTime: currentPageData.estimatedReadingTime
                } : null,
                
                // Configuración
                fontSize: this.state.activeFontSize,
                fontFamily: this.state.activeFont,
                theme: this.state.activeTheme,
                brightness: this.state.activeBrightness,
                
                // Pantalla
                screenWidth: this.state.screenWidth,
                screenHeight: this.state.screenHeight,
                deviceType: this.config.deviceType,
                
                // Sistema
                batteryLevel: this.state.batteryLevel,
                wifiStatus: this.state.wifiStatus,
                currentTime: this.state.currentTime,
                
                // Estadísticas
                totalWords: this.book.totalWords,
                estimatedReadingTime: this.book.estimatedReadingTime,
                readingProgress: {
                    pagesRead: this.state.currentPage,
                    timeSpent: this.state.readingTime,
                    wordsPerMinute: this.state.wordsPerMinute
                }
            };
        }

        /**
         * Destruir Kindle completamente
         */
        destroy() {
            console.log('🗑️ Destruyendo Ultra Realistic Kindle...');
            
            // Detener simulaciones
            this.stopRealisticSimulations();
            
            // Limpiar timers
            Object.values(this.timers).forEach(timer => {
                if (timer) clearInterval(timer);
            });
            
            // Remover event listeners registrados
            this.eventListeners.forEach(({ element, event, handler }) => {
                element.removeEventListener(event, handler);
            });
            this.eventListeners = [];
            
            // Limpiar cache
            this.renderCache.clear();
            this.searchIndex.clear();
            
            // Limpiar contenedor
            if (this.container) {
                this.container.innerHTML = '';
                this.container.className = '';
            }
            
            // Reset estado
            this.state.isInitialized = false;
            this.book = { pages: [], chapters: [], tableOfContents: [], bookmarks: [], annotations: [], highlights: [], notes: [], vocabulary: [] };
            
            // Emitir evento de destrucción
            this.emit('kindleDestroyed', { timestamp: new Date() });
            
            console.log('✅ Ultra Realistic Kindle destruido completamente');
        }

        /**
         * Utility: debounce
         */
        debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func.apply(this, args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }

        /**
         * Emitir evento
         */
        emit(eventName, data = {}) {
            const event = new CustomEvent(`kindle:${eventName}`, {
                detail: { ...data, timestamp: new Date(), kindle: this },
                bubbles: true
            });
            this.container.dispatchEvent(event);
        }

        /**
         * Inyectar CSS avanzado
         */
        async injectAdvancedCSS() {
            if (document.getElementById('ultra-realistic-kindle-css')) return;

            const css = `
                <style id="ultra-realistic-kindle-css">
                    /* Variables CSS para configuraciones dinámicas */
                    .ultra-realistic-kindle {
                        --kindle-font-size: 16px;
                        --kindle-brightness: 0.33;
                        --kindle-warmth: 0.42;
                        --transition-duration: 0.15s;
                        --eink-refresh-time: 85ms;
                        
                        /* Colores por tema */
                        --bg-color: #ffffff;
                        --text-color: #1a1a1a;
                        --border-color: #e0e0e0;
                        --status-color: #666666;
                        --frame-color: #f5f5f5;
                        --button-color: #ffffff;
                        --shadow-color: rgba(0, 0, 0, 0.1);
                        --menu-bg: rgba(255, 255, 255, 0.98);
                        --overlay-bg: rgba(0, 0, 0, 0.5);
                        
                        font-family: system-ui, -apple-system, sans-serif;
                        position: relative;
                        width: 100%;
                        max-width: 800px;
                        margin: 0 auto;
                        user-select: none;
                        -webkit-user-select: none;
                        -moz-user-select: none;
                        -ms-user-select: none;
                    }
                    
                    /* Temas */
                    .ultra-realistic-kindle[data-theme="sepia"] {
                        --bg-color: #f4f1e8;
                        --text-color: #5c4b37;
                        --border-color: #d4c5a9;
                        --status-color: #8b7355;
                        --frame-color: #f0ebe0;
                    }
                    
                    .ultra-realistic-kindle[data-theme="dark"] {
                        --bg-color: #1a1a1a;
                        --text-color: #e5e5e5;
                        --border-color: #404040;
                        --status-color: #888888;
                        --frame-color: #2a2a2a;
                        --shadow-color: rgba(0, 0, 0, 0.3);
                        --menu-bg: rgba(42, 42, 42, 0.98);
                    }
                    
                    /* Marco físico del Kindle */
                    .kindle-frame {
                        background: linear-gradient(145deg, var(--frame-color), #fafafa);
                        border-radius: 20px;
                        padding: 25px;
                        box-shadow: 
                            0 10px 30px var(--shadow-color),
                            inset 0 1px 0 rgba(255, 255, 255, 0.5);
                        position: relative;
                        transform-style: preserve-3d;
                    }
                    
                    /* Pantalla E-ink */
                    .kindle-screen {
                        background: var(--bg-color);
                        border: 2px solid var(--border-color);
                        border-radius: 15px;
                        position: relative;
                        width: 100%;
                        height: 600px;
                        overflow: hidden;
                        filter: brightness(var(--kindle-brightness)) sepia(var(--kindle-warmth));
                        transition: filter var(--transition-duration) ease;
                    }
                    
                    /* Status bar */
                    .kindle-statusbar {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        padding: 12px 20px;
                        border-bottom: 1px solid var(--border-color);
                        font-size: 14px;
                        color: var(--status-color);
                        height: 20px;
                        background: var(--bg-color);
                    }
                    
                    .statusbar-left .book-title {
                        font-weight: 600;
                        max-width: 200px;
                        overflow: hidden;
                        text-overflow: ellipsis;
                        white-space: nowrap;
                    }
                    
                    .statusbar-right {
                        display: flex;
                        align-items: center;
                        gap: 8px;
                        font-size: 12px;
                    }
                    
                    .statusbar-right .battery-level {
                        font-weight: 600;
                    }
                    
                    /* Área de lectura */
                    .kindle-reading-area {
                        position: relative;
                        height: calc(100% - 120px);
                        background: var(--bg-color);
                    }
                    
                    .book-content {
                        height: 100%;
                        position: relative;
                        overflow: hidden;
                    }
                    
                    .page-text {
                        padding: 30px 25px;
                        height: 100%;
                        color: var(--text-color);
                        font-size: var(--kindle-font-size);
                        line-height: 1.4;
                        font-family: 'Bookerly', 'Georgia', serif;
                        text-align: justify;
                        text-justify: inter-word;
                        hyphens: auto;
                        -webkit-hyphens: auto;
                        -moz-hyphens: auto;
                        -ms-hyphens: auto;
                        position: relative;
                        transition: opacity var(--eink-refresh-time) ease;
                    }
                    
                    /* Estilos de contenido Kindle */
                    .kindle-chapter-title {
                        font-size: 1.3em;
                        font-weight: 700;
                        text-align: center;
                        margin: 0 0 1.5em 0;
                        color: var(--text-color);
                        text-indent: 0;
                        line-height: 1.2;
                    }
                    
                    .kindle-paragraph {
                        margin: 0 0 1em 0;
                        text-indent: 1.5em;
                        orphans: 2;
                        widows: 2;
                    }
                    
                    .kindle-paragraph:first-child,
                    .kindle-chapter-title + .kindle-paragraph {
                        text-indent: 0;
                    }
                    
                    .kindle-bold {
                        font-weight: 700;
                    }
                    
                    .kindle-italic {
                        font-style: italic;
                    }
                    
                    /* Animación de carga */
                    .loading-animation {
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        height: 100%;
                        color: var(--status-color);
                    }
                    
                    .kindle-loading-text {
                        font-size: 18px;
                        margin-bottom: 20px;
                        font-weight: 600;
                    }
                    
                    .kindle-progress-dots {
                        display: flex;
                        gap: 8px;
                    }
                    
                    .kindle-progress-dots span {
                        width: 8px;
                        height: 8px;
                        border-radius: 50%;
                        background: var(--status-color);
                        opacity: 0.3;
                        animation: kindle-loading 1.4s infinite ease-in-out both;
                    }
                    
                    .kindle-progress-dots span:nth-child(1) { animation-delay: -0.32s; }
                    .kindle-progress-dots span:nth-child(2) { animation-delay: -0.16s; }
                    .kindle-progress-dots span:nth-child(3) { animation-delay: 0s; }
                    
                    @keyframes kindle-loading {
                        0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
                        40% { opacity: 1; transform: scale(1); }
                    }
                    
                    /* Zonas táctiles invisibles */
                    .touch-zones {
                        position: absolute;
                        top: 0;
                        left: 0;
                        right: 0;
                        bottom: 0;
                        pointer-events: auto;
                        z-index: 10;
                    }
                    
                    .touch-zone {
                        position: absolute;
                        top: 0;
                        bottom: 0;
                        cursor: pointer;
                        transition: background-color 0.1s ease;
                    }
                    
                    .touch-left {
                        left: 0;
                        width: 30%;
                    }
                    
                    .touch-center {
                        left: 30%;
                        width: 40%;
                    }
                    
                    .touch-right {
                        right: 0;
                        width: 30%;
                    }
                    
                    .touch-zone:active {
                        background-color: rgba(128, 128, 128, 0.1);
                    }
                    
                    /* Área de progreso */
                    .reading-progress-area {
                        position: absolute;
                        bottom: 0;
                        left: 0;
                        right: 0;
                        height: 60px;
                        background: var(--bg-color);
                        border-top: 1px solid var(--border-color);
                        padding: 15px 20px;
                    }
                    
                    .progress-bar-container {
                        margin-bottom: 10px;
                    }
                    
                    .progress-bar {
                        width: 100%;
                        height: 3px;
                        background: var(--border-color);
                        border-radius: 2px;
                        overflow: hidden;
                    }
                    
                    .progress-fill {
                        height: 100%;
                        background: var(--text-color);
                        border-radius: 2px;
                        transition: width 0.3s ease;
                        opacity: 0.8;
                    }
                    
                    .page-info {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        font-size: 12px;
                        color: var(--status-color);
                        line-height: 1.2;
                    }
                    
                    .page-info-center {
                        max-width: 200px;
                        text-align: center;
                        overflow: hidden;
                        text-overflow: ellipsis;
                        white-space: nowrap;
                    }
                    
                    /* Menú principal */
                    .kindle-main-menu {
                        position: fixed;
                        top: 0;
                        left: 0;
                        right: 0;
                        bottom: 0;
                        background: var(--overlay-bg);
                        z-index: 1000;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        opacity: 0;
                        visibility: hidden;
                        transition: all 0.3s ease;
                        backdrop-filter: blur(5px);
                        -webkit-backdrop-filter: blur(5px);
                    }
                    
                    .kindle-main-menu.visible {
                        opacity: 1;
                        visibility: visible;
                    }
                    
                    .menu-header {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        padding: 20px;
                        border-bottom: 1px solid var(--border-color);
                        background: var(--menu-bg);
                        border-radius: 15px 15px 0 0;
                    }
                    
                    .menu-header h3 {
                        margin: 0;
                        font-size: 18px;
                        font-weight: 600;
                        color: var(--text-color);
                    }
                    
                    .menu-close {
                        background: none;
                        border: none;
                        font-size: 20px;
                        cursor: pointer;
                        color: var(--status-color);
                        padding: 5px;
                        border-radius: 50%;
                        transition: background-color 0.2s ease;
                    }
                    
                    .menu-close:hover {
                        background-color: var(--border-color);
                    }
                    
                    .menu-content {
                        background: var(--menu-bg);
                        border-radius: 0 0 15px 15px;
                        max-width: 500px;
                        width: 90%;
                        max-height: 80vh;
                        overflow-y: auto;
                        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
                    }
                    
                    .menu-section {
                        padding: 20px;
                        border-bottom: 1px solid var(--border-color);
                    }
                    
                    .menu-section:last-child {
                        border-bottom: none;
                        border-radius: 0 0 15px 15px;
                    }
                    
                    .menu-section h4 {
                        margin: 0 0 15px 0;
                        font-size: 16px;
                        font-weight: 600;
                        color: var(--text-color);
                    }
                    
                    /* Controles de fuente */
                    .font-family-selector {
                        display: flex;
                        gap: 8px;
                        margin-bottom: 20px;
                        flex-wrap: wrap;
                    }
                    
                    .font-btn {
                        padding: 8px 12px;
                        border: 1px solid var(--border-color);
                        background: var(--bg-color);
                        color: var(--text-color);
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 14px;
                        transition: all 0.2s ease;
                    }
                    
                    .font-btn:hover,
                    .font-btn.active {
                        background: var(--text-color);
                        color: var(--bg-color);
                    }
                    
                    .font-size-slider label {
                        display: block;
                        margin-bottom: 10px;
                        font-weight: 600;
                        color: var(--text-color);
                    }
                    
                    .size-controls {
                        display: flex;
                        align-items: center;
                        gap: 15px;
                    }
                    
                    .size-btn {
                        width: 40px;
                        height: 40px;
                        border: 1px solid var(--border-color);
                        background: var(--bg-color);
                        color: var(--text-color);
                        border-radius: 8px;
                        cursor: pointer;
                        font-weight: 700;
                        font-size: 16px;
                        transition: all 0.2s ease;
                    }
                    
                    .size-btn:hover {
                        background: var(--border-color);
                    }
                    
                    .size-indicator {
                        display: flex;
                        gap: 6px;
                        align-items: center;
                    }
                    
                    .size-dot {
                        width: 12px;
                        height: 12px;
                        border: 2px solid var(--border-color);
                        border-radius: 50%;
                        cursor: pointer;
                        transition: all 0.2s ease;
                    }
                    
                    .size-dot.active {
                        background: var(--text-color);
                        border-color: var(--text-color);
                    }
                    
                    /* Controles de tema */
                    .theme-selector {
                        display: flex;
                        gap: 15px;
                        margin-bottom: 20px;
                        justify-content: center;
                    }
                    
                    .theme-option {
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        gap: 8px;
                        padding: 10px;
                        border: 2px solid transparent;
                        border-radius: 8px;
                        cursor: pointer;
                        background: none;
                        color: var(--text-color);
                        transition: border-color 0.2s ease;
                    }
                    
                    .theme-option.active {
                        border-color: var(--text-color);
                    }
                    
                    .theme-preview {
                        width: 40px;
                        height: 30px;
                        border-radius: 4px;
                        border: 1px solid var(--border-color);
                    }
                    
                    .theme-white { background: #ffffff; }
                    .theme-sepia { background: #f4f1e8; }
                    .theme-dark { background: #1a1a1a; }
                    
                    .theme-option span {
                        font-size: 12px;
                        font-weight: 600;
                    }
                    
                    /* Controles de brillo */
                    .brightness-control,
                    .warmth-control {
                        margin-bottom: 15px;
                    }
                    
                    .brightness-control label,
                    .warmth-control label {
                        display: block;
                        margin-bottom: 8px;
                        font-weight: 600;
                        color: var(--text-color);
                    }
                    
                    .brightness-slider,
                    .warmth-slider {
                        display: flex;
                        align-items: center;
                        gap: 10px;
                    }
                    
                    .brightness-slider input,
                    .warmth-slider input {
                        flex: 1;
                        height: 6px;
                        border-radius: 3px;
                        outline: none;
                        background: var(--border-color);
                        -webkit-appearance: none;
                        appearance: none;
                    }
                    
                    .brightness-slider input::-webkit-slider-thumb,
                    .warmth-slider input::-webkit-slider-thumb {
                        -webkit-appearance: none;
                        appearance: none;
                        width: 18px;
                        height: 18px;
                        border-radius: 50%;
                        background: var(--text-color);
                        cursor: pointer;
                    }
                    
                    .brightness-value,
                    .warmth-value {
                        font-weight: 600;
                        min-width: 30px;
                        text-align: center;
                        color: var(--text-color);
                    }
                    
                    /* Botones de navegación */
                    .nav-buttons {
                        display: grid;
                        grid-template-columns: 1fr 1fr;
                        gap: 10px;
                    }
                    
                    .nav-btn {
                        display: flex;
                        align-items: center;
                        gap: 8px;
                        padding: 12px 16px;
                        border: 1px solid var(--border-color);
                        background: var(--bg-color);
                        color: var(--text-color);
                        border-radius: 8px;
                        cursor: pointer;
                        font-size: 14px;
                        transition: all 0.2s ease;
                        text-align: left;
                    }
                    
                    .nav-btn:hover {
                        background: var(--border-color);
                    }
                    
                    /* Efectos E-ink */
                    .kindle-eink-overlay {
                        position: absolute;
                        top: 0;
                        left: 0;
                        right: 0;
                        bottom: 0;
                        background: var(--bg-color);
                        opacity: 0;
                        visibility: hidden;
                        transition: opacity var(--eink-refresh-time) ease;
                        pointer-events: none;
                        z-index: 5;
                    }
                    
                    .kindle-eink-overlay.active {
                        opacity: 0.8;
                        visibility: visible;
                    }
                    
                    /* Error crítico */
                    .kindle-critical-error {
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        height: 400px;
                        text-align: center;
                        color: var(--text-color);
                        padding: 40px;
                    }
                    
                    .error-icon {
                        font-size: 48px;
                        margin-bottom: 20px;
                    }
                    
                    .kindle-critical-error h3 {
                        margin: 0 0 15px 0;
                        font-size: 24px;
                        color: var(--text-color);
                    }
                    
                    .kindle-critical-error p {
                        margin: 0 0 25px 0;
                        color: var(--status-color);
                        max-width: 400px;
                    }
                    
                    .error-reload-btn {
                        padding: 12px 24px;
                        background: var(--text-color);
                        color: var(--bg-color);
                        border: none;
                        border-radius: 8px;
                        font-size: 16px;
                        font-weight: 600;
                        cursor: pointer;
                        transition: opacity 0.2s ease;
                    }
                    
                    .error-reload-btn:hover {
                        opacity: 0.8;
                    }
                    
                    /* Contenido vacío */
                    .no-content {
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        height: 100%;
                        text-align: center;
                        color: var(--status-color);
                        font-size: 18px;
                        line-height: 1.6;
                    }
                    
                    /* Responsive Design */
                    @media (max-width: 768px) {
                        .ultra-realistic-kindle {
                            max-width: 100%;
                            margin: 0;
                        }
                        
                        .kindle-frame {
                            padding: 15px;
                            border-radius: 15px;
                        }
                        
                        .kindle-screen {
                            height: 500px;
                            border-radius: 10px;
                        }
                        
                        .page-text {
                            padding: 20px 15px;
                            font-size: calc(var(--kindle-font-size) * 0.9);
                        }
                        
                        .statusbar-left .book-title {
                            max-width: 150px;
                        }
                        
                        .menu-content {
                            width: 95%;
                        }
                        
                        .nav-buttons {
                            grid-template-columns: 1fr;
                        }
                        
                        .theme-selector {
                            flex-direction: column;
                            align-items: center;
                        }
                        
                        .font-family-selector {
                            justify-content: center;
                        }
                    }
                    
                    @media (max-width: 480px) {
                        .kindle-screen {
                            height: 400px;
                        }
                        
                        .page-text {
                            padding: 15px 10px;
                        }
                        
                        .statusbar-left .book-title {
                            max-width: 120px;
                        }
                        
                        .page-info {
                            font-size: 11px;
                        }
                        
                        .page-info-center {
                            max-width: 120px;
                        }
                    }
                    
                    /* Animaciones adicionales */
                    @keyframes kindle-page-turn {
                        0% { transform: rotateY(0deg); opacity: 1; }
                        50% { transform: rotateY(-5deg); opacity: 0.8; }
                        100% { transform: rotateY(0deg); opacity: 1; }
                    }
                    
                    .kindle-page-turning .page-text {
                        animation: kindle-page-turn var(--eink-refresh-time) ease;
                    }
                </style>
            `;

            document.head.insertAdjacentHTML('beforeend', css);
        }
    }
    
    // Exportar plugin con compatibilidad
    global.UltraRealisticKindleReader = UltraRealisticKindleReader;
    global.KindleReaderPlugin = UltraRealisticKindleReader; // Compatibilidad hacia atrás

    // Auto-detección de elementos con atributo data-kindle
    document.addEventListener('DOMContentLoaded', () => {
        console.log('🔍 Buscando elementos con data-kindle...');
        
        const autoElements = document.querySelectorAll('[data-kindle]');
        console.log(`📦 Encontrados ${autoElements.length} elementos con data-kindle`);
        
        autoElements.forEach((element, index) => {
            console.log(`🚀 Inicializando Kindle Reader #${index + 1}...`);
            
            const content = element.dataset.kindleContent || element.textContent || '';
            const options = {
                container: element,
                content: content,
                fontSize: parseInt(element.dataset.kindleFontSize) || 3,
                theme: element.dataset.kindleTheme || 'white',
                deviceType: element.dataset.kindleDeviceType || 'paperwhite',
                screenSize: element.dataset.kindleScreenSize || 'large',
                eInkEffect: element.dataset.kindleEinkEffect !== 'false',
                pageFlipAnimation: element.dataset.kindlePageFlip !== 'false'
            };
            
            console.log('⚙️ Opciones de configuración:', options);
            
            try {
                const kindle = new UltraRealisticKindleReader(options);
                
                // Inicializar con timeout para debug
                const initPromise = kindle.init();
                
                // Guardar referencia inmediatamente
                element.kindleInstance = kindle;
                
                console.log(`✅ Kindle Reader #${index + 1} iniciado correctamente`);
                
            } catch (error) {
                console.error(`❌ Error inicializando Kindle Reader #${index + 1}:`, error);
            }
        });
        
        if (autoElements.length === 0) {
            console.warn('⚠️ No se encontraron elementos con data-kindle');
        }
    });

})(window);