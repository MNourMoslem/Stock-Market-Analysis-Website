class StockCompare {
    constructor() {
        this.selectedStocks = new Set();
        this.chart = null;
        this.colors = [
            '#3498db', '#e74c3c', '#2ecc71', '#f1c40f', 
            '#9b59b6', '#1abc9c', '#e67e22', '#34495e'
        ];
        this.currentRange = '1M';
        this.metricSelector = document.getElementById('compareMetric');
        this.selectedStocksContainer = document.querySelector('.selected-stocks');
        
        this.initialize();
    }

    initialize() {
        const canvas = document.querySelector('#compare_chart');
        if (canvas) {
            this.chart = new StockChart('#compare_chart', {
                showLegend: true,
                yAxisLabel: 'Value'
            });

            // Add time range change handler
            this.chart.onTimeRangeChange = (range) => {
                this.currentRange = range;
                this.updateChart();
            };
        }

        if (this.metricSelector) {
            this.metricSelector.addEventListener('change', () => {
                this.updateChart();
            });
        }
    }

    async updateChart() {
        if (!this.chart || this.selectedStocks.size === 0) return;

        try {
            const metric = this.metricSelector?.value || 'close_price';
            const metricType = this.metricSelector?.selectedOptions[0]?.dataset?.type || 'price';
            const metricLabel = this.metricSelector?.selectedOptions[0]?.text || 'Value';
            
            const promises = Array.from(this.selectedStocks).map(symbol =>
                fetch(`/api/stock-history/?symbol=${symbol}&range=${this.currentRange}&metric=${metric}`)
                    .then(response => response.json())
            );

            const results = await Promise.all(promises);
            const datasets = results.map((data, index) => ({
                label: Array.from(this.selectedStocks)[index],
                data: data[metric] || data.prices || [],
                borderColor: this.colors[index % this.colors.length],
                backgroundColor: this.colors[index % this.colors.length] + '20',
                borderWidth: 2,
                tension: 0.4,
                fill: true
            }));

            // Update chart with new data and options
            this.chart.updateData({
                labels: results[0]?.dates || [],
                datasets: datasets
            }, {
                metric: metricType,
                yAxisLabel: metricLabel
            });
        } catch (error) {
            console.error('Error updating chart:', error);
        }
    }

    async addStock(stockData) {
        if (!stockData || !stockData.symbol) return;
        
        if (this.selectedStocks.has(stockData.symbol)) return;
        
        try {
            const response = await fetch(`/api/stock-details/?symbol=${stockData.symbol}`);
            if (!response.ok) throw new Error('Failed to fetch stock details');
            
            const stockDetails = await response.json();
            this.selectedStocks.add(stockData.symbol);
            
            // Add stock tag to UI
            const stockTag = document.createElement('div');
            stockTag.className = 'stock-tag';
            stockTag.dataset.stockSymbol = stockData.symbol;
            stockTag.innerHTML = `
                <span class="symbol">${stockData.symbol}</span>
                <button class="remove-btn" title="Remove">×</button>
            `;

            stockTag.querySelector('.remove-btn').addEventListener('click', () => {
                this.removeStock(stockData.symbol);
            });

            document.querySelector('.selected-stocks').appendChild(stockTag);
            
            // Add to table with full details
            this.addStockToTable(stockDetails);
            await this.updateChart();
        } catch (error) {
            console.error('Error adding stock:', error);
            this.selectedStocks.delete(stockData.symbol);
        }
    }

    removeStock(symbol) {
        this.selectedStocks.delete(symbol);
        document.querySelector(`[data-stock-symbol="${symbol}"]`)?.remove();
        document.querySelector(`tr[data-symbol="${symbol}"]`)?.remove();
        
        // Clear chart if no stocks left, otherwise update it
        if (this.selectedStocks.size === 0) {
            this.chart.updateData({
                labels: [],
                datasets: []
            });
        } else {
            this.updateChart();
        }
    }

    addStockToUI(stock) {
        const stockTag = document.createElement('div');y
        stockTag.className = 'stock-tag';
        stockTag.dataset.stockSymbol = stock.symbol;
        stockTag.innerHTML = `
            <span class="symbol">${stock.symbol}</span>
            <button class="remove-btn" title="Remove">×</button>
        `;

        stockTag.querySelector('.remove-btn').addEventListener('click', () => {
            this.removeStock(stock.symbol);
        });

        this.selectedStocksContainer.appendChild(stockTag);
    }

    addStockToTable(stock) {
        if (!stock || !stock.symbol) return;
        
        const tbody = document.querySelector('.stock-table tbody');
        if (!tbody) return;

        // Remove existing row if it exists
        const existingRow = tbody.querySelector(`tr[data-symbol="${stock.symbol}"]`);
        if (existingRow) {
            existingRow.remove();
        }

        const row = document.createElement('tr');
        row.dataset.symbol = stock.symbol;

        // Create fields array based on the table structure
        const fields = [
            `<td class="symbol-cell"><a href="/stock/${stock.symbol}/">${stock.symbol}</a></td>`,
            `<td>${stock.brand || '-'}</td>`,
            `<td>${stock.industry || '-'}</td>`,
            `<td>${stock.sector || '-'}</td>`,
            `<td>${stock.country || '-'}</td>`
        ];

        row.innerHTML = fields.join('');
        tbody.appendChild(row);
    }

    async getCommonDates() {
        const response = await fetch(`/api/stock-history/?symbol=${Array.from(this.selectedStocks)[0]}&range=${this.currentRange}`);
        const data = await response.json();
        return data.dates;
    }
}

// Initialize the compare page
document.addEventListener('DOMContentLoaded', () => {
    window.stockCompare = new StockCompare();
});

// Callback for stock search
function comparePageCallback(symbol, url) {
    if (window.stockCompare) {
        const stockData = {
            symbol: symbol
        };
        window.stockCompare.addStock(stockData);
    } else {
        console.error('stockCompare is not initialized');
    }
}