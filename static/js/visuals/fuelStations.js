// static/js/visuals/fuelStations.js

import { app } from '../pixiApp.js';
import { GAS_STATION_IMG_URL } from '../assets.js';
import { getSimData } from '../simulationData.js';
import { getEarthSprite } from './earth.js'; // Need Earth sprite for positioning

const fuelStations = []; // Keep track of station sprites

export function createFuelStations(textures) {
    console.log("Creating fuel stations...");
    // Clear previous stations
    fuelStations.forEach(fs => fs.destroy());
    fuelStations.length = 0;

    const simData = getSimData();
    const earth = getEarthSprite(); // Get the created Earth sprite

    if (!earth || !earth.parent) {
        console.error("Cannot create fuel stations: Earth sprite not found or not added to stage.");
        return;
    }
     if (!simData || !simData.launchpads || Object.keys(simData.launchpads).length === 0) {
        console.warn("No launchpad data found to create fuel stations.");
        return;
    }
    if (!textures[GAS_STATION_IMG_URL]) {
        console.error("Fuel station texture not found!");
         // Could add fallback graphics here if needed
    }

    const earthRadius = earth.height / 2; // Use height for radius after scaling

    Object.values(simData.launchpads).forEach((launchpadData, index) => {
         try {
            if (!launchpadData || typeof launchpadData.angle1 === 'undefined') {
                 throw new Error(`Missing angle1 data for launchpad index ${index}`);
            }
            const stationAngleDegrees = parseFloat(launchpadData.angle1);
            if (isNaN(stationAngleDegrees)) {
                 throw new Error(`Invalid angle1: ${launchpadData.angle1}`);
            }

            const fuelStation = textures[GAS_STATION_IMG_URL]
                ? new PIXI.Sprite(textures[GAS_STATION_IMG_URL])
                : createFallbackFuelStationGraphic(); // Fallback

            fuelStation.anchor.set(0.5, 0.5); // Anchor at center (updated previously)
            fuelStation.scale.set(0.06); // Adjust scale as needed
            fuelStation.angleData = stationAngleDegrees; // Store angle on the sprite itself

            // Position relative to Earth's center
            const stationAngleRadians = (stationAngleDegrees - 90) * (Math.PI / 180); // Offset so 0 is top

            fuelStation.x = earth.x + earthRadius * Math.cos(stationAngleRadians);
            fuelStation.y = earth.y + earthRadius * Math.sin(stationAngleRadians);
            fuelStation.rotation = stationAngleRadians + Math.PI / 2; // Rotate sprite base towards Earth center

            app.stage.addChild(fuelStation); // Add directly to stage
            fuelStations.push(fuelStation); // Add to array

         } catch(e) {
             console.error(`Error processing launchpad ${index} for fuel station:`, e, launchpadData);
         }
    });
    console.log(`${fuelStations.length} fuel stations created.`);
}


function createFallbackFuelStationGraphic() {
    const graphics = new PIXI.Graphics();
    graphics.beginFill(0xFFFFFF); // White dot
    graphics.drawCircle(0, 0, 3);
    graphics.endFill();
    return graphics;
}


export function resizeFuelStations() {
    const earth = getEarthSprite();
    if (!earth || !earth.parent) return; // Need earth

    const earthRadius = earth.height / 2;
    const centerX = app.screen.width / 2;
    const centerY = app.screen.height / 2;

    fuelStations.forEach(fuelStation => {
        if (fuelStation && fuelStation.parent && typeof fuelStation.angleData !== 'undefined') {
            // Reposition fuel station relative to the new Earth center based on its stored angle
            const stationAngleDegrees = fuelStation.angleData;
            const stationAngleRadians = (stationAngleDegrees - 90) * (Math.PI / 180);

            fuelStation.x = centerX + earthRadius * Math.cos(stationAngleRadians);
            fuelStation.y = centerY + earthRadius * Math.sin(stationAngleRadians);
            fuelStation.rotation = stationAngleRadians + Math.PI / 2; // Maintain rotation
        }
    });
}

// Getter
export function getFuelStations() {
    return fuelStations;
}