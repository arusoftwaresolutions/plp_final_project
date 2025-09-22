// Main JavaScript for SDG 1 Application

let currentUser = null;
let token = null;

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Initialize the application
async function initializeApp() {
    // Check if user is already logged in
    const savedToken = localStorage.getItem('token');
    if (savedToken) {
        token = savedToken;
        await loadUserProfile();
        showDashboard();
    } else {
        showLogin();
    }

    // Initialize charts
    initializeCharts();
}

// Authentication functions
async function login(email, password) {
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                username: email,
                password: password
            })
        });

        if (response.ok) {
            const data = await response.json();
            token = data.access_token;
            localStorage.setItem('token', token);
            await loadUserProfile();
            closeLogin();
            showDashboard();
            showToast('Login successful!', 'success');
        } else {
            const error = await response.json();
            showToast(error.detail || 'Login failed', 'error');
        }
    } catch (error) {
        showToast('Login failed. Please try again.', 'error');
    }
}

async function register(email, username, password, fullName) {
    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                username: username,
                password: password,
                full_name: fullName
            })
        });

        if (response.ok) {
            const data = await response.json();
            showToast('Registration successful! Please login.', 'success');
            closeRegister();
            showLogin();
        } else {
            const error = await response.json();
            showToast(error.detail || 'Registration failed', 'error');
        }
    } catch (error) {
        showToast('Registration failed. Please try again.', 'error');
    }
}

async function loadUserProfile() {
    try {
        const response = await fetch('/api/auth/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            currentUser = await response.json();
            updateUserInterface();
        } else {
            logout();
        }
    } catch (error) {
        logout();
    }
}

function logout() {
    currentUser = null;
    token = null;
    localStorage.removeItem('token');
    updateUserInterface();
    showLogin();
}

function updateUserInterface() {
    const userNameElement = document.getElementById('userName');
    if (currentUser) {
        userNameElement.textContent = currentUser.full_name || currentUser.username;
    } else {
        userNameElement.textContent = 'Login';
    }
}

// Navigation functions
function showDashboard() {
    hideAllSections();
    document.getElementById('dashboardSection').style.display = 'block';
    loadDashboardData();
}

function showTransactions() {
    hideAllSections();
    document.getElementById('transactionsSection').style.display = 'block';
    loadTransactions();
}

function showAI() {
    hideAllSections();
    document.getElementById('aiSection').style.display = 'block';
    loadAIAdvisor();
}

function showCrowdfunding() {
    hideAllSections();
    document.getElementById('crowdfundingSection').style.display = 'block';
    loadCampaigns();
}

function showLoans() {
    hideAllSections();
    document.getElementById('loansSection').style.display = 'block';
    loadLoans();
}

function showPovertyMap() {
    hideAllSections();
    document.getElementById('povertyMapSection').style.display = 'block';
    initializeMap();
}

function showProfile() {
    hideAllSections();
    document.getElementById('profileSection').style.display = 'block';
    loadProfile();
}

function hideAllSections() {
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => {
        section.style.display = 'none';
    });
}

// Modal functions
function showLogin() {
    document.getElementById('loginModal').style.display = 'block';
}

function closeLogin() {
    document.getElementById('loginModal').style.display = 'none';
    document.getElementById('loginForm').reset();
}

function showRegister() {
    document.getElementById('registerModal').style.display = 'block';
}

function closeRegister() {
    document.getElementById('registerModal').style.display = 'none';
    document.getElementById('registerForm').reset();
}

// Toast notifications
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');

    const toast = document.createElement('div');
    toast.className = `toast show bg-${type === 'error' ? 'danger' : type}`;
    toast.innerHTML = `
        <div class="toast-body text-white">
            ${message}
            <button type="button" class="btn-close btn-close-white ms-2" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;

    toastContainer.appendChild(toast);

    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentElement) {
            toast.remove();
        }
    }, 5000);
}

// Form handlers
document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    login(email, password);
});

document.getElementById('registerForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const email = document.getElementById('registerEmail').value;
    const username = document.getElementById('registerUsername').value;
    const password = document.getElementById('registerPassword').value;
    const fullName = document.getElementById('registerFullName').value;
    register(email, username, password, fullName);
});

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Initialize charts
function initializeCharts() {
    // Will be implemented by dashboard.js
}
