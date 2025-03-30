// static/js/script.js - Main Entry Point

import { app } from './pixiApp.js';
import { loadAssets } from './assets.js';
import { loadAndProcessSimulationData } from './simulationData.js';
import { createStars } from './visuals/stars.js';
import { createEarth } from './visuals/earth.js';
import { createOrbits } from './visuals/orbits.js';
import { createSatellites } from './visuals/satellites.js';
import { createFuelStations } from './visuals/fuelStations.js';
import { createRocket } from './visuals/rocket.js';
import { startAnimationLoop } from './animation.js';
import { setupResizeListener } from './resize.js';
import { initMobileControls } from './mobile.js';

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

    // 5. Initialize mobile controls if on a mobile device
    initMobileControls();

    // 6. Show mobile instructions if on touch device
    showMobileInstructions();

    // 7. Start Animation Loop
    startAnimationLoop();

    console.log("Simulation initialization complete.");
}

// Show instructions for mobile users
function showMobileInstructions() {
    // Only show instructions on touch devices
    if (!('ontouchstart' in window)) return;
    
    // Create an informational tooltip for mobile users
    const mobileInstructions = document.createElement('div');
    mobileInstructions.className = 'mobile-instructions';
    mobileInstructions.innerHTML = `
        <div class="instruction-content">
            <p>• One finger: Pan the view</p>
            <p>• Two fingers: Pinch to zoom</p>
            <p>• Double-tap: Reset view</p>
            <button class="close-btn">Got it!</button>
        </div>
    `;
    document.body.appendChild(mobileInstructions);
    
    // Add style for this element
    const style = document.createElement('style');
    style.textContent = `
        .mobile-instructions {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background-color: rgba(0, 0, 0, 0.85);
            color: white;
            border: 1px solid #00A6FB;
            border-radius: 10px;
            padding: 20px;
            z-index: 1000;
            box-shadow: 0 0 15px rgba(0, 166, 251, 0.5);
            max-width: 85%;
        }
        .instruction-content {
            text-align: center;
        }
        .instruction-content p {
            margin: 10px 0;
            font-size: 0.9rem;
        }
        .close-btn {
            background-color: #00A6FB;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 8px 15px;
            margin-top: 15px;
            cursor: pointer;
        }
    `;
    document.head.appendChild(style);
    
    // Add close functionality
    const closeBtn = mobileInstructions.querySelector('.close-btn');
    closeBtn.addEventListener('click', () => {
        mobileInstructions.style.display = 'none';
    });
    
    // Auto-hide after 8 seconds
    setTimeout(() => {
        mobileInstructions.style.opacity = '0';
        mobileInstructions.style.transition = 'opacity 1s ease';
        setTimeout(() => {
            mobileInstructions.style.display = 'none';
        }, 1000);
    }, 8000);
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
    initMobileControls(); // Enable mobile controls
}


// --- Run Initialization ---
// Ensure DOM is ready before trying to access elements like canvas-container
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeSimulation);
} else {
    initializeSimulation();
}
