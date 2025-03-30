// static/js/assets.js

// Define asset URLs relative to the static folder root
const earthImageRelativeUrl = '/static/images/earth.svg';
const satelliteImageRelativeUrl = '/static/images/satellite.png';
const gasStationImageRelativeUrl = '/static/images/gas_station.svg';
const rocketImageRelativeUrl = '/static/images/rocket.svg';

// Function to get absolute URLs (important if paths are resolved incorrectly otherwise)
function getAbsoluteUrl(relativeUrl) {
    // Check if it already looks like an absolute URL (less robust check)
    if (relativeUrl.startsWith('http') || relativeUrl.startsWith('//')) {
        return relativeUrl;
    }
    // Ensure leading slash for root-relative path
    const path = relativeUrl.startsWith('/') ? relativeUrl : '/' + relativeUrl;
    return window.location.origin + path;
}

// Export URLs for potential direct use if needed
export const EARTH_IMG_URL = getAbsoluteUrl(earthImageRelativeUrl);
export const SATELLITE_IMG_URL = getAbsoluteUrl(satelliteImageRelativeUrl);
export const GAS_STATION_IMG_URL = getAbsoluteUrl(gasStationImageRelativeUrl);
export const ROCKET_IMG_URL = getAbsoluteUrl(rocketImageRelativeUrl);
export const CAPSULE_IMG_URL = getAbsoluteUrl('/static/images/capsule.svg');

// Function to load all assets
// Requires PIXI global object
export async function loadAssets() {
    console.log("Loading assets:", EARTH_IMG_URL, SATELLITE_IMG_URL, GAS_STATION_IMG_URL, ROCKET_IMG_URL, CAPSULE_IMG_URL);
    try {
        const textures = await PIXI.Assets.load([
            EARTH_IMG_URL,
            SATELLITE_IMG_URL,
            GAS_STATION_IMG_URL,
            ROCKET_IMG_URL,
            CAPSULE_IMG_URL
        ]);
        console.log("Assets loaded successfully.");
        return textures;
    } catch (error) {
        console.error('Error loading assets:', error);
        // Return an empty object or throw error to indicate failure
        return {};
    }
}