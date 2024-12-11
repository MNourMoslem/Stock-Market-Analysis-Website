document.addEventListener('DOMContentLoaded', function() {
    const chartContainer = document.querySelector('.chart-container');
    if (!chartContainer) return;

    const canvas = chartContainer.querySelector('canvas');
    if (!canvas) return;

    const symbol = document.querySelector('.stock-header h1')?.textContent.split('-')[0].trim();
    if (!symbol) return;

    const chart = new StockChart(`#${canvas.id}`, {
        showLegend: false,
        yAxisLabel: 'Price ($)'
    });

    async function updateChartData(range = '1M') {
        try {
            const response = await fetch(`/api/stock-history/?symbol=${symbol}&range=${range}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            
            if (!data.dates || !data.prices) {
                throw new Error('Invalid data format received from server');
            }

            const chartData = {
                labels: data.dates,
                datasets: [{
                    label: `${symbol} Stock Price`,
                    data: data.prices,
                    borderColor: '#3498db',
                    backgroundColor: '#3498db20',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true
                }]
            };

            chart.updateData(chartData);
        } catch (error) {
            console.error('Error in updateChartData:', error);
        }
    }

    chart.onTimeRangeChange = (range) => {
        updateChartData(range);
    };

    updateChartData('1M');
});