/**
 * Network Module
 * Handles the trade network visualization using vis.js
 */

import { networkData } from './data/networkData.js';

let network = null;

export function initNetworkGraph() {
    const container = document.getElementById('trade-network');
    if (!container) return;
    
    // Create nodes with team data
    const nodes = new vis.DataSet();
    const edges = new vis.DataSet();
    
    // Add nodes
    Object.entries(networkData.nodes).forEach(([teamName, teamData]) => {
        nodes.add({
            id: teamName,
            label: `${teamName}\n${teamData.total_trades} trades`,
            value: teamData.total_trades,
            title: `${teamName}<br>Total Trades: ${teamData.total_trades}<br>Players Acquired: ${teamData.players_acquired}<br>Players Given: ${teamData.players_given}`,
            teamData: teamData
        });
    });
    
    // Add edges
    Object.entries(networkData.edges).forEach(([teamPair, edgeData]) => {
        // Parse team names from string format "('Team1', 'Team2')"
        const match = teamPair.match(/\('([^']+)', '([^']+)'\)/);
        if (match) {
            const [_, team1, team2] = match;
            edges.add({
                from: team1,
                to: team2,
                value: edgeData.weight,
                title: `${edgeData.weight} trades<br>${edgeData.total_players} players<br>${edgeData.total_picks} picks`,
                edgeData: edgeData
            });
        }
    });
    
    const data = { nodes, edges };
    
    const options = {
        nodes: {
            shape: 'dot',
            scaling: {
                min: 20,
                max: 50
            },
            font: {
                size: 12,
                color: '#e0e0e0'
            },
            color: {
                background: '#0066cc',
                border: '#004499',
                highlight: {
                    background: '#0088ff',
                    border: '#0066cc'
                }
            }
        },
        edges: {
            width: 2,
            scaling: {
                min: 1,
                max: 10
            },
            color: {
                color: '#666666',
                highlight: '#0066cc',
                hover: '#0066cc'
            },
            smooth: {
                type: 'continuous'
            }
        },
        interaction: {
            hover: true,
            tooltipDelay: 200,
            hideEdgesOnDrag: true
        },
        physics: {
            forceAtlas2Based: {
                gravitationalConstant: -50,
                centralGravity: 0.01,
                springLength: 100,
                springConstant: 0.08
            },
            maxVelocity: 50,
            solver: 'forceAtlas2Based',
            timestep: 0.35,
            stabilization: {
                enabled: true,
                iterations: 1000,
                updateInterval: 10
            }
        }
    };
    
    // Create network
    network = new vis.Network(container, data, options);
    
    // Add click handlers
    network.on('click', function(params) {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            const node = nodes.get(nodeId);
            if (node && node.teamData) {
                showTeamStats(nodeId, node.teamData);
            }
        }
    });
    
    // Handle edge clicks and double-clicks
    let clickTimer = null;
    let clickDelay = 300;
    
    network.on('selectEdge', function(params) {
        if (clickTimer === null) {
            clickTimer = setTimeout(() => {
                // Single click
                handleEdgeClick(params);
                clickTimer = null;
            }, clickDelay);
        } else {
            // Double click
            clearTimeout(clickTimer);
            clickTimer = null;
            handleEdgeClick(params);
        }
    });
    
    function handleEdgeClick(params) {
        if (params.edges.length > 0) {
            const edgeId = params.edges[0];
            const edge = edges.get(edgeId);
            if (edge) {
                const team1 = edge.from;
                const team2 = edge.to;
                showTeamTrades(team1, team2);
            }
        }
    }
}

export function showTeamStats(teamName, teamData) {
    const detailsContent = document.getElementById('trade-details-content');
    if (!detailsContent) return;
    
    let html = `
        <h4>${teamName} Statistics</h4>
        <div class="team-stats">
            <p><strong>Total Trades:</strong> ${teamData.total_trades}</p>
            <p><strong>Players Acquired:</strong> ${teamData.players_acquired}</p>
            <p><strong>Players Given:</strong> ${teamData.players_given}</p>
            <p><strong>Avg Players/Trade:</strong> ${teamData.avg_players_per_trade.toFixed(2)}</p>
            <p><strong>Most Frequent Partner:</strong> ${teamData.most_frequent_partner}</p>
            <p><strong>Trading Partners:</strong> ${teamData.partners.join(', ')}</p>
        </div>
    `;
    
    detailsContent.innerHTML = html;
}

export function showTeamTrades(team1, team2) {
    const detailsContent = document.getElementById('trade-details-content');
    if (!detailsContent) return;
    
    // Find the edge data
    let edgeData = null;
    let edgeKey = null;
    
    // Try both possible key formats
    const key1 = `('${team1}', '${team2}')`;
    const key2 = `('${team2}', '${team1}')`;
    
    if (networkData.edges[key1]) {
        edgeData = networkData.edges[key1];
        edgeKey = key1;
    } else if (networkData.edges[key2]) {
        edgeData = networkData.edges[key2];
        edgeKey = key2;
    }
    
    if (!edgeData) {
        detailsContent.innerHTML = '<p>No trades found between these teams.</p>';
        return;
    }
    
    let html = `
        <h4>${team1} ↔ ${team2}</h4>
        <p><strong>Total Trades:</strong> ${edgeData.weight}</p>
        <p><strong>Players Traded:</strong> ${edgeData.total_players}</p>
        <p><strong>Draft Picks Traded:</strong> ${edgeData.total_picks}</p>
        <div class="trade-list">
    `;
    
    edgeData.trades.forEach((trade, index) => {
        html += `
            <div class="trade-item-small">
                <h5>Trade ${index + 1} - ${trade.date}</h5>
        `;
        
        trade.details.teams.forEach(team => {
            if (team.team === team1 || team.team === team2) {
                html += `<div class="team-section"><strong>${team.team}</strong>`;
                
                if (team.gives.players.length > 0) {
                    html += '<div class="gives">Gave: ';
                    html += team.gives.players.map(p => p.player).join(', ');
                    html += '</div>';
                }
                
                if (team.receives.players.length > 0) {
                    html += '<div class="receives">Received: ';
                    html += team.receives.players.map(p => p.player).join(', ');
                    html += '</div>';
                }
                
                if (team.gives.draft_picks.length > 0) {
                    html += '<div class="gives">Gave picks: ';
                    html += team.gives.draft_picks.map(p => 
                        `${p.season} Round ${p.round}${p.player_name ? ` (#${p.pick_number} - ${p.player_name})` : ''}`
                    ).join(', ');
                    html += '</div>';
                }
                
                if (team.receives.draft_picks.length > 0) {
                    html += '<div class="receives">Received picks: ';
                    html += team.receives.draft_picks.map(p => 
                        `${p.season} Round ${p.round}${p.player_name ? ` (#${p.pick_number} - ${p.player_name})` : ''}`
                    ).join(', ');
                    html += '</div>';
                }
                
                html += '</div>';
            }
        });
        
        html += '</div>';
    });
    
    html += '</div>';
    detailsContent.innerHTML = html;
}

// Export to window for onclick handlers
window.initNetworkGraph = initNetworkGraph;
window.showTeamTrades = showTeamTrades;