// Panel switching function - defined early so buttons can use it
function showPanel(panelName) {
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
            if (typeof window.showMatchupYear === 'function') {
                window.showMatchupYear();
            }
        } else if (panelName === 'draft') {
            // Initialize draft results if needed
            console.log('🏈 Draft panel activated');
            setTimeout(() => {
                if (typeof showDraftYear === 'function') {
                    showDraftYear();
                }
            }, 100);
        }
    }
}