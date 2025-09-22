// API utility functions

const API_BASE = '/api';

// Generic API request function
async function apiRequest(endpoint, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };

    if (token) {
        defaultOptions.headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers,
        },
    });

    if (response.status === 401) {
        logout();
        throw new Error('Unauthorized');
    }

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(error.detail || 'Request failed');
    }

    return response.json();
}

// Authentication API
const authAPI = {
    login: async (email, password) => {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Login failed' }));
            throw new Error(error.detail || 'Login failed');
        }

        return response.json();
    },

    register: async (userData) => {
        return apiRequest('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    },

    getProfile: async () => {
        return apiRequest('/auth/me');
    },

    updateProfile: async (profileData) => {
        return apiRequest('/auth/profile', {
            method: 'PUT',
            body: JSON.stringify(profileData)
        });
    }
};

// Dashboard API
const dashboardAPI = {
    getData: async () => {
        return apiRequest('/dashboard/');
    },

    getCharts: async () => {
        return apiRequest('/dashboard/charts');
    },

    getGoals: async () => {
        return apiRequest('/dashboard/goals');
    },

    getCommunityImpact: async () => {
        return apiRequest('/dashboard/community-impact');
    }
};

// Transactions API
const transactionsAPI = {
    getAll: async (limit = 50) => {
        return apiRequest(`/transactions/?limit=${limit}`);
    },

    create: async (transactionData) => {
        return apiRequest('/transactions/', {
            method: 'POST',
            body: JSON.stringify(transactionData)
        });
    },

    getCategories: async () => {
        return apiRequest('/transactions/categories');
    },

    getSummary: async () => {
        return apiRequest('/transactions/summary');
    },

    delete: async (transactionId) => {
        return apiRequest(`/transactions/${transactionId}`, {
            method: 'DELETE'
        });
    }
};

// Crowdfunding API
const crowdfundingAPI = {
    getCampaigns: async () => {
        return apiRequest('/crowdfunding/');
    },

    getFeatured: async () => {
        return apiRequest('/crowdfunding/featured');
    },

    create: async (campaignData) => {
        return apiRequest('/crowdfunding/', {
            method: 'POST',
            body: JSON.stringify(campaignData)
        });
    },

    getCampaign: async (campaignId) => {
        return apiRequest(`/crowdfunding/${campaignId}`);
    },

    contribute: async (campaignId, contributionData) => {
        return apiRequest(`/crowdfunding/${campaignId}/contribute`, {
            method: 'POST',
            body: JSON.stringify(contributionData)
        });
    },

    getCategories: async () => {
        return apiRequest('/crowdfunding/categories');
    }
};

// Loans API
const loansAPI = {
    getOffers: async () => {
        return apiRequest('/loans/offers');
    },

    getRecommendations: async () => {
        return apiRequest('/loans/offers/recommendations');
    },

    apply: async (applicationData) => {
        return apiRequest('/loans/apply', {
            method: 'POST',
            body: JSON.stringify(applicationData)
        });
    },

    getApplications: async () => {
        return apiRequest('/loans/applications');
    },

    getApplication: async (applicationId) => {
        return apiRequest(`/loans/applications/${applicationId}`);
    },

    makeRepayment: async (applicationId, amount) => {
        return apiRequest(`/loans/applications/${applicationId}/repay`, {
            method: 'POST',
            body: JSON.stringify({ amount })
        });
    }
};

// Profile API
const profileAPI = {
    getStats: async () => {
        return apiRequest('/profile/stats');
    }
};

// Poverty Map API
const povertyMapAPI = {
    getData: async () => {
        return apiRequest('/poverty-map/data');
    },

    getSummary: async () => {
        return apiRequest('/poverty-map/summary');
    },

    getRegion: async (regionName) => {
        return apiRequest(`/poverty-map/regions/${regionName}`);
    }
};
