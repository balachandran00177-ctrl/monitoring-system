const API_URL = 'http://localhost:5000/api';
let currentUser = null;
let weeklyChart = null;
let costChart = null;
let predictionChart = null;

// Check authentication
function checkAuth() {
    const userData = localStorage.getItem('user');
    if (!userData) {
        window.location.href = '/';
        return null;
    }

    currentUser = JSON.parse(userData);
    document.getElementById('userName').textContent = currentUser.username;
    return currentUser;
}

// Initialize dashboard
window.addEventListener('DOMContentLoaded', () => {
    if (!checkAuth()) return;

    loadStats();
    loadConsumptionData();
    loadAlerts();
    loadRecommendations();
    loadHealthScore();
});

// Section navigation
function showSection(sectionName) {
    const sections = document.querySelectorAll('.section');
    const navItems = document.querySelectorAll('.nav-item');

    sections.forEach(section => section.classList.remove('active'));
    navItems.forEach(item => item.classList.remove('active'));

    document.getElementById(`${sectionName}Section`).classList.add('active');

    const activeNav = Array.from(navItems).find(item =>
        item.getAttribute('onclick').includes(sectionName)
    );
    if (activeNav) activeNav.classList.add('active');
}

// Load statistics
async function loadStats() {
    try {
        const response = await fetch(`${API_URL}/stats/${currentUser.user_id}`);
        const data = await response.json();

        if (data.success) {
            const stats = data.stats;

            document.getElementById('todayConsumption').textContent =
                `${stats.today_consumption.toFixed(2)} kWh`;
            document.getElementById('todayCost').textContent =
                `$${stats.today_cost.toFixed(2)}`;
            document.getElementById('monthConsumption').textContent =
                `${stats.month_consumption.toFixed(2)} kWh`;
            document.getElementById('avgConsumption').textContent =
                `${stats.avg_daily_consumption.toFixed(2)} kWh`;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load consumption data
async function loadConsumptionData() {
    const period = document.getElementById('periodFilter')?.value || 'week';

    try {
        const response = await fetch(`${API_URL}/consumption/${currentUser.user_id}?period=${period}`);
        const result = await response.json();

        if (result.success) {
            updateCharts(result.data);
            updateConsumptionTable(result.data);
        }
    } catch (error) {
        console.error('Error loading consumption data:', error);
    }
}

// Update charts
function updateCharts(data) {
    // Group data by date
    const groupedData = {};

    data.forEach(item => {
        const date = new Date(item.timestamp).toLocaleDateString();
        if (!groupedData[date]) {
            groupedData[date] = { consumption: 0, cost: 0 };
        }
        groupedData[date].consumption += item.consumption_kwh;
        groupedData[date].cost += item.cost;
    });

    const dates = Object.keys(groupedData).slice(0, 7).reverse();
    const consumption = dates.map(date => groupedData[date].consumption.toFixed(2));
    const costs = dates.map(date => groupedData[date].cost.toFixed(2));

    // Weekly consumption chart
    const weeklyCtx = document.getElementById('weeklyChart');
    if (weeklyChart) weeklyChart.destroy();

    weeklyChart = new Chart(weeklyCtx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Consumption (kWh)',
                data: consumption,
                borderColor: '#4f46e5',
                backgroundColor: 'rgba(79, 70, 229, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // Cost chart
    const costCtx = document.getElementById('costChart');
    if (costChart) costChart.destroy();

    costChart = new Chart(costCtx, {
        type: 'bar',
        data: {
            labels: dates,
            datasets: [{
                label: 'Cost ($)',
                data: costs,
                backgroundColor: '#7c3aed',
                borderColor: '#6d28d9',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Update consumption table
function updateConsumptionTable(data) {
    const tbody = document.getElementById('consumptionTableBody');

    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">No data available</td></tr>';
        return;
    }

    tbody.innerHTML = data.map(item => `
         <tr>
             <td>${new Date(item.timestamp).toLocaleString()}</td>
             <td>${item.consumption_kwh.toFixed(2)}</td>
             <td>$${item.cost.toFixed(2)}</td>
             <td>${item.device_name}</td>
             <td>${item.location}</td>
             <td>
                 <button onclick="deleteReading(${item.id})" class="btn btn-danger">
                     Delete
                 </button>
             </td>
         </tr>
    `).join('');
}

// Load health score
async function loadHealthScore() {
    try {
        const response = await fetch(`${API_URL}/consumption/${currentUser.user_id}?period=month`);
        const result = await response.json();

        if (result.success && result.data.length > 0) {
            // Calculate simple health score based on consistency
            const consumptions = result.data.map(d => d.consumption_kwh);
            const avg = consumptions.reduce((a, b) => a + b, 0) / consumptions.length;
            const variance = consumptions.reduce((sum, val) => sum + Math.pow(val - avg, 2), 0) / consumptions.length;
            const stdDev = Math.sqrt(variance);

            const variabilityScore = Math.max(0, 100 - (stdDev / avg * 100));
            const score = Math.round(variabilityScore);

            let status = 'Poor';
            if (score >= 80) status = 'Excellent';
            else if (score >= 60) status = 'Good';
            else if (score >= 40) status = 'Fair';

            document.getElementById('scoreValue').textContent = score;
            document.getElementById('scoreStatus').textContent = status;
            document.getElementById('scoreMessage').textContent =
                `Your consumption pattern is ${status.toLowerCase()}`;
        }
    } catch (error) {
        console.error('Error loading health score:', error);
    }
}

// Load predictions
async function loadPredictions() {
    const days = document.getElementById('predictionDays')?.value || 7;

    try {
        const response = await fetch(`${API_URL}/predict/${currentUser.user_id}?days=${days}`);
        const result = await response.json();

        if (result.success) {
            updatePredictionChart(result.predictions);
            updatePredictionTable(result.predictions);
        } else {
            alert(result.message || 'Unable to generate predictions');
        }
    } catch (error) {
        console.error('Error loading predictions:', error);
        alert('Error generating predictions');
    }
}

// Update prediction chart
function updatePredictionChart(predictions) {
    const ctx = document.getElementById('predictionChart');
    if (predictionChart) predictionChart.destroy();

    predictionChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: predictions.map(p => p.date),
            datasets: [{
                label: 'Predicted Consumption (kWh)',
                data: predictions.map(p => p.value),
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.4,
                fill: true
            }, {
                label: 'Upper Range',
                data: predictions.map(p => p.range_high),
                borderColor: '#f59e0b',
                borderDash: [5, 5],
                fill: false
            }, {
                label: 'Lower Range',
                data: predictions.map(p => p.range_low),
                borderColor: '#f59e0b',
                borderDash: [5, 5],
                fill: false
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function deleteReading(id){

    if(!confirm("Delete this reading?")){
        return;
    }

    fetch(`http://127.0.0.1:5000/api/consumption/delete/${id}`,{
        method:"DELETE"
    })
    .then(res => res.json())
    .then(data => {

        if(data.success){
            alert("Reading deleted successfully");
            location.reload();
        }
        else{
            alert("Delete failed");
        }

    });
}

// Update prediction table
function updatePredictionTable(predictions) {
    const tbody = document.getElementById('predictionTableBody');

    tbody.innerHTML = predictions.map(p => `
        <tr>
            <td>${p.date}</td>
            <td>${p.value} kWh</td>
            <td>${p.range_low} - ${p.range_high} kWh</td>
            <td>${(p.confidence * 100).toFixed(0)}%</td>
        </tr>
    `).join('');
}

// Load alerts
async function loadAlerts() {
    try {
        const response = await fetch(`${API_URL}/alerts/${currentUser.user_id}`);
        const result = await response.json();

        if (result.success) {
            const alertsList = document.getElementById('alertsList');

            if (result.alerts.length === 0) {
                alertsList.innerHTML = '<p class="text-center">No alerts</p>';
                return;
            }

            alertsList.innerHTML = result.alerts.map(alert => `
                <div class="alert-item ${alert.severity}">
                    <div class="alert-header">
                        <span class="alert-type">${alert.alert_type.toUpperCase()}</span>
                        <span class="alert-time">${new Date(alert.timestamp).toLocaleString()}</span>
                    </div>
                    <p>${alert.message}</p>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading alerts:', error);
    }
}

function exportData() {

    fetch("http://127.0.0.1:5000/api/consumption")
    .then(res => res.json())
    .then(data => {

        let csv = "Date,Consumption(kWh),Cost,Device,Location\n";

        data.forEach(item => {
            csv += `${item.timestamp},${item.consumption_kwh},${item.cost},${item.device_name},${item.location}\n`;
        });

        const blob = new Blob([csv], { type: "text/csv" });
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = "energy_data.csv";
        a.click();

    });

}

// Load recommendations
async function loadRecommendations() {
    try {
        const response = await fetch(`${API_URL}/recommendations/${currentUser.user_id}`);
        const result = await response.json();

        if (result.success) {
            const recList = document.getElementById('recommendationsList');

            recList.innerHTML = result.recommendations.map(rec => `
                <div class="recommendation-card">
                    <h3>${rec.title}</h3>
                    <p>${rec.message}</p>
                    <span class="savings-badge">💰 Potential Savings: ${rec.savings_potential}</span>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading recommendations:', error);
    }
}

// Show add consumption modal
function showAddConsumption() {
    document.getElementById('addConsumptionModal').classList.add('active');
}

// Close add consumption modal
function closeAddConsumption() {
    document.getElementById('addConsumptionModal').classList.remove('active');
}

// Add consumption form handler
document.getElementById('addConsumptionForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const consumption_kwh = parseFloat(document.getElementById('consumption').value);
    const cost = parseFloat(document.getElementById('cost').value);
    const device_name = document.getElementById('device').value;
    const location = document.getElementById('location').value;

    try {
        const response = await fetch(`${API_URL}/consumption/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: currentUser.user_id,
                consumption_kwh,
                cost,
                device_name,
                location
            })
        });

        const result = await response.json();

        if (result.success) {
            alert('Energy reading added successfully!');
            closeAddConsumption();
            document.getElementById('addConsumptionForm').reset();
            refreshData();
        } else {
            alert('Failed to add reading');
        }
    } catch (error) {
        console.error('Error adding consumption:', error);
        alert('Error adding reading');
    }
});

// Refresh data
function refreshData() {
    loadStats();
    loadConsumptionData();
    loadAlerts();
    loadHealthScore();
}

// Export data
async function exportData() {
    const format = 'csv';
    window.open(`${API_URL}/export/${currentUser.user_id}?format=${format}`, '_blank');
}

// Save settings
function saveSettings() {
    const rate = document.getElementById('electricityRate').value;
    const threshold = document.getElementById('alertThreshold').value;

    localStorage.setItem('settings', JSON.stringify({ rate, threshold }));
    alert('Settings saved successfully!');
}

// Logout
function logout() {
    localStorage.removeItem('user');
    window.location.href = '/';
}

// Close modal on outside click
window.onclick = function(event) {
    const modal = document.getElementById('addConsumptionModal');
    if (event.target === modal) {
        closeAddConsumption();
    }
}
