// static/js/app.js - Mobile enhancements

// Prevent scrolling on mobile when touching the canvas
document.addEventListener('DOMContentLoaded', function() {
    const canvasContainer = document.getElementById('canvas-container');
    if (canvasContainer) {
        canvasContainer.addEventListener('touchmove', function(e) {
            e.preventDefault();
        }, { passive: false });
    }
    
    // Add touch support for the data panel toggling
    const toggleDataBtn = document.getElementById('toggleDataBtn');
    if (toggleDataBtn) {
        toggleDataBtn.addEventListener('touchend', function(e) {
            e.preventDefault(); // Prevent double-firing with click event
            const panel = document.getElementById('dataPanel');
            if (panel) {
                if (panel.style.display === 'block') {
                    panel.style.display = 'none';
                    this.textContent = 'Show Config';
                } else {
                    panel.style.display = 'block';
                    this.textContent = 'Hide Config';
                }
            }
        });
    }
    
    // Auto-hide status messages after 5 seconds on mobile
    const statusMessage = document.querySelector('.status-message');
    if (statusMessage) {
        setTimeout(() => {
            statusMessage.style.opacity = '0';
            setTimeout(() => {
                statusMessage.style.display = 'none';
            }, 500); // After fade out animation
        }, 5000);
    }
    
    // Fix iOS 100vh issue
    function fixIOSViewportHeight() {
        // iOS Safari has issues with 100vh - this fixes it
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    }
    
    fixIOSViewportHeight();
    window.addEventListener('resize', fixIOSViewportHeight);
}); 