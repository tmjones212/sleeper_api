/**
 * Matchups Module
 * Handles matchup display and filtering
 */

import { getMatchupBreakdowns, getLeagueIdByYear } from './externalData.js';

export function showMatchupYear() {
    console.log('🎯 showMatchupYear called');
    const yearSelect = document.getElementById('matchupYearSelect');
    const selectedYear = yearSelect ? yearSelect.value : '2024';
    
    console.log('Selected year:', selectedYear);
    
    // Hide all year matchups first
    const yearMatchups = document.querySelectorAll('.year-matchups');
    console.log('Found year matchups:', yearMatchups.length);
    
    yearMatchups.forEach(yearDiv => {
        yearDiv.style.display = 'none';
    });
    
    // Show selected year
    const selectedYearDiv = document.querySelector(`.year-matchups[data-year="${selectedYear}"]`);
    if (selectedYearDiv) {
        selectedYearDiv.style.display = 'block';
        console.log('Showing year:', selectedYear);
        
        // Re-attach click handlers for this year's matchups
        const matchupBreakdowns = getMatchupBreakdowns();
        if (matchupBreakdowns && matchupBreakdowns[selectedYear]) {
            addMatchupClickHandlers();
        }
    } else {
        console.error('Year div not found for:', selectedYear);
    }
    
    // Clear any active filters
    clearHeadToHeadFilter();
}

export function filterHeadToHead(team1, team2, showNotification = true) {
    console.log('Filtering head-to-head:', team1, 'vs', team2);
    
    // Show all matchups first
    document.querySelectorAll('.matchup-item').forEach(item => {
        item.style.display = 'block';
    });
    
    // Then hide those that don't match
    document.querySelectorAll('.matchup-item').forEach(item => {
        const teamElements = item.querySelectorAll('.team-name');
        const teams = Array.from(teamElements).map(el => el.textContent.trim());
        
        if (!teams.includes(team1) || !teams.includes(team2)) {
            item.style.display = 'none';
        }
    });
    
    // Update active filter display
    const filterDisplay = document.getElementById('active-filter');
    if (filterDisplay) {
        filterDisplay.innerHTML = `
            <div style="background: #0066cc; color: white; padding: 10px; border-radius: 5px; margin: 10px 0;">
                Showing: ${team1} vs ${team2} 
                <button onclick="clearHeadToHeadFilter()" style="margin-left: 10px; background: white; color: #0066cc; border: none; padding: 2px 8px; border-radius: 3px; cursor: pointer;">Clear Filter</button>
            </div>
        `;
    }
    
    if (showNotification) {
        // Show a temporary notification
        const notification = document.createElement('div');
        notification.style.cssText = 'position: fixed; top: 20px; right: 20px; background: #0066cc; color: white; padding: 15px; border-radius: 5px; z-index: 1000;';
        notification.textContent = `Filtered to ${team1} vs ${team2}`;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 3000);
    }
}

export function clearHeadToHeadFilter() {
    // Show all matchups
    document.querySelectorAll('.matchup-item').forEach(item => {
        item.style.display = 'block';
    });
    
    // Clear active filter display
    const filterDisplay = document.getElementById('active-filter');
    if (filterDisplay) {
        filterDisplay.innerHTML = '';
    }
}

export function loadMatchupBreakdowns() {
    console.log('Loading matchup breakdowns...');
    const matchupBreakdowns = getMatchupBreakdowns();
    if (matchupBreakdowns) {
        console.log('Matchup breakdowns loaded:', Object.keys(matchupBreakdowns));
        // Add click handlers
        addMatchupClickHandlers();
    } else {
        console.error('Matchup breakdowns not found!');
    }
}

export function togglePlayerBreakdowns() {
    const checkbox = document.getElementById('toggleBreakdowns');
    const isEnabled = checkbox ? checkbox.checked : false;
    
    // Store preference
    localStorage.setItem('showPlayerBreakdowns', isEnabled);
    
    if (isEnabled) {
        console.log('Enabling matchup click handlers...');
        addMatchupClickHandlers();
        
        // Show notification
        const notification = document.createElement('div');
        notification.style.cssText = 'position: fixed; top: 20px; right: 20px; background: #4CAF50; color: white; padding: 15px; border-radius: 5px; z-index: 1000;';
        notification.textContent = 'Player breakdowns enabled - click any matchup to see details';
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 3000);
    } else {
        console.log('Disabling matchup click handlers...');
        removeMatchupClickHandlers();
    }
}

export function addMatchupClickHandlers() {
    console.log('Adding matchup click handlers...');
    const matchupItems = document.querySelectorAll('.matchup-item');
    console.log('Found matchup items:', matchupItems.length);
    
    matchupItems.forEach(item => {
        // Remove existing listener to avoid duplicates
        item.removeEventListener('click', handleMatchupClick);
        // Add new listener
        item.addEventListener('click', handleMatchupClick);
        item.style.cursor = 'pointer';
        item.title = 'Click to see player breakdowns';
    });
}

export function removeMatchupClickHandlers() {
    const matchupItems = document.querySelectorAll('.matchup-item');
    matchupItems.forEach(item => {
        item.removeEventListener('click', handleMatchupClick);
        item.style.cursor = 'default';
        item.title = '';
    });
}

export function handleMatchupClick(event) {
    // Prevent clicking on buttons from triggering this
    if (event.target.tagName === 'BUTTON') {
        return;
    }
    
    const matchupItem = event.currentTarget;
    
    // Extract matchup information
    const weekText = matchupItem.querySelector('h4')?.textContent || '';
    const weekMatch = weekText.match(/Week (\d+)/);
    const week = weekMatch ? weekMatch[1] : null;
    
    const teams = matchupItem.querySelectorAll('.team-name');
    const scores = matchupItem.querySelectorAll('.team-score');
    
    if (teams.length >= 2 && scores.length >= 2 && week) {
        const team1Name = teams[0].textContent.trim();
        const team2Name = teams[1].textContent.trim();
        const team1Score = scores[0].textContent.trim();
        const team2Score = scores[1].textContent.trim();
        
        // Get the year from the parent container
        const yearContainer = matchupItem.closest('.year-matchups');
        const year = yearContainer ? yearContainer.getAttribute('data-year') : '2024';
        
        // Get the matchup ID from the data attribute
        const matchupId = matchupItem.getAttribute('data-matchup-id');
        
        console.log('Clicked matchup:', {
            year,
            week,
            teams: [team1Name, team2Name],
            scores: [team1Score, team2Score],
            matchupId
        });
        
        // Get league ID from the year mapping
        const leagueIdByYear = getLeagueIdByYear();
        const leagueId = leagueIdByYear && leagueIdByYear[year];
        
        if (leagueId) {
            showMatchupBreakdownModal(leagueId, week, [team1Name, team2Name], [team1Score, team2Score], matchupId);
        } else {
            console.error('League ID not found for year:', year);
        }
    }
}

export function showMatchupBreakdownModal(leagueId, week, teams, scores, matchupId) {
    console.log('Showing breakdown modal:', { leagueId, week, teams, scores, matchupId });
    
    // Create modal if it doesn't exist
    let modal = document.getElementById('matchupBreakdownModal');
    if (!modal) {
        modal = createBreakdownModal();
    }
    
    // Update modal content
    const modalBody = modal.querySelector('.modal-body');
    modalBody.innerHTML = '<p>Loading player breakdowns...</p>';
    
    // Get year from league ID
    let year = null;
    const leagueIdByYear = getLeagueIdByYear();
    if (leagueIdByYear) {
        for (const [y, id] of Object.entries(leagueIdByYear)) {
            if (id === leagueId) {
                year = y;
                break;
            }
        }
    }
    
    // Update modal title
    const modalTitle = modal.querySelector('.modal-title');
    modalTitle.textContent = `Week ${week} Breakdown - ${teams[0]} (${scores[0]}) vs ${teams[1]} (${scores[1]})`;
    
    // Get breakdown data
    const matchupBreakdowns = getMatchupBreakdowns();
    if (matchupBreakdowns && year && matchupBreakdowns[year]) {
        const weekData = matchupBreakdowns[year][`week_${week}`];
        if (weekData) {
            // Find the specific matchup
            let matchupData = null;
            for (const matchup of weekData) {
                if (matchup.team_1.name === teams[0] && matchup.team_2.name === teams[1]) {
                    matchupData = matchup;
                    break;
                } else if (matchup.team_1.name === teams[1] && matchup.team_2.name === teams[0]) {
                    // Swap teams to match order
                    matchupData = {
                        team_1: matchup.team_2,
                        team_2: matchup.team_1
                    };
                    break;
                }
            }
            
            if (matchupData) {
                const html = generateBreakdownHTML(matchupData, week, teams);
                modalBody.innerHTML = html;
            } else {
                modalBody.innerHTML = '<p>Breakdown data not found for this matchup.</p>';
            }
        } else {
            modalBody.innerHTML = '<p>No breakdown data available for this week.</p>';
        }
    } else {
        modalBody.innerHTML = '<p>Breakdown data not loaded.</p>';
    }
    
    // Show modal
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
}

export function createBreakdownModal() {
    const modal = document.createElement('div');
    modal.id = 'matchupBreakdownModal';
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content" style="width: 90%; max-width: 1000px;">
            <div class="modal-header">
                <h2 class="modal-title">Matchup Breakdown</h2>
                <span class="close" onclick="closeBreakdownModal()">&times;</span>
            </div>
            <div class="modal-body">
                <!-- Content will be dynamically inserted -->
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Close modal when clicking outside
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeBreakdownModal();
        }
    });
    
    return modal;
}

export function generateBreakdownHTML(teams, week, teamNames) {
    let html = '<div class="breakdown-container">';
    
    // Team comparison header
    html += `
        <div class="team-comparison" style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
            <div class="team-breakdown">
                <h3 style="text-align: center; color: #0066cc;">${teams.team_1.name}</h3>
                <div class="score-display" style="text-align: center; font-size: 2em; font-weight: bold; color: ${teams.team_1.score > teams.team_2.score ? '#4CAF50' : '#999'};">
                    ${teams.team_1.score}
                </div>
            </div>
            <div class="team-breakdown">
                <h3 style="text-align: center; color: #0066cc;">${teams.team_2.name}</h3>
                <div class="score-display" style="text-align: center; font-size: 2em; font-weight: bold; color: ${teams.team_2.score > teams.team_1.score ? '#4CAF50' : '#999'};">
                    ${teams.team_2.score}
                </div>
            </div>
        </div>
    `;
    
    // Player breakdowns
    html += '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">';
    
    // Team 1 players
    html += '<div class="team-players">';
    html += '<h4>Starters</h4>';
    html += '<table style="width: 100%; border-collapse: collapse;">';
    html += '<thead><tr><th>Position</th><th>Player</th><th>Points</th></tr></thead>';
    html += '<tbody>';
    
    teams.team_1.starters.forEach(player => {
        html += `
            <tr style="background: ${player.points > 15 ? 'rgba(76, 175, 80, 0.1)' : player.points < 5 ? 'rgba(244, 67, 54, 0.1)' : 'transparent'};">
                <td style="padding: 5px; border: 1px solid #606060;">${player.position}</td>
                <td style="padding: 5px; border: 1px solid #606060;">${player.name}</td>
                <td style="padding: 5px; border: 1px solid #606060; text-align: right; font-weight: bold;">${player.points}</td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    
    if (teams.team_1.bench && teams.team_1.bench.length > 0) {
        html += '<h4 style="margin-top: 15px;">Bench</h4>';
        html += '<table style="width: 100%; border-collapse: collapse;">';
        html += '<tbody>';
        teams.team_1.bench.forEach(player => {
            html += `
                <tr style="opacity: 0.7;">
                    <td style="padding: 5px; border: 1px solid #606060;">${player.position}</td>
                    <td style="padding: 5px; border: 1px solid #606060;">${player.name}</td>
                    <td style="padding: 5px; border: 1px solid #606060; text-align: right;">${player.points}</td>
                </tr>
            `;
        });
        html += '</tbody></table>';
    }
    html += '</div>';
    
    // Team 2 players
    html += '<div class="team-players">';
    html += '<h4>Starters</h4>';
    html += '<table style="width: 100%; border-collapse: collapse;">';
    html += '<thead><tr><th>Position</th><th>Player</th><th>Points</th></tr></thead>';
    html += '<tbody>';
    
    teams.team_2.starters.forEach(player => {
        html += `
            <tr style="background: ${player.points > 15 ? 'rgba(76, 175, 80, 0.1)' : player.points < 5 ? 'rgba(244, 67, 54, 0.1)' : 'transparent'};">
                <td style="padding: 5px; border: 1px solid #606060;">${player.position}</td>
                <td style="padding: 5px; border: 1px solid #606060;">${player.name}</td>
                <td style="padding: 5px; border: 1px solid #606060; text-align: right; font-weight: bold;">${player.points}</td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    
    if (teams.team_2.bench && teams.team_2.bench.length > 0) {
        html += '<h4 style="margin-top: 15px;">Bench</h4>';
        html += '<table style="width: 100%; border-collapse: collapse;">';
        html += '<tbody>';
        teams.team_2.bench.forEach(player => {
            html += `
                <tr style="opacity: 0.7;">
                    <td style="padding: 5px; border: 1px solid #606060;">${player.position}</td>
                    <td style="padding: 5px; border: 1px solid #606060;">${player.name}</td>
                    <td style="padding: 5px; border: 1px solid #606060; text-align: right;">${player.points}</td>
                </tr>
            `;
        });
        html += '</tbody></table>';
    }
    html += '</div>';
    
    html += '</div>'; // End grid
    html += '</div>'; // End container
    
    return html;
}

export function closeBreakdownModal() {
    const modal = document.getElementById('matchupBreakdownModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// Export to window for onclick handlers and panel switching
window.showMatchupYear = showMatchupYear;
window.filterHeadToHead = filterHeadToHead;
window.clearHeadToHeadFilter = clearHeadToHeadFilter;
window.togglePlayerBreakdowns = togglePlayerBreakdowns;
window.showMatchupBreakdownModal = showMatchupBreakdownModal;
window.closeBreakdownModal = closeBreakdownModal;