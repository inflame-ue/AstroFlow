// static/js/mobile.js
// Module for handling mobile-specific functionality

import { app } from './pixiApp.js';

// Track touch interaction state
let touchState = {
    active: false,
    pinching: false,
    lastDistance: 0,
    initialScale: 1,
    currentScale: 1,
    lastTouchX: 0,
    lastTouchY: 0
};

// Configuration
const MIN_SCALE = 0.5;
const MAX_SCALE = 2.5;
const SCALE_SENSITIVITY = 0.01;

// Initialize mobile touch interactions
export function initMobileControls() {
    // Only setup mobile controls if touch is supported
    if ('ontouchstart' in window) {
        console.log('Touch device detected, initializing mobile controls');
        setupTouchEvents();
        setupMobileUI();
    }
}

// Add touch event listeners to the canvas
function setupTouchEvents() {
    const canvas = app.view;
    
    // Touch Start
    canvas.addEventListener('touchstart', (e) => {
        e.preventDefault(); // Prevent default behavior
        
        if (e.touches.length === 1) {
            // Single touch - for panning
            touchState.active = true;
            touchState.pinching = false;
            touchState.lastTouchX = e.touches[0].clientX;
            touchState.lastTouchY = e.touches[0].clientY;
        } else if (e.touches.length === 2) {
            // Two touches - for pinch zooming
            touchState.pinching = true;
            touchState.lastDistance = getTouchDistance(e.touches);
            touchState.initialScale = touchState.currentScale;
        }
    });
    
    // Touch Move
    canvas.addEventListener('touchmove', (e) => {
        e.preventDefault(); // Prevent default behavior
        
        if (!touchState.active) return;
        
        if (touchState.pinching && e.touches.length === 2) {
            // Handle pinch zoom
            const currentDistance = getTouchDistance(e.touches);
            const distanceDelta = currentDistance - touchState.lastDistance;
            
            // Calculate new scale with sensitivity adjustment
            let newScale = touchState.initialScale + (distanceDelta * SCALE_SENSITIVITY);
            
            // Limit zoom level
            newScale = Math.max(MIN_SCALE, Math.min(MAX_SCALE, newScale));
            
            // Apply zoom to the stage
            app.stage.scale.set(newScale);
            touchState.currentScale = newScale;
            
            touchState.lastDistance = currentDistance;
        } else if (e.touches.length === 1) {
            // Handle panning
            const deltaX = e.touches[0].clientX - touchState.lastTouchX;
            const deltaY = e.touches[0].clientY - touchState.lastTouchY;
            
            // Move the stage (adjust sensitivity if needed)
            app.stage.position.x += deltaX;
            app.stage.position.y += deltaY;
            
            touchState.lastTouchX = e.touches[0].clientX;
            touchState.lastTouchY = e.touches[0].clientY;
        }
    });
    
    // Touch End
    canvas.addEventListener('touchend', (e) => {
        if (e.touches.length === 0) {
            // Reset touch state when all fingers are lifted
            touchState.active = false;
            touchState.pinching = false;
        } else if (e.touches.length === 1) {
            // Switch from pinching to single touch
            touchState.pinching = false;
            touchState.lastTouchX = e.touches[0].clientX;
            touchState.lastTouchY = e.touches[0].clientY;
        }
    });
}

// Setup mobile-specific UI adjustments
function setupMobileUI() {
    const toggleButton = document.getElementById('toggleDataBtn');
    if (toggleButton) {
        // Make the button larger and more touch-friendly
        toggleButton.style.padding = '12px 16px';
        toggleButton.style.fontSize = '1rem';
    }
    
    // Add double-tap to reset view
    const canvas = app.view;
    let lastTap = 0;
    
    canvas.addEventListener('touchend', (e) => {
        const currentTime = new Date().getTime();
        const tapLength = currentTime - lastTap;
        
        if (tapLength < 300 && tapLength > 0) {
            // Double tap detected - reset view
            resetView();
            e.preventDefault();
        }
        
        lastTap = currentTime;
    });
}

// Reset view to default position and scale
function resetView() {
    // Animate the reset for a smoother experience
    gsap.to(app.stage.position, {
        x: window.innerWidth / 2,
        y: window.innerHeight / 2,
        duration: 0.5,
        ease: "power2.out"
    });
    
    gsap.to(app.stage.scale, {
        x: 1,
        y: 1,
        duration: 0.5,
        ease: "power2.out",
        onComplete: () => {
            touchState.currentScale = 1;
            touchState.initialScale = 1;
        }
    });
}

// Helper to calculate distance between two touch points
function getTouchDistance(touches) {
    const dx = touches[0].clientX - touches[1].clientX;
    const dy = touches[0].clientY - touches[1].clientY;
    return Math.sqrt(dx * dx + dy * dy);
} 