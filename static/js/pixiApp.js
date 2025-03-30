// static/js/pixiApp.js

// Create the PixiJS application
// PIXI should be globally available from the CDN script tag
if (typeof PIXI === 'undefined') {
    console.error("PIXI is not defined. Make sure PixiJS is loaded before this script.");
}

const app = new PIXI.Application({
    width: window.innerWidth,
    height: window.innerHeight,
    backgroundColor: 0x000000, // Black background
    resolution: window.devicePixelRatio || 1,
    antialias: true,
    autoDensity: true,
});

export { app };
