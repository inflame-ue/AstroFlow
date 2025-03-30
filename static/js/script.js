// static/js/script.js - Main Entry Point

import { app } from './pixiApp.js';
import { loadAssets } from './assets.js';
import { loadAndProcessSimulationData} from './simulationData.js';
import { createStars } from './visuals/stars.js';
import { createEarth } from './visuals/earth.js';
import { createOrbits } from './visuals/orbits.js';
import { createSatellites } from './visuals/satellites.js';
import { createFuelStations } from './visuals/fuelStations.js';
import { createRocket } from './visuals/rocket.js';
import { startAnimationLoop } from './animation.js';
import { setupResizeListener } from './resize.js';

// --- Main Initialization Function ---
async function initializeSimulation() {
    console.log("Initializing simulation...");

    // 1. Append Pixi View to DOM (ensure DOM is ready)
    const containerId = 'canvas-container'; // ID of the div in your HTML
    const container = document.getElementById(containerId);
    if (container) {
        container.appendChild(app.view);
    } else {
        console.error(`Container #${containerId} not found! Appending to body.`);
        document.body.appendChild(app.view);
    }

    // 2. Fetch Data & Load Assets (can run in parallel)
    const [processedData, textures] = await Promise.all([
        loadAndProcessSimulationData(),
        loadAssets()
    ]);

    // Check if loading failed
    if (!textures || Object.keys(textures).length === 0) {
        console.error("Asset loading failed. Cannot proceed.");
        // Optionally display an error message to the user
        createFallbackVisualization(); // Create a simple fallback
        return;
    }
     // No need to check processedData explicitly, simulationData module handles defaults

    console.log("Data loaded and assets loaded. Creating visuals...");

    // 3. Create Visual Elements (Order can matter for layering/dependencies)
    // Background elements first
    createStars();
    createOrbits();
    createSatellites(textures);

    // Central element
    const earth = createEarth(textures);
    // Add Earth *after* orbits/satellites so it's visually on top of them
    if (earth) app.stage.addChild(earth);

    // Elements dependent on Earth position
    createFuelStations(textures);

    // Rocket - depends on stations/orbits being defined
    createRocket(textures);

    // 4. Setup Resize Handling
    setupResizeListener();

    // 5. Start Animation Loop
    startAnimationLoop();

    console.log("Simulation initialization complete.");
}

// --- Fallback Visualization ---
function createFallbackVisualization() {
    console.warn("Creating fallback visualization due to errors.");
    // Simple blue circle for Earth
    const fallbackEarth = new PIXI.Graphics();
    fallbackEarth.beginFill(0x4287f5);
    fallbackEarth.drawCircle(0, 0, 100);
    fallbackEarth.endFill();
    fallbackEarth.x = app.screen.width / 2;
    fallbackEarth.y = app.screen.height / 2;
    app.stage.addChild(fallbackEarth);
    // Maybe add simple stars
    createStars();
    startAnimationLoop(); // Animate stars at least
    setupResizeListener(); // Allow resizing
}

// --- Run Initialization ---
// Ensure DOM is ready before trying to access elements like canvas-container
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeSimulation);
} else {
    initializeSimulation();
}
