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
let fuelStations = []; // Array for multiple fuel stations
let orbitRadiiScaled = []; // Array to hold scaled orbit radii
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

// fetch form data from endpoint
fetch('/api/form_data')
    .then((res)=>{ console.log(res.json()) })


// Load all textures
PIXI.Assets.load([earthImageUrl, satelliteImageUrl, gasStationImageUrl]).then((textures) => {
    // --- Create Orbits --- 
    orbitsContainer = new PIXI.Container();
    app.stage.addChild(orbitsContainer);

    const orbitGraphics = new PIXI.Graphics();
    orbitsContainer.addChild(orbitGraphics);
    orbitsContainer.x = app.screen.width / 2;
    orbitsContainer.y = app.screen.height / 2;
    orbitGraphics.lineStyle(1, 0xFFFFFF, 0.5);

    // Draw orbits based on scaled JSON data
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
    Object.values(FormData).forEach((satData, index) => {
        console.log("satData", satelliteSpeedsParsed[index], orbitRadiiScaled[index], satData);
        const orbitIndex = parseInt(index) - 1; // Convert to 0-based index
        const radius = parseFloat(orbitRadiiScaled[index]) * KM_TO_PIXEL_SCALE;
        const angle = parseFloat(satData) * (Math.PI / 180); // Convert degrees to radians
        const speed = parseFloat(satelliteSpeedsParsed[index]) * 0.0001; // Scale speed appropriately

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
    // --- End Satellites ---

    // Create Earth sprite using the preloaded texture
    earth = new PIXI.Sprite(textures[earthImageUrl]);
    earth.anchor.set(0.5);
    earth.scale.set(0.37);
    earth.x = app.screen.width / 2;
    earth.y = app.screen.height / 2;

    // Add Earth last so it's on top of orbits and satellites
    app.stage.addChild(earth);

    // --- Create Fuel Station Sprites (Multiple) ---
    const stationAnglesJson = document.body.getAttribute('data-station-angles') || '[]'; // Get JSON string
    let stationAngles = [];
    try {
        stationAngles = JSON.parse(stationAnglesJson); // Parse JSON into array
    } catch (e) {
        console.error("Error parsing station angles JSON:", e, stationAnglesJson);
        stationAngles = []; // Default to empty array on error
    }
    
    // Clear previous stations if any (e.g., if re-running init logic)
    fuelStations.forEach(fs => fs.destroy());
    fuelStations = [];
    
    stationAngles.forEach(stationAngleDegrees => {
        const fuelStation = new PIXI.Sprite(textures[gasStationImageUrl]);
        fuelStation.anchor.set(0.5, 0.55); // Anchor at center
        fuelStation.scale.set(0.06); // Make it smaller again
        fuelStation.angleData = stationAngleDegrees; // Store angle on the sprite itself
        
        // Position it relative to Earth's center based on angle
        const stationAngleRadians = (stationAngleDegrees - 90) * (Math.PI / 180); // Convert degrees to radians, offset so 0 is top
        const earthRadius = earth.height / 2; // Use height for vertical radius
        
        fuelStation.x = earth.x + earthRadius * Math.cos(stationAngleRadians);
        fuelStation.y = earth.y + earthRadius * Math.sin(stationAngleRadians); 
        // Keep rotation pointing outwards if desired, or remove if dot shouldn't rotate
        fuelStation.rotation = stationAngleRadians + Math.PI / 2; // Rotate sprite base towards Earth center
        
        app.stage.addChild(fuelStation);
        fuelStations.push(fuelStation); // Add to array
    });
    // --- End Fuel Station Sprites ---

}).catch((error) => {
    console.error('Error loading assets:', error);
    // Create a fallback circle if PNG loading fails
    const fallbackEarth = new PIXI.Graphics();
    fallbackEarth.beginFill(0x4287f5);
    fallbackEarth.drawCircle(0, 0, 100);
    fallbackEarth.endFill();
    fallbackEarth.x = app.screen.width / 2;
    fallbackEarth.y = app.screen.height / 2;
    app.stage.addChild(fallbackEarth);
});

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
app.ticker.add((delta) => { // Pass delta for potential frame-rate independent movement later
    // Animate Stars
    stars.forEach(star => {
        star.alpha = Math.random();
    });

    // Rotate Earth
    if (earth && earth.parent) {
        // earth.rotation += 0.001; // Removed rotation
    }

    // Animate Satellites
    satellites.forEach(sat => {
        sat.angle += sat.speed; // Increment angle by speed
        sat.graphics.x = sat.radius * Math.cos(sat.angle);
        sat.graphics.y = sat.radius * Math.sin(sat.angle);
    });
});

// Handle window resize (adjust orbits, satellites, and ALL fuel stations)
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