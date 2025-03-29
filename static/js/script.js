// Create the PixiJS application
const app = new PIXI.Application({
    width: window.innerWidth,
    height: window.innerHeight,
    backgroundColor: 0x000000,
    resolution: window.devicePixelRatio || 1,
    antialias: true,
    autoDensity: true,
});

// Add the canvas to the container
document.getElementById('canvas-container').appendChild(app.view);

let earth;
let orbitsContainer;
let satellitesContainer; // Container for satellites
let fuelStation; // Graphics for the fuel station
const satellites = []; // Array to hold satellite data

// Orbit definitions (Re-added after merge)
const orbitRadii = [300, 364, 428];
const angularSpeeds = [0.005, 0.003, 0.002]; // Slower speeds for outer orbits (example values)
const satelliteDistribution = [3, 3, 4]; // 3 + 3 + 4 = 10 satellites

// Get the correct URL for the earth.png image
const earthImageUrl = document.body.getAttribute('data-earth-image-url') || '/static/images/earth.png';
const satelliteImageUrl = '/static/images/satellite.png'; // Define path
const gasStationImageUrl = '/static/images/gas_station.png'; // Define path

// Load all textures
PIXI.Assets.load([earthImageUrl, satelliteImageUrl, gasStationImageUrl]).then((textures) => {

    // --- Create Orbits --- 
    orbitsContainer = new PIXI.Container(); // Assign to global scope
    app.stage.addChild(orbitsContainer);
    
    const orbitGraphics = new PIXI.Graphics();
    orbitsContainer.addChild(orbitGraphics);
    orbitsContainer.x = app.screen.width / 2;
    orbitsContainer.y = app.screen.height / 2;
    orbitGraphics.lineStyle(1, 0xFFFFFF, 0.5);
    orbitRadii.forEach(radius => {
        orbitGraphics.drawCircle(0, 0, radius);
    });
    // --- End Orbits ---

    // --- Create Satellites --- 
    satellitesContainer = new PIXI.Container(); // Assign to global scope
    app.stage.addChild(satellitesContainer);
    satellitesContainer.x = app.screen.width / 2;
    satellitesContainer.y = app.screen.height / 2;

    let satelliteIndex = 0;
    for (let i = 0; i < orbitRadii.length; i++) {
        const radius = orbitRadii[i];
        const speed = angularSpeeds[i];
        const numSatellitesOnOrbit = satelliteDistribution[i];

        for (let j = 0; j < numSatellitesOnOrbit; j++) {
            // Use the preloaded satellite texture
            const satellite = new PIXI.Sprite(textures[satelliteImageUrl]); // Use variable path 
            satellite.anchor.set(0.5); // Center the sprite
            satellite.scale.set(0.07); // Made satellites smaller
            // satellite.beginFill(0xFF0000); // Red color for satellites - REMOVED
            // satellite.drawCircle(0, 0, 5); // 5px radius - REMOVED
            // satellite.endFill(); - REMOVED

            const angle = (j / numSatellitesOnOrbit) * Math.PI * 2; // Spread satellites evenly
            
            // Initial position relative to container center (0,0)
            satellite.x = radius * Math.cos(angle);
            satellite.y = radius * Math.sin(angle);

            satellitesContainer.addChild(satellite);
            satellites.push({
                graphics: satellite, // Now stores the sprite
                radius: radius,
                angle: angle,
                speed: speed
            });
            satelliteIndex++;
        }
    }
    // --- End Satellites ---

    // Create Earth sprite using the preloaded texture
    earth = new PIXI.Sprite(textures[earthImageUrl]);
    earth.anchor.set(0.5);
    earth.scale.set(0.8);
    earth.x = app.screen.width / 2;
    earth.y = app.screen.height / 2;

    // Add Earth last so it's on top of orbits and satellites
    app.stage.addChild(earth);

    // --- Create Fuel Station Sprite ---
    fuelStation = new PIXI.Sprite(textures[gasStationImageUrl]); // Use variable path
    fuelStation.anchor.set(0.5, 1); // Anchor at bottom-center
    fuelStation.scale.set(0.06); // Make it smaller again
    
    // Position it relative to Earth's center
    const earthRadius = earth.height / 2; // Use height for vertical radius
    fuelStation.x = earth.x; // Center horizontally with Earth
    fuelStation.y = earth.y - earthRadius; // Place bottom anchor at Earth's top edge
    
    app.stage.addChild(fuelStation);
    // --- End Fuel Station Sprite ---

}).catch((error) => {
    console.error('Error loading assets:', error);
    // Create a fallback circle if PNG loading fails
    const fallbackEarth = new PIXI.Graphics();
    fallbackEarth.beginFill(0x4287f5); // Blue fallback
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

// Handle window resize (adjust orbits, satellites, and fuel station)
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
    if (fuelStation && fuelStation.parent && earth && earth.parent) { // Ensure earth exists for radius calc
        // Reposition fuel station relative to the new Earth center
        const earthRadius = earth.height / 2; 
        fuelStation.x = centerX; // Center horizontally
        fuelStation.y = centerY - earthRadius; // Place at top edge
    }
}); 