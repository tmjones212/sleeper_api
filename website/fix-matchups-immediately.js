// Emergency fix for matchups panel
(function() {
    console.log('=== EMERGENCY MATCHUPS FIX ===');
    
    // Find matchups panel
    const matchupsPanel = document.getElementById('matchups-panel');
    if (!matchupsPanel) {
        console.error('matchups-panel not found!');
        return;
    }
    
    // Find panels container
    const panelsContainer = document.querySelector('.panels-container');
    if (!panelsContainer) {
        console.error('panels-container not found!');
        return;
    }
    
    // Check if matchups is nested
    let parent = matchupsPanel.parentElement;
    let isNested = false;
    while (parent && parent !== panelsContainer) {
        if (parent.classList && parent.classList.contains('visualization-panel')) {
            console.log('Found nesting! matchups-panel is inside:', parent.id || parent.className);
            isNested = true;
            break;
        }
        parent = parent.parentElement;
    }
    
    if (isNested) {
        console.log('Moving matchups-panel to panels-container...');
        
        // Remove from current location
        matchupsPanel.remove();
        
        // Find draft panel (should be last)
        const draftPanel = document.getElementById('draft-panel');
        
        if (draftPanel) {
            // Insert before draft panel
            panelsContainer.insertBefore(matchupsPanel, draftPanel);
        } else {
            // Just append to end
            panelsContainer.appendChild(matchupsPanel);
        }
        
        console.log('✓ Moved matchups-panel to correct location');
    }
    
    // Now fix the display
    console.log('Fixing display...');
    
    // Hide all panels first
    document.querySelectorAll('.visualization-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    
    // Show matchups panel
    matchupsPanel.classList.add('active');
    
    // Force visibility
    matchupsPanel.style.display = 'block';
    matchupsPanel.style.visibility = 'visible';
    matchupsPanel.style.opacity = '1';
    matchupsPanel.style.minHeight = '600px';
    
    const panelContent = matchupsPanel.querySelector('.panel-content');
    if (panelContent) {
        panelContent.style.display = 'block';
        panelContent.style.visibility = 'visible';
        panelContent.style.minHeight = '500px';
    }
    
    const container = document.getElementById('matchupsContainer');
    if (container) {
        container.style.display = 'block';
        container.style.visibility = 'visible';
        container.style.minHeight = '400px';
    }
    
    // Call showMatchupYear if it exists
    if (typeof window.showMatchupYear === 'function') {
        window.showMatchupYear();
    }
    
    console.log('✓ Matchups panel should now be visible!');
    console.log('Panel dimensions:', matchupsPanel.offsetWidth + 'x' + matchupsPanel.offsetHeight);
})();