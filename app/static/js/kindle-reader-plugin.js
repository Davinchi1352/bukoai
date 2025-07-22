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

    /**
     * Plugin principal del lector Kindle completamente rediseñado
     */
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
                
                console.log(`✅ Ultra Realistic Kindle inicializado:`);
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
                                
                                <!-- Overlay para selección de texto -->
                                <div class="text-selection-overlay" id="text-selection"></div>
                                
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
                                    <button class="font-btn" data-font="Bookerly">Bookerly</button>
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
                    
                    <!-- Panel de tabla de contenidos -->
                    <div class="toc-panel" id="toc-panel">
                        <div class="toc-header">
                            <h3>Tabla de Contenidos</h3>
                            <button class="toc-close" id="toc-close">✕</button>
                        </div>
                        <div class="toc-content" id="toc-content">
                            <div class="toc-loading">Generando índice...</div>
                        </div>
                    </div>
                    
                    <!-- Panel de marcadores -->
                    <div class="bookmarks-panel" id="bookmarks-panel">
                        <div class="bookmarks-header">
                            <h3>Marcadores</h3>
                            <button class="bookmarks-close" id="bookmarks-close">✕</button>
                        </div>
                        <div class="bookmarks-content" id="bookmarks-content">
                            <div class="no-bookmarks">No hay marcadores</div>
                        </div>
                    </div>
                    
                    <!-- Panel de búsqueda -->
                    <div class="search-panel" id="search-panel">
                        <div class="search-header">
                            <h3>Buscar en el libro</h3>
                            <button class="search-close" id="search-close">✕</button>
                        </div>
                        <div class="search-content">
                            <div class="search-input-container">
                                <input type="text" id="search-input" placeholder="Escribir término de búsqueda">
                                <button class="search-btn" id="search-btn">🔍</button>
                            </div>
                            <div class="search-results" id="search-results">
                                <div class="search-placeholder">Escribe para buscar</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Overlay de definición -->
                    <div class="definition-popup" id="definition-popup">
                        <div class="definition-content">
                            <div class="definition-word" id="definition-word"></div>
                            <div class="definition-text" id="definition-text"></div>
                            <div class="definition-actions">
                                <button class="def-btn" id="add-vocabulary">Agregar al vocabulario</button>
                                <button class="def-btn" id="close-definition">Cerrar</button>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Overlay de ir a página -->
                    <div class="goto-popup" id="goto-popup">
                        <div class="goto-content">
                            <h4>Ir a página</h4>
                            <div class="goto-input-container">
                                <input type="number" id="goto-input" min="1" max="1" placeholder="1">
                                <span class="goto-total">de <span id="goto-total-pages">--</span></span>
                            </div>
                            <div class="goto-actions">
                                <button class="goto-btn" id="goto-cancel">Cancelar</button>
                                <button class="goto-btn primary" id="goto-confirm">Ir</button>
                            </div>
                        </div>
                    </div>
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
                
                // Botones físicos
                physicalButtons: kindle.querySelector('.physical-buttons'),
                physicalPrev: kindle.querySelector('#physical-prev'),
                physicalNext: kindle.querySelector('#physical-next'),
                
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
                
                // Paneles
                tocPanel: kindle.querySelector('#toc-panel'),
                tocClose: kindle.querySelector('#toc-close'),
                tocContent: kindle.querySelector('#toc-content'),
                
                bookmarksPanel: kindle.querySelector('#bookmarks-panel'),
                bookmarksClose: kindle.querySelector('#bookmarks-close'),
                bookmarksContent: kindle.querySelector('#bookmarks-content'),
                
                searchPanel: kindle.querySelector('#search-panel'),
                searchClose: kindle.querySelector('#search-close'),
                searchInput: kindle.querySelector('#search-input'),
                searchBtnSearch: kindle.querySelector('#search-btn'),
                searchResults: kindle.querySelector('#search-results'),
                
                // Popups
                definitionPopup: kindle.querySelector('#definition-popup'),
                definitionWord: kindle.querySelector('#definition-word'),
                definitionText: kindle.querySelector('#definition-text'),
                addVocabulary: kindle.querySelector('#add-vocabulary'),
                closeDefinition: kindle.querySelector('#close-definition'),
                
                gotoPopup: kindle.querySelector('#goto-popup'),
                gotoInput: kindle.querySelector('#goto-input'),
                gotoTotalPages: kindle.querySelector('#goto-total-pages'),
                gotoCancel: kindle.querySelector('#goto-cancel'),
                gotoConfirm: kindle.querySelector('#goto-confirm'),
                
                // Selección de texto
                textSelection: kindle.querySelector('#text-selection')
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
            
            console.log(`✅ Libro procesado completamente:`);
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
            if (this.elements.gotoTotalPages) {
                this.elements.gotoTotalPages.textContent = this.state.totalPages;
            }
            if (this.elements.gotoInput) {
                this.elements.gotoInput.setAttribute('max', this.state.totalPages);
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
         * Detectar secciones en el contenido
         */
        detectSections() {
            this.sections = [];
            const content = this.config.content;

            // Buscar tabla de contenidos
            const tocMatch = content.match(/(tabla\s+de\s+contenidos|índice|table\s+of\s+contents)([\s\S]*?)(?=#{1,2}\s|\n\n[A-Z]|capítulo\s+\d+|\d+\.\s*[A-Z])/i);
            
            if (tocMatch) {
                this.sections.push({
                    type: 'toc',
                    title: 'Tabla de Contenidos',
                    content: tocMatch[0],
                    startPosition: tocMatch.index
                });
            }

            // Buscar capítulos
            const chapterRegex = /(#{1,2}\s+(.+)|capítulo\s+\d+[:\s]+(.+)|\d+\.\s*([A-Z].+))/gi;
            let match;
            
            while ((match = chapterRegex.exec(content)) !== null) {
                const title = match[2] || match[3] || match[4] || 'Capítulo';
                this.sections.push({
                    type: 'chapter',
                    title: title.trim(),
                    content: '', // Se llenará durante la paginación
                    startPosition: match.index
                });
            }

            // Si no hay secciones definidas, crear una genérica
            if (this.sections.length === 0) {
                this.sections.push({
                    type: 'content',
                    title: 'Contenido Principal',
                    content: content,
                    startPosition: 0
                });
            }

            console.log('📚 Secciones detectadas:', this.sections.map(s => s.title));
        }

        /**
         * Crear páginas con paginación inteligente
         */
        createPages() {
            this.pages = [];
            
            // Calcular límites de página
            const limits = this.calculatePageLimits();
            
            // Procesar cada sección
            for (const section of this.sections) {
                this.paginateSection(section, limits);
            }
        }

        /**
         * Calcular límites de página dinámicamente
         */
        calculatePageLimits() {
            const avgCharWidth = this.config.fontSize * 0.6; // Aproximación
            const lineHeight = this.config.fontSize * this.config.lineHeight;
            
            const charsPerLine = Math.floor(this.state.containerWidth / avgCharWidth);
            const linesPerPage = Math.floor(this.state.containerHeight / lineHeight) - 2; // Margen
            
            const maxCharsPerPage = charsPerLine * linesPerPage * 0.85; // Factor de seguridad
            const maxWordsPerPage = Math.floor(maxCharsPerPage / 5.5); // Promedio chars por palabra
            
            return {
                maxWordsPerPage: Math.max(50, Math.min(maxWordsPerPage, 500)),
                maxCharsPerPage: Math.max(200, Math.min(maxCharsPerPage, 3000)),
                linesPerPage: Math.max(5, linesPerPage),
                charsPerLine: Math.max(20, charsPerLine)
            };
        }

        /**
         * Paginar una sección específica
         */
        paginateSection(section, limits) {
            const sectionStart = this.pages.length;
            
            if (section.type === 'toc') {
                this.paginateTableOfContents(section, limits);
            } else {
                this.paginateTextContent(section, limits);
            }
            
            // Actualizar información de la sección
            section.startPage = sectionStart;
            section.endPage = this.pages.length - 1;
            section.totalPages = this.pages.length - sectionStart;
        }

        /**
         * Paginar tabla de contenidos
         */
        paginateTableOfContents(section, limits) {
            const lines = section.content.split('\n').filter(line => line.trim());
            const maxLinesPerPage = Math.floor(limits.linesPerPage * 0.8);
            
            let currentPageLines = [];
            let currentLineCount = 0;
            
            // Agregar header
            currentPageLines.push(`<div class="toc-header">${section.title}</div>`);
            currentLineCount = 2; // Header toma 2 líneas
            
            for (const line of lines) {
                if (currentLineCount >= maxLinesPerPage) {
                    // Crear nueva página
                    this.pages.push({
                        content: this.formatTOCPage(currentPageLines),
                        section: section,
                        type: 'toc'
                    });
                    
                    currentPageLines = [`<div class="toc-header">${section.title} (cont.)</div>`];
                    currentLineCount = 2;
                }
                
                currentPageLines.push(`<div class="toc-line">${this.escapeHtml(line)}</div>`);
                currentLineCount++;
            }
            
            // Agregar última página
            if (currentPageLines.length > 1) {
                this.pages.push({
                    content: this.formatTOCPage(currentPageLines),
                    section: section,
                    type: 'toc'
                });
            }
        }

        /**
         * Paginar contenido de texto
         */
        paginateTextContent(section, limits) {
            const paragraphs = section.content.split(/\n\s*\n/).filter(p => p.trim());
            
            let currentPageContent = '';
            let currentWordCount = 0;
            
            for (const paragraph of paragraphs) {
                const paragraphWords = this.countWords(paragraph);
                const testContent = currentPageContent + (currentPageContent ? '\n\n' : '') + paragraph;
                
                if (this.fitsInPage(testContent, limits) && 
                    currentWordCount + paragraphWords <= limits.maxWordsPerPage) {
                    
                    // Cabe en la página actual
                    currentPageContent = testContent;
                    currentWordCount += paragraphWords;
                } else {
                    // No cabe, crear nueva página
                    if (currentPageContent.trim()) {
                        this.pages.push({
                            content: this.formatTextPage(currentPageContent),
                            section: section,
                            type: 'text',
                            wordCount: currentWordCount
                        });
                    }
                    
                    // Manejar párrafos muy largos
                    if (paragraphWords > limits.maxWordsPerPage) {
                        const splitParts = this.splitLongParagraph(paragraph, limits);
                        for (const part of splitParts) {
                            this.pages.push({
                                content: this.formatTextPage(part),
                                section: section,
                                type: 'text',
                                wordCount: this.countWords(part)
                            });
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
                this.pages.push({
                    content: this.formatTextPage(currentPageContent),
                    section: section,
                    type: 'text',
                    wordCount: currentWordCount
                });
            }
        }

        /**
         * Verificar si el contenido cabe en una página
         */
        fitsInPage(content, limits) {
            const charCount = content.length;
            const wordCount = this.countWords(content);
            
            // Verificaciones básicas
            if (charCount > limits.maxCharsPerPage) return false;
            if (wordCount > limits.maxWordsPerPage) return false;
            
            // Estimar líneas
            const estimatedLines = Math.ceil(charCount / limits.charsPerLine) + 
                                 (content.match(/\n/g) || []).length;
            
            return estimatedLines <= limits.linesPerPage;
        }

        /**
         * Dividir párrafos largos inteligentemente
         */
        splitLongParagraph(paragraph, limits) {
            const sentences = paragraph.split(/([.!?]+\s+)/).filter(s => s.trim());
            const parts = [];
            const maxWordsPerPart = Math.floor(limits.maxWordsPerPage * 0.9);
            
            let currentPart = '';
            let currentWords = 0;
            
            for (const sentence of sentences) {
                const sentenceWords = this.countWords(sentence);
                
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
         * Contar palabras en un texto
         */
        countWords(text) {
            return text.trim().split(/\s+/).filter(word => word.length > 0).length;
        }

        /**
         * Formatear página de tabla de contenidos
         */
        formatTOCPage(lines) {
            return `<div class="toc-page">${lines.join('')}</div>`;
        }

        /**
         * Formatear página de texto
         */
        formatTextPage(content) {
            // Procesar markdown básico
            let formatted = content
                .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.+?)\*/g, '<em>$1</em>')
                .replace(/^#{1,2}\s+(.+)$/gm, '<h2 class="chapter-title">$1</h2>')
                .replace(/\n\n/g, '</p><p>')
                .replace(/^\s*<p>/, '<p>')
                .replace(/<\/p>\s*$/, '</p>');

            return `<div class="text-page">${formatted}</div>`;
        }

        /**
         * Escapar HTML
         */
        escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        /**
         * Setup de eventos
         */
        setupEvents() {
            // Botones de navegación
            this.elements.btnPrev?.addEventListener('click', this.previousPage);
            this.elements.btnNext?.addEventListener('click', this.nextPage);
            this.elements.btnMenu?.addEventListener('click', () => this.toggleSettings());

            // Controles de fuente
            this.elements.decreaseFont?.addEventListener('click', () => this.changeFontSize(-1));
            this.elements.increaseFont?.addEventListener('click', () => this.changeFontSize(1));

            // Botones de tema
            this.elements.themeButtons?.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    this.changeTheme(e.target.dataset.theme);
                });
            });

            // Gestos táctiles
            if (this.config.enableGestures) {
                this.setupTouchGestures();
            }

            // Navegación por teclado
            document.addEventListener('keydown', (e) => this.handleKeydown(e));

            // Resize handler
            window.addEventListener('resize', this.debounce(this.handleResize, 300));

            // Click en overlay para cerrar settings
            this.elements.touchOverlay?.addEventListener('click', () => this.hideSettings());
        }

        /**
         * Setup de gestos táctiles
         */
        setupTouchGestures() {
            let startX = 0;
            let startTime = 0;

            this.elements.screen?.addEventListener('touchstart', (e) => {
                startX = e.touches[0].clientX;
                startTime = Date.now();
            }, { passive: true });

            this.elements.screen?.addEventListener('touchend', (e) => {
                const endX = e.changedTouches[0].clientX;
                const endTime = Date.now();
                const deltaX = endX - startX;
                const deltaTime = endTime - startTime;

                // Verificar si es un swipe válido
                if (Math.abs(deltaX) > 50 && deltaTime < 300) {
                    if (deltaX < 0) {
                        this.nextPage(); // Swipe left = next page
                    } else {
                        this.previousPage(); // Swipe right = previous page
                    }
                }
            }, { passive: true });
        }

        /**
         * Manejar teclas
         */
        handleKeydown(e) {
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
                case 'Home':
                    e.preventDefault();
                    this.goToPage(0);
                    break;
                case 'End':
                    e.preventDefault();
                    this.goToPage(this.pages.length - 1);
                    break;
                case 'Escape':
                    this.hideSettings();
                    break;
            }
        }

        /**
         * Manejar resize de ventana
         */
        handleResize() {
            if (!this.state.isInitialized) return;

            console.log('🔄 Recalculando por resize...');
            
            // Guardar posición actual
            const currentProgress = this.pages.length > 0 ? this.state.currentPage / this.pages.length : 0;
            
            // Remedir y recalcular
            this.measureContainer();
            this.processContent();
            
            // Restaurar posición aproximada
            this.state.currentPage = Math.min(
                Math.floor(currentProgress * this.pages.length),
                this.pages.length - 1
            );
            
            this.updateDisplay();
        }

        /**
         * Navegar a página siguiente
         */
        nextPage() {
            if (this.state.currentPage < this.pages.length - 1 && !this.state.isTransitioning) {
                this.goToPage(this.state.currentPage + 1, 'next');
            }
        }

        /**
         * Navegar a página anterior
         */
        previousPage() {
            if (this.state.currentPage > 0 && !this.state.isTransitioning) {
                this.goToPage(this.state.currentPage - 1, 'prev');
            }
        }

        /**
         * Ir a página específica
         */
        goToPage(pageNumber, direction = 'next') {
            if (pageNumber < 0 || pageNumber >= this.pages.length || this.state.isTransitioning) {
                return;
            }

            this.state.isTransitioning = true;
            
            // Animación de transición
            this.animatePageTransition(direction, () => {
                this.state.currentPage = pageNumber;
                this.updateDisplay();
                this.state.isTransitioning = false;
                
                // Emitir evento
                this.emit('pageChanged', {
                    currentPage: this.state.currentPage,
                    totalPages: this.pages.length,
                    direction: direction
                });
            });

            // Sonido si está habilitado
            if (this.config.enableSounds) {
                this.playPageSound();
            }
        }

        /**
         * Animar transición de página
         */
        animatePageTransition(direction, callback) {
            const textElement = this.elements.text;
            if (!textElement) {
                callback();
                return;
            }

            // Aplicar clase de transición
            textElement.classList.add('transitioning', `transition-${direction}`);

            // Ejecutar callback después de la animación
            setTimeout(() => {
                callback();
                textElement.classList.remove('transitioning', `transition-${direction}`);
            }, 300);
        }

        /**
         * Actualizar display
         */
        updateDisplay() {
            const currentPage = this.pages[this.state.currentPage];
            if (!currentPage) return;

            // Actualizar contenido
            if (this.elements.text) {
                this.elements.text.innerHTML = currentPage.content;
            }

            // Actualizar información de página
            if (this.elements.pageNumber) {
                this.elements.pageNumber.textContent = this.state.currentPage + 1;
            }
            
            if (this.elements.totalPages) {
                this.elements.totalPages.textContent = this.pages.length;
            }

            // Actualizar progreso
            const progress = this.pages.length > 0 ? 
                ((this.state.currentPage + 1) / this.pages.length) * 100 : 0;
                
            if (this.elements.progressFill) {
                this.elements.progressFill.style.width = progress + '%';
            }

            // Actualizar información de sección
            if (this.elements.sectionInfo && currentPage.section) {
                this.elements.sectionInfo.textContent = currentPage.section.title;
            }

            // Actualizar estado de botones
            if (this.elements.btnPrev) {
                this.elements.btnPrev.disabled = this.state.currentPage === 0;
            }
            
            if (this.elements.btnNext) {
                this.elements.btnNext.disabled = this.state.currentPage >= this.pages.length - 1;
            }
        }

        /**
         * Cambiar tamaño de fuente
         */
        changeFontSize(delta) {
            const newSize = Math.max(12, Math.min(24, this.config.fontSize + delta));
            if (newSize !== this.config.fontSize) {
                this.config.fontSize = newSize;
                
                // Actualizar display
                if (this.elements.currentFontSize) {
                    this.elements.currentFontSize.textContent = newSize + 'px';
                }
                
                // Aplicar al plugin
                if (this.elements.plugin) {
                    this.elements.plugin.style.setProperty('--font-size', newSize + 'px');
                }
                
                // Recalcular páginas
                this.handleResize();
                
                this.emit('fontSizeChanged', { fontSize: newSize });
            }
        }

        /**
         * Cambiar tema
         */
        changeTheme(theme) {
            if (this.config.theme !== theme) {
                this.config.theme = theme;
                
                if (this.elements.plugin) {
                    this.elements.plugin.setAttribute('data-theme', theme);
                }
                
                // Actualizar estado de botones de tema
                this.elements.themeButtons?.forEach(btn => {
                    btn.classList.toggle('active', btn.dataset.theme === theme);
                });
                
                this.emit('themeChanged', { theme });
            }
        }

        /**
         * Toggle panel de configuración
         */
        toggleSettings() {
            const panel = this.elements.settingsPanel;
            if (!panel) return;

            const isVisible = panel.classList.contains('visible');
            
            if (isVisible) {
                this.hideSettings();
            } else {
                this.showSettings();
            }
        }

        /**
         * Mostrar configuración
         */
        showSettings() {
            const panel = this.elements.settingsPanel;
            const overlay = this.elements.touchOverlay;
            
            if (panel) panel.classList.add('visible');
            if (overlay) overlay.classList.add('visible');
        }

        /**
         * Ocultar configuración
         */
        hideSettings() {
            const panel = this.elements.settingsPanel;
            const overlay = this.elements.touchOverlay;
            
            if (panel) panel.classList.remove('visible');
            if (overlay) overlay.classList.remove('visible');
        }

        /**
         * Reproducir sonido de página
         */
        playPageSound() {
            // Implementación simple de sonido
            if (!this.config.enableSounds || !window.AudioContext) return;

            try {
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const oscillator = audioContext.createOscillator();
                const gainNode = audioContext.createGain();
                
                oscillator.connect(gainNode);
                gainNode.connect(audioContext.destination);
                
                oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
                oscillator.type = 'sine';
                
                gainNode.gain.setValueAtTime(0, audioContext.currentTime);
                gainNode.gain.linearRampToValueAtTime(0.1, audioContext.currentTime + 0.01);
                gainNode.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 0.1);
                
                oscillator.start(audioContext.currentTime);
                oscillator.stop(audioContext.currentTime + 0.1);
            } catch (e) {
                // Fallar silenciosamente
            }
        }

        /**
         * Mostrar error
         */
        showError(message) {
            this.container.innerHTML = `
                <div class="kindle-error">
                    <h3>Error del Lector Kindle</h3>
                    <p>${message}</p>
                    <button onclick="location.reload()">Recargar</button>
                </div>
            `;
        }

        /**
         * Sistema de eventos simple
         */
        emit(eventName, data) {
            const event = new CustomEvent('kindle:' + eventName, { 
                detail: data,
                bubbles: true
            });
            this.container.dispatchEvent(event);
        }

        /**
         * Debounce utility
         */
        debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }

        // API pública
        /**
         * Actualizar contenido
         */
        setContent(content) {
            this.config.content = content;
            this.processContent();
            this.state.currentPage = 0;
            this.updateDisplay();
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
    }

    /**
     * Inyectar CSS del plugin
     */
    KindleReaderPlugin.prototype.injectCSS = function() {
        if (document.getElementById('kindle-reader-css')) return;

        const css = `
            <style id="kindle-reader-css">
                .kindle-plugin {
                    --font-size: ${this.config.fontSize}px;
                    --line-height: ${this.config.lineHeight};
                    --primary-color: #232323;
                    --bg-color: #ffffff;
                    --text-color: #000000;
                    --border-color: #d1d1d1;
                    --shadow-color: rgba(0,0,0,0.1);
                    
                    font-family: 'Georgia', 'Times New Roman', serif;
                    max-width: 100%;
                    margin: 0 auto;
                    position: relative;
                }
                
                .kindle-plugin[data-theme="sepia"] {
                    --bg-color: #f4f1e8;
                    --text-color: #5c4b37;
                    --border-color: #d4c5a9;
                }
                
                .kindle-plugin[data-theme="dark"] {
                    --bg-color: #1a1a1a;
                    --text-color: #e5e5e5;
                    --border-color: #404040;
                    --shadow-color: rgba(0,0,0,0.3);
                }

                .kindle-device {
                    background: linear-gradient(145deg, #f0f0f0, #ffffff);
                    border-radius: 20px;
                    padding: 20px;
                    box-shadow: 0 10px 30px var(--shadow-color);
                    max-width: 600px;
                    margin: 0 auto;
                    position: relative;
                }

                .kindle-screen {
                    background: var(--bg-color);
                    border: 2px solid var(--border-color);
                    border-radius: 15px;
                    position: relative;
                    min-height: 500px;
                    overflow: hidden;
                }

                .kindle-content {
                    padding: 40px 30px 80px 30px;
                    min-height: 420px;
                    position: relative;
                }

                .kindle-text {
                    color: var(--text-color);
                    font-size: var(--font-size);
                    line-height: var(--line-height);
                    text-align: justify;
                    text-justify: inter-word;
                    transition: all 0.3s ease;
                }

                .kindle-text.transitioning {
                    opacity: 0.3;
                    transform: translateX(10px);
                }

                .kindle-text.transition-next {
                    transform: translateX(-10px);
                }

                .kindle-text.transition-prev {
                    transform: translateX(10px);
                }

                .text-page p {
                    margin: 1em 0;
                    text-indent: 1.5em;
                }

                .text-page p:first-child,
                .text-page h2 + p {
                    text-indent: 0;
                }

                .chapter-title {
                    color: var(--primary-color);
                    font-size: 1.3em;
                    font-weight: bold;
                    text-align: center;
                    margin: 0 0 1.5em 0;
                    text-indent: 0;
                }

                .toc-header {
                    font-size: 1.2em;
                    font-weight: bold;
                    text-align: center;
                    margin: 0 0 1em 0;
                    padding: 0 0 0.5em 0;
                    border-bottom: 1px solid var(--border-color);
                }

                .toc-line {
                    margin: 0.3em 0;
                    padding-left: 1em;
                    text-indent: -1em;
                }

                .kindle-progress-bar {
                    position: absolute;
                    bottom: 50px;
                    left: 30px;
                    right: 30px;
                    height: 3px;
                    background: var(--border-color);
                    border-radius: 2px;
                    overflow: hidden;
                }

                .progress-fill {
                    height: 100%;
                    background: var(--primary-color);
                    border-radius: 2px;
                    transition: width 0.3s ease;
                }

                .kindle-page-info {
                    position: absolute;
                    bottom: 20px;
                    left: 30px;
                    right: 30px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    font-size: 0.85em;
                    color: var(--text-color);
                    opacity: 0.7;
                }

                .kindle-controls {
                    display: flex;
                    justify-content: center;
                    gap: 15px;
                    margin-top: 20px;
                }

                .kindle-btn {
                    background: linear-gradient(145deg, #ffffff, #f0f0f0);
                    border: 1px solid var(--border-color);
                    border-radius: 10px;
                    width: 50px;
                    height: 50px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    color: var(--primary-color);
                }

                .kindle-btn:hover:not(:disabled) {
                    background: linear-gradient(145deg, #f8f8f8, #e8e8e8);
                    transform: translateY(-2px);
                    box-shadow: 0 5px 15px var(--shadow-color);
                }

                .kindle-btn:disabled {
                    opacity: 0.4;
                    cursor: not-allowed;
                    transform: none;
                }

                .kindle-btn svg {
                    stroke: currentColor;
                    stroke-width: 2;
                    fill: none;
                }

                .kindle-settings-panel {
                    position: absolute;
                    top: 100%;
                    left: 0;
                    right: 0;
                    background: var(--bg-color);
                    border: 1px solid var(--border-color);
                    border-radius: 15px;
                    margin-top: 10px;
                    padding: 20px;
                    box-shadow: 0 10px 30px var(--shadow-color);
                    transform: translateY(-10px) scale(0.95);
                    opacity: 0;
                    visibility: hidden;
                    transition: all 0.3s ease;
                    z-index: 1000;
                }

                .kindle-settings-panel.visible {
                    transform: translateY(0) scale(1);
                    opacity: 1;
                    visibility: visible;
                }

                .settings-content h3 {
                    margin: 0 0 20px 0;
                    color: var(--text-color);
                    text-align: center;
                }

                .setting-group {
                    margin-bottom: 20px;
                }

                .setting-group label {
                    display: block;
                    margin-bottom: 8px;
                    color: var(--text-color);
                    font-weight: bold;
                    font-size: 0.9em;
                }

                .font-size-controls {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 15px;
                }

                .size-btn {
                    background: linear-gradient(145deg, #ffffff, #f0f0f0);
                    border: 1px solid var(--border-color);
                    border-radius: 8px;
                    width: 40px;
                    height: 40px;
                    cursor: pointer;
                    font-weight: bold;
                    color: var(--primary-color);
                }

                .current-size {
                    font-weight: bold;
                    color: var(--text-color);
                    min-width: 50px;
                    text-align: center;
                }

                .theme-controls {
                    display: flex;
                    gap: 10px;
                    justify-content: center;
                }

                .theme-btn {
                    background: linear-gradient(145deg, #ffffff, #f0f0f0);
                    border: 1px solid var(--border-color);
                    border-radius: 8px;
                    padding: 8px 16px;
                    cursor: pointer;
                    font-size: 0.9em;
                    color: var(--primary-color);
                    transition: all 0.2s ease;
                }

                .theme-btn:hover,
                .theme-btn.active {
                    background: var(--primary-color);
                    color: var(--bg-color);
                }

                .nav-info p {
                    margin: 5px 0;
                    font-size: 0.85em;
                    color: var(--text-color);
                    opacity: 0.8;
                }

                .kindle-touch-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(0,0,0,0.3);
                    opacity: 0;
                    visibility: hidden;
                    transition: all 0.3s ease;
                    z-index: 999;
                }

                .kindle-touch-overlay.visible {
                    opacity: 1;
                    visibility: visible;
                }

                .no-content,
                .kindle-error {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 300px;
                    color: var(--text-color);
                    text-align: center;
                    font-style: italic;
                }

                .kindle-error button {
                    margin-top: 20px;
                    padding: 10px 20px;
                    background: var(--primary-color);
                    color: var(--bg-color);
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                }

                /* Responsive */
                @media (max-width: 768px) {
                    .kindle-device {
                        padding: 15px;
                        margin: 10px;
                    }
                    
                    .kindle-content {
                        padding: 30px 20px 70px 20px;
                        min-height: 350px;
                    }
                    
                    .kindle-text {
                        font-size: calc(var(--font-size) * 0.9);
                    }
                    
                    .kindle-btn {
                        width: 45px;
                        height: 45px;
                    }
                    
                    .kindle-settings-panel {
                        position: fixed;
                        top: 50%;
                        left: 10px;
                        right: 10px;
                        transform: translateY(-50%) scale(0.95);
                        margin: 0;
                    }
                    
                    .kindle-settings-panel.visible {
                        transform: translateY(-50%) scale(1);
                    }
                }
            </style>
        `;

        document.head.insertAdjacentHTML('beforeend', css);
    };

    // Exportar plugin con compatibilidad
    global.UltraRealisticKindleReader = UltraRealisticKindleReader;
    global.KindleReaderPlugin = UltraRealisticKindleReader; // Compatibilidad hacia atrás

    // Auto-detección de elementos con atributo data-kindle
    document.addEventListener('DOMContentLoaded', () => {
        const autoElements = document.querySelectorAll('[data-kindle]');
        autoElements.forEach(element => {
            const content = element.dataset.kindleContent || element.textContent;
            const options = {
                container: element,
                content: content,
                fontSize: parseInt(element.dataset.kindleFontSize) || 16,
                theme: element.dataset.kindleTheme || 'light'
            };
            
            const kindle = new KindleReaderPlugin(options);
            kindle.init();
            
            // Guardar referencia
            element.kindleInstance = kindle;
        });
    });

})(window);