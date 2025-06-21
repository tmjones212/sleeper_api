/**
 * Player Journey Module
 * Handles player journey search and visualization
 */

let playerJourneyNetwork = null;

export async function searchPlayerJourney() {
    const searchInput = document.getElementById('player-search');
    const playerName = searchInput ? searchInput.value.trim() : '';
    
    if (!playerName) {
        alert('Please enter a player name');
        return;
    }
    
    const resultsDiv = document.getElementById('player-journey-results');
    if (!resultsDiv) return;
    
    // Show loading state
    resultsDiv.innerHTML = '<p>Searching for player journey...</p>';
    
    try {
        // In a real implementation, this would fetch from an API
        // For now, we'll use a mock search
        displayLocalPlayerSearch(playerName);
    } catch (error) {
        console.error('Error searching player:', error);
        resultsDiv.innerHTML = '<p style="color: #ff6666;">Error searching for player. Please try again.</p>';
    }
}

export function displayPlayerJourney(journeyData) {
    const resultsDiv = document.getElementById('player-journey-results');
    if (!resultsDiv) return;
    
    let html = '<div class="player-journey">';
    
    // Player header
    html += `
        <div class="player-header" style="display: flex; align-items: center; gap: 20px; margin-bottom: 20px;">
            <img src="${journeyData.image_url}" alt="${journeyData.player_name}" 
                 style="width: 80px; height: 80px; border-radius: 50%; object-fit: cover;"
                 onerror="this.src='https://sleepercdn.com/images/v2/icons/player_default.webp'">
            <div>
                <h3>${journeyData.player_name}</h3>
                <p>Position: ${journeyData.position} | Team: ${journeyData.team || 'FA'}</p>
                <p>Total Trades: ${journeyData.total_trades}</p>
            </div>
        </div>
    `;
    
    // Journey timeline
    html += '<div class="journey-timeline">';
    html += '<h4>Trade History</h4>';
    
    journeyData.journey.forEach((step, index) => {
        const isLastStep = index === journeyData.journey.length - 1;
        html += `
            <div class="timeline-step" style="margin-bottom: 20px; padding-left: 30px; border-left: 3px solid ${isLastStep ? 'transparent' : '#0066cc'};">
                <div class="step-marker" style="position: absolute; left: -8px; width: 16px; height: 16px; border-radius: 50%; background: #0066cc; border: 3px solid #1a1a1a;"></div>
                <div class="step-content" style="background: #2d2d2d; padding: 15px; border-radius: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <h5 style="margin: 0 0 5px 0; color: #0066cc;">${step.team}</h5>
                            <p style="margin: 0; color: #999; font-size: 0.9em;">${step.acquired_date || 'Original Team'}</p>
                        </div>
                        ${step.traded_date ? `
                            <div style="text-align: right;">
                                <p style="margin: 0; color: #ff6666; font-size: 0.9em;">Traded: ${step.traded_date}</p>
                                <p style="margin: 0; color: #999; font-size: 0.8em;">To: ${step.traded_to}</p>
                            </div>
                        ` : '<span style="color: #66ff66;">Current Team</span>'}
                    </div>
                    ${step.trade_details ? `
                        <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #404040;">
                            <p style="margin: 0; font-size: 0.9em;">Trade Details: ${step.trade_details}</p>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    
    // Network visualization
    html += '<div class="journey-network" style="margin-top: 30px;">';
    html += '<h4>Team Network</h4>';
    html += '<div id="player-journey-network" style="height: 400px; background: #2d2d2d; border: 1px solid #404040; border-radius: 8px;"></div>';
    html += '</div>';
    
    html += '</div>';
    
    resultsDiv.innerHTML = html;
    
    // Create network visualization
    setTimeout(() => createPlayerJourneyNetwork(journeyData), 100);
}

export function createPlayerJourneyNetwork(journeyData) {
    const container = document.getElementById('player-journey-network');
    if (!container) return;
    
    // Create nodes for each team
    const nodes = new vis.DataSet();
    const edges = new vis.DataSet();
    
    const teamSet = new Set();
    journeyData.journey.forEach(step => {
        teamSet.add(step.team);
        if (step.traded_to) {
            teamSet.add(step.traded_to);
        }
    });
    
    // Add nodes
    let nodeId = 0;
    const teamToNodeId = {};
    teamSet.forEach(team => {
        teamToNodeId[team] = nodeId;
        nodes.add({
            id: nodeId,
            label: team,
            color: {
                background: team === journeyData.current_team ? '#66ff66' : '#0066cc',
                border: team === journeyData.current_team ? '#44dd44' : '#004499'
            }
        });
        nodeId++;
    });
    
    // Add edges for trades
    journeyData.journey.forEach((step, index) => {
        if (step.traded_to) {
            edges.add({
                from: teamToNodeId[step.team],
                to: teamToNodeId[step.traded_to],
                label: step.traded_date,
                arrows: 'to',
                color: {
                    color: '#666666',
                    highlight: '#0066cc'
                }
            });
        }
    });
    
    const data = { nodes, edges };
    
    const options = {
        nodes: {
            shape: 'dot',
            size: 30,
            font: {
                size: 14,
                color: '#e0e0e0'
            }
        },
        edges: {
            font: {
                size: 12,
                color: '#999999',
                align: 'middle'
            },
            smooth: {
                type: 'cubicBezier',
                forceDirection: 'horizontal',
                roundness: 0.4
            }
        },
        layout: {
            hierarchical: {
                direction: 'LR',
                sortMethod: 'directed',
                levelSeparation: 200
            }
        },
        interaction: {
            hover: true,
            tooltipDelay: 200
        },
        physics: false
    };
    
    playerJourneyNetwork = new vis.Network(container, data, options);
    
    // Add click handler
    playerJourneyNetwork.on('click', function(params) {
        if (params.edges.length > 0) {
            const edgeId = params.edges[0];
            const edge = edges.get(edgeId);
            
            // Find the trade details
            journeyData.journey.forEach(step => {
                if (step.traded_date === edge.label) {
                    showJourneyStepDetails(step, journeyData);
                }
            });
        }
    });
}

export function showJourneyStepDetails(stepData, journeyData) {
    // Create a modal or update a details panel with trade information
    const detailsHtml = `
        <div style="background: #2d2d2d; padding: 20px; border-radius: 8px; margin-top: 20px;">
            <h4>Trade Details</h4>
            <p><strong>Date:</strong> ${stepData.traded_date}</p>
            <p><strong>From:</strong> ${stepData.team}</p>
            <p><strong>To:</strong> ${stepData.traded_to}</p>
            ${stepData.trade_details ? `<p><strong>Details:</strong> ${stepData.trade_details}</p>` : ''}
        </div>
    `;
    
    // You could append this to the results or show in a modal
    const resultsDiv = document.getElementById('player-journey-results');
    const existingDetails = resultsDiv.querySelector('.trade-details-panel');
    if (existingDetails) {
        existingDetails.innerHTML = detailsHtml;
    } else {
        const detailsPanel = document.createElement('div');
        detailsPanel.className = 'trade-details-panel';
        detailsPanel.innerHTML = detailsHtml;
        resultsDiv.appendChild(detailsPanel);
    }
}

export function displayLocalPlayerSearch(playerName) {
    const resultsDiv = document.getElementById('player-journey-results');
    if (!resultsDiv) return;
    
    // For now, show a message that we need to search through trades
    // In a real implementation, this would search through the trade data
    resultsDiv.innerHTML = `
        <div style="background: #2d2d2d; padding: 20px; border-radius: 8px;">
            <h4>Player Search: ${playerName}</h4>
            <p>To see player journeys, the system needs to process all trade data to track player movements.</p>
            <p>This feature would show:</p>
            <ul style="margin-left: 20px;">
                <li>Complete trade history for the player</li>
                <li>Teams they've been on</li>
                <li>Trade partners and dates</li>
                <li>Visual network of their journey</li>
            </ul>
            <p style="margin-top: 15px; color: #999;">
                Try searching for players you know have been traded multiple times in your league.
            </p>
        </div>
    `;
}

// Export to window for onclick handlers
window.searchPlayerJourney = searchPlayerJourney;