// static/js/animation.js

import { app } from './pixiApp.js';
import { animateStars } from './visuals/stars.js';
import { animateSatellites } from './visuals/satellites.js';
import { animateRocket } from './visuals/rocket.js';
import { ROCKET_SPEED } from './constants.js'; // Import rocket speed

let tickerHandler = null;

export function startAnimationLoop() {
    console.log("Starting animation loop...");
    // Remove previous ticker if exists to prevent duplicates
    if (tickerHandler) {
        app.ticker.remove(tickerHandler);
    }

    tickerHandler = (delta) => {
        // Call animation functions for each element type
        animateStars(delta);
        animateSatellites(delta);
        animateRocket(delta, ROCKET_SPEED); // Pass speed
    };

    app.ticker.add(tickerHandler);
}

export function stopAnimationLoop() {
     if (tickerHandler) {
        console.log("Stopping animation loop.");
        app.ticker.remove(tickerHandler);
        tickerHandler = null;
    }
}