// ============= EXTRACTED FUNCTIONS FROM OLD HTML =============
// These functions handle the draft and matchup year functionality

// ------------- showMatchupYear Function -------------
        function showMatchupYear() {
            const selectedYear = document.getElementById('matchupYearSelect').value;
            const yearMatchups = document.querySelectorAll('.year-matchups');
            
            yearMatchups.forEach(yearDiv => {
                if (selectedYear === 'all') {
                    yearDiv.style.display = 'block';
                } else {
                    const yearValue = yearDiv.getAttribute('data-year');
                    yearDiv.style.display = yearValue === selectedYear ? 'block' : 'none';
                }
            });
            
            // Reapply head-to-head filter if active
            if (window.currentHeadToHeadFilter) {
                filterHeadToHead(window.currentHeadToHeadFilter.team1, window.currentHeadToHeadFilter.team2, false);
            }
        }

// ------------- Head-to-Head Filter Functions -------------
        function filterHeadToHead(team1, team2, showNotification = true) {
            // Store current filter
            window.currentHeadToHeadFilter = { team1, team2 };
            
            // Show filter indicator
            const filterDiv = document.getElementById('headToHeadFilter');
            const filterText = document.getElementById('filterText');
            filterText.textContent = `Showing: ${team1} vs ${team2}`;
            filterDiv.style.display = 'inline-block';
            
            // Find all matchup divs using the class selector
            const allMatchupDivs = document.querySelectorAll('.matchup-card');
            let visibleMatchups = 0;
            
            allMatchupDivs.forEach(matchupDiv => {
                const teamNameDivs = matchupDiv.querySelectorAll('.team > div:first-child');
                if (teamNameDivs.length >= 2) {
                    const matchupTeam1 = teamNameDivs[0].textContent.trim();
                    const matchupTeam2 = teamNameDivs[1].textContent.trim();
                    
                    // Check if this matchup involves both selected teams
                    const isMatch = (matchupTeam1 === team1 && matchupTeam2 === team2) || 
                                  (matchupTeam1 === team2 && matchupTeam2 === team1);
                    
                    if (isMatch) {
                        matchupDiv.style.display = 'flex';
                        visibleMatchups++;
                    } else {
                        matchupDiv.style.display = 'none';
                    }
                }
            });
            
            // Hide week cards that have no visible matchups
            const weekCards = document.querySelectorAll('.week-card');
            weekCards.forEach(weekCard => {
                const visibleMatchupsInWeek = Array.from(weekCard.querySelectorAll('.matchup-card'))
                    .filter(div => div.style.display !== 'none').length;
                weekCard.style.display = visibleMatchupsInWeek > 0 ? 'block' : 'none';
            });
            
            if (showNotification && visibleMatchups === 0) {
                alert(`No matchups found between ${team1} and ${team2}`);
                clearHeadToHeadFilter();
            }
        }

        function clearHeadToHeadFilter() {
            // Clear filter storage
            window.currentHeadToHeadFilter = null;
            
            // Hide filter indicator
            document.getElementById('headToHeadFilter').style.display = 'none';
            
            // Show all matchups using the class selector
            const allMatchupDivs = document.querySelectorAll('.matchup-card');
            allMatchupDivs.forEach(matchupDiv => {
                matchupDiv.style.display = 'flex';
            });
            
            // Show all week cards that have any matchups
            const weekCards = document.querySelectorAll('.week-card');
            weekCards.forEach(weekCard => {
                const hasAnyMatchups = weekCard.querySelectorAll('.matchup-card').length > 0;
                weekCard.style.display = hasAnyMatchups ? 'block' : 'none';
            });
        }

// ------------- showDraftYear and createDraftBoard Functions -------------
        function showDraftYear() {
            const selectedYear = document.getElementById('draftYearSelect').value;
            const draftResults = document.getElementById('draftResults');
            
            if (!draftData.drafts_by_year[selectedYear] || draftData.drafts_by_year[selectedYear].length === 0) {
                draftResults.innerHTML = `
                    <div style="text-align: center; color: #b0b0b0; padding: 40px;">
                        <h3>📭 No Draft Data for ${selectedYear}</h3>
                        <p>No draft information found for this year.</p>
                    </div>
                `;
                return;
            }
            
            const draftInfo = draftData.drafts_by_year[selectedYear][0];
            createDraftBoard(draftInfo, draftResults);
        }

        // Create draft board layout
        function createDraftBoard(draftInfo, container) {
            // Get teams ordered by their draft position (1st pick, 2nd pick, etc.)
            const teamsByPosition = {};
            draftInfo.picks.forEach(pick => {
                if (pick.round === 1) {
                    teamsByPosition[pick.pick_in_round] = pick.original_owner;
                }
            });
            
            // Sort teams by their draft position
            const teams = Object.keys(teamsByPosition)
                .sort((a, b) => parseInt(a) - parseInt(b))
                .map(position => teamsByPosition[position]);
            
            const rounds = Math.max(...draftInfo.picks.map(pick => pick.round));
            
            // Create a lookup for picks by original owner and round
            const picksByTeamAndRound = {};
            draftInfo.picks.forEach(pick => {
                if (!picksByTeamAndRound[pick.original_owner]) {
                    picksByTeamAndRound[pick.original_owner] = {};
                }
                picksByTeamAndRound[pick.original_owner][pick.round] = pick;
            });

            let draftHTML = `
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>${draftInfo.stats.total_picks}</h3>
                        <p>Total Picks</p>
                    </div>
                    <div class="stat-card">
                        <h3>${draftInfo.stats.traded_picks}</h3>
                        <p>Traded Picks</p>
                    </div>
                    <div class="stat-card">
                        <h3>${draftInfo.stats.total_rounds}</h3>
                        <p>Rounds</p>
                    </div>
                </div>
                
                <div class="draft-board">
                    <table>
                        <thead>
                            <tr>
                                <th>Round</th>
                                ${teams.map(team => `<th>${team}</th>`).join('')}
                            </tr>
                        </thead>
                        <tbody>
            `;
            
            for (let round = 1; round <= rounds; round++) {
                draftHTML += '<tr>';
                draftHTML += `<td class="round-number">R${round}</td>`;
                
                teams.forEach(team => {
                    const pick = picksByTeamAndRound[team] && picksByTeamAndRound[team][round];
                    if (pick) {
                        const isTraded = pick.current_owner !== pick.original_owner;
                        const cellClass = isTraded ? 'traded' : '';
                        
                        draftHTML += `<td class="draft-pick ${cellClass}">`;
                        
                        if (pick.player_name) {
                            draftHTML += `
                                <div class="pick-number">#${pick.overall_pick}</div>
                                <div class="player-name">${pick.player_name}</div>
                            `;
                            if (isTraded) {
                                draftHTML += `<div class="traded-to">→ ${pick.current_owner}</div>`;
                            }
                        } else {
                            // Future pick
                            draftHTML += `<div class="future-pick">Future Pick</div>`;
                            if (isTraded) {
                                draftHTML += `<div class="traded-to">→ ${pick.current_owner}</div>`;
                            }
                        }
                        
                        draftHTML += '</td>';
                    } else {
                        draftHTML += '<td class="draft-pick empty">-</td>';
                    }
                });
                
                draftHTML += '</tr>';
            }
            
            draftHTML += `
                        </tbody>
                    </table>
                </div>
                <div class="draft-legend">
                    <span class="legend-item"><span class="legend-box"></span> Original Owner</span>
                    <span class="legend-item"><span class="legend-box traded"></span> Traded Pick</span>
                </div>
            `;
            
            container.innerHTML = draftHTML;
        }
// ------------- Matchup Breakdown Modal Functions -------------
        function showMatchupBreakdownModal(leagueId, week, teams, scores, matchupId) {
            console.log('showMatchupBreakdownModal called with:', leagueId, week, teams, scores, matchupId);
            
            // Create and show modal
            let modal = document.getElementById('playerBreakdownModal');
            if (!modal) {
                console.log('Creating new modal');
                modal = createBreakdownModal();
            }
            
            const modalContent = modal.querySelector('.breakdown-modal-content');
            modalContent.innerHTML = '<div class="breakdown-loading">Loading player breakdown...</div>';
            modal.style.display = 'block';
            // Force display with important flag
            modal.style.setProperty('display', 'block', 'important');
            console.log('Modal should be visible now');
            console.log('Modal display style:', modal.style.display);
            console.log('Modal in DOM:', document.contains(modal));
            console.log('Modal element:', modal);
            
            // Find breakdown data
            const cacheKey = `${leagueId}_${week}`;
            console.log('Looking for cache key:', cacheKey);
            const weekData = MATCHUP_BREAKDOWNS[cacheKey];
            console.log('Found week data:', weekData ? weekData.length + ' teams' : 'null');
            
            if (!weekData) {
                modalContent.innerHTML = '<div class="breakdown-error">No breakdown data available for this week<br>Cache key: ' + cacheKey + '</div>';
                return;
            }
            
            // Find the specific matchup by matchup_id (much more reliable than score matching)
            console.log('Looking for teams:', teams, 'matchupId:', matchupId);
            
            let matchupTeams = [];
            
            if (matchupId) {
                // Use matchup_id directly (most reliable)
                matchupTeams = weekData.filter(team => team.matchup_id === parseInt(matchupId));
                console.log('Found teams by matchup_id:', matchupTeams.length);
            } else {
                // Fallback to score matching if no matchup_id provided
                const matchupGroups = {};
                
                // Group by matchup_id
                weekData.forEach(team => {
                    const teamMatchupId = team.matchup_id;
                    if (!matchupGroups[teamMatchupId]) {
                        matchupGroups[teamMatchupId] = [];
                    }
                    matchupGroups[teamMatchupId].push(team);
                });
                
                // Find the matchup with matching scores
                if (scores && scores.length === 2) {
                    for (const teamMatchupId in matchupGroups) {
                        const matchup = matchupGroups[teamMatchupId];
                        if (matchup.length === 2) {
                            const matchupScores = matchup.map(t => t.total_points);
                            // Check if scores match (in either order)
                            if ((Math.abs(matchupScores[0] - scores[0]) < 0.1 && Math.abs(matchupScores[1] - scores[1]) < 0.1) ||
                                (Math.abs(matchupScores[0] - scores[1]) < 0.1 && Math.abs(matchupScores[1] - scores[0]) < 0.1)) {
                                matchupTeams = matchup;
                                break;
                            }
                        }
                    }
                }
                
                if (matchupTeams.length === 0) {
                    console.log('Could not find matchup by scores, using first matchup');
                    matchupTeams = Object.values(matchupGroups)[0] || [];
                }
            }
            
            console.log('Found matchup teams:', matchupTeams);
            
            // Pass the actual team names from the clicked matchup
            modalContent.innerHTML = generateBreakdownHTML(matchupTeams, week, teams);
        }

        function createBreakdownModal() {
            const modal = document.createElement('div');
            modal.id = 'playerBreakdownModal';
            modal.style.cssText = `
                position: fixed;
                z-index: 10000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.8);
                overflow-y: auto;
                display: none;
            `;
            modal.innerHTML = `
                    <div class="breakdown-modal-content" style="
                        background-color: #2d2d2d;
                        margin: 50px auto;
                        padding: 20px;
                        border-radius: 15px;
                        width: 90%;
                        max-width: 1200px;
                        color: #e0e0e0;
                        position: relative;
                    ">
                        <span onclick="closeBreakdownModal()" style="
                            color: #aaa;
                            float: right;
                            font-size: 28px;
                            font-weight: bold;
                            cursor: pointer;
                            padding: 10px;
                        ">&times;</span>
                        <!-- Content will be loaded here -->
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            return modal;
        }

        function generateBreakdownHTML(teams, week, teamNames) {
            if (!teams || teams.length === 0) {
                return '<div class="breakdown-error">No team data available</div>';
            }
            
            let html = `
                <h2 style="color: #e0e0e0; margin-bottom: 20px;">Week ${week} Player Breakdown</h2>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
            `;
            
            teams.forEach((team, index) => {
                // Calculate actual bench points
                const actualBenchPoints = team.bench.reduce((sum, player) => sum + player.points, 0);
                // Use the team names from the clicked matchup
                const teamName = (teamNames && teamNames[index]) ? teamNames[index] : `Roster ${team.roster_id}`;
                
                html += `
                    <div style="border: 1px solid #555; border-radius: 10px; padding: 15px;">
                        <h3 style="text-align: center; color: #667eea; margin-bottom: 15px;">
                            ${teamName} - ${team.total_points.toFixed(1)} pts
                        </h3>
                        
                        <div style="background: #404040; padding: 10px; border-radius: 5px; margin-bottom: 15px; text-align: center;">
                            <strong>Starters: ${team.starter_points.toFixed(1)} | Bench: ${actualBenchPoints.toFixed(1)}</strong>
                        </div>
                        
                        <h4 style="color: #667eea; margin-bottom: 10px;">Starters</h4>
                        <div style="margin-bottom: 20px;">
                `;
                
                team.starters.forEach(player => {
                    html += `
                        <div style="display: grid; grid-template-columns: 50px 1fr 40px 50px; gap: 10px; padding: 5px; background: #404040; margin-bottom: 2px; border-radius: 3px; align-items: center;">
                            <span style="background: #667eea; color: white; padding: 2px 4px; border-radius: 3px; font-size: 12px; text-align: center;">${player.roster_slot}</span>
                            <span>${player.name}</span>
                            <span style="font-size: 12px; color: #aaa;">${player.position}</span>
                            <span style="font-weight: bold; text-align: right; color: #4CAF50;">${player.points.toFixed(1)}</span>
                        </div>
                    `;
                });
                
                html += `
                        </div>
                        <h4 style="color: #667eea; margin-bottom: 10px;">Bench</h4>
                        <div>
                `;
                
                team.bench.slice(0, 8).forEach(player => { // Show top 8 bench players
                    html += `
                        <div style="display: grid; grid-template-columns: 50px 1fr 40px 50px; gap: 10px; padding: 5px; background: #353535; margin-bottom: 2px; border-radius: 3px; align-items: center;">
                            <span style="background: #666; color: white; padding: 2px 4px; border-radius: 3px; font-size: 12px; text-align: center;">BN</span>
                            <span>${player.name}</span>
                            <span style="font-size: 12px; color: #aaa;">${player.position}</span>
                            <span style="font-weight: bold; text-align: right; color: #4CAF50;">${player.points.toFixed(1)}</span>
                        </div>
                    `;
                });
                
                html += '</div></div>';
            });
            
            html += '</div>';
            return html;
        }

        function closeBreakdownModal() {
            const modal = document.getElementById('playerBreakdownModal');
            if (modal) {
                modal.style.display = 'none';
            }
        }
