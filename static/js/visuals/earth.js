// static/js/visuals/earth.js

import { app } from '../pixiApp.js';
import { EARTH_IMG_URL } from '../assets.js';

let earthSprite = null;

// Requires textures object from asset loading
export function createEarth(textures) {
    console.log("Creating Earth...");
    // Destroy previous if exists
    if (earthSprite) {
        earthSprite.destroy();
    }

    if (!textures[EARTH_IMG_URL]) {
        console.error("Earth texture not found!");
        // Optionally create a fallback graphic
        const fallbackEarth = new PIXI.Graphics();
        fallbackEarth.beginFill(0x4287f5); // Blue circle
        fallbackEarth.drawCircle(0, 0, 100);
        fallbackEarth.endFill();
        earthSprite = fallbackEarth;
    } else {
         earthSprite = new PIXI.Sprite(textures[EARTH_IMG_URL]);
    }

    earthSprite.anchor.set(0.5);
    earthSprite.scale.set(0.37); // Adjust scale as needed
    earthSprite.x = app.screen.width / 2;
    earthSprite.y = app.screen.height / 2;

    // Add Earth to the stage (layering is handled in main script)
    // app.stage.addChild(earthSprite); // DON'T add here, add in main script after orbits/sats

    console.log("Earth created.");
    return earthSprite; // Return the created sprite
}

export function resizeEarth() {
    if (earthSprite && earthSprite.parent) {
        earthSprite.x = app.screen.width / 2;
        earthSprite.y = app.screen.height / 2;
    }
}

// Getter for the sprite
export function getEarthSprite() {
    return earthSprite;
}