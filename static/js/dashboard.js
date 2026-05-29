// Global variables
let performanceChart = null;
let metricsChart = null;

// Initialize charts when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard loaded successfully!');
    initializeCharts();
    setupEventListeners();
    loadMLflowData();
});

// Initialize performance charts with data from page
function initializeCharts() {
    // Get data from the page (passed from backend)
    const chartData = getChartDataFromTable();
    
    // Performance Trends Chart
    const perfCtx = document.getElementById('performanceChart');
    if (perfCtx) {
        const ctx = perfCtx.getContext('2d');
        performanceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'F1 Score',
                    data: chartData.f1Scores,
                    borderColor: '#4299e1',
                    backgroundColor: 'rgba(66, 153, 225, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointRadius: 5,
                    pointHoverRadius: 7
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { 
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 1,
                        ticks: {
                            callback: function(value) {
                                return value.toFixed(2);
                            }
                        }
                    }
                }
            }
        });
    }

    // Metrics Comparison Chart
    const metricsCtx = document.getElementById('metricsChart');
    if (metricsCtx) {
        const ctx = metricsCtx.getContext('2d');
        metricsChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['F1 Score', 'Precision', 'Recall'],
                datasets: [{
                    label: 'Best Model Metrics',
                    data: chartData.bestMetrics,
                    backgroundColor: [
                        'rgba(72, 187, 120, 0.8)',
                        'rgba(66, 153, 225, 0.8)',
                        'rgba(237, 137, 54, 0.8)'
                    ],
                    borderColor: [
                        '#48bb78',
                        '#4299e1',
                        '#ed8936'
                    ],
                    borderWidth: 2,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { 
                        display: false 
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.parsed.y.toFixed(4);
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 1,
                        ticks: {
                            callback: function(value) {
                                return value.toFixed(2);
                            }
                        }
                    }
                }
            }
        });
    }
}

// Extract chart data from the experiments table
function getChartDataFromTable() {
    const table = document.getElementById('experiments-table');
    const labels = [];
    const f1Scores = [];
    const precisions = [];
    const recalls = [];
    
    if (table && table.tBodies[0]) {
        const rows = table.tBodies[0].rows;
        const maxRows = Math.min(rows.length, 10);
        
        for (let i = maxRows - 1; i >= 0; i--) {
            const row = rows[i];
            labels.push(`Run ${maxRows - i}`);
            
            // Extract F1 score
            const f1Cell = row.cells[2];
            if (f1Cell) {
                const f1Text = f1Cell.textContent.trim();
                const f1Value = parseFloat(f1Text) || 0;
                f1Scores.push(f1Value);
            }
            
            // Extract Precision
            const precCell = row.cells[3];
            if (precCell) {
                const precValue = parseFloat(precCell.textContent.trim()) || 0;
                precisions.push(precValue);
            }
            
            // Extract Recall
            const recallCell = row.cells[4];
            if (recallCell) {
                const recallValue = parseFloat(recallCell.textContent.trim()) || 0;
                recalls.push(recallValue);
            }
        }
    }
    
    // If no data from table, use default values
    if (f1Scores.length === 0) {
        return {
            labels: ['No data'],
            f1Scores: [0],
            bestMetrics: [0, 0, 0]
        };
    }
    
    // Get best metrics (first row in table is usually best)
    const bestMetrics = [
        f1Scores[f1Scores.length - 1] || 0,
        precisions[precisions.length - 1] || 0,
        recalls[recalls.length - 1] || 0
    ];
    
    return {
        labels,
        f1Scores,
        bestMetrics
    };
}

// Setup event listeners
function setupEventListeners() {
    // Prediction form
    const predictionForm = document.getElementById('prediction-form');
    if (predictionForm) {
        predictionForm.addEventListener('submit', handlePrediction);
    }
}

// Handle training
async function startTraining() {
    const statusDiv = document.getElementById('training-status');
    const trainButton = event.target;
    
    // Disable button and show status
    trainButton.disabled = true;
    statusDiv.style.display = 'block';
    statusDiv.innerHTML = `
        <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
        <span class="ms-2 text-primary">Training in progress...</span>
    `;
    
    try {
        const response = await fetch('/train', {
            method: 'GET'
        });
        
        const result = await response.text();
        
        statusDiv.innerHTML = `
            <div class="alert alert-success mt-2">
                <i class="fas fa-check-circle"></i> ${result}
            </div>
        `;
        
        // Reload page after 2 seconds to show new results
        setTimeout(() => {
            window.location.reload();
        }, 2000);
        
    } catch (error) {
        statusDiv.innerHTML = `
            <div class="alert alert-danger mt-2">
                <i class="fas fa-exclamation-circle"></i> Training failed: ${error.message}
            </div>
        `;
        trainButton.disabled = false;
    }
}

// Handle prediction
async function handlePrediction(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('prediction-file');
    const resultDiv = document.getElementById('prediction-result');
    const submitButton = e.target.querySelector('button[type="submit"]');
    
    if (!fileInput.files[0]) {
        resultDiv.innerHTML = '<div class="alert alert-warning mt-2">Please select a CSV file</div>';
        return;
    }
    
    // Disable submit button
    submitButton.disabled = true;
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    resultDiv.innerHTML = `
        <div class="mt-2">
            <div class="spinner-border spinner-border-sm text-success" role="status"></div>
            <span class="ms-2 text-success">Processing predictions...</span>
        </div>
    `;
    
    try {
        const response = await fetch('/predict', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            resultDiv.innerHTML = `
                <div class="alert alert-success mt-2">
                    <i class="fas fa-check-circle"></i> Prediction complete! 
                    <br><small><a href="/output_prediction/predicted_data.csv" class="alert-link" download>Download Results</a></small>
                </div>
            `;
            
            // Reset form
            fileInput.value = '';
        } else {
            throw new Error('Prediction request failed');
        }
    } catch (error) {
        resultDiv.innerHTML = `
            <div class="alert alert-danger mt-2">
                <i class="fas fa-exclamation-circle"></i> Error: ${error.message}
            </div>
        `;
    } finally {
        submitButton.disabled = false;
    }
}

// Load MLflow data via API
async function loadMLflowData() {
    try {
        const response = await fetch('/api/mlflow/runs');
        if (response.ok) {
            const runs = await response.json();
            console.log('Loaded MLflow runs:', runs.length);
            // Can be used for dynamic updates
        }
    } catch (error) {
        console.log('MLflow API not available yet:', error.message);
    }
}

// Refresh data periodically (optional)
function startAutoRefresh() {
    setInterval(async () => {
        try {
            const response = await fetch('/api/mlflow/runs');
            if (response.ok) {
                const runs = await response.json();
                console.log('Auto-refreshed data:', runs.length, 'runs');
                // Update UI if needed
            }
        } catch (error) {
            console.log('Auto-refresh failed:', error.message);
        }
    }, 60000); // Refresh every 60 seconds
}

// Utility function to format dates
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

// Utility function to format numbers
function formatNumber(num, decimals = 4) {
    return parseFloat(num).toFixed(decimals);
}
