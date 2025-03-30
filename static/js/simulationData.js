// static/js/simulationData.js

import { DEFAULT_SIM_DATA, KM_TO_PIXEL_SCALE, DEFAULT_RESULT_SIM_DATA } from './constants.js';

// Globally accessible simulation data and derived data
let simData = DEFAULT_SIM_DATA;
let orbitRadiiScaled = [];
// Add global variable for simulation results
let simResults = DEFAULT_RESULT_SIM_DATA;
let processedTrajectory = [];

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

async function fetchSimulationResults() {
    try {
        const response = await fetch('/api/simulation_results');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const fetchedData = await response.json();
        console.log("Fetched Simulation Results", fetchedData);
        return fetchedData;
    } catch (error) {
        console.error("Could not fetch simulation results:", error);
        return null; // Return null or default data on error
    }
}

function processSimulationResults(fetchedData) {
    if (!fetchedData) {
        console.log("No simulation results to process.");
        simResults = { ...DEFAULT_RESULT_SIM_DATA }; // Use copy of default
        processedTrajectory = [];
        return processedTrajectory;
    }

    // Store the raw data
    simResults = fetchedData;
    
    // Process trajectory data
    processedTrajectory = [];
    if (simResults.trajectory && Array.isArray(simResults.trajectory)) {
        // Convert trajectory points, scale if needed
        processedTrajectory = simResults.trajectory.map(point => {
            try {
                if (Array.isArray(point) && point.length >= 3) {
                    // Assuming format [time, x, y]
                    const time = parseFloat(point[0]);
                    // Scale x and y if they're in kilometers
                    const x = parseFloat(point[1]) * KM_TO_PIXEL_SCALE;
                    const y = parseFloat(point[2]) * KM_TO_PIXEL_SCALE;
                    
                    if (isNaN(time) || isNaN(x) || isNaN(y)) {
                        throw new Error(`Invalid trajectory point values: ${point}`);
                    }
                    
                    return [time, x, y];
                }
                throw new Error(`Invalid trajectory point format: ${point}`);
            } catch (e) {
                console.warn("Error processing trajectory point:", point, e);
                return null; // Use null for invalid points
            }
        }).filter(p => p !== null); // Filter out invalid points
    }
    
    console.log(`Processed ${processedTrajectory.length} trajectory points`);
    return processedTrajectory;
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

// Function to load and process simulation data
export async function loadAndProcessSumulationResults() {
    const results = await fetchSimulationResults();
    if (results) {
        return processSimulationResults(results);
    }
    return []; // Return empty array if no results
}

// Function combining fetch and process
export async function loadAndProcessSimulationData() {
    const data = await fetchSimulationData();
    processSimulationData(data);
    
    const results = await fetchSimulationResults();
    if (results) {
        processSimulationResults(results);
    }
    
    // Return the processed data structures if needed
    return { simData, orbitRadiiScaled, simResults, processedTrajectory };
}

// Export getters for potentially easier access from other modules
export function getSimData() {
    return simData;
}

export function getOrbitRadiiScaled() {
    return orbitRadiiScaled;
}

// Add getters for simulation results
export function getSimResults() {
    return simResults;
}

export function getProcessedTrajectory() {
    return processedTrajectory;
}