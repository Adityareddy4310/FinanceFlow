/**
 * FinanceFlow - Shared Utilities
 * Common functions used across all pages
 */

// Form Validation
const FormValidator = {
    email: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
    required: (value) => value && value.trim().length > 0,
    minLength: (value, min) => value.length >= min,
    phone: (value) => /^\d{10,}$/.test(value.replace(/\D/g, '')),
    
    validate(form) {
        let isValid = true;
        form.querySelectorAll('[data-validate]').forEach(field => {
            const rules = field.dataset.validate.split('|');
            rules.forEach(rule => {
                if (!this.validateField(field, rule)) {
                    this.showError(field);
                    isValid = false;
                } else {
                    this.clearError(field);
                }
            });
        });
        return isValid;
    },
    
    validateField(field, rule) {
        const value = field.value;
        if (rule === 'required') return this.required(value);
        if (rule === 'email') return this.email(value);
        if (rule.startsWith('min:')) {
            const min = parseInt(rule.split(':')[1]);
            return this.minLength(value, min);
        }
        return true;
    },
    
    showError(field) {
        field.classList.add('error');
    },
    
    clearError(field) {
        field.classList.remove('error');
    }
};

// Storage Utilities
const Storage = {
    set(key, value) {
        localStorage.setItem(key, JSON.stringify(value));
    },
    
    get(key) {
        const value = localStorage.getItem(key);
        return value ? JSON.parse(value) : null;
    },
    
    remove(key) {
        localStorage.removeItem(key);
    },
    
    clear() {
        localStorage.clear();
    }
};

// Animation Utilities
const Animations = {
    fadeIn(element, duration = 300) {
        element.style.opacity = '0';
        element.style.transition = `opacity ${duration}ms`;
        setTimeout(() => {
            element.style.opacity = '1';
        }, 10);
    },
    
    slideUp(element, distance = 20, duration = 300) {
        element.style.transform = `translateY(${distance}px)`;
        element.style.opacity = '0';
        element.style.transition = `all ${duration}ms`;
        setTimeout(() => {
            element.style.transform = 'translateY(0)';
            element.style.opacity = '1';
        }, 10);
    }
};

// Responsive Helpers
const Responsive = {
    isMobile() {
        return window.innerWidth < 768;
    },
    
    isTablet() {
        return window.innerWidth >= 768 && window.innerWidth < 1024;
    },
    
    isDesktop() {
        return window.innerWidth >= 1024;
    }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize dropdowns
    document.querySelectorAll('.dropdown').forEach(dropdown => {
        dropdown.addEventListener('click', function(e) {
            if (e.target.classList.contains('dropdown-toggle')) {
                this.classList.toggle('open');
            }
        });
    });
});