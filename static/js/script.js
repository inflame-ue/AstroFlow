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
let rocket; // Declare rocket variable
let rocketPath = []; // Array for rocket path coordinates {x, y}
let currentPathIndex = 0;
const rocketSpeed = 2; // Pixels per frame, adjust as needed

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
const rocketImageUrl = origin + '/static/images/rocket.svg'; // Add rocket image URL

console.log("Using image URLs:", earthImageUrl, satelliteImageUrl, gasStationImageUrl, rocketImageUrl);

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
        return PIXI.Assets.load([earthImageUrl, satelliteImageUrl, gasStationImageUrl, rocketImageUrl])
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

    // --- Generate Rocket Path (Example: Ellipse around Earth) ---
    // This needs to run AFTER Earth is created to know its radius
    const centerX = app.screen.width / 2;
    const centerY = app.screen.height / 2;
    const earthRadiusPx = earth.height / 2;
    const pathPoints = 500;
    const ellipseSemiMajor = earthRadiusPx * 2.5; // Make ellipse larger than earth
    const ellipseSemiMinor = earthRadiusPx * 1.5;
    
    for (let i = 0; i < pathPoints; i++) {
        const angle = (i / pathPoints) * 2 * Math.PI;
        const x = centerX + ellipseSemiMajor * Math.cos(angle);
        const y = centerY + ellipseSemiMinor * Math.sin(angle);
        rocketPath.push({ x, y });
    }
    console.log("Generated rocket path with", rocketPath.length, "points.");

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

    // --- Create Rocket Sprite ---
    rocket = new PIXI.Sprite(textures[rocketImageUrl]);
    rocket.anchor.set(0.5); // Anchor at center
    rocket.scale.set(0.05); // Adjust scale as needed

    // Place rocket at the start of the path
    if (rocketPath.length > 0) {
        rocket.x = rocketPath[0].x;
        rocket.y = rocketPath[0].y;
    } else {
        // Default position if path is empty
        rocket.x = centerX + ellipseSemiMajor;
        rocket.y = centerY;
    }
    
    app.stage.addChild(rocket);
    console.log("Rocket created at:", rocket.x, rocket.y);
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
    
    // Add properties for smoother twinkling
    star.twinkleSpeed = 0.01 + Math.random() * 0.03; // Varied slow speeds
    star.twinklePhase = Math.random() * Math.PI * 2; // Random starting phase
    
    stars.push(star);
    app.stage.addChild(star);
}

// Animation loop
app.ticker.add((delta) => {
    // Animate Stars with smoother twinkling
    stars.forEach(star => {
        // Update phase and use sine wave for smooth alpha transitions
        star.twinklePhase += star.twinkleSpeed * delta;
        // Oscillate between 0.2 and 1.0 for visible but subtle twinkling
        star.alpha = 0.2 + 0.8 * (0.5 + 0.5 * Math.sin(star.twinklePhase));
    });

    // Animate Satellites
    satellites.forEach(sat => {
        sat.angle += sat.speed * delta; // Use delta for smoother animation
        sat.graphics.x = sat.radius * Math.cos(sat.angle);
        sat.graphics.y = sat.radius * Math.sin(sat.angle);
    });

    // Animate Rocket
    if (rocket && rocketPath.length > 0) {
        const targetPoint = rocketPath[currentPathIndex];
        const dx = targetPoint.x - rocket.x;
        const dy = targetPoint.y - rocket.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < rocketSpeed * delta) { 
            // Reached the target point (or very close)
            rocket.x = targetPoint.x;
            rocket.y = targetPoint.y;
            currentPathIndex = (currentPathIndex + 1) % rocketPath.length; // Move to next point (loop)
            
            // Set rotation towards the *next* target point for smoother turns
            const nextTargetPoint = rocketPath[currentPathIndex];
            const nextDx = nextTargetPoint.x - rocket.x;
            const nextDy = nextTargetPoint.y - rocket.y;
            rocket.rotation = Math.atan2(nextDy, nextDx) + Math.PI / 2; // Point forward (+90 deg adjust)

        } else {
            // Move towards the target point
            const angle = Math.atan2(dy, dx);
            rocket.x += Math.cos(angle) * rocketSpeed * delta;
            rocket.y += Math.sin(angle) * rocketSpeed * delta;
            rocket.rotation = angle + Math.PI / 2; // Point forward (+90 deg adjust)
        }
    }
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

    // --- Regenerate Rocket Path on Resize --- 
    // Recalculate path based on new screen size and Earth position
    if (earth && earth.parent) {
        const earthRadiusPx = earth.height / 2;
        const pathPoints = 500;
        const ellipseSemiMajor = earthRadiusPx * 2.5;
        const ellipseSemiMinor = earthRadiusPx * 1.5;
        rocketPath = []; // Clear old path
        for (let i = 0; i < pathPoints; i++) {
            const angle = (i / pathPoints) * 2 * Math.PI;
            const x = centerX + ellipseSemiMajor * Math.cos(angle);
            const y = centerY + ellipseSemiMinor * Math.sin(angle);
            rocketPath.push({ x, y });
        }
        // Optionally reset rocket position to start of new path
        // if (rocket && rocketPath.length > 0 && currentPathIndex < rocketPath.length) {
        //     rocket.x = rocketPath[currentPathIndex].x; 
        //     rocket.y = rocketPath[currentPathIndex].y;
        // }
        console.log("Regenerated rocket path on resize.");
    } 
});