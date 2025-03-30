// static/js/visuals/flame.js
import { app } from '../pixiApp.js';

let flameTrailContainer = null;
const flameParticles = []; // Array to track flame particles

export function createFlameContainer() {
    if (flameTrailContainer) {
        flameTrailContainer.destroy({ children: true });
    }
    flameTrailContainer = new PIXI.Container();
    app.stage.addChild(flameTrailContainer); // Add directly to stage
    // Ensure it's behind the rocket maybe? Or handle layering in main.
    // Could set zIndex if needed, or add it before rocket in main script.
    return flameTrailContainer;
}

// Call this from rocket animation when moving
export function addFlameParticle(rocketX, rocketY, rocketRotation) {
    if (!flameTrailContainer || !flameTrailContainer.parent) return; // Safety check

    // Calculate offset direction based on rocket's visual rotation
    // The direction opposite the rocket nose (rotation + PI)
    const flameDirectionAngle = rocketRotation + Math.PI; 
    const offsetDistance = 5; // Reset offset distance for testing new angle

    const particleX = rocketX + Math.cos(flameDirectionAngle) * offsetDistance;
    const particleY = rocketY + Math.sin(flameDirectionAngle) * offsetDistance;

    // Create a particle
    const particle = new PIXI.Graphics();
    // Flame colors - orange/yellow/white gradient could be nice
    // const color = Math.random() < 0.5 ? 0xFF8C00 : (Math.random() < 0.5 ? 0xFFFF00 : 0xFFFFFF);
    particle.beginFill(0xFFFFFF); // Always use white
    particle.drawCircle(0, 0, 1 + Math.random() * 2); // Small, varied size
    particle.endFill();
    particle.x = particleX;
    particle.y = particleY;
    particle.alpha = 0.8 + Math.random() * 0.2; // Start bright
    // particle.alpha = 0.8; // Start bright
    particle.lifespan = 15 + Math.random() * 15; // Frames until disappearing (15-30)

    flameTrailContainer.addChild(particle);
    flameParticles.push(particle);
}

// Call this every frame from the main animation loop
export function animateFlameParticles(delta) {
     if (!flameTrailContainer) return;

     for (let i = flameParticles.length - 1; i >= 0; i--) {
        const particle = flameParticles[i];
        particle.lifespan -= delta; // Use delta for frame-rate independence
        particle.alpha -= (0.04 * delta); // Fade out based on delta

        // Optionally add slight movement away from rocket?
        // particle.x += (Math.random() - 0.5) * 0.5 * delta;
        // particle.y += (Math.random() - 0.5) * 0.5 * delta;

        // Remove dead particles
        if (particle.lifespan <= 0 || particle.alpha <= 0) {
            flameTrailContainer.removeChild(particle);
            particle.destroy();
            flameParticles.splice(i, 1);
        }
    }
}