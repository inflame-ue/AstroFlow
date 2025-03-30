// static/js/visuals/capsules.js
import { app } from '../pixiApp.js';
import { CAPSULE_IMG_URL } from '../assets.js';
import { getSimData } from '../simulationData.js'; // Need simData for orbit speeds

let capsulesContainer = null;
const capsules = []; // Array to track deployed capsules {sprite, orbitRadius, orbitIndex, angle, speed, age}
const deployedOrbits = new Set(); // Track which orbits already received capsules

// Store textures locally after loading
let capsuleTexture = null;

export function createCapsulesContainer(textures) {
    if (capsulesContainer) {
        capsulesContainer.destroy({ children: true });
    }
    capsulesContainer = new PIXI.Container();
    app.stage.addChild(capsulesContainer); // Add directly to stage

    // Store texture
    capsuleTexture = textures[CAPSULE_IMG_URL];
    if (!capsuleTexture) {
        console.error("Capsule texture not found during container creation!");
    }

    // Clear tracking arrays/sets
    capsules.length = 0;
    deployedOrbits.clear();

    return capsulesContainer;
}

// Call this from rocket animation when crossing an orbit
export function deployCapsule(rocketX, rocketY, orbitRadiusPx, orbitIndex) {
    if (!capsulesContainer || !capsulesContainer.parent) return;
    if (deployedOrbits.has(orbitIndex)) return; // Don't deploy twice

    console.log(`Deploying capsule at orbit index ${orbitIndex}`);

    if (!capsuleTexture) {
        console.error("Cannot deploy capsule: Texture not available.");
        // Could create fallback graphic here
        return;
    }

    const simData = getSimData();
    const centerX = app.screen.width / 2;
    const centerY = app.screen.height / 2;

    const capsule = new PIXI.Sprite(capsuleTexture);
    capsule.anchor.set(0.5);
    capsule.scale.set(0); // Start small
    capsule.x = rocketX;
    capsule.y = rocketY;
    capsule.alpha = 0; // Start transparent

    // Add tracking data
    capsule.orbitRadius = orbitRadiusPx;
    capsule.orbitIndex = orbitIndex;
    capsule.angle = Math.atan2(rocketY - centerY, rocketX - centerX); // Angle relative to center
    capsule.age = 0;

    // Get the orbit speed from the matching orbit in simData
    let calculatedSpeed = 0.003; // Default fallback speed
    try {
        // Assuming simData.orbits is an object/dict keyed by ID, need to find the one at orbitIndex
        const orbitIds = Object.keys(simData.orbits || {});
        if (orbitIds.length > orbitIndex) {
             const orbitId = orbitIds[orbitIndex]; // Get ID based on index (fragile if order changes!)
             // A better approach might be to pass the specific orbit's speed when calling deploy
             if (orbitId && simData.orbits[orbitId] && simData.orbits[orbitId].speed) {
                 calculatedSpeed = parseFloat(simData.orbits[orbitId].speed) * 0.0001; // Use same scaling as satellites
                 if(isNaN(calculatedSpeed)) calculatedSpeed = 0.003; // Fallback if parsing fails
             }
        }
    } catch (e) {
        console.warn("Error getting orbit speed for capsule:", e);
    }
    capsule.speed = calculatedSpeed;


    // Add to container and array
    capsulesContainer.addChild(capsule);
    capsules.push(capsule);

    // Mark this orbit as having a capsule
    deployedOrbits.add(orbitIndex);
}

// Call this every frame from the main animation loop
export function animateCapsules(delta) {
    if (!capsulesContainer) return;

    const centerX = app.screen.width / 2;
    const centerY = app.screen.height / 2;

    // Use for...i loop so we can remove items while iterating
    for (let i = capsules.length - 1; i >= 0; i--) {
        const capsule = capsules[i];
        if (!capsule || !capsule.parent) {
            // Remove invalid capsules
            capsules.splice(i, 1);
            continue;
        }

        if (capsule.retrieving) {
            // Handle retrieval animation
            const retrievalTime = Date.now() - capsule.retrievalStartTime;
            const animationDuration = 1500; // 1.5 seconds
            
            if (retrievalTime >= animationDuration) {
                // Retrieval animation complete - remove capsule
                console.log(`Capsule from orbit ${capsule.orbitIndex} retrieval complete`);
                capsulesContainer.removeChild(capsule);
                capsule.destroy();
                capsules.splice(i, 1);
                deployedOrbits.delete(capsule.orbitIndex);
                continue;
            }
            
            // Animation progress from 0 to 1
            const progress = retrievalTime / animationDuration;
            
            // Shrink and fade out
            capsule.scale.set(0.03 * (1 - progress)); // Scale from 0.03 to 0
            capsule.alpha = 1 - progress; // Alpha from 1 to 0
            
            // Get rocket position for flight animation
            const rocketSprite = window.getRocketSprite ? window.getRocketSprite() : null;
            
            if (rocketSprite) {
                // Move toward rocket with easing
                capsule.x = capsule.originalX + (rocketSprite.x - capsule.originalX) * progress;
                capsule.y = capsule.originalY + (rocketSprite.y - capsule.originalY) * progress;
            }
        } 
        else {
            // Normal orbit animation - unchanged
            // Set final scale and alpha if not already set
            if (capsule.scale.x !== 0.03) { 
                capsule.scale.set(0.03);
                capsule.alpha = 1;
            }

            // Animate Orbit
            capsule.angle += capsule.speed * delta;

            // Update position to stay on its orbit
            capsule.x = centerX + capsule.orbitRadius * Math.cos(capsule.angle);
            capsule.y = centerY + capsule.orbitRadius * Math.sin(capsule.angle);
        }
    }
}

export function resetCapsules() {
     deployedOrbits.clear();
     capsules.forEach(c => c.destroy());
     capsules.length = 0;
     console.log("Capsules reset.");
}

// Add this function to handle capsule retrieval
export function retrieveCapsule(orbitIndex) {
    if (!capsulesContainer) {
        console.warn("Cannot retrieve capsule: Container not available");
        return false;
    }
    
    // Find the capsule in this orbit
    const capsuleIndex = capsules.findIndex(cap => cap.orbitIndex === orbitIndex);
    if (capsuleIndex === -1) {
        console.warn(`No capsule found in orbit ${orbitIndex} to retrieve`);
        return false;
    }
    
    const capsule = capsules[capsuleIndex];
    console.log(`Retrieving capsule from orbit ${orbitIndex}`);
    
    // Mark for retrieval animation
    capsule.retrieving = true;
    capsule.retrievalStartTime = Date.now();
    
    // Store original position for animation
    capsule.originalX = capsule.x;
    capsule.originalY = capsule.y;
    
    return true;
}