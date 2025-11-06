// Dashboard JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard components
    initializeSidebar();
    initializeCharts();
    initializeTooltips();
    initializeLoadingStates();
    
    // Set up page-specific functionality
    const currentPage = window.location.pathname;
    setActiveNavigation(currentPage);
    
    // Initialize auto-refresh for data
    initializeAutoRefresh();
});

/**
 * Sidebar functionality
 */
function initializeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('toggleBtn');
    const mainContent = document.getElementById('mainContent');
    
    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            
            // Update toggle button icon
            const icon = toggleBtn.querySelector('i');
            if (sidebar.classList.contains('collapsed')) {
                icon.className = 'fas fa-chevron-right';
            } else {
                icon.className = 'fas fa-bars';
            }
        });
        
        // Handle responsive sidebar
        if (window.innerWidth <= 768) {
            sidebar.addEventListener('click', function(e) {
                if (e.target === sidebar) {
                    sidebar.classList.remove('open');
                }
            });
            
            // Add mobile menu toggle
            const mobileToggleBtn = document.createElement('button');
            mobileToggleBtn.className = 'mobile-menu-toggle';
            mobileToggleBtn.innerHTML = '<i class="fas fa-bars"></i>';
            mobileToggleBtn.style.cssText = `
                position: fixed;
                top: 20px;
                left: 20px;
                z-index: 9999;
                background: var(--accent-color);
                color: white;
                border: none;
                padding: 10px;
                border-radius: 4px;
                display: none;
            `;
            
            document.body.appendChild(mobileToggleBtn);
            
            mobileToggleBtn.addEventListener('click', function() {
                sidebar.classList.toggle('open');
            });
            
            // Show mobile toggle on small screens
            function handleMobileToggle() {
                if (window.innerWidth <= 768) {
                    mobileToggleBtn.style.display = 'block';
                } else {
                    mobileToggleBtn.style.display = 'none';
                    sidebar.classList.remove('open');
                }
            }
            
            window.addEventListener('resize', handleMobileToggle);
            handleMobileToggle();
        }
    }
}

/**
 * Set active navigation based on current page
 */
function setActiveNavigation(currentPath) {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

/**
 * Initialize chart animations and interactions
 */
function initializeCharts() {
    // Animate charts when they come into view
    const chartObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const canvas = entry.target;
                if (canvas.dataset.animated !== 'true') {
                    animateChart(canvas);
                    canvas.dataset.animated = 'true';
                }
            }
        });
    }, {
        threshold: 0.1
    });
    
    // Observe all chart canvases
    document.querySelectorAll('canvas').forEach(canvas => {
        chartObserver.observe(canvas);
    });
}

/**
 * Animate chart loading
 */
function animateChart(canvas) {
    const ctx = canvas.getContext('2d');
    const parent = canvas.parentElement;
    
    // Show loading animation
    const loadingEl = document.createElement('div');
    loadingEl.className = 'chart-loading';
    loadingEl.innerHTML = '<div class="spinner"></div><span>Loading chart data...</span>';
    loadingEl.style.cssText = `
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        display: flex;
        align-items: center;
        gap: 10px;
        color: var(--text-secondary);
        font-size: 0.9em;
    `;
    
    parent.appendChild(loadingEl);
    
    // Remove loading after a short delay (simulating data fetch)
    setTimeout(() => {
        if (loadingEl && loadingEl.parentElement) {
            loadingEl.remove();
        }
    }, 1000);
}

/**
 * Initialize tooltips and help icons
 */
function initializeTooltips() {
    // Simple tooltip implementation
    const tooltipElements = document.querySelectorAll('[title]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function(e) {
            showTooltip(e.target.getAttribute('title'), e.target);
        });
        
        element.addEventListener('mouseleave', function() {
            hideTooltip();
        });
    });
}

/**
 * Show tooltip
 */
function showTooltip(text, element) {
    const tooltip = document.createElement('div');
    tooltip.className = 'custom-tooltip';
    tooltip.textContent = text;
    tooltip.style.cssText = `
        position: absolute;
        background: rgba(0, 0, 0, 0.8);
        color: white;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 0.8em;
        z-index: 10000;
        pointer-events: none;
        max-width: 200px;
        word-wrap: break-word;
    `;
    
    document.body.appendChild(tooltip);
    
    const rect = element.getBoundingClientRect();
    tooltip.style.left = rect.left + 'px';
    tooltip.style.top = (rect.top - tooltip.offsetHeight - 5) + 'px';
    
    // Adjust if tooltip goes off screen
    if (tooltip.offsetLeft + tooltip.offsetWidth > window.innerWidth) {
        tooltip.style.left = (window.innerWidth - tooltip.offsetWidth - 10) + 'px';
    }
}

/**
 * Hide tooltip
 */
function hideTooltip() {
    const tooltip = document.querySelector('.custom-tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

/**
 * Initialize loading states for data tables
 */
function initializeLoadingStates() {
    const loadingElements = document.querySelectorAll('.loading');
    
    loadingElements.forEach(element => {
        if (element.textContent.trim() === 'Loading data...' || 
            element.textContent.trim() === 'Loading...') {
            // Auto-hide loading after 5 seconds
            setTimeout(() => {
                if (element.textContent.includes('Loading')) {
                    element.textContent = 'No data available';
                    element.classList.remove('loading');
                }
            }, 5000);
        }
    });
}

/**
 * Initialize auto-refresh functionality
 */
function initializeAutoRefresh() {
    // Refresh data every 5 minutes
    const refreshInterval = 5 * 60 * 1000; // 5 minutes
    
    setInterval(() => {
        refreshCurrentPageData();
    }, refreshInterval);
}

/**
 * Refresh data for current page
 */
function refreshCurrentPageData() {
    const currentPath = window.location.pathname;
    
    switch (currentPath) {
        case '/trends':
            if (typeof loadTrendsData === 'function') {
                loadTrendsData();
            }
            break;
        case '/gross-commission':
            if (typeof loadGrossCommissionData === 'function') {
                loadGrossCommissionData();
            }
            break;
        case '/net-commission':
            if (typeof loadNetCommissionData === 'function') {
                loadNetCommissionData();
            }
            break;
    }
}

/**
 * Utility functions for data formatting and display
 */
const DashboardUtils = {
    /**
     * Format currency for South African Rand
     */
    formatCurrency: function(amount) {
        return new Intl.NumberFormat('en-ZA', {
            style: 'currency',
            currency: 'ZAR'
        }).format(amount);
    },
    
    /**
     * Format percentage
     */
    formatPercentage: function(value, decimals = 1) {
        return value.toFixed(decimals) + '%';
    },
    
    /**
     * Format large numbers with K, M, B suffixes
     */
    formatNumber: function(num) {
        if (num >= 1e9) {
            return (num / 1e9).toFixed(1) + 'B';
        }
        if (num >= 1e6) {
            return (num / 1e6).toFixed(1) + 'M';
        }
        if (num >= 1e3) {
            return (num / 1e3).toFixed(1) + 'K';
        }
        return num.toLocaleString();
    },
    
    /**
     * Calculate percentage change
     */
    calculateChange: function(current, previous) {
        if (previous === 0) return current > 0 ? 100 : 0;
        return ((current - previous) / previous) * 100;
    },
    
    /**
     * Debounce function for search inputs
     */
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    /**
     * Export table data to CSV
     */
    exportToCSV: function(tableId, filename) {
        const table = document.getElementById(tableId);
        if (!table) return;
        
        let csv = [];
        const rows = table.querySelectorAll('tr');
        
        for (let i = 0; i < rows.length; i++) {
            const row = [];
            const cols = rows[i].querySelectorAll('td, th');
            
            for (let j = 0; j < cols.length; j++) {
                row.push('"' + cols[j].innerText.replace(/"/g, '""') + '"');
            }
            csv.push(row.join(','));
        }
        
        // Download CSV
        const csvContent = csv.join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        
        if (link.download !== undefined) {
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', filename || 'data.csv');
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    }
};

/**
 * Chart utilities
 */
const ChartUtils = {
    /**
     * Set default chart colors
     */
    colors: {
        primary: '#4e73df',
        success: '#1cc88a',
        warning: '#f6c23e',
        danger: '#e74a3c',
        info: '#36b9cc',
        secondary: '#858796'
    },
    
    /**
     * Get gradient colors
     */
    getGradient: function(ctx, color, opacity = 0.3) {
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, this.hexToRgba(color, opacity));
        gradient.addColorStop(1, this.hexToRgba(color, 0));
        return gradient;
    },
    
    /**
     * Convert hex to rgba
     */
    hexToRgba: function(hex, alpha) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }
};

/**
 * Table utilities
 */
const TableUtils = {
    /**
     * Sort table by column
     */
    sortTable: function(tableId, columnIndex, dataType = 'string') {
        const table = document.getElementById(tableId);
        if (!table) return;
        
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        const isAscending = table.dataset.sortDirection !== 'asc';
        table.dataset.sortDirection = isAscending ? 'asc' : 'desc';
        
        rows.sort((a, b) => {
            const aValue = a.cells[columnIndex].textContent.trim();
            const bValue = b.cells[columnIndex].textContent.trim();
            
            let comparison = 0;
            if (dataType === 'number') {
                comparison = parseFloat(aValue.replace(/[^\d.-]/g, '')) - parseFloat(bValue.replace(/[^\d.-]/g, ''));
            } else if (dataType === 'currency') {
                comparison = parseFloat(aValue.replace(/[^\d.-]/g, '')) - parseFloat(bValue.replace(/[^\d.-]/g, ''));
            } else {
                comparison = aValue.localeCompare(bValue);
            }
            
            return isAscending ? comparison : -comparison;
        });
        
        // Clear tbody and append sorted rows
        tbody.innerHTML = '';
        rows.forEach(row => tbody.appendChild(row));
        
        // Update sort icons
        this.updateSortIcons(table, columnIndex, isAscending);
    },
    
    /**
     * Update sort icons in table headers
     */
    updateSortIcons: function(table, activeColumn, isAscending) {
        const headers = table.querySelectorAll('th');
        headers.forEach((header, index) => {
            const icon = header.querySelector('i');
            if (icon) {
                if (index === activeColumn) {
                    icon.className = isAscending ? 'fas fa-sort-up' : 'fas fa-sort-down';
                } else {
                    icon.className = 'fas fa-sort';
                }
            }
        });
    },
    
    /**
     * Filter table rows
     */
    filterTable: function(tableId, searchTerm, columnIndex = 0) {
        const table = document.getElementById(tableId);
        if (!table) return;
        
        const rows = table.querySelectorAll('tbody tr');
        const term = searchTerm.toLowerCase();
        
        rows.forEach(row => {
            const cellValue = row.cells[columnIndex].textContent.toLowerCase();
            row.style.display = cellValue.includes(term) ? '' : 'none';
        });
    }
};

/**
 * Notification system
 */
const Notifications = {
    /**
     * Show success notification
     */
    success: function(message) {
        this.show(message, 'success');
    },
    
    /**
     * Show error notification
     */
    error: function(message) {
        this.show(message, 'error');
    },
    
    /**
     * Show warning notification
     */
    warning: function(message) {
        this.show(message, 'warning');
    },
    
    /**
     * Show info notification
     */
    info: function(message) {
        this.show(message, 'info');
    },
    
    /**
     * Generic notification show function
     */
    show: function(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        const colors = {
            success: '#27ae60',
            error: '#e74c3c',
            warning: '#f39c12',
            info: '#3498db'
        };
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${colors[type]};
            color: white;
            padding: 15px 20px;
            border-radius: 4px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            z-index: 10000;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s ease;
            max-width: 300px;
            word-wrap: break-word;
        `;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, 300);
        }, 5000);
    }
};

// Make utilities globally available
window.DashboardUtils = DashboardUtils;
window.ChartUtils = ChartUtils;
window.TableUtils = TableUtils;
window.Notifications = Notifications;
