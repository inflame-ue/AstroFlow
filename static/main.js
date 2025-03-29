// Canvas setup
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

// Set canvas size based on window size
function resizeCanvas() {
    const size = Math.min(window.innerWidth - 40, window.innerHeight - 40);
    canvas.width = size;
    canvas.height = size;
    
    // Update center points
    CENTER_X = canvas.width / 2;
    CENTER_Y = canvas.height / 2;
    
    // Update orbit radii based on canvas size
    const baseRadius = Math.min(canvas.width, canvas.height) / 8;
    ORBIT_RADIUSES[0] = baseRadius * 1.5;
    ORBIT_RADIUSES[1] = baseRadius * 2.5;
    ORBIT_RADIUSES[2] = baseRadius * 3.5;
    
    // Update Earth radius
    EARTH_RADIUS = baseRadius;
    
    // Update object sizes
    SATELLITE_RADIUS = baseRadius / 10;
    ROCKET_RADIUS = baseRadius / 10;
    FUEL_STATION_RADIUS = baseRadius / 10;
    
    // Reinitialize satellites with new dimensions
    initializeSatellites();
}

// Constants (will be updated on resize)
let CENTER_X = 0;
let CENTER_Y = 0;
let EARTH_RADIUS = 0;
let ORBIT_RADIUSES = [0, 0, 0];
let SATELLITE_RADIUS = 0;
let ROCKET_RADIUS = 0;
let FUEL_STATION_RADIUS = 0;

// Colors
const EARTH_COLOR = '#4287f5';
const ORBIT_COLOR = '#333333';
const SATELLITE_COLOR = '#00ff00';
const ROCKET_COLOR = '#ff0000';
const FUEL_STATION_COLOR = '#00ff00';
const PATH_COLOR = '#ff00ff';

// Simulation state
let satellites = [];
let rocket = null;
let pathPoints = [];
let isAnimating = false;
let currentPathIndex = 0;
let orbitSpeeds = [0.02, 0.015, 0.01]; // Reduced speeds for each orbit

// Initialize satellites
function initializeSatellites() {
    satellites = [];
    ORBIT_RADIUSES.forEach((radius, orbitIndex) => {
        // Generate 2-3 satellites per orbit
        const numSatellites = Math.floor(Math.random() * 2) + 2;
        for (let i = 0; i < numSatellites; i++) {
            const angle = (Math.PI * 2 * i) / numSatellites;
            satellites.push({
                orbitIndex,
                radius,
                angle,
                speed: orbitSpeeds[orbitIndex],
                x: CENTER_X + radius * Math.cos(angle),
                y: CENTER_Y + radius * Math.sin(angle)
            });
        }
    });
}

// Draw Earth
function drawEarth() {
    ctx.beginPath();
    ctx.arc(CENTER_X, CENTER_Y, EARTH_RADIUS, 0, Math.PI * 2);
    ctx.fillStyle = EARTH_COLOR;
    ctx.fill();
    ctx.strokeStyle = '#ffffff';
    ctx.stroke();
}

// Draw orbits
function drawOrbits() {
    ORBIT_RADIUSES.forEach(radius => {
        ctx.beginPath();
        ctx.arc(CENTER_X, CENTER_Y, radius, 0, Math.PI * 2);
        ctx.strokeStyle = ORBIT_COLOR;
        ctx.stroke();
    });
}

// Draw fuel station
function drawFuelStation() {
    ctx.beginPath();
    ctx.arc(CENTER_X, CENTER_Y - EARTH_RADIUS, FUEL_STATION_RADIUS, 0, Math.PI * 2);
    ctx.fillStyle = FUEL_STATION_COLOR;
    ctx.fill();
}

// Draw satellites
function drawSatellites() {
    satellites.forEach(satellite => {
        ctx.beginPath();
        ctx.arc(satellite.x, satellite.y, SATELLITE_RADIUS, 0, Math.PI * 2);
        ctx.fillStyle = SATELLITE_COLOR;
        ctx.fill();
    });
}

// Draw rocket
function drawRocket() {
    if (rocket) {
        ctx.beginPath();
        ctx.arc(rocket.x, rocket.y, ROCKET_RADIUS, 0, Math.PI * 2);
        ctx.fillStyle = ROCKET_COLOR;
        ctx.fill();
    }
}

// Draw path
function drawPath() {
    if (pathPoints.length > 1) {
        ctx.beginPath();
        ctx.moveTo(pathPoints[0].x, pathPoints[0].y);
        for (let i = 1; i < pathPoints.length; i++) {
            ctx.lineTo(pathPoints[i].x, pathPoints[i].y);
        }
        ctx.strokeStyle = PATH_COLOR;
        ctx.stroke();
    }
}

// Update satellite positions
function updateSatellites() {
    satellites.forEach(satellite => {
        satellite.angle += satellite.speed;
        satellite.x = CENTER_X + satellite.radius * Math.cos(satellite.angle);
        satellite.y = CENTER_Y + satellite.radius * Math.sin(satellite.angle);
    });
}

// Generate a sample path (to be replaced with your team's algorithm)
function generatePath() {
    const startPoint = { x: CENTER_X, y: CENTER_Y - EARTH_RADIUS };
    const points = [startPoint];
    
    // Generate a sample path that visits each satellite
    satellites.forEach(satellite => {
        // Add intermediate points for smooth movement
        const steps = 50;
        const lastPoint = points[points.length - 1];
        
        for (let i = 0; i <= steps; i++) {
            const t = i / steps;
            points.push({
                x: lastPoint.x + (satellite.x - lastPoint.x) * t,
                y: lastPoint.y + (satellite.y - lastPoint.y) * t
            });
        }
    });
    
    return points;
}

// Animation loop
function animate() {
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Update and draw everything
    updateSatellites();
    drawOrbits();
    drawEarth();
    drawFuelStation();
    drawSatellites();
    drawPath();
    
    // Update rocket position if path exists and animation is running
    if (isAnimating && pathPoints.length > 0 && currentPathIndex < pathPoints.length) {
        rocket = pathPoints[currentPathIndex];
        currentPathIndex++;
    }
    
    drawRocket();
    
    requestAnimationFrame(animate);
}

// Start simulation
function startSimulation() {
    if (!isAnimating) {
        isAnimating = true;
        pathPoints = generatePath();
        currentPathIndex = 0;
    }
}

// Reset simulation
function resetSimulation() {
    isAnimating = false;
    currentPathIndex = 0;
    rocket = { x: CENTER_X, y: CENTER_Y - EARTH_RADIUS }; // Reset rocket to fuel station
    pathPoints = [];
    initializeSatellites();
}

// Handle window resize
window.addEventListener('resize', resizeCanvas);

// Initialize and start
resizeCanvas();
animate(); 