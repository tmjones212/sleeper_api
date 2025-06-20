// Fix for matchups and draft tabs not showing content

document.addEventListener('DOMContentLoaded', function() {
    console.log('Running tab fix...');
    
    // Debug function to check panel visibility
    function debugPanels() {
        const panels = ['overview', 'network', 'matrix', 'timeline', 'players', 'matchups', 'draft'];
        panels.forEach(panelName => {
            const panel = document.getElementById(panelName + '-panel');
            if (panel) {
                const isActive = panel.classList.contains('active');
                const display = window.getComputedStyle(panel).display;
                console.log(`Panel ${panelName}: active=${isActive}, display=${display}`);
            } else {
                console.log(`Panel ${panelName}: NOT FOUND`);
            }
        });
    }
    
    // Check initial state
    console.log('Initial panel state:');
    debugPanels();
    
    // Ensure showMatchupYear and showDraftYear are called after a delay
    setTimeout(() => {
        console.log('Delayed initialization...');
        
        // Initialize matchups
        if (typeof showMatchupYear === 'function') {
            console.log('Calling showMatchupYear...');
            showMatchupYear();
            
            // Check if matchups panel is active and has content
            const matchupsPanel = document.getElementById('matchups-panel');
            if (matchupsPanel && matchupsPanel.classList.contains('active')) {
                const yearMatchups = matchupsPanel.querySelectorAll('.year-matchups');
                console.log(`Found ${yearMatchups.length} year-matchups divs`);
                yearMatchups.forEach(div => {
                    console.log(`Year ${div.getAttribute('data-year')}: display=${div.style.display}, children=${div.querySelector('.weeks-container')?.children.length || 0}`);
                });
            }
        }
        
        // Initialize draft
        if (typeof showDraftYear === 'function') {
            console.log('Calling showDraftYear...');
            showDraftYear();
            
            // Check draft results
            const draftResults = document.getElementById('draftResults');
            if (draftResults) {
                console.log(`Draft results content length: ${draftResults.innerHTML.length}`);
            }
        }
    }, 1000);
    
    // Override showPanel to add debugging
    const originalShowPanel = window.showPanel;
    window.showPanel = function(panelName) {
        console.log(`showPanel called with: ${panelName}`);
        
        // Call original function
        if (typeof originalShowPanel === 'function') {
            originalShowPanel(panelName);
        }
        
        // Additional logging
        setTimeout(() => {
            const panel = document.getElementById(panelName + '-panel');
            if (panel) {
                console.log(`Panel ${panelName} after switch: active=${panel.classList.contains('active')}, display=${window.getComputedStyle(panel).display}`);
                
                // Special handling for matchups and draft
                if (panelName === 'matchups' && typeof showMatchupYear === 'function') {
                    console.log('Re-initializing matchups...');
                    showMatchupYear();
                }
                if (panelName === 'draft' && typeof showDraftYear === 'function') {
                    console.log('Re-initializing draft...');
                    showDraftYear();
                }
            }
        }, 100);
    };
});

console.log('Tab fix script loaded');