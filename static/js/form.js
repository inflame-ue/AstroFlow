// Create the PixiJS application
const app = new PIXI.Application({
    width: window.innerWidth,
    height: window.innerHeight,
    backgroundColor: 0x000000,
    resolution: window.devicePixelRatio || 1,  // Use 4 for 4K resolution
    antialias: true,
    autoDensity: true,
});

// Append the Pixi canvas to the dedicated background div
document.getElementById('pixi-background').appendChild(app.view);

// --- Starry Background Logic --- 
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

// Animation loop for stars
app.ticker.add((delta) => {
    stars.forEach(star => {
        star.alpha = Math.random(); // Twinkle effect
    });
});

// Handle window resize for stars
window.addEventListener('resize', () => {
    app.renderer.resize(window.innerWidth, window.innerHeight);
    // Reposition stars randomly within the new bounds
    stars.forEach(star => {
        if (star && star.parent) { 
            star.x = Math.random() * app.screen.width;
            star.y = Math.random() * app.screen.height;
        }
    });
});
// --- End Starry Background Logic --- 

document.addEventListener('DOMContentLoaded', function () {
  const launchpadsContainer = document.getElementById('launchpadsContainer');
  const orbitsContainer = document.getElementById('orbitsContainer');
  const satellitesContainer = document.getElementById('satellitesContainer');
  const addLaunchpadBtn = document.getElementById('addLaunchpadBtn');
  const addOrbitBtn = document.getElementById('addOrbitBtn');
  const addSatelliteBtn = document.getElementById('addSatelliteBtn');
  const satelliteForm = document.getElementById('satelliteForm');
  const formSummary = document.getElementById('formSummary');
  const summaryContent = document.getElementById('summaryContent');

  let launchpadCount = 0;
  let orbitCount = 0;
  let satelliteCount = 0;

  // Helper function to create launchpad
  function createLaunchpad(id) {
      const launchpadDiv = document.createElement('div');
      launchpadDiv.className = 'item-container launchpad-item';
      launchpadDiv.dataset.id = id;

      launchpadDiv.innerHTML = `
          <div class="header-row">
              <h3>Launchpad ${id}</h3>
              <button type="button" class="remove-btn" id="removeLaunchpad${id}">Remove</button>
          </div>
          <div class="form-row">
              <div class="form-group">
                  <label for="launchpad${id}Angle1">Angle <span class="unit">(degrees)</span></label>
                  <input type="number" id="launchpad${id}Angle1" name="launchpad[${id}][angle1]" min="0" max="360" step="0.1" placeholder="e.g., 93.0" required>
              </div>
          </div>
      `;

      launchpadsContainer.appendChild(launchpadDiv);

      // Add remove button event listener
      document.getElementById(`removeLaunchpad${id}`).addEventListener('click', function() {
          if (document.querySelectorAll('.launchpad-item').length > 1) {
              launchpadDiv.remove();
          } else {
              alert('You need at least one launchpad.');
          }
      });

      return launchpadDiv;
  }

  // Helper function to create orbit
  function createOrbit(id) {
      const orbitDiv = document.createElement('div');
      orbitDiv.className = 'item-container orbit-item';
      orbitDiv.dataset.id = id;

      orbitDiv.innerHTML = `
          <div class="header-row">
              <h3>Orbit ${id}</h3>
              <button type="button" class="remove-btn" id="removeOrbit${id}">Remove</button>
          </div>
          <div class="form-row">
              <div class="form-group">
                  <label for="orbit${id}Radius">Radius <span class="unit">(km)</span></label>
                  <input type="number" id="orbit${id}Radius" name="orbit[${id}][radius]" min="0" step="0.1" placeholder="e.g., 6878.0" required>
              </div>
              <div class="form-group">
                  <label for="orbit${id}Speed">Satellite Speed <span class="unit">(km/s)</span></label>
                  <input type="number" id="orbit${id}Speed" name="orbit[${id}][speed]" min="0" step="0.001" placeholder="e.g., 7.8" required>
              </div>
          </div>
      `;

      orbitsContainer.appendChild(orbitDiv);
      
      // Add remove button event listener
      document.getElementById(`removeOrbit${id}`).addEventListener('click', function() {
          if (document.querySelectorAll('.orbit-item').length > 1) {
              // Check if any satellite is using this orbit
              const satellitesUsingOrbit = document.querySelectorAll(`.satellite-item select[name^="satellite"][value="${id}"]`);
              if (satellitesUsingOrbit.length > 0) {
                  alert(`Cannot remove Orbit ${id} because it's being used by satellites. Please reassign those satellites first.`);
                  return;
              }
              orbitDiv.remove();
              // Update orbit dropdown options in all satellites
              updateSatelliteOrbitOptions();
          } else {
              alert('You need at least one orbit.');
          }
      });
      
      return orbitDiv;
  }

  // Helper function to create satellite
  function createSatellite(id) {
      const satelliteDiv = document.createElement('div');
      satelliteDiv.className = 'item-container satellite-item';
      satelliteDiv.dataset.id = id;

      // Create orbit options
      let orbitOptions = '';
      const orbitItems = document.querySelectorAll('.orbit-item');
      orbitItems.forEach(orbit => {
          const orbitId = orbit.dataset.id;
          orbitOptions += `<option value="${orbitId}">Orbit ${orbitId}</option>`;
      });

      satelliteDiv.innerHTML = `
          <div class="header-row">
              <h3>Satellite ${id}</h3>
              <button type="button" class="remove-btn" id="removeSatellite${id}">Remove</button>
          </div>
          <div class="form-row">
              <div class="form-group">
                  <label for="satellite${id}Angle">Angle <span class="unit">(degrees)</span></label>
                  <input type="number" id="satellite${id}Angle" name="satellite[${id}][angle]" min="0" max="360" step="0.1" placeholder="e.g., 45.0" required>
              </div>
              <div class="form-group">
                  <label for="satellite${id}Orbit">Assigned Orbit</label>
                  <select id="satellite${id}Orbit" name="satellite[${id}][orbitId]" required>
                      ${orbitOptions}
                  </select>
              </div>
          </div>
          <div class="orbit-info">
              <div class="speed-info">Speed and radius are determined by the assigned orbit</div>
          </div>
      `;

      satellitesContainer.appendChild(satelliteDiv);

      // Add remove button event listener
      document.getElementById(`removeSatellite${id}`).addEventListener('click', function() {
          if (document.querySelectorAll('.satellite-item').length > 1) {
              satelliteDiv.remove();
          } else {
              alert('You need at least one satellite.');
          }
      });

      // Add change event to orbit selection
      const orbitSelect = document.getElementById(`satellite${id}Orbit`);
      orbitSelect.addEventListener('change', function() {
          updateSatelliteOrbitInfo(id, this.value);
      });

      // Initialize orbit info
      updateSatelliteOrbitInfo(id, orbitSelect.value);

      return satelliteDiv;
  }

  // Update satellite orbit options when orbits change
  function updateSatelliteOrbitOptions() {
      const satellites = document.querySelectorAll('.satellite-item');
      const orbits = document.querySelectorAll('.orbit-item');

      let orbitOptions = '';
      orbits.forEach(orbit => {
          const orbitId = orbit.dataset.id;
          orbitOptions += `<option value="${orbitId}">Orbit ${orbitId}</option>`;
      });

      satellites.forEach(satellite => {
          const satelliteId = satellite.dataset.id;
          const orbitSelect = document.getElementById(`satellite${satelliteId}Orbit`);
          if (!orbitSelect) return; // Skip if element doesn't exist
          
          const currentValue = orbitSelect.value;

          // Check if current orbit still exists
          const orbitExists = Array.from(orbits).some(orbit => orbit.dataset.id === currentValue);

          orbitSelect.innerHTML = orbitOptions;

          // Restore previous value if it exists
          if (orbitExists) {
              orbitSelect.value = currentValue;
          } else {
              // Default to the first orbit if the previous one is gone
              const firstOrbit = orbits[0]?.dataset.id;
              if (firstOrbit) {
                  orbitSelect.value = firstOrbit;
                  updateSatelliteOrbitInfo(satelliteId, firstOrbit);
              }
          }
      });
  }

  // Update satellite orbit info based on selected orbit
  function updateSatelliteOrbitInfo(satelliteId, orbitId) {
      const radiusInput = document.getElementById(`orbit${orbitId}Radius`);
      const speedInput = document.getElementById(`orbit${orbitId}Speed`);
      
      if (radiusInput && speedInput) {
          const radius = radiusInput.value || "not set";
          const speed = speedInput.value || "not set";
          
          const infoDiv = document.querySelector(`.satellite-item[data-id="${satelliteId}"] .orbit-info`);
          if (infoDiv) {
              infoDiv.innerHTML = `
                  <div class="speed-info">
                      <span class="unit">Radius:</span> ${radius} km, 
                      <span class="unit">Speed:</span> ${speed} km/s
                  </div>
              `;
          }
      }
  }

  // Add initial items
  createLaunchpad(++launchpadCount);
  createOrbit(++orbitCount);
  createSatellite(++satelliteCount);

  // Event listeners for add buttons
  addLaunchpadBtn.addEventListener('click', function() {
      createLaunchpad(++launchpadCount);
  });

  addOrbitBtn.addEventListener('click', function() {
      createOrbit(++orbitCount);
      updateSatelliteOrbitOptions();
  });

  addSatelliteBtn.addEventListener('click', function() {
      createSatellite(++satelliteCount);
  });

  // Update all satellite orbit info when orbit data changes
  document.addEventListener('change', function(e) {
      const target = e.target;
      if ((target.id.startsWith('orbit') && (target.id.includes('Radius') || target.id.includes('Speed')))) {
          const orbitId = target.id.match(/orbit(\d+)/)[1];
          document.querySelectorAll(`.satellite-item select[value="${orbitId}"]`).forEach(select => {
              const satelliteId = select.closest('.satellite-item').dataset.id;
              updateSatelliteOrbitInfo(satelliteId, orbitId);
          });
      }
  });

  // Form submission
  satelliteForm.addEventListener('submit', function(e) {
      e.preventDefault();

      try {
          // Collect form data
          const formData = new FormData(satelliteForm);
          const formDataObj = {};
          // Process form data
          formDataObj.launchpads = {};
          formDataObj.orbits = {};
          formDataObj.satellites = {};

          const launchpadPattern = /^launchpad\[(\d+)\]\[(.*?)\]$/;
          const orbitPattern = /^orbit\[(\d+)\]\[(.*?)\]$/;
          const satellitePattern = /^satellite\[(\d+)\]\[(.*?)\]$/;

          for (const [key, value] of formData.entries()) {
            let match;
            if ((match = key.match(launchpadPattern))) {
              const id = match[1], field = match[2];
              if (!formDataObj.launchpads[id]) formDataObj.launchpads[id] = {};
              formDataObj.launchpads[id][field] = value;
            } else if ((match = key.match(orbitPattern))) {
              const id = match[1], field = match[2];
              if (!formDataObj.orbits[id]) formDataObj.orbits[id] = {};
              formDataObj.orbits[id][field] = value;
            } else if ((match = key.match(satellitePattern))) {
              const id = match[1], field = match[2];
              if (!formDataObj.satellites[id]) formDataObj.satellites[id] = {};
              formDataObj.satellites[id][field] = value;
            }
          }

          // Process satellites to include radius and speed from their assigned orbit
          for (const satelliteId in formDataObj.satellites) {
              const satellite = formDataObj.satellites[satelliteId];
              const orbitId = satellite.orbitId;

              if (formDataObj.orbits[orbitId]) {
                  satellite.radius = formDataObj.orbits[orbitId].radius;
                  satellite.speed = formDataObj.orbits[orbitId].speed;
              }
          }

          // Display the summary
          summaryContent.textContent = JSON.stringify(formDataObj, null, 2);
          formSummary.style.display = 'block';

          console.log('Form Data:', formDataObj);
          
          // Visual feedback - hide form and show toggle bar
          const formContainer = document.querySelector('.form-container');
          const toggleBar = document.querySelector('.toggle-bar');
          formContainer.classList.add('hidden');
          toggleBar.classList.add('visible');
          
          // Use fetch to submit the data directly to the server
          fetch('/', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/x-www-form-urlencoded',
              },
              body: new URLSearchParams({
                  'formData': JSON.stringify(formDataObj)
              }),
              redirect: 'follow' // Allow the browser to follow redirects
          })
          .then(response => {
              if (!response.ok && !response.redirected) {
                  throw new Error(`Form submission failed: ${response.status} ${response.statusText}`);
              }
              
              // Check if response is a redirect and manually navigate to simulation page
              if (response.redirected) {
                  window.location.href = response.url;
              } else {
                  // If for some reason it wasn't redirected, go to simulation anyway
                  window.location.href = '/simulation';
              }
          })
          .catch(error => {
              console.error('Error submitting form:', error);
              alert('An error occurred while submitting the form. Please try again.');
              
              // Show form again in case of error
              formContainer.classList.remove('hidden');
              toggleBar.classList.remove('visible');
          });
          
      } catch (error) {
          console.error("Form submission error:", error);
          alert("An error occurred while processing the form. Please check the console for details.");
          
          // Show form again in case of error
          formContainer.classList.remove('hidden');
          toggleBar.classList.remove('visible');
      }
  });

  const formContainer = document.querySelector('.form-container');
  const toggleBar = document.querySelector('.toggle-bar');

  // Show form when clicking the toggle bar
  toggleBar.addEventListener('click', function() {
      formContainer.classList.remove('hidden');
      toggleBar.classList.remove('visible');
  });

  // Function to update the summary content
  function updateSummary() {
      // This function is no longer needed as the summary is updated in the submit handler
  }
});