// Initialize Pixi.js application
const app = new PIXI.Application({
  width: window.innerWidth,
  height: window.innerHeight,
  view: document.getElementById('simulationCanvas'),
  backgroundColor: 0x000000, // Black background
});

// Create background with stars
const background = new PIXI.Graphics();
background.beginFill(0x000000);
background.drawRect(0, 0, app.screen.width, app.screen.height);
background.endFill();
for (let i = 0; i < 100; i++) {
  const x = Math.random() * app.screen.width;
  const y = Math.random() * app.screen.height;
  background.beginFill(0xffffff); // White stars
  background.drawCircle(x, y, 1);
  background.endFill();
}
app.stage.addChild(background);

// First create and position the Earth sprite to use its position as a reference
const earth = new PIXI.Sprite(PIXI.Texture.from('earth.png')); 
earth.anchor.set(0.3, 0.7); // Anchor point near bottom-left corner
earth.scale.set(1, 1); // Adjust scale as needed for your image
// Position Earth at bottom left with 20% off-screen
const earthCenterX = 0; // Left edge
const earthCenterY = app.screen.height; // Bottom edge
earth.position.set(earthCenterX, earthCenterY);

// Create orbital paths around Earth (dashed lines)
const orbits = new PIXI.Graphics();

// Calculate the true center of the Earth (accounting for anchor point)
// With anchor(0.3, 0.7), we need to move the orbit center relative to the earth position
const earthRadius = 150; // Approximate size of the Earth sprite

// We need to load the texture and wait for it to load to get accurate dimensions
PIXI.Assets.load('earth.png').then((texture) => {
  // Get the actual dimensions of the Earth sprite
  const earthWidth = texture.width * earth.scale.x;
  const earthHeight = texture.height * earth.scale.y;
  
  // Calculate the actual center of the Earth based on its position and anchor
  // For anchor(0.3, 0.7), the center is offset from the position
  const trueEarthCenterX = earthCenterX + earthWidth * (0.21);
  const trueEarthCenterY = earthCenterY - earthHeight * (0.21);
  
  // Clear previous orbits if any
  orbits.clear();
  
  // Use the light blue color with low alpha for the orbits
  orbits.lineStyle({
    width: 1,
    color: 0x3498db,
    alpha: 0.5,
    alignment: 1,
    cap: PIXI.LINE_CAP.ROUND,
    join: PIXI.LINE_JOIN.ROUND,
    dash: [5, 10],
    dashOffset: 0
  });
  
  // Draw 5 elliptical orbits around the true Earth center
  for (let i = 1; i <= 5; i++) {
    // Calculate orbit size based on index - starting much smaller
    const orbitWidth = earthWidth * 0.3 + i * 60;  // Width of orbit ellipse (smaller starting size)
    const orbitHeight = earthWidth * 0.3 + i * 60;  // Same height for perfect circles
    
    // Draw the circular orbit - using pure circles for clear 2D look
    orbits.drawEllipse(trueEarthCenterX, trueEarthCenterY, orbitWidth, orbitHeight);
  }
  
  // Ensure proper rendering order
  app.stage.removeChild(orbits);
  app.stage.removeChild(earth);
  app.stage.addChild(orbits);
  app.stage.addChild(earth);
});

// Apply darkening filter to the Earth
const colorMatrix = new PIXI.filters.ColorMatrixFilter();
colorMatrix.brightness(0.5); // 50% darker
earth.filters = [colorMatrix];

// Create rocket
const rocket = new PIXI.Graphics();
rocket.beginFill(0xff0000); // Red color
rocket.drawRect(-10, -20, 20, 40); // Rectangle shape
rocket.endFill();
app.stage.addChild(rocket);

// Create satellite
const satellite = new PIXI.Graphics();
satellite.beginFill(0x00ff00); // Green color
satellite.drawCircle(0, 0, 10); // Circle shape
satellite.endFill();
app.stage.addChild(satellite);

// Initialize Matter.js
const engine = Matter.Engine.create();
const world = engine.world;

// Create satellite body
const satelliteBody = Matter.Bodies.circle(250, 200, 10, { friction: 0, restitution: 0 });
Matter.Body.setVelocity(satelliteBody, { x: 10, y: 0 }); // Moves right
Matter.World.add(world, satelliteBody);

// Create rocket body
const rocketBody = Matter.Bodies.rectangle(400, 500, 20, 40, { friction: 0, restitution: 0 });
Matter.Body.setVelocity(rocketBody, { x: 0, y: 0 }); // Starts stationary
Matter.World.add(world, rocketBody);

// Simulation variables
let simulationTime = 0;
const timeStep = 1 / 60; // Assuming 60 fps
let launched = false;
const t_launch = 0; // Hardcoded launch time (replace with API call)

// Animation loop
app.ticker.add((delta) => {
  // Update physics
  Matter.Engine.update(engine, 1000 / 60); // 1000ms / 60fps
  simulationTime += timeStep;

  // Launch rocket at specified time
  if (simulationTime >= t_launch && !launched) {
      Matter.Body.setVelocity(rocketBody, { x: 0, y: -20 }); // Moves up
      launched = true;
  }

  // Sync sprite positions with physics bodies
  rocket.x = rocketBody.position.x;
  rocket.y = rocketBody.position.y;
  satellite.x = satelliteBody.position.x;
  satellite.y = satelliteBody.position.y;

  // Check proximity for refueling
  const dx = rocket.x - satellite.x;
  const dy = rocket.y - satellite.y;
  const distance = Math.sqrt(dx * dx + dy * dy);
  if (distance < 20) {
      console.log("Refueling initiated!");
      // Add refueling animation here (e.g., particles)
  }
});

// Optional: Fetch launch time from API (uncomment and adjust URL)
/*
fetch('https://api.example.com/getLaunchTime')
  .then(response => response.json())
  .then(data => {
      t_launch = data.launchTime; // Assign API-provided launch time
  })
  .catch(error => console.error('API error:', error));
*/