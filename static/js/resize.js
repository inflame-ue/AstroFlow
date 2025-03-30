// static/js/resize.js

import { app } from './pixiApp.js';
import { resizeStars } from './visuals/stars.js';
import { resizeEarth } from './visuals/earth.js';
import { resizeOrbits } from './visuals/orbits.js';
import { resizeSatellites } from './visuals/satellites.js';
import { resizeFuelStations } from './visuals/fuelStations.js';
import { resizeRocket } from './visuals/rocket.js';

let resizeTimeout;

function handleResize() {
    // Debounce resize event for performance
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
        console.log("Handling resize event...");
        app.renderer.resize(window.innerWidth, window.innerHeight);

        // Call resize handlers for each visual component
        // Order might matter depending on dependencies (e.g., stations need Earth)
        resizeEarth();
        resizeOrbits();
        resizeSatellites();
        resizeFuelStations(); // Needs Earth's new position
        resizeRocket(); // Needs stations/orbits' new positions
        resizeStars();

        console.log("Resize handling complete.");
    }, 100); // Debounce delay 100ms
}

export function setupResizeListener() {
    window.addEventListener('resize', handleResize);
    console.log("Resize listener set up.");
}

export function removeResizeListener() {
     window.removeEventListener('resize', handleResize);
     console.log("Resize listener removed.");
}