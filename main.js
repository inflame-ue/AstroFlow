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

// Create orbital paths around Earth (dashed lines)
const orbits = new PIXI.Graphics();
// Use a light blue color with low alpha for the orbits
orbits.lineStyle({
  width: 1,
  color: 0x3498db,
  alpha: 0.5,
  alignment: 0,
  cap: PIXI.LINE_CAP.ROUND,
  join: PIXI.LINE_JOIN.ROUND,
  // Create dashed effect
  dash: [5, 10],
  dashOffset: 0
});

// Earth position reference point (aligned with the Earth sprite)
// We'll position this where the Earth will be positioned
const earthRadius = 150; // Approximate size of the Earth sprite
const earthCenterX = earthRadius * 0.5; // Adjust based on Earth position
const earthCenterY = app.screen.height - earthRadius * 0.5; // Bottom aligned

// Draw 5 elliptical orbits with increasing size
for (let i = 1; i <= 5; i++) {
  // Calculate orbit size based on index
  const orbitWidth = earthRadius * 0.8 + i * 70;  // Width of orbit ellipse
  const orbitHeight = earthRadius * 0.6 + i * 50;  // Height of orbit ellipse (slightly smaller for perspective)
  
  // Draw the elliptical orbit
  orbits.drawEllipse(earthCenterX, earthCenterY, orbitWidth, orbitHeight);
}
app.stage.addChild(orbits);

// Create Earth using an image sprite instead of a drawn circle
const earth = new PIXI.Sprite(PIXI.Texture.from('earth.png')); 
earth.anchor.set(0.5, 0.5); // Center anchor point
earth.scale.set(1, 1); // Adjust scale as needed for your image

// Position Earth at bottom left with 20% off-screen
// This should align with the orbit center we defined above
earth.position.set(earthCenterX, earthCenterY);

// Move 20% off-screen to the left and bottom
const offsetX = earth.width * 0.2;
const offsetY = earth.height * 0.2;
earth.position.x -= offsetX;
earth.position.y += offsetY;

app.stage.addChild(earth);

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