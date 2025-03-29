// Three.js setup
let scene, camera, renderer, controls;
let earth, rocket, satellites = [];
let satelliteObjects = [];
let pathLine;
let isAnimating = false;
let currentPathIndex = 0;
let pathPoints = [];

// Initialize the scene
function init() {
    // Create scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x000000);

    // Create camera
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 15;

    // Create renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    document.body.appendChild(renderer.domElement);

    // Add controls
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.minDistance = 5;
    controls.maxDistance = 50;

    // Create Earth
    const earthGeometry = new THREE.SphereGeometry(5, 32, 32);
    const earthTexture = new THREE.TextureLoader().load('https://threejs.org/examples/textures/planets/earth_atmos_2048.jpg');
    const earthMaterial = new THREE.MeshPhongMaterial({ map: earthTexture });
    earth = new THREE.Mesh(earthGeometry, earthMaterial);
    scene.add(earth);

    // Add ambient light
    const ambientLight = new THREE.AmbientLight(0x404040);
    scene.add(ambientLight);

    // Add directional light
    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(5, 3, 5);
    scene.add(directionalLight);

    // Create rocket
    const rocketGeometry = new THREE.ConeGeometry(0.2, 1, 32);
    const rocketMaterial = new THREE.MeshPhongMaterial({ color: 0xff0000 });
    rocket = new THREE.Mesh(rocketGeometry, rocketMaterial);
    rocket.position.set(0, 5, 0);
    scene.add(rocket);

    // Create path line
    const pathGeometry = new THREE.BufferGeometry();
    const pathMaterial = new THREE.LineBasicMaterial({ color: 0x00ff00 });
    pathLine = new THREE.Line(pathGeometry, pathMaterial);
    scene.add(pathLine);

    // Handle window resize
    window.addEventListener('resize', onWindowResize, false);
}

// Handle window resize
function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
}

// Generate random satellites
async function generateRandomSatellites() {
    try {
        const response = await fetch('http://localhost:8001/satellites/random/5');
        const satellites = await response.json();
        
        // Clear existing satellites
        satelliteObjects.forEach(obj => scene.remove(obj));
        satelliteObjects = [];

        // Create new satellites
        satellites.forEach(pos => {
            const satelliteGeometry = new THREE.SphereGeometry(0.2, 16, 16);
            const satelliteMaterial = new THREE.MeshPhongMaterial({ color: 0x00ff00 });
            const satellite = new THREE.Mesh(satelliteGeometry, satelliteMaterial);
            satellite.position.set(pos.x / 1000, pos.y / 1000, pos.z / 1000);
            scene.add(satellite);
            satelliteObjects.push(satellite);
        });
    } catch (error) {
        console.error('Error generating satellites:', error);
    }
}

// Start refueling mission
async function startRefueling() {
    if (satelliteObjects.length === 0) {
        alert('Please generate satellites first!');
        return;
    }

    const rocketPosition = {
        x: 0,
        y: 5,
        z: 0
    };

    const satellitesPositions = satelliteObjects.map(sat => ({
        x: sat.position.x * 1000,
        y: sat.position.y * 1000,
        z: sat.position.z * 1000
    }));

    try {
        const response = await fetch('http://localhost:8001/calculate-path', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                rocket_position: rocketPosition,
                satellites: satellitesPositions
            })
        });

        pathPoints = await response.json();
        currentPathIndex = 0;
        isAnimating = true;

        // Update path line
        const points = pathPoints.map(point => 
            new THREE.Vector3(point.x / 1000, point.y / 1000, point.z / 1000)
        );
        pathLine.geometry.setFromPoints(points);
        pathLine.geometry.computeBoundingSphere();
    } catch (error) {
        console.error('Error calculating path:', error);
    }
}

// Reset scene
function resetScene() {
    isAnimating = false;
    currentPathIndex = 0;
    rocket.position.set(0, 5, 0);
    rocket.rotation.set(0, 0, 0);
    
    // Clear path line
    pathLine.geometry.setFromPoints([]);
    pathLine.geometry.computeBoundingSphere();
}

// Animation loop
function animate() {
    requestAnimationFrame(animate);

    if (isAnimating && currentPathIndex < pathPoints.length) {
        const point = pathPoints[currentPathIndex];
        rocket.position.set(point.x / 1000, point.y / 1000, point.z / 1000);
        
        // Calculate rocket rotation to point in direction of movement
        if (currentPathIndex < pathPoints.length - 1) {
            const nextPoint = pathPoints[currentPathIndex + 1];
            const direction = new THREE.Vector3(
                nextPoint.x - point.x,
                nextPoint.y - point.y,
                nextPoint.z - point.z
            ).normalize();
            
            rocket.lookAt(
                rocket.position.x + direction.x,
                rocket.position.y + direction.y,
                rocket.position.z + direction.z
            );
        }

        currentPathIndex++;
    }

    controls.update();
    renderer.render(scene, camera);
}

// Initialize and start animation
init();
animate(); 