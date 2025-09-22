// Crowdfunding JavaScript

// Load campaigns
async function loadCampaigns() {
    try {
        const campaigns = await crowdfundingAPI.getCampaigns();
        displayCampaigns(campaigns);

        // Load featured campaigns
        loadFeaturedCampaigns();

    } catch (error) {
        showToast('Failed to load campaigns', 'error');
        console.error('Campaigns error:', error);
    }
}

// Display campaigns
function displayCampaigns(campaigns) {
    const container = document.getElementById('campaignsList');

    if (!campaigns || campaigns.length === 0) {
        container.innerHTML = '<p class="text-muted">No active campaigns found. <a href="#" onclick="showCreateCampaign()">Create the first campaign</a></p>';
        return;
    }

    const html = campaigns.map(campaign => {
        const progress = (campaign.current_amount / campaign.goal_amount) * 100;
        const daysRemaining = Math.ceil((new Date(campaign.end_date) - new Date()) / (1000 * 60 * 60 * 24));

        return `
            <div class="card campaign-card mb-3">
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-8">
                            <h5 class="card-title">${campaign.title}</h5>
                            <p class="card-text text-muted">${campaign.description.substring(0, 150)}...</p>
                            <div class="mb-2">
                                <span class="badge bg-primary">${campaign.category}</span>
                                <small class="text-muted ms-2">by ${campaign.creator_name}</small>
                            </div>
                        </div>
                        <div class="col-md-4 text-end">
                            <h4 class="text-success">${formatCurrency(campaign.current_amount)}</h4>
                            <small class="text-muted">of ${formatCurrency(campaign.goal_amount)}</small>
                            <div class="progress mb-2">
                                <div class="progress-bar" role="progressbar" style="width: ${Math.min(progress, 100)}%"></div>
                            </div>
                            <small class="text-muted">${daysRemaining} days remaining</small>
                        </div>
                    </div>
                    <div class="row mt-3">
                        <div class="col-12">
                            <button class="btn btn-sm btn-outline-primary me-2" onclick="viewCampaign(${campaign.id})">
                                <i class="fas fa-eye me-1"></i>View Details
                            </button>
                            <button class="btn btn-sm btn-success" onclick="contributeToCampaign(${campaign.id})">
                                <i class="fas fa-heart me-1"></i>Contribute
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');

    container.innerHTML = html;
}

// Load featured campaigns
async function loadFeaturedCampaigns() {
    try {
        const featured = await crowdfundingAPI.getFeatured();
        displayFeaturedCampaigns(featured);
    } catch (error) {
        console.error('Featured campaigns error:', error);
    }
}

// Display featured campaigns
function displayFeaturedCampaigns(featured) {
    const container = document.getElementById('featuredCampaigns');

    let html = '<h6>Most Funded</h6>';

    if (featured.most_funded && featured.most_funded.length > 0) {
        html += featured.most_funded.map(campaign => {
            const progress = (campaign.current_amount / campaign.goal_amount) * 100;
            return `
                <div class="card mb-2">
                    <div class="card-body p-3">
                        <h6 class="card-title mb-1">${campaign.title}</h6>
                        <div class="progress mb-1" style="height: 5px;">
                            <div class="progress-bar" style="width: ${Math.min(progress, 100)}%"></div>
                        </div>
                        <small class="text-muted">${formatCurrency(campaign.current_amount)}</small>
                    </div>
                </div>
            `;
        }).join('');
    } else {
        html += '<p class="text-muted">No featured campaigns</p>';
    }

    container.innerHTML = html;
}

// Show create campaign form
function showCreateCampaign() {
    const container = document.querySelector('#crowdfundingSection .col-md-8 .card-body');

    const formHtml = `
        <div id="createCampaignForm" class="mt-4 p-4 border rounded bg-light">
            <h6>Create New Campaign</h6>
            <form onsubmit="createCampaign(event)">
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">Campaign Title</label>
                            <input type="text" class="form-control" id="campaignTitle" required>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">Goal Amount</label>
                            <input type="number" class="form-control" id="campaignGoal" step="0.01" min="0" required>
                        </div>
                    </div>
                </div>
                <div class="mb-3">
                    <label class="form-label">Description</label>
                    <textarea class="form-control" id="campaignDescription" rows="3" required></textarea>
                </div>
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">Category</label>
                            <select class="form-control" id="campaignCategory" required>
                                <option value="">Select Category</option>
                                <!-- Options will be populated by loadCampaignCategories() -->
                            </select>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">End Date</label>
                            <input type="date" class="form-control" id="campaignEndDate" required>
                        </div>
                    </div>
                </div>
                <div class="mt-3">
                    <button type="submit" class="btn btn-primary">Create Campaign</button>
                    <button type="button" class="btn btn-secondary" onclick="cancelCreateCampaign()">Cancel</button>
                </div>
            </form>
        </div>
    `;

    container.insertAdjacentHTML('beforeend', formHtml);
    loadCampaignCategories();
}

// Load campaign categories
async function loadCampaignCategories() {
    try {
        const categories = await crowdfundingAPI.getCategories();
        const select = document.getElementById('campaignCategory');

        select.innerHTML = '<option value="">Select Category</option>';

        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category.charAt(0).toUpperCase() + category.slice(1).replace('_', ' ');
            select.appendChild(option);
        });

    } catch (error) {
        console.error('Categories loading error:', error);
    }
}

// Create campaign
async function createCampaign(event) {
    event.preventDefault();

    const title = document.getElementById('campaignTitle').value;
    const description = document.getElementById('campaignDescription').value;
    const goalAmount = parseFloat(document.getElementById('campaignGoal').value);
    const category = document.getElementById('campaignCategory').value;
    const endDate = document.getElementById('campaignEndDate').value;

    if (!category) {
        showToast('Please select a category', 'error');
        return;
    }

    try {
        await crowdfundingAPI.create({
            title: title,
            description: description,
            goal_amount: goalAmount,
            category: category,
            end_date: new Date(endDate).toISOString()
        });

        showToast('Campaign created successfully', 'success');
        cancelCreateCampaign();
        loadCampaigns(); // Refresh the list

    } catch (error) {
        showToast('Failed to create campaign', 'error');
        console.error('Create campaign error:', error);
    }
}

// Cancel create campaign
function cancelCreateCampaign() {
    const form = document.getElementById('createCampaignForm');
    if (form) {
        form.remove();
    }
}

// View campaign details
async function viewCampaign(campaignId) {
    try {
        const data = await crowdfundingAPI.getCampaign(campaignId);

        // Create modal for campaign details
        const modalHtml = `
            <div id="campaignModal" class="modal" style="display: block;">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${data.campaign.title}</h5>
                            <button type="button" class="btn-close" onclick="closeCampaignModal()"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-8">
                                    <p>${data.campaign.description}</p>
                                    <p><strong>Category:</strong> <span class="badge bg-primary">${data.campaign.category}</span></p>
                                    <p><strong>Created by:</strong> ${data.campaign.creator_name}</p>
                                    <p><strong>End Date:</strong> ${formatDate(data.campaign.end_date)}</p>
                                    <p><strong>Days Remaining:</strong> ${data.days_remaining}</p>
                                </div>
                                <div class="col-md-4">
                                    <h4 class="text-success">${formatCurrency(data.campaign.current_amount)}</h4>
                                    <p class="text-muted">of ${formatCurrency(data.campaign.goal_amount)}</p>
                                    <div class="progress mb-3">
                                        <div class="progress-bar" style="width: ${data.progress}%"></div>
                                    </div>
                                    <button class="btn btn-success" onclick="contributeToCampaign(${data.campaign.id})">
                                        Contribute Now
                                    </button>
                                </div>
                            </div>

                            <h6 class="mt-4">Recent Contributions</h6>
                            ${data.contributions && data.contributions.length > 0 ?
                                data.contributions.slice(0, 5).map(contrib => `
                                    <div class="border-bottom py-2">
                                        <strong>${formatCurrency(contrib.amount)}</strong>
                                        ${contrib.message ? ` - ${contrib.message}` : ''}
                                        <small class="text-muted"> by Anonymous</small>
                                    </div>
                                `).join('') :
                                '<p class="text-muted">No contributions yet</p>'
                            }
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);

    } catch (error) {
        showToast('Failed to load campaign details', 'error');
        console.error('View campaign error:', error);
    }
}

// Close campaign modal
function closeCampaignModal() {
    const modal = document.getElementById('campaignModal');
    if (modal) {
        modal.remove();
    }
}

// Contribute to campaign
async function contributeToCampaign(campaignId) {
    const amount = prompt('Enter contribution amount:');

    if (!amount || isNaN(amount) || parseFloat(amount) <= 0) {
        showToast('Please enter a valid amount', 'error');
        return;
    }

    const message = prompt('Leave a message (optional):');

    try {
        await crowdfundingAPI.contribute(campaignId, {
            amount: parseFloat(amount),
            message: message
        });

        showToast('Contribution successful!', 'success');
        closeCampaignModal();
        loadCampaigns(); // Refresh the list

    } catch (error) {
        showToast('Failed to contribute', 'error');
        console.error('Contribute error:', error);
    }
}
