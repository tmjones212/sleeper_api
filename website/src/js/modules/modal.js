/**
 * Modal Module
 * Handles modal creation and management
 */

export function showTradeModal(content) {
    const modal = document.getElementById('tradeModal') || createModal();
    const modalContent = modal.querySelector('.modal-body');
    modalContent.innerHTML = content;
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
}

export function closeTradeModal() {
    const modal = document.getElementById('tradeModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

function createModal() {
    const modal = document.createElement('div');
    modal.id = 'tradeModal';
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h2>Trade Details</h2>
                <span class="close" onclick="closeTradeModal()">&times;</span>
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
            closeTradeModal();
        }
    });
    
    return modal;
}

// Export to window for onclick handlers
window.showTradeModal = showTradeModal;
window.closeTradeModal = closeTradeModal;