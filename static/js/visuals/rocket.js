// static/js/visuals/rocket.js

import { app } from '../pixiApp.js';
import { ROCKET_IMG_URL } from '../assets.js';
import { getOrbitRadiiScaled, loadAndProcessSumulationResults } from '../simulationData.js';
import { getFuelStations } from './fuelStations.js';
import { createFlameContainer, addFlameParticle } from './flame.js';
import { createCapsulesContainer, deployCapsule, resetCapsules } from './capsules.js';

let rocketSprite = null;
let rocketPath = loadAndProcessSumulationResults(); // Array for rocket path coordinates {x, y}
let currentPathIndex = 0;

// Function to calculate the path dynamically [station -> orbit]
function calculateRocketPath() {
    const path = [];
    const stations = getFuelStations();
    const orbitRadii = getOrbitRadiiScaled();
    const centerX = app.screen.width / 2;
    const centerY = app.screen.height / 2;

    let startPoint = null;
    let endPoint = null;

    // Get Start Point (First Fuel Station)
    if (stations.length > 0 && stations[0].parent) { // Check it's added
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
        console.log("Calculated rocket path:", path);
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

    // Calculate path *after* stations/orbits exist
    rocketPath = calculateRocketPath();
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


function createFallbackRocketGraphic() {
    const graphics = new PIXI.Graphics();
    graphics.beginFill(0xFF0000); // Red triangle
    graphics.moveTo(0, -10);
    graphics.lineTo(-5, 10);
    graphics.lineTo(5, 10);
    graphics.closePath();
    graphics.endFill();
    return graphics;
}


export function animateRocket(delta, ROCKET_SPEED) {
    if (rocketSprite && rocketSprite.visible && rocketPath.length === 2 && currentPathIndex === 0) {
       const targetPoint = rocketPath[1]; // Target the end point
       const dx = targetPoint.x - rocketSprite.x;
       const dy = targetPoint.y - rocketSprite.y;
       const distance = Math.sqrt(dx * dx + dy * dy);

       const moveDistance = ROCKET_SPEED * delta; // Use passed constant

       if (distance < moveDistance) {
           // Reached the target point
           rocketSprite.x = targetPoint.x;
           rocketSprite.y = targetPoint.y;
           currentPathIndex = 1; // Mark as finished
           console.log("Rocket reached final destination (farthest orbit).");
       } else {
           // Still moving
           const angle = Math.atan2(dy, dx); // Angle of movement
           rocketSprite.x += Math.cos(angle) * moveDistance;
           rocketSprite.y += Math.sin(angle) * moveDistance;
           // Keep rotation fixed towards target (set initially)

           // --- Add Flame Particle ---
           if (Math.random() < 0.6) { // Adjust frequency
                 // Pass rocket's actual rotation, not movement angle
                 addFlameParticle(rocketSprite.x, rocketSprite.y, rocketSprite.rotation);
           }

           // --- Check for Capsule Deployment ---
           const centerX = app.screen.width / 2;
           const centerY = app.screen.height / 2;
           const rocketDistToCenter = Math.sqrt(
               Math.pow(rocketSprite.x - centerX, 2) +
               Math.pow(rocketSprite.y - centerY, 2)
           );
           
           const orbitRadii = getOrbitRadiiScaled(); // Get current scaled radii
           orbitRadii.forEach((orbitRadiusPx, orbitIndex) => {
               const distToOrbit = Math.abs(rocketDistToCenter - orbitRadiusPx);
               
               // Deploy if crossing within threshold (e.g., 5 pixels)
               if (distToOrbit < 5) { 
                   deployCapsule(rocketSprite.x, rocketSprite.y, orbitRadiusPx, orbitIndex);
               }
           });
       }
    }
}


export function resizeRocket() {
    // Recalculate path based on new element positions
    rocketPath = calculateRocketPath();
    currentPathIndex = 0; // Reset path progress

    if (rocketSprite && rocketSprite.parent) {
         if (rocketPath.length === 2) {
            // Reset position and rotation
            rocketSprite.x = rocketPath[0].x;
            rocketSprite.y = rocketPath[0].y;
            rocketSprite.visible = true;
            const nextDx = rocketPath[1].x - rocketSprite.x;
            const nextDy = rocketPath[1].y - rocketSprite.y;
            rocketSprite.rotation = Math.atan2(nextDy, nextDx) + Math.PI / 2;
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