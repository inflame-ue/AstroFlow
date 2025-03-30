// static/js/visuals/satellites.js

import { app } from '../pixiApp.js';
import { SATELLITE_IMG_URL } from '../assets.js';
import { getSimData, getOrbitRadiiScaled } from '../simulationData.js'; // We need simData for structure
import { KM_TO_PIXEL_SCALE } from '../constants.js';

let satellitesContainer = null;
const satellites = []; // Array to hold satellite animation data { graphics, radius, angle, speed }

export function createSatellites(textures) {
    console.log("Creating satellites...");
    if (satellitesContainer) {
        satellitesContainer.destroy(true);
    }
    // Clear satellite animation data array
    satellites.length = 0;

    satellitesContainer = new PIXI.Container();
    satellitesContainer.x = app.screen.width / 2;
    satellitesContainer.y = app.screen.height / 2;

    const simData = getSimData();
    const orbitRadiiPx = getOrbitRadiiScaled(); // Get the already scaled radii

    if (!simData || !simData.satellites || Object.keys(simData.satellites).length === 0) {
        console.warn("No satellite data found.");
        app.stage.addChild(satellitesContainer); // Add empty container
        return satellitesContainer;
    }
     if (!simData.orbits || Object.keys(simData.orbits).length === 0) {
        console.error("Cannot create satellites without orbit data.");
         app.stage.addChild(satellitesContainer);
        return satellitesContainer;
    }
    if (!textures[SATELLITE_IMG_URL]) {
        console.error("Satellite texture not found!");
        // Could add fallback graphics here if needed
    }

    // Need a mapping from orbitId to its processed data (radiusPx, speed)
     const orbitDataMap = {};
     Object.entries(simData.orbits).forEach(([orbitId, orbitInfo]) => {
         try {
             const radiusKm = parseFloat(orbitInfo.radius);
             const speedKms = parseFloat(-orbitInfo.speed || 0);
             if(isNaN(radiusKm) || radiusKm <= 0) return; // Skip invalid
             orbitDataMap[orbitId] = {
                 radiusPx: radiusKm * KM_TO_PIXEL_SCALE,
                 speed: speedKms * 0.0001 // Adjust speed scaling as needed
             };
         } catch (e) { console.warn(`Error processing orbit ${orbitId} for satellite mapping:`, e);}
     });


    Object.entries(simData.satellites).forEach(([satId, satInfo]) => {
        try {
            const orbitId = satInfo.orbitId;
            const orbitData = orbitDataMap[orbitId];

            if (!orbitData) {
                throw new Error(`Orbit data not found for orbitId: ${orbitId}`);
            }

            const angleDegrees = parseFloat(satInfo.angle);
            if (isNaN(angleDegrees)) {
                throw new Error(`Invalid angle: ${satInfo.angle}`);
            }

            const angleRadians = angleDegrees * (Math.PI / 180);
            const radiusPx = orbitData.radiusPx;
            const speed = orbitData.speed;

            const satellite = textures[SATELLITE_IMG_URL]
                ? new PIXI.Sprite(textures[SATELLITE_IMG_URL])
                : createFallbackSatelliteGraphic(); // Use fallback if texture missing

            satellite.anchor.set(0.5);
            satellite.scale.set(0.07); // Adjust scale as needed

            // Initial position
            satellite.x = radiusPx * Math.cos(angleRadians);
            satellite.y = radiusPx * Math.sin(angleRadians);

            satellitesContainer.addChild(satellite);
            satellites.push({ // Store data for animation
                graphics: satellite,
                radius: radiusPx,
                angle: angleRadians,
                speed: speed
            });
        } catch (e) {
            console.error(`Error processing satellite ${satId}:`, e, satInfo);
        }
    });

    app.stage.addChild(satellitesContainer); // Add container to stage
    console.log(`${satellites.length} satellites created.`);
    return satellitesContainer;
}

function createFallbackSatelliteGraphic() {
    const graphics = new PIXI.Graphics();
    graphics.beginFill(0xCCCCCC); // Grey square
    graphics.drawRect(-5, -5, 10, 10);
    graphics.endFill();
    return graphics;
}


export function animateSatellites(delta) {
    satellites.forEach(sat => {
        if (sat && sat.graphics && sat.graphics.parent) {
            sat.angle += sat.speed * delta; // Use delta for frame-rate independence
            sat.graphics.x = sat.radius * Math.cos(sat.angle);
            sat.graphics.y = sat.radius * Math.sin(sat.angle);
            // Optional: Make satellite point outwards/along orbit
            // sat.graphics.rotation = sat.angle + Math.PI / 2;
        }
    });
}

export function resizeSatellites() {
     if (satellitesContainer && satellitesContainer.parent) {
        satellitesContainer.x = app.screen.width / 2;
        satellitesContainer.y = app.screen.height / 2;
        // Individual satellite positions relative to container are handled by animation loop
    }
}

// Getter
export function getSatellitesContainer() {
    return satellitesContainer;
}
export { satellites }; // Export animation data array