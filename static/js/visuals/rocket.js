// static/js/visuals/rocket.js

import { app } from '../pixiApp.js';
import { ROCKET_IMG_URL } from '../assets.js';
import { 
    getOrbitRadiiScaled, 
    getSimResults, 
    getProcessedTrajectory, 
    loadAndProcessSumulationResults 
} from '../simulationData.js';
import { getFuelStations } from './fuelStations.js';
import { createFlameContainer, addFlameParticle } from './flame.js';
import { createCapsulesContainer, deployCapsule, resetCapsules, retrieveCapsule } from './capsules.js';

let rocketSprite = null;
let simulationPath = []; // Store the raw simulation path data [[t, x, y], [t, x, y],...]
let rocketPath = []; // Converted path with screen coordinates [{x, y}, {x, y},...]
let currentPathIndex = 0;
const ROCKET_SPEED = 2; // Base speed - can be adjusted

// Add a timestamp variable to track when we last logged
let lastCoordinateLogTime = 0;

// Add these variables near the top of your file with the other declarations
let currentSimTime = 0; // Current simulation time in seconds
let lastSimTime = 0; // Track last simulation time to avoid duplicate events
let pendingEvents = []; // Store processed event triggers
let processedEvents = new Set(); // Track which events have been processed

// Add missing function for fallback rocket graphic
function createFallbackRocketGraphic() {
    console.log("Creating fallback rocket graphic");
    const rocket = new PIXI.Graphics();
    rocket.beginFill(0xFF0000); // Red
    rocket.drawPolygon([0, -10, 5, 10, -5, 10]);
    rocket.endFill();
    return rocket;
}

// Function to convert simulation data to screen coordinates
function convertSimulationPathToScreenCoordinates() {
    const centerX = app.screen.width / 2;
    const centerY = app.screen.height / 2;
    const path = [];
    
    // Get PROCESSED trajectory data (already scaled with KM_TO_PIXEL_SCALE)
    const processedTrajectory = getProcessedTrajectory();
    
    if (!processedTrajectory || !Array.isArray(processedTrajectory) || processedTrajectory.length === 0) {
        console.warn("No valid processed trajectory available for rocket path.");
        return calculateFallbackPath(); // Use the simple path as fallback
    }
    
    console.log("Processed trajectory loaded, points:", processedTrajectory.length);
    
    // Convert each [time, x, y] to screen coordinates {x, y}
    for (const point of processedTrajectory) {
        if (Array.isArray(point) && point.length >= 3) {
            // Use the already scaled x,y values but add additional visualization scaling
            path.push({
                x: centerX + -(point[1]),
                y: centerY + (point[2])
            });
        }
    }
    
    if (path.length === 0) {
        console.warn("Failed to convert trajectory to screen coordinates");
        return calculateFallbackPath();
    }
    
    // Log first and last point for debugging
    console.log("Converted trajectory path:", 
                path.length, "points",
                "first:", path[0], 
                "last:", path[path.length-1]);
    return path;
}

// Original function now serves as fallback
function calculateFallbackPath() {
    const path = [];
    const stations = getFuelStations();
    const orbitRadii = getOrbitRadiiScaled();
    const centerX = app.screen.width / 2;
    const centerY = app.screen.height / 2;

    let startPoint = null;
    let endPoint = null;

    // Get Start Point (First Fuel Station)
    if (stations.length > 0 && stations[0].parent) {
        startPoint = { x: stations[0].x, y: stations[0].y };
    } else {
        console.warn("No fuel station available for rocket start point.");
    }

    // Get End Point (Top of Farthest Orbit)
    if (orbitRadii.length > 0) {
        const maxRadiusPx = Math.max(...orbitRadii);
        if (maxRadiusPx > 0) {
             const targetAngle = -Math.PI / 2; // Point at the top
             endPoint = {
                x: centerX + maxRadiusPx * Math.cos(targetAngle),
                y: centerY + maxRadiusPx * Math.sin(targetAngle)
             };
        } else {
             console.warn("No valid orbits found for rocket end point.");
        }
    } else {
        console.warn("No orbits available for rocket end point.");
    }

    // Define the final path
    if (startPoint && endPoint) {
        path.push(startPoint, endPoint);
        console.log("Using fallback rocket path");
    } else {
         console.warn("Could not define rocket path.");
    }
    return path;
}

// Requires textures object
export function createRocket(textures) {
    console.log("Creating rocket, flame container, and capsules container...");
    if (rocketSprite) {
        rocketSprite.destroy();
    }
    // Create containers for effects (BEFORE rocket so they are visually behind if needed)
    createFlameContainer(); 
    createCapsulesContainer(textures); // Pass textures to capsules for its sprite
    resetCapsules(); // Ensure deployment tracking is reset

    // Process event data for capsules
    processSimulationEvents();

    // Calculate path *after* stations/orbits exist
    rocketPath = convertSimulationPathToScreenCoordinates();
    currentPathIndex = 0; // Reset index

    if (!textures[ROCKET_IMG_URL]) {
         console.error("Rocket texture not found!");
         // Could add fallback graphics here
         rocketSprite = createFallbackRocketGraphic();
    } else {
        rocketSprite = new PIXI.Sprite(textures[ROCKET_IMG_URL]);
    }

    rocketSprite.anchor.set(0.5); // Anchor at center
    rocketSprite.scale.set(0.05); // Adjust scale as needed

    // Place rocket at the start of the path
    if (rocketPath.length > 0) {
        rocketSprite.x = rocketPath[0].x;
        rocketSprite.y = rocketPath[0].y;
        rocketSprite.visible = true;
        // Initial rotation towards the second point (if it exists)
        if (rocketPath.length > 1) {
            const nextDx = rocketPath[1].x - rocketSprite.x;
            const nextDy = rocketPath[1].y - rocketSprite.y;
            rocketSprite.rotation = Math.atan2(nextDy, nextDx) + Math.PI / 2; // Adjust if SVG points differently
        } else {
            rocketSprite.rotation = 0; // Default rotation
        }
    } else {
        // Default position and hide if path is empty
        rocketSprite.x = -1000; // Off-screen
        rocketSprite.y = -1000;
        rocketSprite.visible = false;
        console.warn("Rocket path is empty, placing rocket off-screen.");
    }

    app.stage.addChild(rocketSprite);
    console.log("Rocket created.");
    return rocketSprite;
}

export function animateRocket(delta) {
    if (!rocketSprite || !rocketSprite.visible || rocketPath.length < 2) return;
    
    if (currentPathIndex >= rocketPath.length - 1) {
        // Reached the end of the path
        return;
    }
    
    // Update simulation time based on path progress
    const pathProgress = currentPathIndex / (rocketPath.length - 1);
    const simDuration = 62500; // Total duration from events (approx 62473s)
    const prevSimTime = currentSimTime;
    currentSimTime = pathProgress * simDuration;
    
    // Only check events if time has advanced
    if (currentSimTime > lastSimTime) {
        checkEventsTriggers();
        lastSimTime = currentSimTime;
    }
    
    // Log coordinates and simulation time once per second
    const currentTime = Date.now();
    if (currentTime - lastCoordinateLogTime >= 1000) {
        console.log(`Rocket: x=${Math.round(rocketSprite.x)}, y=${Math.round(rocketSprite.y)}, simTime=${Math.round(currentSimTime)}s, progress=${Math.round(pathProgress*100)}%`);
        lastCoordinateLogTime = currentTime;
    }
    
    // Get current target point
    const targetPoint = rocketPath[currentPathIndex + 1];
    const dx = targetPoint.x - rocketSprite.x;
    const dy = targetPoint.y - rocketSprite.y;
    const distance = Math.sqrt(dx * dx + dy * dy);

    const moveDistance = ROCKET_SPEED * delta;

    if (distance < moveDistance) {
        // Reached the current waypoint
        rocketSprite.x = targetPoint.x;
        rocketSprite.y = targetPoint.y;
        currentPathIndex++;
        
        if (currentPathIndex >= rocketPath.length - 1) {
            console.log("Rocket reached final destination.");
            return;
        }
        
        // Set rotation towards next waypoint
        const nextPoint = rocketPath[currentPathIndex + 1];
        const nextDx = nextPoint.x - rocketSprite.x;
        const nextDy = nextPoint.y - rocketSprite.y;
        rocketSprite.rotation = Math.atan2(nextDy, nextDx) + Math.PI / 2;
    } else {
        // Still moving towards current waypoint
        const angle = Math.atan2(dy, dx);
        rocketSprite.x += Math.cos(angle) * moveDistance;
        rocketSprite.y += Math.sin(angle) * moveDistance;
        rocketSprite.rotation = angle + Math.PI / 2; // Update rotation to match movement

        // --- Add Flame Particle ---
        if (Math.random() < 0.6) {
            addFlameParticle(rocketSprite.x, rocketSprite.y, rocketSprite.rotation);
        }
    }
}

// Add this function to check for events based on simulation time
function checkEventsTriggers() {
    pendingEvents.forEach(event => {
        // Only process events that haven't been handled yet and are due
        if (!processedEvents.has(event.id) && currentSimTime >= event.time) {
            console.log(`Processing event at sim time ${Math.round(currentSimTime)}s: ${event.description}`);
            
            if (event.action === "deploy") {
                // Handle capsule deployment
                const orbitRadii = getOrbitRadiiScaled();
                if (orbitRadii && orbitRadii.length > event.orbitIndex) {
                    const orbitRadius = orbitRadii[event.orbitIndex];
                    console.log(`Deploying capsule at orbit ${event.orbitIndex}`);
                    deployCapsule(rocketSprite.x, rocketSprite.y, orbitRadius, event.orbitIndex);
                }
            } 
            else if (event.action === "retrieve") {
                console.log(`Retrieving capsule from orbit ${event.orbitIndex}`);
                retrieveCapsule(event.orbitIndex);
            }
            
            // Mark as processed
            processedEvents.add(event.id);
        }
    });
}

// Update the processSimulationEvents function
function processSimulationEvents() {
    pendingEvents = [];
    const results = getSimResults();
    
    if (!results || !results.events || !Array.isArray(results.events)) {
        console.warn("No valid events found in simulation results");
        return;
    }
    
    console.log(`Processing ${results.events.length} simulation events`);
    
    // Process each event to find capsule actions
    results.events.forEach((event, index) => {
        if (!Array.isArray(event) || event.length < 2) return;
        
        const time = parseFloat(event[0]);
        const description = event[1];
        
        if (isNaN(time)) return;
        
        console.log(`Checking event: [${time}] ${description}`);
        
        let actionType = null;
        let orbitIndex = -1;
        
        // First check for "(Index X)" pattern
        const orbitIndexMatch = description.match(/orbit \d+[\d.]+ km \(Index (\d+)\)/i);
        if (orbitIndexMatch && orbitIndexMatch.length > 1) {
            orbitIndex = parseInt(orbitIndexMatch[1]);
            console.log(`Found orbit index in description: ${orbitIndex}`);
        } else {
            // Try to extract orbit radius and infer index
            const orbitRadiusMatch = description.match(/orbit (\d+[\d.]+) km/i);
            if (orbitRadiusMatch && orbitRadiusMatch.length > 1) {
                const radius = parseFloat(orbitRadiusMatch[1]);
                console.log(`Extracted orbit radius: ${radius}km`);
                
                // Map known radii to indices based on your simulation
                if (radius === 8000.0) orbitIndex = 0;
                else if (radius === 11000.0) orbitIndex = 1;
                else if (radius === 17000.0) orbitIndex = 2;
                
                console.log(`Inferred orbit index ${orbitIndex} from radius ${radius}`);
            }
        }
        
        // Determine action type based on event description
        if (description.includes("Deployed shuttle") && orbitIndex >= 0) {
            actionType = "deploy";
            console.log(`Found deployment event at ${time}s for orbit ${orbitIndex}`);
        } else if (description.includes("Recovered shuttle") && orbitIndex >= 0) {
            actionType = "retrieve";
            console.log(`Found retrieval event at ${time}s for orbit ${orbitIndex}`);
        }
        
        if (actionType) {
            pendingEvents.push({
                id: `${actionType}-${orbitIndex}-${index}`,
                time,
                action: actionType,
                orbitIndex,
                description
            });
        }
    });
    
    pendingEvents.sort((a, b) => a.time - b.time);
    console.log(`Found ${pendingEvents.length} capsule-related events:`, pendingEvents);
    
    // Reset tracking variables
    currentSimTime = 0;
    lastSimTime = 0;
    processedEvents.clear();
}

export function resizeRocket() {
    // Recalculate path based on new element positions
    rocketPath = convertSimulationPathToScreenCoordinates();
    currentPathIndex = 0; // Reset path progress

    if (rocketSprite && rocketSprite.parent) {
        if (rocketPath.length >= 1) {
            // Reset position and rotation
            rocketSprite.x = rocketPath[0].x;
            rocketSprite.y = rocketPath[0].y;
            rocketSprite.visible = true;
            
            if (rocketPath.length >= 2) {
                const nextDx = rocketPath[1].x - rocketSprite.x;
                const nextDy = rocketPath[1].y - rocketSprite.y;
                rocketSprite.rotation = Math.atan2(nextDy, nextDx) + Math.PI / 2;
            }
        } else {
            // Hide rocket if path couldn't be calculated
            rocketSprite.visible = false;
        }
    }
    resetCapsules(); // Reset deployed status on resize
    console.log("Regenerated rocket path and reset rocket/capsules on resize.");
}

// Getter
export function getRocketSprite() {
    return rocketSprite;
}

// Add this to make the function accessible without causing circular imports
window.getRocketSprite = getRocketSprite;