/**
 * Sistema de Navegación para Ebooks Profesionales
 * Buko AI - Funcionalidades interactivas
 */

class EbookNavigator {
    constructor() {
        this.currentChapter = 0;
        this.chapters = [];
        this.toc = [];
        this.searchIndex = {};
        this.bookmarks = [];
        this.readingProgress = 0;
        
        this.init();
    }
    
    init() {
        // Inicializar elementos
        this.initChapters();
        this.initTableOfContents();
        this.initKeyboardNavigation();
        this.initProgressTracking();
        this.initSearchFunctionality();
        this.initBookmarks();
        this.initPrintOptimization();
        
        // Restaurar estado guardado
        this.restoreState();
    }
    
    initChapters() {
        // Recolectar todos los capítulos
        this.chapters = document.querySelectorAll('.chapter-container');
        
        // Asignar IDs únicos si no tienen
        this.chapters.forEach((chapter, index) => {
            if (!chapter.id) {
                chapter.id = `chapter-${index + 1}`;
            }
            
            // Agregar numeración de páginas
            const pageNumber = document.createElement('div');
            pageNumber.className = 'page-number';
            pageNumber.textContent = `Página ${this.calculatePageNumber(chapter)}`;
            chapter.appendChild(pageNumber);
        });
    }
    
    initTableOfContents() {
        const tocLinks = document.querySelectorAll('.toc-list a');
        
        tocLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = link.getAttribute('href').substring(1);
                this.navigateToElement(targetId);
            });
            
            // Agregar números de página
            const target = document.getElementById(link.getAttribute('href').substring(1));
            if (target) {
                link.setAttribute('data-page', this.calculatePageNumber(target));
            }
        });
    }
    
    initKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            switch(e.key) {
                case 'ArrowLeft':
                case 'PageUp':
                    this.previousChapter();
                    break;
                case 'ArrowRight':
                case 'PageDown':
                    this.nextChapter();
                    break;
                case 'Home':
                    this.goToBeginning();
                    break;
                case 'End':
                    this.goToEnd();
                    break;
                case 'f':
                case 'F':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.openSearch();
                    }
                    break;
                case 'b':
                case 'B':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.toggleBookmark();
                    }
                    break;
                case 'p':
                case 'P':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.printBook();
                    }
                    break;
            }
        });
    }
    
    initProgressTracking() {
        // Crear barra de progreso
        const progressBar = document.createElement('div');
        progressBar.className = 'reading-progress-bar';
        progressBar.innerHTML = `
            <div class="progress-fill"></div>
            <span class="progress-text">0% completado</span>
        `;
        document.body.appendChild(progressBar);
        
        // Actualizar progreso al hacer scroll
        window.addEventListener('scroll', () => {
            this.updateReadingProgress();
        });
    }
    
    initSearchFunctionality() {
        // Crear índice de búsqueda
        const content = document.querySelector('.ebook-content');
        if (content) {
            this.buildSearchIndex(content);
        }
        
        // Crear interfaz de búsqueda
        this.createSearchInterface();
    }
    
    initBookmarks() {
        // Cargar bookmarks guardados
        const savedBookmarks = localStorage.getItem('ebook-bookmarks');
        if (savedBookmarks) {
            this.bookmarks = JSON.parse(savedBookmarks);
        }
        
        // Crear interfaz de bookmarks
        this.createBookmarksInterface();
    }
    
    initPrintOptimization() {
        // Agregar estilos específicos para impresión
        window.addEventListener('beforeprint', () => {
            document.body.classList.add('printing');
            this.optimizeForPrint();
        });
        
        window.addEventListener('afterprint', () => {
            document.body.classList.remove('printing');
        });
    }
    
    // Navegación
    navigateToElement(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth', block: 'start' });
            
            // Resaltar temporalmente
            element.classList.add('highlighted');
            setTimeout(() => {
                element.classList.remove('highlighted');
            }, 2000);
            
            // Actualizar estado
            this.updateCurrentChapter();
        }
    }
    
    nextChapter() {
        if (this.currentChapter < this.chapters.length - 1) {
            this.currentChapter++;
            this.chapters[this.currentChapter].scrollIntoView({ behavior: 'smooth' });
            this.updateCurrentChapter();
        }
    }
    
    previousChapter() {
        if (this.currentChapter > 0) {
            this.currentChapter--;
            this.chapters[this.currentChapter].scrollIntoView({ behavior: 'smooth' });
            this.updateCurrentChapter();
        }
    }
    
    goToBeginning() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        this.currentChapter = 0;
        this.updateCurrentChapter();
    }
    
    goToEnd() {
        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
        this.currentChapter = this.chapters.length - 1;
        this.updateCurrentChapter();
    }
    
    // Búsqueda
    buildSearchIndex(container) {
        const elements = container.querySelectorAll('p, h1, h2, h3, h4, .expr-text, .translation-text');
        
        elements.forEach((element, index) => {
            const text = element.textContent.toLowerCase();
            const words = text.split(/\s+/);
            
            words.forEach(word => {
                word = word.replace(/[^a-záéíóúñü]/g, '');
                if (word.length > 2) {
                    if (!this.searchIndex[word]) {
                        this.searchIndex[word] = [];
                    }
                    this.searchIndex[word].push({
                        element: element,
                        index: index,
                        context: element.textContent.substring(0, 100)
                    });
                }
            });
        });
    }
    
    createSearchInterface() {
        const searchModal = document.createElement('div');
        searchModal.className = 'search-modal';
        searchModal.innerHTML = `
            <div class="search-content">
                <h3>Buscar en el libro</h3>
                <input type="text" class="search-input" placeholder="Ingrese término de búsqueda...">
                <div class="search-results"></div>
                <button class="close-search">Cerrar</button>
            </div>
        `;
        document.body.appendChild(searchModal);
        
        // Event listeners
        const searchInput = searchModal.querySelector('.search-input');
        const searchResults = searchModal.querySelector('.search-results');
        const closeButton = searchModal.querySelector('.close-search');
        
        searchInput.addEventListener('input', (e) => {
            this.performSearch(e.target.value, searchResults);
        });
        
        closeButton.addEventListener('click', () => {
            searchModal.classList.remove('active');
        });
    }
    
    openSearch() {
        const searchModal = document.querySelector('.search-modal');
        searchModal.classList.add('active');
        searchModal.querySelector('.search-input').focus();
    }
    
    performSearch(query, resultsContainer) {
        resultsContainer.innerHTML = '';
        
        if (query.length < 3) {
            return;
        }
        
        const queryWords = query.toLowerCase().split(/\s+/);
        const results = [];
        
        queryWords.forEach(word => {
            if (this.searchIndex[word]) {
                results.push(...this.searchIndex[word]);
            }
        });
        
        // Eliminar duplicados y ordenar por relevancia
        const uniqueResults = [...new Set(results.map(r => r.element))];
        
        uniqueResults.slice(0, 10).forEach(element => {
            const resultItem = document.createElement('div');
            resultItem.className = 'search-result-item';
            resultItem.innerHTML = `
                <strong>${element.tagName}</strong>: ${element.textContent.substring(0, 100)}...
            `;
            resultItem.addEventListener('click', () => {
                element.scrollIntoView({ behavior: 'smooth' });
                document.querySelector('.search-modal').classList.remove('active');
            });
            resultsContainer.appendChild(resultItem);
        });
    }
    
    // Bookmarks
    createBookmarksInterface() {
        const bookmarksPanel = document.createElement('div');
        bookmarksPanel.className = 'bookmarks-panel';
        bookmarksPanel.innerHTML = `
            <h3>Marcadores</h3>
            <div class="bookmarks-list"></div>
            <button class="add-bookmark">Agregar marcador aquí</button>
        `;
        document.body.appendChild(bookmarksPanel);
        
        // Event listeners
        const addButton = bookmarksPanel.querySelector('.add-bookmark');
        addButton.addEventListener('click', () => {
            this.addBookmark();
        });
        
        this.updateBookmarksList();
    }
    
    toggleBookmark() {
        const bookmarksPanel = document.querySelector('.bookmarks-panel');
        bookmarksPanel.classList.toggle('active');
    }
    
    addBookmark() {
        const currentPosition = window.pageYOffset;
        const currentElement = this.getCurrentVisibleElement();
        
        const bookmark = {
            id: Date.now(),
            position: currentPosition,
            elementId: currentElement?.id,
            text: currentElement?.textContent.substring(0, 50),
            chapter: this.currentChapter,
            date: new Date().toISOString()
        };
        
        this.bookmarks.push(bookmark);
        this.saveBookmarks();
        this.updateBookmarksList();
    }
    
    saveBookmarks() {
        localStorage.setItem('ebook-bookmarks', JSON.stringify(this.bookmarks));
    }
    
    updateBookmarksList() {
        const bookmarksList = document.querySelector('.bookmarks-list');
        if (!bookmarksList) return;
        
        bookmarksList.innerHTML = '';
        
        this.bookmarks.forEach(bookmark => {
            const item = document.createElement('div');
            item.className = 'bookmark-item';
            item.innerHTML = `
                <span>${bookmark.text}...</span>
                <button class="remove-bookmark" data-id="${bookmark.id}">×</button>
            `;
            
            item.addEventListener('click', () => {
                window.scrollTo({ top: bookmark.position, behavior: 'smooth' });
            });
            
            const removeButton = item.querySelector('.remove-bookmark');
            removeButton.addEventListener('click', (e) => {
                e.stopPropagation();
                this.removeBookmark(bookmark.id);
            });
            
            bookmarksList.appendChild(item);
        });
    }
    
    removeBookmark(bookmarkId) {
        this.bookmarks = this.bookmarks.filter(b => b.id !== bookmarkId);
        this.saveBookmarks();
        this.updateBookmarksList();
    }
    
    // Progreso de lectura
    updateReadingProgress() {
        const scrollTop = window.pageYOffset;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const progress = (scrollTop / docHeight) * 100;
        
        this.readingProgress = Math.round(progress);
        
        const progressBar = document.querySelector('.reading-progress-bar');
        if (progressBar) {
            progressBar.querySelector('.progress-fill').style.width = `${progress}%`;
            progressBar.querySelector('.progress-text').textContent = `${this.readingProgress}% completado`;
        }
        
        // Guardar progreso
        this.saveState();
    }
    
    updateCurrentChapter() {
        // Encontrar capítulo visible actual
        const scrollPosition = window.pageYOffset + window.innerHeight / 2;
        
        this.chapters.forEach((chapter, index) => {
            const rect = chapter.getBoundingClientRect();
            const absoluteTop = rect.top + window.pageYOffset;
            
            if (absoluteTop <= scrollPosition) {
                this.currentChapter = index;
            }
        });
    }
    
    getCurrentVisibleElement() {
        const elements = document.querySelectorAll('.ebook-content > *');
        const scrollPosition = window.pageYOffset + window.innerHeight / 2;
        
        for (let element of elements) {
            const rect = element.getBoundingClientRect();
            const absoluteTop = rect.top + window.pageYOffset;
            
            if (absoluteTop <= scrollPosition && absoluteTop + rect.height >= scrollPosition) {
                return element;
            }
        }
        
        return null;
    }
    
    // Utilidades
    calculatePageNumber(element) {
        // Simulación de número de página basado en posición
        const pageHeight = 900; // Altura aproximada de una página
        const elementTop = element.offsetTop;
        return Math.floor(elementTop / pageHeight) + 1;
    }
    
    optimizeForPrint() {
        // Optimizaciones para impresión
        const images = document.querySelectorAll('img');
        images.forEach(img => {
            if (img.naturalWidth > 600) {
                img.style.maxWidth = '100%';
            }
        });
        
        // Asegurar saltos de página correctos
        const chapters = document.querySelectorAll('.chapter-container');
        chapters.forEach(chapter => {
            chapter.style.pageBreakBefore = 'always';
        });
    }
    
    printBook() {
        window.print();
    }
    
    // Estado y persistencia
    saveState() {
        const state = {
            currentChapter: this.currentChapter,
            readingProgress: this.readingProgress,
            scrollPosition: window.pageYOffset,
            lastRead: new Date().toISOString()
        };
        
        localStorage.setItem('ebook-reading-state', JSON.stringify(state));
    }
    
    restoreState() {
        const savedState = localStorage.getItem('ebook-reading-state');
        if (savedState) {
            const state = JSON.parse(savedState);
            
            this.currentChapter = state.currentChapter || 0;
            this.readingProgress = state.readingProgress || 0;
            
            // Restaurar posición de scroll
            if (state.scrollPosition) {
                setTimeout(() => {
                    window.scrollTo({ top: state.scrollPosition });
                }, 100);
            }
        }
    }
}

// Estilos CSS para las funcionalidades
const styles = `
<style>
/* Barra de progreso */
.reading-progress-bar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: rgba(0, 0, 0, 0.1);
    z-index: 1000;
}

.progress-fill {
    height: 100%;
    background: var(--ebook-accent-color);
    transition: width 0.3s ease;
}

.progress-text {
    position: absolute;
    right: 10px;
    top: 10px;
    font-size: 12px;
    background: white;
    padding: 2px 8px;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Modal de búsqueda */
.search-modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s ease;
    z-index: 2000;
}

.search-modal.active {
    opacity: 1;
    visibility: visible;
}

.search-content {
    background: white;
    padding: 2em;
    border-radius: 8px;
    width: 90%;
    max-width: 600px;
}

.search-input {
    width: 100%;
    padding: 0.75em;
    font-size: 16px;
    border: 2px solid var(--ebook-border-color);
    border-radius: 4px;
    margin: 1em 0;
}

.search-results {
    max-height: 300px;
    overflow-y: auto;
    margin: 1em 0;
}

.search-result-item {
    padding: 0.75em;
    border-bottom: 1px solid var(--ebook-border-color);
    cursor: pointer;
    transition: background 0.2s ease;
}

.search-result-item:hover {
    background: rgba(0, 0, 0, 0.05);
}

/* Panel de marcadores */
.bookmarks-panel {
    position: fixed;
    right: -300px;
    top: 50px;
    width: 280px;
    height: calc(100vh - 100px);
    background: white;
    box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1);
    padding: 1.5em;
    transition: right 0.3s ease;
    z-index: 1500;
    overflow-y: auto;
}

.bookmarks-panel.active {
    right: 0;
}

.bookmarks-list {
    margin: 1em 0;
}

.bookmark-item {
    padding: 0.75em;
    margin: 0.5em 0;
    background: rgba(0, 0, 0, 0.05);
    border-radius: 4px;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.bookmark-item:hover {
    background: rgba(0, 0, 0, 0.1);
}

.remove-bookmark {
    background: none;
    border: none;
    font-size: 20px;
    cursor: pointer;
    color: var(--ebook-secondary-color);
}

.add-bookmark {
    width: 100%;
    padding: 0.75em;
    background: var(--ebook-accent-color);
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
}

/* Resaltado temporal */
.highlighted {
    background: rgba(255, 235, 59, 0.3);
    transition: background 2s ease;
}

/* Números de página */
.page-number {
    position: absolute;
    bottom: 20px;
    right: 20px;
    font-size: 12px;
    color: var(--ebook-secondary-color);
}

/* Estado de impresión */
.printing .reading-progress-bar,
.printing .search-modal,
.printing .bookmarks-panel {
    display: none !important;
}

.close-search {
    padding: 0.5em 1em;
    background: var(--ebook-secondary-color);
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}
</style>
`;

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    // Agregar estilos
    document.head.insertAdjacentHTML('beforeend', styles);
    
    // Inicializar navegador
    window.ebookNavigator = new EbookNavigator();
});