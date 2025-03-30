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

// --- Hardcoded Rocket Path (Relative to Center 0,0) ---
// Replace this with your 500 points later
const hardcodedRelativePath = [
  { x: 0, y: -150 }, { x: 50, y: -160 }, { x: 100, y: -180 }, { x: 150, y: -220 }, 
  { x: 180, y: -250 }, { x: 200, y: -280 }, { x: 180, y: -310 }, { x: 150, y: -330 },
  { x: 100, y: -340 }, { x: 50, y: -330 }, { x: 0, y: -320 }, { x: -50, y: -330 }, 
  { x: -100, y: -340 }, { x: -150, y: -330 }, { x: -180, y: -310 }, { x: -200, y: -280 }, 
  { x: -180, y: -250 }, { x: -150, y: -220 }, { x: -100, y: -180 }, { x: -50, y: -160 }, 
  { x: 0, y: -150 } 
];
// --- End Hardcoded Path ---

// --- Get Combined Simulation Data --- 
let simData = {}; // Make this globally accessible

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
    .then((fetchedData) => { // Rename parameter to avoid shadowing
        console.log("Fetched FormData", fetchedData);
        simData = fetchedData; // Assign to the global variable
        
        // Process orbit data
        orbitRadiiScaled = []; // Clear previous scaled radii
        if (simData && simData.orbits) {
            // Calculate scaled orbit radii
            orbitRadiiScaled = Object.values(simData.orbits).map(orbit => {
                try {
                     return parseFloat(orbit.radius) * KM_TO_PIXEL_SCALE;
                } catch (e) {
                    console.warn("Error parsing orbit radius:", orbit.radius, e);
                    return 0; // Or handle appropriately
                }
            }).filter(r => r > 0); // Filter out invalid radii
        }
        
        // Load assets and create visualization after we have the data
        return PIXI.Assets.load([earthImageUrl, satelliteImageUrl, gasStationImageUrl, rocketImageUrl])
            .then((textures) => {
                // Now we have both data and textures, create the visualization
                createVisualization(textures); // Pass only textures, simData is global
            });
    })
    .catch((error) => {
        console.error('Error loading data or assets:', error);
        // Create a fallback
        createFallbackVisualization();
    });

function createVisualization(textures) { // Remove formData parameter
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
    if (simData && simData.satellites) {
        Object.entries(simData.satellites).forEach(([satId, satData]) => {
            const orbitId = satData.orbitId;
            const orbitData = simData.orbits[orbitId];
            
            // Calculate radius and speed from the matching orbit
            const radius = parseFloat(orbitData.radius) * KM_TO_PIXEL_SCALE;
            const angle = parseFloat(satData.angle - 90) * (Math.PI / 180); // Convert degrees to radians
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
    // Ensure fuelStations array is cleared BEFORE creating new ones
    fuelStations.forEach(fs => fs.destroy());
    fuelStations = []; 

    if (simData && simData.launchpads) {
        Object.values(simData.launchpads).forEach(launchpad => {
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

    app.stage.addChild(earth); // Add earth first
    // Add fuel stations 
    fuelStations.forEach(fs => app.stage.addChild(fs)); 

    // --- Calculate Rocket Path (Start Station to Farthest Orbit Top) ---
    rocketPath = []; 
    currentPathIndex = 0;
    let startPoint = null;
    let endPoint = null;
    const centerX = app.screen.width / 2;
    const centerY = app.screen.height / 2;

    // 1. Get Start Point (First Fuel Station)
    if (fuelStations.length > 0) {
        startPoint = { x: fuelStations[0].x, y: fuelStations[0].y };
        console.log("Rocket starting point (Fuel Station 0):", startPoint);
    } else {
        console.warn("No fuel stations found, cannot define rocket start point.");
    }

    // 2. Get End Point (Top of Farthest Orbit)
    if (orbitRadiiScaled.length > 0) {
        const maxRadiusPx = Math.max(...orbitRadiiScaled);
        if (maxRadiusPx > 0) {
             const targetAngle = -Math.PI / 2; // Point at the top
             endPoint = {
                x: centerX + maxRadiusPx * Math.cos(targetAngle),
                y: centerY + maxRadiusPx * Math.sin(targetAngle)
             };
             console.log("Rocket end point (Farthest Orbit Top):", endPoint);
        } else {
            console.warn("No valid orbits found, cannot define rocket end point.");
        }
    }

    // 3. Define the final path (if both points exist)
    if (startPoint && endPoint) {
        rocketPath = [startPoint, endPoint];
        console.log("Final rocket path defined:", rocketPath);
    } else {
        console.warn("Could not define rocket path due to missing start/end points.");
    }
    
    // --- Create Rocket Sprite --- 
    // Destroy previous rocket if it exists
    if (rocket) {
        rocket.destroy();
    }
    rocket = new PIXI.Sprite(textures[rocketImageUrl]);
    rocket.anchor.set(0.5); // Anchor at center
    rocket.scale.set(0.05); // Adjust scale as needed

    // Place rocket at the start of the path
    if (rocketPath.length > 0) {
        rocket.x = rocketPath[0].x;
        rocket.y = rocketPath[0].y;
        // Initial rotation towards the second point (if it exists)
        if (rocketPath.length > 1) {
            const nextDx = rocketPath[1].x - rocket.x;
            const nextDy = rocketPath[1].y - rocket.y;
            rocket.rotation = Math.atan2(nextDy, nextDx) + Math.PI / 2;
        } else {
            rocket.rotation = 0; // Default rotation if only one point
        }
    } else {
        // Default position and hide if path is empty
        rocket.x = -1000; // Off-screen
        rocket.y = -1000;
        rocket.visible = false;
        console.warn("Rocket path is empty, placing rocket off-screen.");
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
    if (rocket && rocket.visible && rocketPath.length === 2 && currentPathIndex === 0) { // Only run if path is [start, end] and we are at the start (index 0)
        const targetPoint = rocketPath[1]; // Target the end point
        const dx = targetPoint.x - rocket.x;
        const dy = targetPoint.y - rocket.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        const moveDistance = rocketSpeed * delta;

        if (distance < moveDistance) { 
            // Reached the target point (or very close)
            rocket.x = targetPoint.x;
            rocket.y = targetPoint.y;
            currentPathIndex = 1; // Mark as finished (at index 1)
            console.log("Rocket reached final destination (farthest orbit).");
            // Keep final rotation
        } else {
            // Move towards the target point
            const angle = Math.atan2(dy, dx);
            rocket.x += Math.cos(angle) * moveDistance;
            rocket.y += Math.sin(angle) * moveDistance;
            // Rotation is set initially and shouldn't need updating for a straight path
            // If needed, uncomment: rocket.rotation = angle + Math.PI / 2; 
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

    // Recalculate dynamic path [start_station, farthest_orbit_top] 
    if (earth && earth.parent) { 
        // 1. Clear old path and reset index
        rocketPath = [];
        currentPathIndex = 0; // Reset path index
        let startPoint = null;
        let endPoint = null;
        const centerX = app.screen.width / 2;
        const centerY = app.screen.height / 2;

        // 2. Recalculate Start Point
        if (fuelStations.length > 0 && fuelStations[0].parent) { 
            startPoint = { x: fuelStations[0].x, y: fuelStations[0].y };
        } else {
             console.warn("Cannot recalculate rocket start point on resize: No fuel station.");
        }

        // 3. Recalculate End Point (needs global simData)
        if (simData && simData.orbits) { 
             const currentOrbitRadiiKm = Object.values(simData.orbits).map(o => parseFloat(o.radius)).filter(r => !isNaN(r) && r > 0);
             if (currentOrbitRadiiKm.length > 0) {
                const maxRadiusKm = Math.max(...currentOrbitRadiiKm);
                const maxRadiusPx = maxRadiusKm * KM_TO_PIXEL_SCALE;
                const targetAngle = -Math.PI / 2; // Top of orbit
                endPoint = {
                    x: centerX + maxRadiusPx * Math.cos(targetAngle),
                    y: centerY + maxRadiusPx * Math.sin(targetAngle)
                };
            } else {
                 console.warn("Cannot recalculate rocket end point on resize: No valid orbits.");
            }
        }

        // 4. Set the final path
        if (startPoint && endPoint) {
            rocketPath = [startPoint, endPoint];
        } else {
            rocketPath = []; // Ensure path is empty if points couldn't be calculated
        }

        // 5. Reset rocket position to the start of the newly calculated path
        if (rocket && rocket.parent) { 
             if (rocketPath.length === 2) {
                currentPathIndex = 0; // Always reset to start for this path type
                rocket.x = rocketPath[0].x; 
                rocket.y = rocketPath[0].y;
                rocket.visible = true;
                // Set rotation towards the end point
                const nextDx = rocketPath[1].x - rocket.x;
                const nextDy = rocketPath[1].y - rocket.y;
                rocket.rotation = Math.atan2(nextDy, nextDx) + Math.PI / 2;
             } else {
                 // Hide rocket if path is now empty
                 rocket.visible = false;
                 currentPathIndex = 0; // Reset index
             }
        }
        console.log("Regenerated dynamic [station -> orbit] rocket path on resize.");
    } 
});