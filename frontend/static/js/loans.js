// Loans JavaScript

// Load loans
async function loadLoans() {
    try {
        const offers = await loansAPI.getOffers();
        const recommendations = await loansAPI.getRecommendations();
        const applications = await loansAPI.getApplications();

        displayLoanOffers(offers, recommendations);
        displayLoanApplications(applications);

    } catch (error) {
        showToast('Failed to load loan information', 'error');
        console.error('Loans error:', error);
    }
}

// Display loan offers
function displayLoanOffers(offers, recommendations) {
    const container = document.getElementById('loansContent');

    let html = '<h6>Available Loan Offers</h6>';

    if (!offers || offers.length === 0) {
        html += '<p class="text-muted">No loan offers available at this time.</p>';
    } else {
        html += '<div class="row">';

        offers.forEach(offer => {
            const recommendation = recommendations.find(r => r.loan_id === offer.id);
            const fitScore = recommendation ? recommendation.fit_score : 0;

            html += `
                <div class="col-md-6 mb-3">
                    <div class="card">
                        <div class="card-body">
                            <h6 class="card-title">${offer.title}</h6>
                            <p class="card-text text-muted">${offer.description}</p>

                            <div class="row">
                                <div class="col-6">
                                    <small><strong>Max Amount:</strong></small><br>
                                    <span class="text-success">${formatCurrency(offer.max_amount)}</span>
                                </div>
                                <div class="col-6">
                                    <small><strong>Interest Rate:</strong></small><br>
                                    <span class="text-primary">${offer.interest_rate}%</span>
                                </div>
                            </div>

                            <div class="row mt-2">
                                <div class="col-6">
                                    <small><strong>Max Term:</strong></small><br>
                                    <span>${offer.max_term_months} months</span>
                                </div>
                                <div class="col-6">
                                    <small><strong>Min Credit Score:</strong></small><br>
                                    <span>${offer.min_credit_score}</span>
                                </div>
                            </div>

                            ${recommendation ? `
                                <div class="mt-2">
                                    <small><strong>AI Recommendation:</strong></small><br>
                                    <div class="progress mb-1" style="height: 5px;">
                                        <div class="progress-bar bg-${getScoreColor(fitScore)}" style="width: ${fitScore * 100}%"></div>
                                    </div>
                                    <small class="text-muted">${recommendation.reasoning}</small>
                                </div>
                            ` : ''}

                            <button class="btn btn-primary btn-sm mt-2" onclick="applyForLoan(${offer.id})">
                                Apply Now
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });

        html += '</div>';
    }

    container.innerHTML = html;
}

// Get score color based on fit score
function getScoreColor(score) {
    if (score >= 0.8) return 'success';
    if (score >= 0.6) return 'info';
    if (score >= 0.4) return 'warning';
    return 'danger';
}

// Display loan applications
function displayLoanApplications(applications) {
    let html = '<h6 class="mt-4">My Loan Applications</h6>';

    if (!applications || applications.length === 0) {
        html += '<p class="text-muted">No loan applications found.</p>';
    } else {
        html += '<div class="table-responsive"><table class="table table-sm"><thead><tr><th>Loan Type</th><th>Amount</th><th>Status</th><th>Monthly Payment</th><th>Actions</th></tr></thead><tbody>';

        applications.forEach(app => {
            const statusBadge = getStatusBadge(app.status);
            html += `
                <tr>
                    <td>${app.loan_title}</td>
                    <td>${formatCurrency(app.amount)}</td>
                    <td><span class="badge ${statusBadge}">${app.status}</span></td>
                    <td>${formatCurrency(app.monthly_payment)}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-info" onclick="viewApplication(${app.id})">
                            <i class="fas fa-eye"></i>
                        </button>
                        ${app.status === 'approved' ? `<button class="btn btn-sm btn-success" onclick="makeRepayment(${app.id})">
                            <i class="fas fa-credit-card"></i>
                        </button>` : ''}
                    </td>
                </tr>
            `;
        });

        html += '</tbody></table></div>';
    }

    document.getElementById('loansContent').insertAdjacentHTML('beforeend', html);
}

// Get status badge class
function getStatusBadge(status) {
    switch (status) {
        case 'approved': return 'bg-success';
        case 'rejected': return 'bg-danger';
        case 'completed': return 'bg-info';
        default: return 'bg-warning';
    }
}

// Apply for loan
async function applyForLoan(offerId) {
    const amount = prompt('Enter loan amount:');
    const termMonths = prompt('Enter term in months:');

    if (!amount || isNaN(amount) || parseFloat(amount) <= 0) {
        showToast('Please enter a valid amount', 'error');
        return;
    }

    if (!termMonths || isNaN(termMonths) || parseInt(termMonths) <= 0) {
        showToast('Please enter a valid term', 'error');
        return;
    }

    try {
        await loansAPI.apply({
            loan_offer_id: offerId,
            amount: parseFloat(amount),
            term_months: parseInt(termMonths)
        });

        showToast('Loan application submitted successfully', 'success');
        loadLoans(); // Refresh the list

    } catch (error) {
        showToast('Failed to submit loan application', 'error');
        console.error('Apply loan error:', error);
    }
}

// View application details
async function viewApplication(applicationId) {
    try {
        const data = await loansAPI.getApplication(applicationId);

        const modalHtml = `
            <div id="applicationModal" class="modal" style="display: block;">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Loan Application Details</h5>
                            <button type="button" class="btn-close" onclick="closeApplicationModal()"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6>Application Summary</h6>
                                    <p><strong>Loan Amount:</strong> ${formatCurrency(data.application.amount)}</p>
                                    <p><strong>Term:</strong> ${data.application.term_months} months</p>
                                    <p><strong>Monthly Payment:</strong> ${formatCurrency(data.application.monthly_payment)}</p>
                                    <p><strong>Total Amount:</strong> ${formatCurrency(data.application.total_amount)}</p>
                                    <p><strong>Status:</strong> <span class="badge ${getStatusBadge(data.application.status)}">${data.application.status}</span></p>
                                </div>
                                <div class="col-md-6">
                                    <h6>Repayment Schedule</h6>
                                    <div class="table-responsive">
                                        <table class="table table-sm">
                                            <thead>
                                                <tr>
                                                    <th>Due Date</th>
                                                    <th>Amount</th>
                                                    <th>Status</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                ${data.repayments ? data.repayments.map(repayment => `
                                                    <tr>
                                                        <td>${formatDate(repayment.due_date)}</td>
                                                        <td>${formatCurrency(repayment.amount)}</td>
                                                        <td>
                                                            <span class="badge ${repayment.is_paid ? 'bg-success' : 'bg-warning'}">
                                                                ${repayment.is_paid ? 'Paid' : 'Pending'}
                                                            </span>
                                                        </td>
                                                    </tr>
                                                `).join('') : '<tr><td colspan="3">No repayments scheduled</td></tr>'}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>

                            ${data.next_payment && !data.next_payment.is_paid ? `
                                <div class="alert alert-info mt-3">
                                    <strong>Next Payment Due:</strong> ${formatCurrency(data.next_payment.amount)} on ${formatDate(data.next_payment.due_date)}
                                    <button class="btn btn-success btn-sm ms-3" onclick="makeRepayment(${data.application.id})">
                                        Make Payment
                                    </button>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);

    } catch (error) {
        showToast('Failed to load application details', 'error');
        console.error('View application error:', error);
    }
}

// Close application modal
function closeApplicationModal() {
    const modal = document.getElementById('applicationModal');
    if (modal) {
        modal.remove();
    }
}

// Make loan repayment
async function makeRepayment(applicationId) {
    const amount = prompt('Enter payment amount:');

    if (!amount || isNaN(amount) || parseFloat(amount) <= 0) {
        showToast('Please enter a valid amount', 'error');
        return;
    }

    try {
        await loansAPI.makeRepayment(applicationId, parseFloat(amount));
        showToast('Payment processed successfully', 'success');
        closeApplicationModal();
        loadLoans(); // Refresh the list

    } catch (error) {
        showToast('Failed to process payment', 'error');
        console.error('Repayment error:', error);
    }
}
