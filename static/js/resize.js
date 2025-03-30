// static/js/resize.js

import { app } from './pixiApp.js';
import { resizeStars } from './visuals/stars.js';
import { resizeEarth } from './visuals/earth.js';
import { resizeOrbits } from './visuals/orbits.js';
import { resizeSatellites } from './visuals/satellites.js';
import { resizeFuelStations } from './visuals/fuelStations.js';
import { resizeRocket } from './visuals/rocket.js';

let resizeTimeout;

// Function to handle all types of resize events, including orientation changes
function handleResize() {
    // Debounce resize event for performance
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
        console.log("Handling resize event...");
        
        // Get the current viewport dimensions
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        
        // Update the renderer size
        app.renderer.resize(viewportWidth, viewportHeight);

        // Call resize handlers for each visual component
        // Order might matter depending on dependencies (e.g., stations need Earth)
        resizeEarth();
        resizeOrbits();
        resizeSatellites();
        resizeFuelStations(); // Needs Earth's new position
        resizeRocket(); // Needs stations/orbits' new positions
        resizeStars();

        console.log(`Resize complete: ${viewportWidth}x${viewportHeight}`);
    }, 100); // Debounce delay 100ms
}

export function setupResizeListener() {
    // Listen for window resize on desktop
    window.addEventListener('resize', handleResize);
    
    // Listen for orientation change on mobile
    window.addEventListener('orientationchange', () => {
        console.log("Orientation changed, triggering resize...");
        // Force a slight delay to ensure dimensions are updated after orientation change
        setTimeout(handleResize, 200);
    });
    
    console.log("Resize and orientation change listeners set up.");
}

export function removeResizeListener() {
    window.removeEventListener('resize', handleResize);
    window.removeEventListener('orientationchange', handleResize);
    console.log("All resize listeners removed.");
}