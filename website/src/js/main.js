/**
 * Main Application Module
 * Initializes all modules and sets up the application
 */

// Import all modules
import './modules/panels.js';
import { initializeFirebase, manualRefreshRatings } from './modules/firebase.js';
import './modules/charts.js';
import './modules/network.js';
import { initializeTradeHistory } from './modules/tradeHistory.js';
import { loadMatchupBreakdowns } from './modules/matchups.js';
import './modules/draft.js';
import './modules/playerJourney.js';
import './modules/modal.js';
import { checkExternalData } from './modules/externalData.js';

// Initialize the application when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initializing Eazy Pickens application...');
    
    // Check for external data first
    checkExternalData();
    
    // Initialize Firebase
    initializeFirebase();
    
    // Initialize trade history features
    initializeTradeHistory();
    
    // Load matchup breakdowns if available
    loadMatchupBreakdowns();
    
    // Set up refresh button for ratings
    const refreshButton = document.querySelector('button[onclick="refreshTradingSummary()"]');
    if (refreshButton) {
        refreshButton.onclick = function() {
            manualRefreshRatings(false);
        };
    }
    
    // Initialize with overview panel
    if (typeof showPanel === 'function') {
        showPanel('overview');
    }
    
    // Set up any global event listeners
    setupGlobalEventListeners();
    
    // Check for saved preferences
    loadUserPreferences();
    
    console.log('✅ Application initialized successfully');
});

function setupGlobalEventListeners() {
    // Handle keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Escape key closes modals
        if (e.key === 'Escape') {
            if (typeof closeTradeModal === 'function') closeTradeModal();
            if (typeof closeBreakdownModal === 'function') closeBreakdownModal();
        }
    });
    
    // Handle window resize for responsive elements
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(function() {
            // Re-initialize any size-dependent visualizations
            const activePanel = document.querySelector('.visualization-panel.active');
            if (activePanel) {
                const panelId = activePanel.id;
                if (panelId === 'network-panel' && typeof initNetworkGraph === 'function') {
                    initNetworkGraph();
                } else if (panelId === 'overview-panel' && typeof initMonthlyChart === 'function') {
                    initMonthlyChart();
                }
            }
        }, 250);
    });
}

function loadUserPreferences() {
    // Load saved preferences from localStorage
    const preferences = {
        showPlayerBreakdowns: localStorage.getItem('showPlayerBreakdowns') === 'true',
        userName: localStorage.getItem('userName'),
        lastPanel: localStorage.getItem('lastPanel') || 'overview'
    };
    
    // Apply preferences
    const breakdownCheckbox = document.getElementById('toggleBreakdowns');
    if (breakdownCheckbox && preferences.showPlayerBreakdowns) {
        breakdownCheckbox.checked = true;
        if (typeof togglePlayerBreakdowns === 'function') {
            togglePlayerBreakdowns();
        }
    }
    
    // You could also restore the last viewed panel, but for now we always start with overview
    // to ensure consistent initial state
}

// Export any functions that need to be globally available
window.APP = {
    version: '1.0.0',
    initialized: true,
    modules: {
        firebase: { initializeFirebase, manualRefreshRatings },
        tradeHistory: { initializeTradeHistory },
        matchups: { loadMatchupBreakdowns }
    }
};