// Visualization creation functions
import { app, globals, imageUrls } from './app.js';

export function createVisualization(textures) {
    // --- Create Orbits ---
    globals.orbitsContainer = new PIXI.Container();
    app.stage.addChild(globals.orbitsContainer);

    const orbitGraphics = new PIXI.Graphics();
    globals.orbitsContainer.addChild(orbitGraphics);
    globals.orbitsContainer.x = app.screen.width / 2;
    globals.orbitsContainer.y = app.screen.height / 2;
    orbitGraphics.lineStyle(1, 0xFFFFFF, 0.5);

    // Draw orbits based on scaled radii
    globals.orbitRadiiScaled.forEach(radius => {
        orbitGraphics.drawCircle(0, 0, radius);
    });

    // --- Create Satellites ---
    globals.satellitesContainer = new PIXI.Container();
    app.stage.addChild(globals.satellitesContainer);
    globals.satellitesContainer.x = app.screen.width / 2;
    globals.satellitesContainer.y = app.screen.height / 2;

    createSatellites(textures);
    createEarth(textures);
    createFuelStations(textures);
    calculateRocketPath();
    createRocket(textures);
}

function createSatellites(textures) {
    if (globals.simData && globals.simData.satellites) {
        Object.entries(globals.simData.satellites).forEach(([satId, satData]) => {
            const orbitId = satData.orbitId;
            const orbitData = globals.simData.orbits[orbitId];
            
            const radius = parseFloat(orbitData.radius) * globals.KM_TO_PIXEL_SCALE;
            const angle = parseFloat(satData.angle - 90) * (Math.PI / 180);
            const speed = parseFloat(orbitData.speed) * 0.0001;
            
            console.log(`Creating satellite ${satId} at angle ${satData.angle}° in orbit ${orbitId} with radius ${radius}px`);

            const satellite = new PIXI.Sprite(textures[imageUrls.satellite]);
            satellite.anchor.set(0.5);
            satellite.scale.set(0.07);
            satellite.x = radius * Math.cos(angle);
            satellite.y = radius * Math.sin(angle);

            globals.satellitesContainer.addChild(satellite);
            globals.satellites.push({
                graphics: satellite,
                radius: radius,
                angle: angle,
                speed: speed
            });
        });
    }
}

function createEarth(textures) {
    globals.earth = new PIXI.Sprite(textures[imageUrls.earth]);
    globals.earth.anchor.set(0.5);
    globals.earth.scale.set(0.37);
    globals.earth.x = app.screen.width / 2;
    globals.earth.y = app.screen.height / 2;
    app.stage.addChild(globals.earth);
}

function createFuelStations(textures) {
    // Clean up any existing fuel stations
    globals.fuelStations.forEach(fs => fs.destroy());
    globals.fuelStations = [];
    
    if (globals.simData && globals.simData.launchpads) {
        Object.values(globals.simData.launchpads).forEach(launchpad => {
            if (launchpad.angle1) {
                const stationAngleDegrees = parseFloat(launchpad.angle1);
                
                const fuelStation = new PIXI.Sprite(textures[imageUrls.gasStation]);
                fuelStation.anchor.set(0.5, 0.55);
                fuelStation.scale.set(0.06);
                fuelStation.angleData = stationAngleDegrees;
                
                const stationAngleRadians = (stationAngleDegrees - 90) * (Math.PI / 180);
                const earthRadius = globals.earth.height / 2;
                
                fuelStation.x = globals.earth.x + earthRadius * Math.cos(stationAngleRadians);
                fuelStation.y = globals.earth.y + earthRadius * Math.sin(stationAngleRadians);
                fuelStation.rotation = stationAngleRadians + Math.PI / 2;
                
                app.stage.addChild(fuelStation);
                globals.fuelStations.push(fuelStation);
            }
        });
    }
}

function calculateRocketPath() {
    globals.rocketPath = [];
    globals.currentPathIndex = 0;
    let startPoint = null;
    let endPoint = null;
    const centerX = app.screen.width / 2;
    const centerY = app.screen.height / 2;

    // Get start point from first fuel station
    if (globals.fuelStations.length > 0) {
        startPoint = { x: globals.fuelStations[0].x, y: globals.fuelStations[0].y };
        console.log("Rocket starting point (Fuel Station 0):", startPoint);
    } else {
        console.warn("No fuel stations found, cannot define rocket start point.");
    }

    // Get end point at top of farthest orbit
    if (globals.orbitRadiiScaled.length > 0) {
        const maxRadiusPx = Math.max(...globals.orbitRadiiScaled);
        if (maxRadiusPx > 0) {
            const targetAngle = -Math.PI / 2; // Top of orbit
            endPoint = {
                x: centerX + maxRadiusPx * Math.cos(targetAngle),
                y: centerY + maxRadiusPx * Math.sin(targetAngle)
            };
            console.log("Rocket end point (Farthest Orbit Top):", endPoint);
        }
    }

    // Set path if both points exist
    if (startPoint && endPoint) {
        globals.rocketPath = [startPoint, endPoint];
        console.log("Final rocket path defined:", globals.rocketPath);
    }
}

function createRocket(textures) {
    // Clean up previous rocket
    if (globals.rocket) {
        globals.rocket.destroy();
    }
    
    // Create flame trail container
    if (globals.flameTrailContainer) {
        globals.flameTrailContainer.destroy();
    }
    globals.flameTrailContainer = new PIXI.Container();
    app.stage.addChild(globals.flameTrailContainer);
    
    globals.rocket = new PIXI.Sprite(textures[imageUrls.rocket]);
    globals.rocket.anchor.set(0.5);
    globals.rocket.scale.set(0.05);

    if (globals.rocketPath.length > 0) {
        globals.rocket.x = globals.rocketPath[0].x;
        globals.rocket.y = globals.rocketPath[0].y;
        
        if (globals.rocketPath.length > 1) {
            const nextDx = globals.rocketPath[1].x - globals.rocket.x;
            const nextDy = globals.rocketPath[1].y - globals.rocket.y;
            globals.rocket.rotation = Math.atan2(nextDy, nextDx) + Math.PI / 2;
        }
    } else {
        globals.rocket.x = -1000;
        globals.rocket.y = -1000;
        globals.rocket.visible = false;
    }
    
    app.stage.addChild(globals.rocket);
    console.log("Rocket created at:", globals.rocket.x, globals.rocket.y);
}

export function createFallbackVisualization() {
    const fallbackEarth = new PIXI.Graphics();
    fallbackEarth.beginFill(0x4287f5);
    fallbackEarth.drawCircle(0, 0, 100);
    fallbackEarth.endFill();
    fallbackEarth.x = app.screen.width / 2;
    fallbackEarth.y = app.screen.height / 2;
    app.stage.addChild(fallbackEarth);
}