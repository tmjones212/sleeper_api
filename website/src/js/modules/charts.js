/**
 * Charts Module
 * Handles initialization and management of Chart.js visualizations
 */

import { timelineData } from './data/timelineData.js';

let monthlyChart = null;

export function initMonthlyChart() {
    const ctx = document.getElementById('monthlyChart');
    if (!ctx) return;
    
    const monthlyData = timelineData.monthly_breakdown;
    const labels = Object.keys(monthlyData).sort();
    const data = labels.map(month => monthlyData[month]);
    
    if (monthlyChart) {
        monthlyChart.destroy();
    }
    
    monthlyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of Trades',
                data: data,
                backgroundColor: 'rgba(0, 102, 204, 0.6)',
                borderColor: 'rgba(0, 102, 204, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                        color: '#e0e0e0'
                    },
                    grid: {
                        color: 'rgba(96, 96, 96, 0.3)'
                    }
                },
                x: {
                    ticks: {
                        color: '#e0e0e0',
                        maxRotation: 45,
                        minRotation: 45
                    },
                    grid: {
                        color: 'rgba(96, 96, 96, 0.3)'
                    }
                }
            }
        }
    });
}

// Export to window for panel switching
window.initMonthlyChart = initMonthlyChart;