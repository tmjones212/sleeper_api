/**
 * Trade History Module
 * Handles trade history timeline, filtering, and grading
 */

import { getDb, saveTradeGradeToFirebase, loadAverageRatings, updateTradeGradeDisplay } from './firebase.js';

export function initializeTradeHistory() {
    // Populate team filter dropdown
    populateTeamFilter();
    
    // Add trading graders to all trades
    addTradingGradersToAllTrades();
    
    // Load saved grades
    loadTradeGrades();
    
    // Load average ratings from Firebase
    loadAverageRatings();
}

export function addTradingGradersToAllTrades() {
    const tradeItems = document.querySelectorAll('.trade-item');
    tradeItems.forEach((item, index) => {
        // Check if grader already exists
        if (!item.querySelector('.trade-grade-container')) {
            const graderHtml = `
                <div class="trade-grade-container">
                    <div style="margin-bottom: 8px; color: #e0e0e0; font-weight: 600;">👤 Your Trade Grade:</div>
                    <input type="range" min="0" max="100" value="50" 
                           class="trade-grade-slider" 
                           id="trade-grade-${index}"
                           onchange="updateTradeGrade('${index}', this.value)">
                    <div class="trade-grade-labels">
                        <span>Team 1 Won</span>
                        <span>Even</span>
                        <span>Team 2 Won</span>
                    </div>
                    <div class="trade-grade-result" id="trade-result-${index}">
                        <span style="color: #999999;">Move slider to grade</span>
                    </div>
                </div>
            `;
            item.insertAdjacentHTML('beforeend', graderHtml);
        }
    });
}

export function populateTeamFilter() {
    const filterSelect = document.getElementById('team-filter');
    if (!filterSelect) return;
    
    // Get all unique team names from trade items
    const teams = new Set();
    document.querySelectorAll('.trade-teams .team-side h4').forEach(el => {
        teams.add(el.textContent.trim());
    });
    
    // Clear existing options except "All Teams"
    filterSelect.innerHTML = '<option value="">All Teams</option>';
    
    // Add team options
    Array.from(teams).sort().forEach(team => {
        const option = document.createElement('option');
        option.value = team;
        option.textContent = team;
        filterSelect.appendChild(option);
    });
}

export function filterTradesByTeam() {
    const filterValue = document.getElementById('team-filter').value;
    const tradeItems = document.querySelectorAll('.trade-item');
    
    tradeItems.forEach(item => {
        if (!filterValue) {
            item.style.display = 'block';
        } else {
            const teamNames = Array.from(item.querySelectorAll('.team-side h4')).map(el => el.textContent.trim());
            if (teamNames.includes(filterValue)) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        }
    });
}

export function resetTradeFilter() {
    document.getElementById('team-filter').value = '';
    filterTradesByTeam();
}

export function updateTradeGrade(tradeIndex, value) {
    const slider = document.getElementById(`trade-grade-${tradeIndex}`);
    const resultDiv = document.getElementById(`trade-result-${tradeIndex}`);
    
    if (!slider || !resultDiv) return;
    
    // Get teams from the trade item
    const tradeItem = slider.closest('.trade-item');
    const teams = tradeItem.querySelectorAll('.team-side h4');
    const team1 = teams[0]?.textContent || 'Team 1';
    const team2 = teams[1]?.textContent || 'Team 2';
    
    // Determine result based on value
    let resultText = '';
    let resultColor = '';
    
    if (value < 40) {
        resultText = `You say: ${team1} won`;
        resultColor = '#66ff66';
    } else if (value > 60) {
        resultText = `You say: ${team2} won`;
        resultColor = '#ff6666';
    } else {
        resultText = 'You say: Even trade';
        resultColor = '#ffcc66';
    }
    
    resultDiv.innerHTML = `<span style="color: ${resultColor};">${resultText}</span>`;
    
    // Save the grade
    saveTradeGrade(tradeIndex, value);
}

export function saveTradeGrade(tradeIndex, gradeValue) {
    // Save to localStorage
    const grades = JSON.parse(localStorage.getItem('tradeGrades') || '{}');
    grades[tradeIndex] = gradeValue;
    localStorage.setItem('tradeGrades', JSON.stringify(grades));
    
    // Save to Firebase if available
    const userName = getUserName();
    saveTradeGradeToFirebase(tradeIndex, gradeValue, userName);
}

export function loadTradeGrades() {
    const grades = JSON.parse(localStorage.getItem('tradeGrades') || '{}');
    
    Object.entries(grades).forEach(([index, value]) => {
        const slider = document.getElementById(`trade-grade-${index}`);
        if (slider) {
            slider.value = value;
            // Use display-only function to avoid infinite loop
            updateTradeGradeDisplay(index, value);
        }
    });
}

export function getUserName() {
    let userName = localStorage.getItem('userName');
    if (!userName) {
        userName = prompt('Please enter your name for trade grading:') || 'Anonymous';
        localStorage.setItem('userName', userName);
    }
    return userName;
}

export function generateTradingSummary() {
    const container = document.getElementById('trading-summary-container');
    if (!container) return;
    
    const db = getDb();
    if (!db) {
        container.innerHTML = '<p style="color: #ff6666;">❌ Firebase not connected. Summary unavailable.</p>';
        return;
    }
    
    // Show loading state
    container.innerHTML = '<p style="color: #999;">Loading trading summary...</p>';
    
    // Render the table (will be updated with data later)
    renderTradingSummaryTable();
}

export function renderTradingSummaryTable() {
    const container = document.getElementById('trading-summary-container');
    if (!container) return;
    
    const html = `
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
            <thead>
                <tr style="background: #0066cc; color: white;">
                    <th style="padding: 10px; border: 1px solid #606060; cursor: pointer;" onclick="sortTradingTable('team')">Team ↕</th>
                    <th style="padding: 10px; border: 1px solid #606060; cursor: pointer;" onclick="sortTradingTable('trades')">Trades ↕</th>
                    <th style="padding: 10px; border: 1px solid #606060; cursor: pointer;" onclick="sortTradingTable('winRate')">Win Rate ↕</th>
                    <th style="padding: 10px; border: 1px solid #606060; cursor: pointer;" onclick="sortTradingTable('avgGrade')">Avg Grade ↕</th>
                    <th style="padding: 10px; border: 1px solid #606060;">Good Trades</th>
                    <th style="padding: 10px; border: 1px solid #606060;">Bad Trades</th>
                </tr>
            </thead>
            <tbody id="trading-summary-tbody">
                <tr>
                    <td colspan="6" style="text-align: center; padding: 20px; color: #999;">
                        Calculating team statistics...
                    </td>
                </tr>
            </tbody>
        </table>
        <p style="font-size: 0.9em; color: #999;">
            <strong>Note:</strong> Based on community trade grades. Win = grade < 40, Loss = grade > 60
        </p>
    `;
    
    container.innerHTML = html;
    
    // Calculate and display stats
    calculateTeamTradingStats();
}

let sortColumn = 'trades';
let sortDirection = 'desc';

export function sortTradingTable(column) {
    if (sortColumn === column) {
        sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        sortColumn = column;
        sortDirection = 'desc';
    }
    
    calculateTeamTradingStats();
}

export function calculateTeamTradingStats() {
    const teamStats = {};
    
    // Initialize team stats
    document.querySelectorAll('.trade-item').forEach((item, index) => {
        const teams = Array.from(item.querySelectorAll('.team-side h4')).map(el => el.textContent.trim());
        teams.forEach(team => {
            if (!teamStats[team]) {
                teamStats[team] = {
                    totalTrades: 0,
                    wins: 0,
                    losses: 0,
                    evens: 0,
                    totalGrade: 0,
                    gradedTrades: 0
                };
            }
            teamStats[team].totalTrades++;
        });
    });
    
    // Count wins/losses based on grades
    document.querySelectorAll('.trade-item').forEach((item, index) => {
        const slider = item.querySelector(`#trade-grade-${index}`);
        if (slider && slider.value !== '50') {
            const teams = Array.from(item.querySelectorAll('.team-side h4')).map(el => el.textContent.trim());
            const value = parseInt(slider.value);
            
            if (teams.length >= 2) {
                const team1 = teams[0];
                const team2 = teams[1];
                
                if (value < 40) {
                    // Team 1 won
                    teamStats[team1].wins++;
                    teamStats[team2].losses++;
                    teamStats[team1].totalGrade += (100 - value);
                    teamStats[team2].totalGrade += value;
                } else if (value > 60) {
                    // Team 2 won
                    teamStats[team2].wins++;
                    teamStats[team1].losses++;
                    teamStats[team2].totalGrade += (100 - value);
                    teamStats[team1].totalGrade += value;
                } else {
                    // Even trade
                    teamStats[team1].evens++;
                    teamStats[team2].evens++;
                    teamStats[team1].totalGrade += 50;
                    teamStats[team2].totalGrade += 50;
                }
                
                teamStats[team1].gradedTrades++;
                teamStats[team2].gradedTrades++;
            }
        }
    });
    
    // Convert to array and sort
    let sortedTeams = Object.entries(teamStats).map(([team, stats]) => {
        const winRate = stats.gradedTrades > 0 ? (stats.wins / stats.gradedTrades * 100).toFixed(1) : '0.0';
        const avgGrade = stats.gradedTrades > 0 ? (stats.totalGrade / stats.gradedTrades).toFixed(1) : '50.0';
        
        return {
            team,
            trades: stats.totalTrades,
            winRate: parseFloat(winRate),
            avgGrade: parseFloat(avgGrade),
            wins: stats.wins,
            losses: stats.losses,
            evens: stats.evens,
            gradedTrades: stats.gradedTrades
        };
    });
    
    // Sort based on current column
    sortedTeams.sort((a, b) => {
        let aVal, bVal;
        
        switch (sortColumn) {
            case 'team':
                aVal = a.team;
                bVal = b.team;
                break;
            case 'trades':
                aVal = a.trades;
                bVal = b.trades;
                break;
            case 'winRate':
                aVal = a.winRate;
                bVal = b.winRate;
                break;
            case 'avgGrade':
                aVal = a.avgGrade;
                bVal = b.avgGrade;
                break;
            default:
                aVal = a.trades;
                bVal = b.trades;
        }
        
        if (sortColumn === 'team') {
            return sortDirection === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
        } else {
            return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
        }
    });
    
    // Update table
    const tbody = document.getElementById('trading-summary-tbody');
    if (!tbody) return;
    
    tbody.innerHTML = sortedTeams.map(team => {
        const gradeClass = getGradeClass(team.avgGrade);
        const gradeText = getGradeText(team.avgGrade);
        
        return `
            <tr>
                <td style="padding: 10px; border: 1px solid #606060; font-weight: bold;">${team.team}</td>
                <td style="padding: 10px; border: 1px solid #606060; text-align: center;">${team.trades}</td>
                <td style="padding: 10px; border: 1px solid #606060; text-align: center;">
                    ${team.gradedTrades > 0 ? `${team.winRate}%` : '-'}
                    ${team.gradedTrades > 0 ? `<br><small>(${team.gradedTrades} graded)</small>` : ''}
                </td>
                <td style="padding: 10px; border: 1px solid #606060; text-align: center;" class="${gradeClass}">
                    ${team.gradedTrades > 0 ? `${team.avgGrade} (${gradeText})` : '-'}
                </td>
                <td style="padding: 10px; border: 1px solid #606060; text-align: center; color: #66ff66;">
                    ${team.wins}
                </td>
                <td style="padding: 10px; border: 1px solid #606060; text-align: center; color: #ff6666;">
                    ${team.losses}
                </td>
            </tr>
        `;
    }).join('');
}

export function getGradeClass(averageScore) {
    if (averageScore >= 70) return 'grade-a';
    if (averageScore >= 60) return 'grade-b';
    if (averageScore >= 50) return 'grade-c';
    if (averageScore >= 40) return 'grade-d';
    return 'grade-f';
}

export function getGradeText(averageScore) {
    if (averageScore >= 70) return 'A';
    if (averageScore >= 60) return 'B';
    if (averageScore >= 50) return 'C';
    if (averageScore >= 40) return 'D';
    return 'F';
}

export function refreshTradingSummary() {
    generateTradingSummary();
}

export function updateSummaryWithAverages(allRatings) {
    // Recalculate team stats with Firebase data
    const teamStats = {};
    
    // Initialize team stats
    document.querySelectorAll('.trade-item').forEach((item, index) => {
        const teams = Array.from(item.querySelectorAll('.team-side h4')).map(el => el.textContent.trim());
        teams.forEach(team => {
            if (!teamStats[team]) {
                teamStats[team] = {
                    totalTrades: 0,
                    wins: 0,
                    losses: 0,
                    evens: 0,
                    totalGrade: 0,
                    gradedTrades: 0
                };
            }
            teamStats[team].totalTrades++;
        });
    });
    
    // Count wins/losses based on Firebase ratings
    document.querySelectorAll('.trade-item').forEach((item, index) => {
        const dateEl = item.querySelector('.trade-date');
        const summaryEl = item.querySelector('.trade-summary strong');
        const tradeId = `${dateEl?.textContent.trim()}_${summaryEl?.textContent.trim()}`.replace(/[^a-zA-Z0-9]/g, '_');
        
        if (allRatings[tradeId]) {
            const teams = Array.from(item.querySelectorAll('.team-side h4')).map(el => el.textContent.trim());
            const value = allRatings[tradeId].average;
            
            if (teams.length >= 2) {
                const team1 = teams[0];
                const team2 = teams[1];
                
                if (value < 40) {
                    // Team 1 won
                    teamStats[team1].wins++;
                    teamStats[team2].losses++;
                    teamStats[team1].totalGrade += (100 - value);
                    teamStats[team2].totalGrade += value;
                } else if (value > 60) {
                    // Team 2 won
                    teamStats[team2].wins++;
                    teamStats[team1].losses++;
                    teamStats[team2].totalGrade += (100 - value);
                    teamStats[team1].totalGrade += value;
                } else {
                    // Even trade
                    teamStats[team1].evens++;
                    teamStats[team2].evens++;
                    teamStats[team1].totalGrade += 50;
                    teamStats[team2].totalGrade += 50;
                }
                
                teamStats[team1].gradedTrades++;
                teamStats[team2].gradedTrades++;
            }
        }
    });
    
    // Re-render the table with updated stats
    calculateTeamTradingStats();
}

// Export to window for onclick handlers
window.updateTradeGrade = updateTradeGrade;
window.filterTradesByTeam = filterTradesByTeam;
window.resetTradeFilter = resetTradeFilter;
window.sortTradingTable = sortTradingTable;
window.refreshTradingSummary = refreshTradingSummary;