class StockSearch {
    constructor(container) {
        this.container = container;
        this.input = container.querySelector('.stock-search-input');
        this.suggestionsDiv = container.querySelector('.search-suggestions');
        this.callbackFunction = container.dataset.callback || 'defaultSearchCallback';
        this.debounceTimer = null;
        this.selectedIndex = -1;
        
        this.initialize();
    }

    initialize() {
        this.input.addEventListener('input', () => this.handleInput());
        this.input.addEventListener('focus', () => this.handleFocus());
        this.input.addEventListener('keydown', (e) => this.handleKeyDown(e));
        document.addEventListener('click', (e) => this.handleClickOutside(e));
    }

    handleKeyDown(e) {
        const suggestions = this.suggestionsDiv.querySelectorAll('.suggestion-item');
        
        switch(e.key) {
            case 'ArrowDown':
                e.preventDefault();
                if (this.selectedIndex < suggestions.length - 1) {
                    this.updateSelection(this.selectedIndex + 1);
                }
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                if (this.selectedIndex > 0) {
                    this.updateSelection(this.selectedIndex - 1);
                }
                break;
                
            case 'Enter':
                e.preventDefault();
                if (this.selectedIndex >= 0) {
                    suggestions[this.selectedIndex].click();
                } else if (suggestions.length > 0) {
                    suggestions[0].click();
                }
                break;
                
            case 'Escape':
                e.preventDefault();
                this.suggestionsDiv.classList.remove('active');
                this.selectedIndex = -1;
                break;
        }
    }

    updateSelection(newIndex) {
        const suggestions = this.suggestionsDiv.querySelectorAll('.suggestion-item');
        
        suggestions.forEach(item => item.classList.remove('selected'));
        
        this.selectedIndex = newIndex;
        
        if (this.selectedIndex >= 0) {
            const selectedItem = suggestions[this.selectedIndex];
            selectedItem.classList.add('selected');
            
            const container = this.suggestionsDiv;
            const itemTop = selectedItem.offsetTop;
            const itemBottom = itemTop + selectedItem.offsetHeight;
            
            if (itemBottom > container.scrollTop + container.offsetHeight) {
                container.scrollTop = itemBottom - container.offsetHeight;
            } else if (itemTop < container.scrollTop) {
                container.scrollTop = itemTop;
            }
        }
    }

    handleInput() {
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => this.performSearch(), 300);
        this.selectedIndex = -1;
    }

    handleFocus() {
        if (this.suggestionsDiv.children.length > 0) {
            this.suggestionsDiv.classList.add('active');
        }
    }

    handleClickOutside(e) {
        if (!this.container.contains(e.target)) {
            this.suggestionsDiv.classList.remove('active');
            this.selectedIndex = -1;
        }
    }

    async performSearch() {
        const query = this.input.value.trim();
        
        if (!query) {
            this.suggestionsDiv.innerHTML = '';
            this.suggestionsDiv.classList.remove('active');
            return;
        }

        try {
            const response = await fetch(`/api/search/?query=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            this.renderSuggestions(data.results);
        } catch (error) {
            console.error('خطأ في البحث:', error);
        }
    }

    renderSuggestions(results) {
        if (results.length === 0) {
            this.suggestionsDiv.innerHTML = `
                <div class="no-suggestions">
                    No results found
                </div>
            `;
            this.selectedIndex = -1;
        } else {
            this.suggestionsDiv.innerHTML = results.map(stock => `
                <div class="suggestion-item" 
                     data-symbol="${stock.symbol}"
                     data-url="${stock.url}">
                    <div>
                        <span class="symbol">${stock.symbol}</span>
                        <span class="brand">${stock.brand}</span>
                    </div>
                    <div class="price">${stock.price}</div>
                </div>
            `).join('');

            this.suggestionsDiv.querySelectorAll('.suggestion-item').forEach(item => {
                item.addEventListener('click', (e) => this.handleSuggestionClick(e));
            });
            
            this.selectedIndex = 0;
            this.updateSelection(0);
        }
        
        this.suggestionsDiv.classList.add('active');
    }

    handleSuggestionClick(e) {
        const item = e.currentTarget;
        const symbol = item.dataset.symbol;
        const url = item.dataset.url;

        if (window[this.callbackFunction]) {
            window[this.callbackFunction](symbol, url);
        } else {
            window.location.href = url;
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.stock-search-container').forEach(container => {
        new StockSearch(container);
    });
});

function defaultSearchCallback(symbol, url) {
    window.location.href = url;
}

function comparePageCallback(symbol, url) {
    if (window.stockCompare) {
        window.stockCompare.addStock(symbol);
    } else {
        console.error('stockCompare is not initialized');
    }
} 