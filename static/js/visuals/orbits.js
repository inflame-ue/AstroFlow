// static/js/visuals/orbits.js

import { app } from '../pixiApp.js';
import { getOrbitRadiiScaled } from '../simulationData.js';

let orbitsContainer = null;
let orbitGraphics = null;

export function createOrbits() {
    console.log("Creating orbits...");
    if (orbitsContainer) {
        orbitsContainer.destroy(true); // Destroy container and children
    }

    orbitsContainer = new PIXI.Container();
    orbitGraphics = new PIXI.Graphics();
    orbitsContainer.addChild(orbitGraphics);

    // Center the container
    orbitsContainer.x = app.screen.width / 2;
    orbitsContainer.y = app.screen.height / 2;

    orbitGraphics.lineStyle(1, 0xFFFFFF, 0.5); // White lines, 50% alpha

    const radii = getOrbitRadiiScaled();
    if (radii.length === 0) {
        console.warn("No orbit radii data available to draw orbits.");
    }

    radii.forEach(radiusPx => {
        if (radiusPx > 0) {
            orbitGraphics.drawCircle(0, 0, radiusPx);
        }
    });

    app.stage.addChild(orbitsContainer); // Add container to stage
    console.log(`Orbits drawn for ${radii.length} radii.`);
    return orbitsContainer;
}

export function resizeOrbits() {
    if (orbitsContainer && orbitsContainer.parent) {
        orbitsContainer.x = app.screen.width / 2;
        orbitsContainer.y = app.screen.height / 2;
        // Note: The graphics themselves don't need resizing unless KM_TO_PIXEL_SCALE changes dynamically
    }
}

// Getter
export function getOrbitsContainer() {
    return orbitsContainer;
}