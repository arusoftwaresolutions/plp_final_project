// Dashboard JavaScript

let incomeExpenseChart = null;
let categoryChart = null;

// Load dashboard data
async function loadDashboardData() {
    try {
        const data = await dashboardAPI.getData();

        // Update financial overview
        updateFinancialOverview(data);

        // Update AI recommendations
        updateAIRecommendations(data.ai_recommendations);

        // Update community impact
        updateCommunityImpact(data);

        // Load charts
        loadDashboardCharts();

        // Load goals
        loadGoals();

    } catch (error) {
        showToast('Failed to load dashboard data', 'error');
        console.error('Dashboard error:', error);
    }
}

// Update financial overview cards
function updateFinancialOverview(data) {
    document.getElementById('balanceAmount').textContent = formatCurrency(data.balance);
    document.getElementById('incomeAmount').textContent = formatCurrency(data.monthly_income);
    document.getElementById('expensesAmount').textContent = formatCurrency(data.monthly_expenses);
    document.getElementById('savingsAmount').textContent = formatCurrency(data.savings);

    // Update card colors based on values
    const balanceCard = document.getElementById('balanceAmount').parentElement.parentElement;
    const savingsCard = document.getElementById('savingsAmount').parentElement.parentElement;

    balanceCard.className = data.balance >= 0 ? 'card bg-light' : 'card bg-light';
    savingsCard.className = data.savings >= 0 ? 'card bg-light' : 'card bg-light';
}

// Update AI recommendations
function updateAIRecommendations(recommendations) {
    const container = document.getElementById('aiRecommendations');

    if (!recommendations || recommendations.length === 0) {
        container.innerHTML = '<p class="text-muted">No recommendations available at this time.</p>';
        return;
    }

    const html = recommendations.map(rec => `
        <div class="alert alert-info mb-2">
            <i class="fas fa-lightbulb me-2"></i>
            ${rec}
        </div>
    `).join('');

    container.innerHTML = html;
}

// Update community impact
function updateCommunityImpact(data) {
    const container = document.getElementById('communityImpact');

    const html = `
        <div class="row text-center">
            <div class="col-6">
                <h4 class="text-primary">${formatCurrency(data.total_contributions)}</h4>
                <small class="text-muted">Total Contributions</small>
            </div>
            <div class="col-6">
                <h4 class="text-success">${data.campaigns_created}</h4>
                <small class="text-muted">Campaigns Created</small>
            </div>
        </div>
        <div class="row text-center mt-3">
            <div class="col-6">
                <h4 class="text-warning">${data.loans_received}</h4>
                <small class="text-muted">Loans Received</small>
            </div>
            <div class="col-6">
                <h4 class="text-info">${data.impact_score}</h4>
                <small class="text-muted">Impact Score</small>
            </div>
        </div>
    `;

    container.innerHTML = html;
}

// Load dashboard charts
async function loadDashboardCharts() {
    try {
        const chartData = await dashboardAPI.getCharts();
        createIncomeExpenseChart(chartData);
        createCategoryChart(chartData);
    } catch (error) {
        console.error('Chart loading error:', error);
    }
}

// Create income vs expense chart
function createIncomeExpenseChart(data) {
    const ctx = document.getElementById('incomeExpenseChart').getContext('2d');

    if (incomeExpenseChart) {
        incomeExpenseChart.destroy();
    }

    incomeExpenseChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => d.month),
            datasets: [
                {
                    label: 'Income',
                    data: data.map(d => d.income),
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    fill: true
                },
                {
                    label: 'Expenses',
                    data: data.map(d => d.expenses),
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    fill: true
                },
                {
                    label: 'Balance',
                    data: data.map(d => d.balance),
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': $' + context.parsed.y.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

// Create category spending chart
function createCategoryChart(data) {
    const ctx = document.getElementById('categoryChart').getContext('2d');

    if (categoryChart) {
        categoryChart.destroy();
    }

    // Get latest month data for category breakdown
    const latestData = data[data.length - 1];
    const expenseData = latestData ? latestData.expenses : 0;

    // Sample category data (in real app, this would come from API)
    const categoryData = {
        'Food': 0.3,
        'Transport': 0.15,
        'Housing': 0.25,
        'Utilities': 0.1,
        'Healthcare': 0.05,
        'Other': 0.15
    };

    categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(categoryData),
            datasets: [{
                data: Object.values(categoryData).map(v => v * expenseData),
                backgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56',
                    '#4BC0C0',
                    '#9966FF',
                    '#FF9F40'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return context.label + ': $' + context.parsed.toLocaleString() + ' (' + percentage + '%)';
                        }
                    }
                }
            }
        }
    });
}

// Load financial goals
async function loadGoals() {
    try {
        const goals = await dashboardAPI.getGoals();

        const container = document.querySelector('#dashboardSection .card-body');
        let goalsHtml = '<div class="row mt-4">';

        goals.forEach(goal => {
            const progress = (goal.current_amount / goal.target_amount) * 100;
            goalsHtml += `
                <div class="col-md-6 mb-3">
                    <div class="card">
                        <div class="card-body">
                            <h6>${goal.title}</h6>
                            <div class="progress mb-2">
                                <div class="progress-bar" role="progressbar" style="width: ${Math.min(progress, 100)}%"></div>
                            </div>
                            <small class="text-muted">
                                ${formatCurrency(goal.current_amount)} of ${formatCurrency(goal.target_amount)}
                            </small>
                        </div>
                    </div>
                </div>
            `;
        });

        goalsHtml += '</div>';
        container.insertAdjacentHTML('beforeend', goalsHtml);

    } catch (error) {
        console.error('Goals loading error:', error);
    }
}
