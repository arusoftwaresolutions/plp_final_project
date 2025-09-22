// Transactions JavaScript

let transactionChart = null;

// Load transactions
async function loadTransactions() {
    try {
        const transactions = await transactionsAPI.getAll();
        displayTransactions(transactions);

        // Load transaction summary
        loadTransactionSummary();

    } catch (error) {
        showToast('Failed to load transactions', 'error');
        console.error('Transactions error:', error);
    }
}

// Display transactions in table
function displayTransactions(transactions) {
    const container = document.getElementById('transactionsTable');

    if (!transactions || transactions.length === 0) {
        container.innerHTML = '<p class="text-muted">No transactions found. <a href="#" onclick="showAddTransaction()">Add your first transaction</a></p>';
        return;
    }

    const html = `
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Description</th>
                        <th>Category</th>
                        <th>Type</th>
                        <th>Amount</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${transactions.map(transaction => `
                        <tr class="transaction-row">
                            <td>${formatDate(transaction.date)}</td>
                            <td>${transaction.description}</td>
                            <td><span class="badge bg-secondary">${transaction.category}</span></td>
                            <td>
                                <span class="badge ${transaction.type === 'income' ? 'bg-success' : 'bg-danger'}">
                                    ${transaction.type}
                                </span>
                            </td>
                            <td class="${transaction.type === 'income' ? 'text-success' : 'text-danger'}">
                                ${transaction.type === 'income' ? '+' : '-'}${formatCurrency(Math.abs(transaction.amount))}
                            </td>
                            <td>
                                <button class="btn btn-sm btn-outline-danger" onclick="deleteTransaction(${transaction.id})">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;

    container.innerHTML = html;
}

// Load transaction summary
async function loadTransactionSummary() {
    try {
        const summary = await transactionsAPI.getSummary();

        // Create or update summary charts
        createTransactionSummaryChart(summary);

    } catch (error) {
        console.error('Summary loading error:', error);
    }
}

// Create transaction summary chart
function createTransactionSummaryChart(summary) {
    const ctx = document.createElement('canvas');
    ctx.id = 'transactionSummaryChart';
    ctx.style.maxHeight = '300px';

    const existingChart = document.getElementById('transactionSummaryChart');
    if (existingChart) {
        existingChart.remove();
    }

    const container = document.querySelector('#transactionsSection .card-body');
    container.appendChild(ctx);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Income', 'Expenses'],
            datasets: [{
                label: 'Amount',
                data: [summary.total_income, summary.total_expenses],
                backgroundColor: [
                    'rgba(40, 167, 69, 0.8)',
                    'rgba(220, 53, 69, 0.8)'
                ],
                borderColor: [
                    'rgba(40, 167, 69, 1)',
                    'rgba(220, 53, 69, 1)'
                ],
                borderWidth: 1
            }]
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
                            return '$' + context.parsed.y.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

// Show add transaction modal
function showAddTransaction() {
    // This would typically open a modal or form
    // For now, we'll create a simple inline form
    const container = document.querySelector('#transactionsSection .card-body');

    const formHtml = `
        <div id="addTransactionForm" class="mt-4 p-4 border rounded bg-light">
            <h6>Add New Transaction</h6>
            <form onsubmit="addTransaction(event)">
                <div class="row">
                    <div class="col-md-3">
                        <div class="mb-3">
                            <label class="form-label">Type</label>
                            <select class="form-control" id="transactionType" required>
                                <option value="income">Income</option>
                                <option value="expense">Expense</option>
                            </select>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="mb-3">
                            <label class="form-label">Amount</label>
                            <input type="number" class="form-control" id="transactionAmount" step="0.01" min="0" required>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="mb-3">
                            <label class="form-label">Category</label>
                            <select class="form-control" id="transactionCategory" required>
                                <option value="">Select Category</option>
                                <!-- Options will be populated by loadCategories() -->
                            </select>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="mb-3">
                            <label class="form-label">Description</label>
                            <input type="text" class="form-control" id="transactionDescription" required>
                        </div>
                    </div>
                </div>
                <div class="mt-3">
                    <button type="submit" class="btn btn-primary">Add Transaction</button>
                    <button type="button" class="btn btn-secondary" onclick="cancelAddTransaction()">Cancel</button>
                </div>
            </form>
        </div>
    `;

    container.insertAdjacentHTML('beforeend', formHtml);
    loadCategories();
}

// Load transaction categories
async function loadCategories() {
    try {
        const categories = await transactionsAPI.getCategories();
        const select = document.getElementById('transactionCategory');

        // Clear existing options
        select.innerHTML = '<option value="">Select Category</option>';

        // Add income categories
        const incomeOptgroup = document.createElement('optgroup');
        incomeOptgroup.label = 'Income';
        categories.income.forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category.charAt(0).toUpperCase() + category.slice(1);
            incomeOptgroup.appendChild(option);
        });

        // Add expense categories
        const expenseOptgroup = document.createElement('optgroup');
        expenseOptgroup.label = 'Expense';
        categories.expense.forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category.charAt(0).toUpperCase() + category.slice(1);
            expenseOptgroup.appendChild(option);
        });

        select.appendChild(incomeOptgroup);
        select.appendChild(expenseOptgroup);

    } catch (error) {
        console.error('Categories loading error:', error);
    }
}

// Add transaction
async function addTransaction(event) {
    event.preventDefault();

    const type = document.getElementById('transactionType').value;
    const amount = parseFloat(document.getElementById('transactionAmount').value);
    const category = document.getElementById('transactionCategory').value;
    const description = document.getElementById('transactionDescription').value;

    if (!category) {
        showToast('Please select a category', 'error');
        return;
    }

    try {
        await transactionsAPI.create({
            type: type,
            amount: amount,
            category: category,
            description: description
        });

        showToast('Transaction added successfully', 'success');
        cancelAddTransaction();
        loadTransactions(); // Refresh the list

    } catch (error) {
        showToast('Failed to add transaction', 'error');
        console.error('Add transaction error:', error);
    }
}

// Cancel add transaction
function cancelAddTransaction() {
    const form = document.getElementById('addTransactionForm');
    if (form) {
        form.remove();
    }
}

// Delete transaction
async function deleteTransaction(transactionId) {
    if (!confirm('Are you sure you want to delete this transaction?')) {
        return;
    }

    try {
        await transactionsAPI.delete(transactionId);
        showToast('Transaction deleted successfully', 'success');
        loadTransactions(); // Refresh the list
    } catch (error) {
        showToast('Failed to delete transaction', 'error');
        console.error('Delete transaction error:', error);
    }
}
