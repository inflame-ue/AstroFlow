// Create the PixiJS application
const app = new PIXI.Application({
    width: window.innerWidth,
    height: window.innerHeight,
    backgroundColor: 0x000000,
    resolution: window.devicePixelRatio || 1,  // Use 4 for 4K resolution
    antialias: true,
    autoDensity: true,
});

// Add the canvas to the container
document.getElementById('canvas-container').appendChild(app.view);

let earth;
let orbitsContainer;
let satellitesContainer; // Container for satellites
let fuelStations = []; // Fix: Initialize as empty array
let orbitRadiiScaled = []; // Fix: Initialize as empty array
const satellites = []; // Array to hold satellite data

// Scale factor: 97.84 kilometers per pixel
const KM_TO_PIXEL_SCALE = 1 / 43.05;

// --- Get Combined Simulation Data --- 
let simData = {}; 
// ... (try/catch for parsing simData) ...
console.log("Parsed Simulation Data:", simData);

// --- Image URLs (Construct Absolute Paths) --- 
const origin = window.location.origin; // e.g., http://127.0.0.1:5000
let earthImageRelativeUrl = document.body.getAttribute('data-earth-image-url') || '/static/images/earth.svg';
const earthImageUrl = origin + earthImageRelativeUrl;
const satelliteImageUrl = origin + '/static/images/satellite.png';
const gasStationImageUrl = origin + '/static/images/gas_station.svg';

console.log("Using image URLs:", earthImageUrl, satelliteImageUrl, gasStationImageUrl);

// Fetch form data and process it
fetch('/api/form_data')
    .then((res) => res.json())
    .then((formData) => {
        console.log("FormData", formData);
        
        // Process orbit data
        if (formData && formData.orbits) {
            // Calculate scaled orbit radii
            orbitRadiiScaled = Object.values(formData.orbits).map(orbit => {
                return parseFloat(orbit.radius) * KM_TO_PIXEL_SCALE;
            });
        }
        
        // Load assets and create visualization after we have the data
        return PIXI.Assets.load([earthImageUrl, satelliteImageUrl, gasStationImageUrl])
            .then((textures) => {
                // Now we have both data and textures, create the visualization
                createVisualization(formData, textures);
            });
    })
    .catch((error) => {
        console.error('Error loading data or assets:', error);
        // Create a fallback
        createFallbackVisualization();
    });

function createVisualization(formData, textures) {
    // --- Create Orbits --- 
    orbitsContainer = new PIXI.Container();
    app.stage.addChild(orbitsContainer);

    const orbitGraphics = new PIXI.Graphics();
    orbitsContainer.addChild(orbitGraphics);
    orbitsContainer.x = app.screen.width / 2;
    orbitsContainer.y = app.screen.height / 2;
    orbitGraphics.lineStyle(1, 0xFFFFFF, 0.5);

    // Draw orbits based on scaled radii
    orbitRadiiScaled.forEach(radius => {
        orbitGraphics.drawCircle(0, 0, radius);
    });
    // --- End Orbits ---

    // --- Create Satellites --- 
    satellitesContainer = new PIXI.Container();
    app.stage.addChild(satellitesContainer);
    satellitesContainer.x = app.screen.width / 2;
    satellitesContainer.y = app.screen.height / 2;

    // Create satellites based on JSON data
    if (formData && formData.satellites) {
        Object.entries(formData.satellites).forEach(([satId, satData]) => {
            const orbitId = satData.orbitId;
            const orbitData = formData.orbits[orbitId];
            
            // Calculate radius and speed from the matching orbit
            const radius = parseFloat(orbitData.radius) * KM_TO_PIXEL_SCALE;
            const angle = parseFloat(satData.angle) * (Math.PI / 180); // Convert degrees to radians
            const speed = parseFloat(orbitData.speed) * 0.0001; // Scale speed appropriately
            
            console.log(`Creating satellite ${satId} at angle ${satData.angle}° in orbit ${orbitId} with radius ${radius}px`);

            const satellite = new PIXI.Sprite(textures[satelliteImageUrl]);
            satellite.anchor.set(0.5);
            satellite.scale.set(0.07);

            // Initial position
            satellite.x = radius * Math.cos(angle);
            satellite.y = radius * Math.sin(angle);

            satellitesContainer.addChild(satellite);
            satellites.push({
                graphics: satellite,
                radius: radius,
                angle: angle,
                speed: speed
            });
        });
    }
    // --- End Satellites ---

    // Create Earth sprite using the preloaded texture
    earth = new PIXI.Sprite(textures[earthImageUrl]);
    earth.anchor.set(0.5);
    earth.scale.set(0.37);
    earth.x = app.screen.width / 2;
    earth.y = app.screen.height / 2;

    // Add Earth last so it's on top of orbits and satellites
    app.stage.addChild(earth);

    // --- Create Fuel Station Sprites from Launchpads ---
    if (formData && formData.launchpads) {
        Object.values(formData.launchpads).forEach(launchpad => {
            if (launchpad.angle1) {
                const stationAngleDegrees = parseFloat(launchpad.angle1);
                
                const fuelStation = new PIXI.Sprite(textures[gasStationImageUrl]);
                fuelStation.anchor.set(0.5, 0.55); // Anchor at center
                fuelStation.scale.set(0.06); // Make it smaller again
                fuelStation.angleData = stationAngleDegrees; // Store angle on the sprite itself
                
                // Position it relative to Earth's center based on angle
                const stationAngleRadians = (stationAngleDegrees - 90) * (Math.PI / 180); // Convert degrees to radians
                const earthRadius = earth.height / 2; // Use height for vertical radius
                
                fuelStation.x = earth.x + earthRadius * Math.cos(stationAngleRadians);
                fuelStation.y = earth.y + earthRadius * Math.sin(stationAngleRadians); 
                fuelStation.rotation = stationAngleRadians + Math.PI / 2; // Rotate sprite base towards Earth center
                
                app.stage.addChild(fuelStation);
                fuelStations.push(fuelStation); // Add to array
            }
        });
    }
    // --- End Fuel Station Sprites ---
}

function createFallbackVisualization() {
    // Create a fallback circle if loading fails
    const fallbackEarth = new PIXI.Graphics();
    fallbackEarth.beginFill(0x4287f5);
    fallbackEarth.drawCircle(0, 0, 100);
    fallbackEarth.endFill();
    fallbackEarth.x = app.screen.width / 2;
    fallbackEarth.y = app.screen.height / 2;
    app.stage.addChild(fallbackEarth);
}

// Create stars
const stars = [];
const numStars = 200;

for (let i = 0; i < numStars; i++) {
    const star = new PIXI.Graphics();
    star.beginFill(0xFFFFFF);
    star.drawCircle(0, 0, Math.random() * 2);
    star.endFill();

    star.x = Math.random() * app.screen.width;
    star.y = Math.random() * app.screen.height;

    stars.push(star);
    app.stage.addChild(star);
}

// Animation loop
app.ticker.add((delta) => {
    // Animate Stars
    stars.forEach(star => {
        star.alpha = Math.random();
    });

    // Animate Satellites
    satellites.forEach(sat => {
        sat.angle += sat.speed; // Increment angle by speed
        sat.graphics.x = sat.radius * Math.cos(sat.angle);
        sat.graphics.y = sat.radius * Math.sin(sat.angle);
    });
});

// Handle window resize
window.addEventListener('resize', () => {
    app.renderer.resize(window.innerWidth, window.innerHeight);
    const centerX = app.screen.width / 2;
    const centerY = app.screen.height / 2;
    if (earth && earth.parent) {
        earth.x = centerX;
        earth.y = centerY;
    }
    if (orbitsContainer && orbitsContainer.parent) {
        orbitsContainer.x = centerX;
        orbitsContainer.y = centerY;
    }
    if (satellitesContainer && satellitesContainer.parent) {
        satellitesContainer.x = centerX;
        satellitesContainer.y = centerY;
    }
    if (earth && earth.parent) { // Ensure earth exists for radius calc
        const earthRadius = earth.height / 2; 
        fuelStations.forEach(fuelStation => {
            if (fuelStation && fuelStation.parent) {
                // Reposition fuel station relative to the new Earth center based on its stored angle
                const stationAngleDegrees = fuelStation.angleData; // Get stored angle
                const stationAngleRadians = (stationAngleDegrees - 90) * (Math.PI / 180);
                
                fuelStation.x = centerX + earthRadius * Math.cos(stationAngleRadians);
                fuelStation.y = centerY + earthRadius * Math.sin(stationAngleRadians); 
                fuelStation.rotation = stationAngleRadians + Math.PI / 2; // Maintain rotation
            }
        });
    }
    
    // Reposition stars randomly within the new bounds
    stars.forEach(star => {
        if (star && star.parent) { // Check if star exists and is on stage
            star.x = Math.random() * app.screen.width;
            star.y = Math.random() * app.screen.height;
        }
    });
});