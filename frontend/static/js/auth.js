// Authentication JavaScript

// This file is integrated into main.js
// Additional auth-specific functions can be added here if needed

// Password strength checker for registration
function checkPasswordStrength(password) {
    let strength = 0;
    const checks = {
        length: password.length >= 8,
        uppercase: /[A-Z]/.test(password),
        lowercase: /[a-z]/.test(password),
        numbers: /\d/.test(password),
        special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
    };

    strength = Object.values(checks).filter(Boolean).length;

    return {
        score: strength,
        checks: checks,
        isValid: strength >= 3
    };
}

// Email validation
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Form validation helpers
function validateLoginForm(email, password) {
    const errors = [];

    if (!email) {
        errors.push('Email is required');
    } else if (!validateEmail(email)) {
        errors.push('Please enter a valid email address');
    }

    if (!password) {
        errors.push('Password is required');
    } else if (password.length < 6) {
        errors.push('Password must be at least 6 characters long');
    }

    return errors;
}

function validateRegisterForm(email, username, password, fullName) {
    const errors = [];

    if (!email) {
        errors.push('Email is required');
    } else if (!validateEmail(email)) {
        errors.push('Please enter a valid email address');
    }

    if (!username) {
        errors.push('Username is required');
    } else if (username.length < 3) {
        errors.push('Username must be at least 3 characters long');
    } else if (!/^[a-zA-Z0-9_]+$/.test(username)) {
        errors.push('Username can only contain letters, numbers, and underscores');
    }

    if (!password) {
        errors.push('Password is required');
    } else {
        const strength = checkPasswordStrength(password);
        if (!strength.isValid) {
            errors.push('Password must be at least 8 characters and contain uppercase, lowercase, and numbers');
        }
    }

    if (!fullName) {
        errors.push('Full name is required');
    } else if (fullName.length < 2) {
        errors.push('Full name must be at least 2 characters long');
    }

    return errors;
}
