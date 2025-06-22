/**
 * Draft Module
 * Handles draft board display and year selection
 */

import { getDraftData } from './externalData.js';

export function showDraftYear() {
    console.log('🏈 showDraftYear called');
    
    // Get draft data
    const draftData = getDraftData();
    
    // Check if draftData exists
    if (!draftData) {
        console.error('Draft data not loaded yet');
        return;
    }
    
    const yearSelect = document.getElementById('draftYearSelect');
    const selectedYear = yearSelect ? yearSelect.value : '2025';
    const container = document.getElementById('draftContainer');
    
    if (!container) {
        console.error('Draft container not found');
        return;
    }
    
    console.log('Selected draft year:', selectedYear);
    
    // Show loading state
    container.innerHTML = '<p style="text-align: center; color: #999;">Loading draft data...</p>';
    
    // Get draft info for selected year
    const yearData = draftData[selectedYear];
    
    if (!yearData) {
        container.innerHTML = `<p style="text-align: center; color: #ff6666;">No draft data available for ${selectedYear}</p>`;
        return;
    }
    
    // Create draft board
    createDraftBoard(yearData, container);
}

export function createDraftBoard(draftInfo, container) {
    if (!draftInfo || !draftInfo.picks) {
        container.innerHTML = '<p style="text-align: center; color: #ff6666;">Invalid draft data</p>';
        return;
    }
    
    const picks = draftInfo.picks;
    const settings = draftInfo.settings || {};
    const rounds = settings.rounds || 15;
    const teams = settings.teams || 10;
    
    // Build draft board HTML
    let html = '<div class="draft-board-container" style="overflow-x: auto;">';
    html += '<h3 style="margin-bottom: 20px;">Draft Results - ' + (draftInfo.season || 'Unknown Season') + '</h3>';
    
    // Create table
    html += '<table class="draft-board" style="width: 100%; border-collapse: collapse;">';
    
    // Header row with team names
    html += '<thead><tr>';
    html += '<th style="padding: 10px; background: #404040; border: 1px solid #606060; position: sticky; left: 0; z-index: 10;">Round</th>';
    
    // Get team names for columns
    const teamNames = [];
    for (let i = 1; i <= teams; i++) {
        const firstPick = picks.find(p => p.draft_slot === i);
        const teamName = firstPick ? firstPick.picked_by : `Team ${i}`;
        teamNames.push(teamName);
        html += `<th style="padding: 10px; background: #404040; border: 1px solid #606060; min-width: 120px;">${teamName}</th>`;
    }
    
    html += '</tr></thead>';
    html += '<tbody>';
    
    // Create rows for each round
    for (let round = 1; round <= rounds; round++) {
        html += '<tr>';
        html += `<td style="padding: 10px; background: #404040; border: 1px solid #606060; font-weight: bold; position: sticky; left: 0; z-index: 5;">Round ${round}</td>`;
        
        // Add picks for each team in this round
        for (let slot = 1; slot <= teams; slot++) {
            const pick = picks.find(p => p.round === round && p.draft_slot === slot);
            
            if (pick && pick.metadata) {
                const player = pick.metadata;
                const positionClass = getPositionClass(player.position);
                
                html += `
                    <td style="padding: 5px; border: 1px solid #606060; background: rgba(0, 102, 204, 0.1);">
                        <div class="draft-pick ${positionClass}" style="text-align: center;">
                            <div style="font-weight: bold; font-size: 0.8em; color: ${getPositionColor(player.position)};">
                                ${player.position}
                            </div>
                            <div style="font-size: 0.9em; margin: 2px 0;">
                                ${player.first_name} ${player.last_name}
                            </div>
                            <div style="font-size: 0.8em; color: #999;">
                                ${player.team || 'FA'}
                            </div>
                            <div style="font-size: 0.7em; color: #666;">
                                Pick ${pick.pick_no}
                            </div>
                        </div>
                    </td>
                `;
            } else {
                html += '<td style="padding: 5px; border: 1px solid #606060; text-align: center; color: #666;">-</td>';
            }
        }
        
        html += '</tr>';
    }
    
    html += '</tbody></table>';
    html += '</div>';
    
    // Add draft summary
    html += '<div style="margin-top: 20px;">';
    html += '<h4>Draft Summary</h4>';
    html += '<div class="stats-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 10px;">';
    
    // Position breakdown
    const positionCounts = {};
    picks.forEach(pick => {
        if (pick.metadata && pick.metadata.position) {
            positionCounts[pick.metadata.position] = (positionCounts[pick.metadata.position] || 0) + 1;
        }
    });
    
    Object.entries(positionCounts).sort((a, b) => b[1] - a[1]).forEach(([pos, count]) => {
        html += `
            <div class="stat-card" style="background: #2d2d2d; padding: 15px; border-radius: 10px; border: 1px solid #404040;">
                <h3 style="color: ${getPositionColor(pos)}; margin: 0;">${count}</h3>
                <p style="margin: 5px 0 0 0; color: #e0e0e0;">${pos}s drafted</p>
            </div>
        `;
    });
    
    html += '</div>';
    html += '</div>';
    
    container.innerHTML = html;
}

function getPositionClass(position) {
    const pos = position.toUpperCase();
    if (pos === 'QB') return 'position-qb';
    if (pos === 'RB') return 'position-rb';
    if (pos === 'WR') return 'position-wr';
    if (pos === 'TE') return 'position-te';
    if (pos === 'DEF') return 'position-def';
    if (pos === 'K') return 'position-k';
    return 'position-other';
}

function getPositionColor(position) {
    const pos = position.toUpperCase();
    if (pos === 'QB') return '#ff6b6b';
    if (pos === 'RB') return '#4ecdc4';
    if (pos === 'WR') return '#45b7d1';
    if (pos === 'TE') return '#f39c12';
    if (pos === 'DEF') return '#9b59b6';
    if (pos === 'K') return '#95a5a6';
    return '#e0e0e0';
}

// Export to window for panel switching
window.showDraftYear = showDraftYear;