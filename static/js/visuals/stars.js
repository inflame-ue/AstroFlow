// static/js/visuals/stars.js

import { app } from '../pixiApp.js';
import { STAR_COUNT } from '../constants.js';

let stars = []; // Keep track of star objects

export function createStars() {
    console.log("Creating stars...");
    // Clear existing stars if any
    stars.forEach(star => star.destroy());
    stars = [];

    for (let i = 0; i < STAR_COUNT; i++) {
        const star = new PIXI.Graphics();
        star.beginFill(0xFFFFFF);
        star.drawCircle(0, 0, Math.random() * 1.5 + 0.5); // Slightly larger min size
        star.endFill();

        star.x = Math.random() * app.screen.width;
        star.y = Math.random() * app.screen.height;
        star.alpha = Math.random() * 0.5 + 0.2; // Initial random alpha

        stars.push(star);
        app.stage.addChild(star);
    }
    console.log(`${stars.length} stars created.`);
}

export function animateStars(delta) {
    stars.forEach(star => {
        // Simple twinkle effect
        star.alpha = Math.random() * 0.8 + 0.2;
    });
}

export function resizeStars() {
    console.log("Resizing stars...");
    stars.forEach(star => {
        if (star && star.parent) {
            star.x = Math.random() * app.screen.width;
            star.y = Math.random() * app.screen.height;
        }
    });
}

// Optional: Export the stars array if needed elsewhere
export { stars };