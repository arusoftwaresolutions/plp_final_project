// Profile JavaScript

// Load profile
async function loadProfile() {
    try {
        const profile = await authAPI.getProfile();
        const stats = await profileAPI.getStats();

        displayProfile(profile);
        displayProfileStats(stats);

    } catch (error) {
        showToast('Failed to load profile', 'error');
        console.error('Profile error:', error);
    }
}

// Display profile information
function displayProfile(profile) {
    const container = document.getElementById('profileContent');

    const html = `
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h6>Personal Information</h6>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <label class="form-label"><strong>Full Name:</strong></label>
                            <div id="profileName">${profile.full_name || 'Not set'}</div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label"><strong>Email:</strong></label>
                            <div>${profile.email}</div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label"><strong>Username:</strong></label>
                            <div>${profile.username}</div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label"><strong>Monthly Income:</strong></label>
                            <div id="profileIncome">${formatCurrency(profile.monthly_income)}</div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label"><strong>Member Since:</strong></label>
                            <div>${formatDate(profile.created_at)}</div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label"><strong>Account Type:</strong></label>
                            <div>
                                <span class="badge ${profile.is_admin ? 'bg-danger' : 'bg-primary'}">
                                    ${profile.is_admin ? 'Administrator' : 'Regular User'}
                                </span>
                            </div>
                        </div>
                        <button class="btn btn-primary" onclick="editProfile()">
                            <i class="fas fa-edit me-1"></i>Edit Profile
                        </button>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div id="profileEditForm" style="display: none;">
                    <div class="card">
                        <div class="card-header">
                            <h6>Edit Profile</h6>
                        </div>
                        <div class="card-body">
                            <form onsubmit="updateProfile(event)">
                                <div class="mb-3">
                                    <label class="form-label">Full Name</label>
                                    <input type="text" class="form-control" id="editFullName" value="${profile.full_name || ''}">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Monthly Income</label>
                                    <input type="number" class="form-control" id="editMonthlyIncome" value="${profile.monthly_income}" step="0.01" min="0">
                                </div>
                                <button type="submit" class="btn btn-success">Save Changes</button>
                                <button type="button" class="btn btn-secondary" onclick="cancelEditProfile()">Cancel</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    container.innerHTML = html;
}

// Display profile statistics
function displayProfileStats(stats) {
    const container = document.getElementById('profileContent');

    const html = `
        <div class="row mt-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h6>Financial Summary</h6>
                    </div>
                    <div class="card-body">
                        <div class="row text-center">
                            <div class="col-6">
                                <h4 class="text-success">${formatCurrency(stats.transaction_stats.total_income)}</h4>
                                <small class="text-muted">Total Income</small>
                            </div>
                            <div class="col-6">
                                <h4 class="text-danger">${formatCurrency(stats.transaction_stats.total_expenses)}</h4>
                                <small class="text-muted">Total Expenses</small>
                            </div>
                        </div>
                        <hr>
                        <div class="text-center">
                            <h4 class="${stats.transaction_stats.net_worth >= 0 ? 'text-success' : 'text-danger'}">
                                ${formatCurrency(stats.transaction_stats.net_worth)}
                            </h4>
                            <small class="text-muted">Net Worth</small>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h6>Activity Summary</h6>
                    </div>
                    <div class="card-body">
                        <div class="row text-center">
                            <div class="col-4">
                                <h5 class="text-primary">${stats.campaign_stats.campaigns_created}</h5>
                                <small class="text-muted">Campaigns Created</small>
                            </div>
                            <div class="col-4">
                                <h5 class="text-success">${stats.contribution_stats.contributions_made}</h5>
                                <small class="text-muted">Contributions Made</small>
                            </div>
                            <div class="col-4">
                                <h5 class="text-info">${stats.loan_stats.loans_approved}</h5>
                                <small class="text-muted">Loans Approved</small>
                            </div>
                        </div>
                        <hr>
                        <div class="row text-center">
                            <div class="col-6">
                                <h5 class="text-warning">${formatCurrency(stats.campaign_stats.total_raised)}</h5>
                                <small class="text-muted">Total Raised</small>
                            </div>
                            <div class="col-6">
                                <h5 class="text-info">${formatCurrency(stats.contribution_stats.total_contributed)}</h5>
                                <small class="text-muted">Total Contributed</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    container.insertAdjacentHTML('beforeend', html);
}

// Edit profile
function editProfile() {
    document.getElementById('profileEditForm').style.display = 'block';
    document.querySelector('.col-md-6:first-child .card').style.display = 'none';
}

// Cancel edit profile
function cancelEditProfile() {
    document.getElementById('profileEditForm').style.display = 'none';
    document.querySelector('.col-md-6:first-child .card').style.display = 'block';
}

// Update profile
async function updateProfile(event) {
    event.preventDefault();

    const fullName = document.getElementById('editFullName').value;
    const monthlyIncome = parseFloat(document.getElementById('editMonthlyIncome').value);

    try {
        await authAPI.updateProfile({
            full_name: fullName,
            monthly_income: monthlyIncome
        });

        showToast('Profile updated successfully', 'success');
        cancelEditProfile();
        loadProfile(); // Refresh the profile

    } catch (error) {
        showToast('Failed to update profile', 'error');
        console.error('Update profile error:', error);
    }
}

// Load AI advisor content
async function loadAIAdvisor() {
    const container = document.getElementById('aiAdvisorContent');

    try {
        const data = await dashboardAPI.getData();

        const html = `
            <div class="row">
                <div class="col-md-8">
                    <h6>AI Financial Analysis</h6>
                    <div id="aiAnalysis">
                        ${data.spending_analysis ? `
                            <div class="alert alert-info">
                                <h6>Spending Overview</h6>
                                <p>Total Expenses: ${formatCurrency(data.spending_analysis.total_expenses)}</p>
                                <p>Spending Ratio: ${(data.spending_analysis.spending_ratio * 100).toFixed(1)}%</p>
                            </div>
                            <h6>Spending by Category</h6>
                            <div class="row">
                                ${Object.entries(data.spending_analysis.category_breakdown).map(([category, amount]) => `
                                    <div class="col-md-6 mb-2">
                                        <div class="d-flex justify-content-between">
                                            <span>${category.charAt(0).toUpperCase() + category.slice(1)}:</span>
                                            <strong>${formatCurrency(amount)}</strong>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        ` : '<p class="text-muted">No spending data available for analysis.</p>'}
                    </div>
                </div>
                <div class="col-md-4">
                    <h6>AI Recommendations</h6>
                    <div id="aiAdvisorRecommendations">
                        ${data.ai_recommendations && data.ai_recommendations.length > 0 ?
                            data.ai_recommendations.map(rec => `
                                <div class="alert alert-light mb-2">
                                    <i class="fas fa-lightbulb text-warning me-2"></i>
                                    ${rec}
                                </div>
                            `).join('') :
                            '<p class="text-muted">No recommendations available.</p>'
                        }
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = html;

    } catch (error) {
        container.innerHTML = '<p class="text-muted">Unable to load AI advisor content.</p>';
        console.error('AI advisor error:', error);
    }
}
