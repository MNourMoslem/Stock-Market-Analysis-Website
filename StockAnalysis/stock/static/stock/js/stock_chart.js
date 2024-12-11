class StockChart {
    constructor(selector, options = {}) {
        this.container = document.querySelector(selector);
        this.options = options;
        this.timeRangeButtons = document.querySelectorAll('.time-range-button');
        this.initializeChart();
        this.setupEventListeners();
    }

    formatNumber(value) {
        if (Math.abs(value) >= 1.0e+9) {
            return (value / 1.0e+9).toFixed(2) + "B";
        } else if (Math.abs(value) >= 1.0e+6) {
            return (value / 1.0e+6).toFixed(2) + "M";
        } else {
            return value;
        }
    }

    initializeChart() {
        this.chart = new Chart(this.container, {
            type: 'line',
            data: {
                labels: [],
                datasets: []
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 750,
                    easing: 'easeInOutQuart'
                },
                transitions: {
                    active: {
                        animation: {
                            duration: 0
                        }
                    }
                },
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: {
                        display: this.options.showLegend ?? true,
                        labels: {
                            usePointStyle: true,
                            pointStyle: 'circle',
                            padding: 20,
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(255, 255, 255, 0.9)',
                        titleColor: '#2c3e50',
                        bodyColor: '#2c3e50',
                        borderColor: '#ddd',
                        borderWidth: 1,
                        padding: 10,
                        displayColors: true,
                        callbacks: {
                            label: (context) => {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    const value = context.parsed.y;
                                    const metric = this.options.metric || 'price';
                                    
                                    if (['volume', 'shares_outstanding', 'market_cap'].includes(metric)) {
                                        label += this.formatNumber(value);
                                    } else {
                                        label += new Intl.NumberFormat('en-US', {
                                            style: 'currency',
                                            currency: 'USD'
                                        }).format(value);
                                    }
                                }
                                return label;
                            }
                        }
                    },
                    decimation: {
                        enabled: true,
                        algorithm: 'min-max'
                    }
                },
                scales: {
                    y: {
                        title: {
                            display: true,
                            text: this.options.yAxisLabel || '',
                            font: {
                                size: 14
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)',
                            drawBorder: false
                        },
                        ticks: {
                            font: {
                                size: 12
                            },
                            callback: (value) => {
                                const metric = this.options.metric || 'price';
                                if (['volume', 'shares_outstanding', 'market_cap'].includes(metric)) {
                                    return this.formatNumber(value);
                                }
                                return new Intl.NumberFormat('en-US', {
                                    style: 'currency',
                                    currency: 'USD',
                                    minimumFractionDigits: 0,
                                    maximumFractionDigits: 0
                                }).format(value);
                            }
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            maxTicksLimit: 10,
                            maxRotation: 0,
                            autoSkip: true,
                            font: {
                                size: 12
                            }
                        }
                    }
                },
                elements: {
                    point: {
                        radius: 0,
                        hitRadius: 10,
                        hoverRadius: 4
                    },
                    line: {
                        borderWidth: 2,
                        tension: 0.4
                    }
                }
            }
        });
    }

    setupEventListeners() {
        this.timeRangeButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.timeRangeButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                if (this.onTimeRangeChange) {
                    this.onTimeRangeChange(button.dataset.range);
                }
            });
        });
    }

    updateData(data) {
        if (data.labels && data.labels.length > 200) {
            const skipFactor = Math.floor(data.labels.length / 200);
            data.labels = data.labels.filter((_, i) => i % skipFactor === 0);
            data.datasets = data.datasets.map(dataset => ({
                ...dataset,
                data: dataset.data.filter((_, i) => i % skipFactor === 0)
            }));
        }

        this.chart.data = data;
        this.chart.update();
    }
}