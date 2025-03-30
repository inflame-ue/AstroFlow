// static/js/simulationData.js

import { DEFAULT_SIM_DATA, KM_TO_PIXEL_SCALE } from './constants.js';

// Globally accessible simulation data and derived data
let simData = DEFAULT_SIM_DATA;
let orbitRadiiScaled = [];

// Function to fetch data from the backend API
async function fetchSimulationData() {
    try {
        const response = await fetch('/api/form_data');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const fetchedData = await response.json();
        console.log("Fetched FormData", fetchedData);
        return fetchedData;
    } catch (error) {
        console.error("Could not fetch simulation data:", error);
        return null; // Return null or default data on error
    }
}

// Function to process fetched data (calculate scaled radii, etc.)
function processSimulationData(fetchedData) {
    if (!fetchedData) {
        simData = { ...DEFAULT_SIM_DATA }; // Use a copy
        orbitRadiiScaled = [];
        console.log("Using default simulation data due to fetch error.");
        return;
    }

    simData = fetchedData; // Assign to global

    // Process orbit data
    orbitRadiiScaled = []; // Clear previous scaled radii
    if (simData && simData.orbits) {
        orbitRadiiScaled = Object.values(simData.orbits).map(orbit => {
            try {
                 const radiusKm = parseFloat(orbit.radius);
                 if (isNaN(radiusKm) || radiusKm <= 0) {
                    throw new Error(`Invalid radius: ${orbit.radius}`);
                 }
                 return radiusKm * KM_TO_PIXEL_SCALE;
            } catch (e) {
                console.warn("Error processing orbit radius:", orbit.radius, e);
                return 0; // Use 0 for invalid radii
            }
        }).filter(r => r > 0); // Filter out invalid/zero radii
    }
    console.log("Processed Scaled Orbit Radii (px):", orbitRadiiScaled);
}

// Function combining fetch and process
export async function loadAndProcessSimulationData() {
    const data = await fetchSimulationData();
    processSimulationData(data);
    // Return the processed data structure if needed, though it's also global
    return { simData, orbitRadiiScaled };
}

// Export getters for potentially easier access from other modules
export function getSimData() {
    return simData;
}

export function getOrbitRadiiScaled() {
    return orbitRadiiScaled;
}