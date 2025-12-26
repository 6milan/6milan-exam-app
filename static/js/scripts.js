// static/js/scripts.js

document.addEventListener('DOMContentLoaded', function () {
    // === Password Show/Hide Checkbox Toggles (Global) ===
    // This handles ALL password fields with "Show" checkboxes across login, signup, and reset pages
    const togglePasswordCheckboxes = document.querySelectorAll('.form-check-input[type="checkbox"]');
    
    togglePasswordCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function () {
            // Find the nearest password input within the same input-group
            const inputGroup = this.closest('.input-group');
            if (!inputGroup) return;
            
            const passwordField = inputGroup.querySelector('input[type="password"], input[type="text"]');
            if (passwordField) {
                passwordField.type = this.checked ? 'text' : 'password';
            }
        });
    });

    // === Score Progress Chart (Student Profile Page) ===
    const chartCanvas = document.getElementById('scoreChart');
    if (!chartCanvas) {
        return; // Not on a page with the chart
    }

    // Show loading message
    const container = chartCanvas.parentElement;
    container.innerHTML = '<p style="text-align:center; color:#64748b;">Loading your progress chart...</p>';

    // Parse data safely
    let labels = [];
    let scores = [];
    try {
        labels = JSON.parse(chartCanvas.dataset.labels || '[]');
        scores = JSON.parse(chartCanvas.dataset.scores || '[]');
    } catch (e) {
        console.error("Error parsing chart data:", e);
        container.innerHTML = '<p style="text-align:center; color:#ef4444;">Error loading chart data.</p>';
        return;
    }

    // If no data yet
    if (labels.length === 0 || scores.length === 0) {
        container.innerHTML = `
            <div style="text-align:center; padding:60px 20px; color:#64748b;">
                <h3>No Exam Records Yet</h3>
                <p>Complete your first exam to see your progress chart here!</p>
                <span style="font-size:60px;">📊</span>
            </div>
        `;
        return;
    }

    // Determine max score (default 20, but flexible)
    const maxScore = Math.max(...scores, 20);

    // Restore canvas
    container.innerHTML = '<canvas id="scoreChart"></canvas>';
    const canvas = document.getElementById('scoreChart');

    // Generate gradient
    const ctx = canvas.getContext('2d');
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(79, 70, 229, 0.3)');
    gradient.addColorStop(1, 'rgba(79, 70, 229, 0.05)');

    // Create Chart.js chart
    new Chart(canvas, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Your Exam Scores',
                data: scores,
                borderColor: '#4F46E5',
                backgroundColor: gradient,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#4F46E5',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 3,
                pointRadius: 6,
                pointHoverRadius: 10,
                pointHoverBackgroundColor: '#4F46E5',
                pointHoverBorderColor: '#ffffff',
                pointHoverBorderWidth: 4,
                borderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 1500,
                easing: 'easeOutQuart'
            },
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        font: {
                            size: 16,
                            weight: 'bold'
                        },
                        color: '#1e293b',
                        padding: 20
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(30, 41, 59, 0.95)',
                    titleFont: { size: 14, weight: 'bold' },
                    bodyFont: { size: 16 },
                    padding: 12,
                    cornerRadius: 8,
                    displayColors: false,
                    callbacks: {
                        title: function(tooltipItems) {
                            return 'Date: ' + tooltipItems[0].label;
                        },
                        label: function(context) {
                            return `Score: ${context.parsed.y} / ${maxScore}`;
                        },
                        afterLabel: function(context) {
                            const percentage = ((context.parsed.y / maxScore) * 100).toFixed(1);
                            return `Performance: ${percentage}%`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: maxScore + 2,
                    grid: {
                        color: 'rgba(148, 163, 184, 0.2)',
                        drawBorder: false
                    },
                    ticks: {
                        stepSize: maxScore <= 20 ? 2 : 5,
                        font: { size: 14 },
                        color: '#64748b',
                        callback: function(value) {
                            return value + '/' + maxScore;
                        }
                    },
                    title: {
                        display: true,
                        text: 'Score',
                        font: { size: 16, weight: 'bold' },
                        color: '#1e293b'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: { size: 14 },
                        color: '#64748b',
                        maxRotation: 45,
                        minRotation: 0
                    },
                    title: {
                        display: true,
                        text: 'Exam Date',
                        font: { size: 16, weight: 'bold' },
                        color: '#1e293b'
                    }
                }
            },
            hover: {
                animationDuration: 300
            }
        }
    });

    // Subtle celebration on score improvement
    if (scores.length >= 2 && scores[scores.length - 1] > scores[scores.length - 2]) {
        setTimeout(() => {
            container.style.boxShadow = '0 0 20px rgba(79, 70, 229, 0.4)';
            setTimeout(() => {
                container.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
            }, 1000);
        }, 1000);
    }
});