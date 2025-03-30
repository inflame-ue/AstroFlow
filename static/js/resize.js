// static/js/resize.js

import { app } from './pixiApp.js';
import { resizeStars } from './visuals/stars.js';
import { resizeEarth } from './visuals/earth.js';
import { resizeOrbits } from './visuals/orbits.js';
import { resizeSatellites } from './visuals/satellites.js';
import { resizeFuelStations } from './visuals/fuelStations.js';
import { resizeRocket } from './visuals/rocket.js';

let resizeTimeout;
let initialOrientation = window.innerWidth > window.innerHeight ? 'landscape' : 'portrait';

function handleResize() {
    // Debounce resize event for performance
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
        console.log("Handling resize event...");
        
        // Check if orientation changed on mobile
        const currentOrientation = window.innerWidth > window.innerHeight ? 'landscape' : 'portrait';
        const orientationChanged = currentOrientation !== initialOrientation;
        initialOrientation = currentOrientation;
        
        // Force a slight delay on orientation changes to let the browser settle
        const resizeDelay = orientationChanged ? 300 : 0;
        
        setTimeout(() => {
            const newWidth = window.innerWidth;
            const newHeight = window.innerHeight;
            
            app.renderer.resize(newWidth, newHeight);
            
            // Call resize handlers for each visual component
            // Order might matter depending on dependencies (e.g., stations need Earth)
            resizeEarth();
            resizeOrbits();
            resizeSatellites();
            resizeFuelStations(); // Needs Earth's new position
            resizeRocket(); // Needs stations/orbits' new positions
            resizeStars();
            
            console.log("Resize handling complete. New dimensions:", newWidth, "x", newHeight);
        }, resizeDelay);
    }, 100); // Debounce delay 100ms
}

export function setupResizeListener() {
    // Handle both resize and orientation change events
    window.addEventListener('resize', handleResize);
    
    // Special handling for iOS devices
    if ('ontouchend' in document) {
        window.addEventListener('orientationchange', () => {
            // Force a more aggressive resize on orientation change
            setTimeout(handleResize, 300);
        });
    }
    
    console.log("Resize and orientation listeners set up.");
}

export function removeResizeListener() {
    window.removeEventListener('resize', handleResize);
    if ('ontouchend' in document) {
        window.removeEventListener('orientationchange', handleResize);
    }
    console.log("Resize and orientation listeners removed.");
}