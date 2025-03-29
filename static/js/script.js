// Create the PixiJS application
const app = new PIXI.Application({
    width: window.innerWidth,
    height: window.innerHeight,
    backgroundColor: 0x000000, // Restore background color
    resolution: window.devicePixelRatio || 1,
});

// Add the canvas to the container
document.getElementById('canvas-container').appendChild(app.view);

let earth; // Declare earth variable

// Get the correct URL for the earth.png image
const earthImageUrl = document.body.getAttribute('data-earth-image-url') || '/static/images/earth.png';

// Load the Earth PNG texture
PIXI.Assets.load(earthImageUrl).then((texture) => {

    // --- Create Orbits --- 
    const orbitsContainer = new PIXI.Container();
    app.stage.addChild(orbitsContainer);
    
    const orbitGraphics = new PIXI.Graphics();
    orbitsContainer.addChild(orbitGraphics);

    // Center orbits on the screen (where Earth will be)
    orbitsContainer.x = app.screen.width / 2;
    orbitsContainer.y = app.screen.height / 2;

    const orbitRadii = [300, 364, 428]; // Decreased gap between orbits
    orbitGraphics.lineStyle(1, 0xFFFFFF, 0.5); // 1px white line, 50% alpha

    orbitRadii.forEach(radius => {
        orbitGraphics.drawCircle(0, 0, radius);
    });
    // --- End Orbits ---

    // Create Earth sprite once texture is loaded
    earth = new PIXI.Sprite(texture);
    earth.anchor.set(0.5); // Center the sprite
    // Adjust scale as needed based on the PNG dimensions
    earth.scale.set(0.8); // Made Earth smaller

    // Position Earth in the center
    earth.x = app.screen.width / 2;
    earth.y = app.screen.height / 2;

    app.stage.addChild(earth); // Add Earth *after* orbits container

}).catch((error) => {
    console.error('Error loading Earth PNG asset:', error);
    // Create a fallback circle if PNG loading fails
    const fallbackEarth = new PIXI.Graphics();
    fallbackEarth.beginFill(0x4287f5); // Blue fallback
    fallbackEarth.drawCircle(0, 0, 100);
    fallbackEarth.endFill();
    fallbackEarth.x = app.screen.width / 2;
    fallbackEarth.y = app.screen.height / 2;
    app.stage.addChild(fallbackEarth);
});

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
    
    stars.push(star);
    app.stage.addChild(star);
}

// Animation loop
app.ticker.add(() => {
    stars.forEach(star => {
        star.alpha = Math.random();
    });
    
    // Add a subtle rotation to Earth (check if earth exists)
    if (earth && earth.parent) { // Check if earth is loaded and added to stage
        earth.rotation += 0.001;
    }
});

// Handle window resize
window.addEventListener('resize', () => {
    app.renderer.resize(window.innerWidth, window.innerHeight);
    // Reposition Earth after resize (check if earth exists)
    if (earth && earth.parent) {
        earth.x = app.screen.width / 2;
        earth.y = app.screen.height / 2;
        // Also reposition orbits container
        const orbitsContainer = app.stage.getChildAt(0); // Assuming it's the first child
        if (orbitsContainer) {
             orbitsContainer.x = app.screen.width / 2;
             orbitsContainer.y = app.screen.height / 2;
        }
    }
}); 