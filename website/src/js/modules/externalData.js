/**
 * External Data Module
 * Handles loading and managing external script data
 * (matchupBreakdowns, leagueIdByYear, draftData)
 */

// These will be populated by external scripts
let matchupBreakdowns = null;
let leagueIdByYear = null;
let draftData = null;

// Check if data is already loaded from external scripts
export function checkExternalData() {
    if (typeof window.matchupBreakdowns !== 'undefined') {
        matchupBreakdowns = window.matchupBreakdowns;
        console.log('✅ Matchup breakdowns loaded');
    }
    
    if (typeof window.leagueIdByYear !== 'undefined') {
        leagueIdByYear = window.leagueIdByYear;
        console.log('✅ League mapping loaded');
    }
    
    if (typeof window.draftData !== 'undefined') {
        draftData = window.draftData;
        console.log('✅ Draft data loaded');
    }
}

// Getters for the data
export function getMatchupBreakdowns() {
    if (!matchupBreakdowns) {
        checkExternalData();
    }
    return matchupBreakdowns;
}

export function getLeagueIdByYear() {
    if (!leagueIdByYear) {
        checkExternalData();
    }
    return leagueIdByYear;
}

export function getDraftData() {
    if (!draftData) {
        checkExternalData();
    }
    return draftData;
}

// Initialize on load
setTimeout(checkExternalData, 100);

// Also make them available globally for backward compatibility
window.getMatchupBreakdowns = getMatchupBreakdowns;
window.getLeagueIdByYear = getLeagueIdByYear;
window.getDraftData = getDraftData;