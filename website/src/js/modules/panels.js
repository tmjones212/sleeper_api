/**
 * Panel Management Module
 * Handles switching between different visualization panels
 */

export function showPanel(panelName) {
    console.log('Switching to panel:', panelName);
    
    // Hide all panels
    document.querySelectorAll('.visualization-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });
    
    // Show selected panel
    const targetPanel = document.getElementById(panelName + '-panel');
    if (targetPanel) {
        targetPanel.classList.add('active');
        console.log('Activated panel:', panelName + '-panel');
        console.log('Panel classList:', targetPanel.classList.toString());
        const computedStyle = window.getComputedStyle(targetPanel);
        const panelStyle = {
            display: computedStyle.display,
            visibility: computedStyle.visibility,
            opacity: computedStyle.opacity,
            position: computedStyle.position,
            width: targetPanel.clientWidth,
            height: targetPanel.clientHeight,
            offsetWidth: targetPanel.offsetWidth,
            offsetHeight: targetPanel.offsetHeight,
            overflow: computedStyle.overflow
        };
        console.log('Panel computed style:', JSON.stringify(panelStyle, null, 2));
        console.log('Panel innerHTML length:', targetPanel.innerHTML.length);
        console.log('Panel has children:', targetPanel.children.length);
        
        // Check panel-content
        const panelContent = targetPanel.querySelector('.panel-content');
        if (panelContent) {
            console.log('Panel content width:', panelContent.clientWidth);
            console.log('Panel content height:', panelContent.clientHeight);
        }
        
        // Check panels-container
        const panelsContainer = document.querySelector('.panels-container');
        if (panelsContainer) {
            console.log('Panels container width:', panelsContainer.clientWidth);
            console.log('Panels container height:', panelsContainer.clientHeight);
            console.log('Panels container display:', window.getComputedStyle(panelsContainer).display);
        }
        
        // Check matchupsContainer specifically
        if (panelName === 'matchups') {
            const container = document.getElementById('matchupsContainer');
            if (container) {
                console.log('matchupsContainer width:', container.clientWidth);
                console.log('matchupsContainer height:', container.clientHeight);
                console.log('matchupsContainer display:', window.getComputedStyle(container).display);
            }
        }
    } else {
        console.error('Panel not found:', panelName + '-panel');
    }
    
    // Find and activate the corresponding button
    document.querySelectorAll('.tab-button').forEach(button => {
        if (button.textContent.toLowerCase().includes(panelName)) {
            button.classList.add('active');
        }
    });
    
    // Initialize visualizations if needed
    if (panelName === 'network' && typeof initNetworkGraph === 'function') {
        initNetworkGraph();
    } else if (panelName === 'overview' && typeof initMonthlyChart === 'function') {
        initMonthlyChart();
    } else if (panelName === 'matchups') {
        // Initialize matchups if needed
        console.log('🎯 Matchups panel activated');
        // Call immediately without timeout
        if (typeof window.showMatchupYear === 'function') {
            console.log('Calling showMatchupYear...');
            window.showMatchupYear();
        } else {
            console.error('ERROR: showMatchupYear function not found!');
            // Try to define it inline if not found
            window.showMatchupYear = function() {
                console.log('Using inline showMatchupYear');
                const yearMatchups = document.querySelectorAll('.year-matchups');
                yearMatchups.forEach(yearDiv => {
                    if (yearDiv.getAttribute('data-year') === '2024') {
                        yearDiv.style.display = 'block';
                    }
                });
            };
            window.showMatchupYear();
        }
    } else if (panelName === 'draft') {
        // Initialize draft results if needed
        console.log('🏈 Draft panel activated');
        setTimeout(() => {
            if (typeof showDraftYear === 'function') {
                console.log('Calling showDraftYear...');
                showDraftYear();
            } else {
                console.log('showDraftYear function not found');
            }
        }, 100);
    }
}

// Export to window for onclick handlers
window.showPanel = showPanel;