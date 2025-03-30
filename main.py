from flask import Flask, render_template, request, redirect, url_for, jsonify, session # type: ignore
from dotenv import load_dotenv
from utils.parser import normalize_form_data
import json
import os
import numpy as np # Needed for deg2rad

# --- Import from your algorithm ---
try:
    from astroalgo.algorithm import SimulateMission, Tanker, LaunchPad, Orbit, Satellite, EARTH_RADIUS
    ASTROALGO_AVAILABLE = True
except ImportError as e:
    print(f"WARNING: Could not import astroalgo. Simulation will not run. Error: {e}")
    ASTROALGO_AVAILABLE = False
    # Define dummy classes if import fails, so the rest of the Flask app doesn't crash
    class SimulateMission: pass
    class Tanker: pass
    class LaunchPad: pass
    class Orbit: pass
    class Satellite: pass
    EARTH_RADIUS = 6378.137 # Provide a fallback value

# --- Load Environment Variables ---
load_dotenv()
app = Flask(__name__)

# secret key for session
app.secret_key = os.environ.get("SECRET_KEY")  # without it the app will not work

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        form_data = request.form.get('formData')
        session.pop('form_data', None) # Clear previous data first
        session.pop('simulation_results', None) # Clear previous results

        if form_data:
            try:
                data = json.loads(form_data)
                # Normalize data using your parser
                data_normalized = normalize_form_data(data)
                if data_normalized: # Check if normalization didn't return None/empty
                    print("Normalized form data:", json.dumps(data_normalized, indent=2))
                    session['form_data'] = data_normalized # store data in session
                    # Redirect with success status
                    return redirect(url_for('simulation', status='success'))
                else:
                    print("Normalization failed or returned empty data.")
                    return redirect(url_for('simulation', status='error', message='Form data normalization failed.'))

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON form data: {e}")
                return redirect(url_for('simulation', status='error', message='Invalid form data format.'))
            except Exception as e:
                print(f"Error processing form data: {e}")
                # Optionally log the full traceback here
                return redirect(url_for('simulation', status='error', message='Could not process form data.'))
        else:
             print("No form data received in POST request.")
             # Redirect with warning/error if no data submitted
             return redirect(url_for('simulation', status='warning', message='No configuration data submitted.'))

    # For GET requests, clear old data and render the form
    session.pop('form_data', None)
    session.pop('simulation_results', None)
    return render_template('form.html')

@app.route('/simulation')
def simulation():
    # Data from session if available
    form_data = session.get('form_data', None)
    status = request.args.get('status')
    message = request.args.get('message')
    simulation_results = None # Initialize results variabl``
    sim_error_message = None # Specific error during simulation run

    print(f"ASTROALGO_AVAILABLE: {ASTROALGO_AVAILABLE}")
    if form_data and ASTROALGO_AVAILABLE:
        print("Attempting to initialize and run simulation...")
        try:
            # --- Initialize Simulation from Form Data ---
            # 1. Create Tanker and Sim objects
            # Tanker starts at Earth radius, angle will be set by launchpad choice
            tanker = Tanker(EARTH_RADIUS, 0, 0)
            sim = SimulateMission(EARTH_RADIUS, tanker)

            # 2. Add Launch Pads
            if 'launchpads' in form_data:
                for lp_id, lp_data in form_data['launchpads'].items():
                    try:
                        # Assuming form uses 'angle1' and it's in degrees
                        angle_deg = float(lp_data.get('angle1', 0.0))
                        sim.add_launch_pad(LaunchPad(EARTH_RADIUS, np.deg2rad(angle_deg)))
                    except (ValueError, TypeError, KeyError) as e:
                        print(f"Skipping invalid launchpad {lp_id}: {e}")

            if not sim.launch_pads:
                 raise ValueError("No valid launch pads configured.")

            # 3. Add Orbits (and map internal ID to Orbit object)
            orbit_map = {}
            if 'orbits' in form_data:
                 # Sort by radius to ensure algorithm processes them correctly if needed
                 sorted_orbit_items = sorted(
                     form_data['orbits'].items(),
                     key=lambda item: float(item[1].get('radius', 'inf'))
                 )
                 for orb_id, orb_data in sorted_orbit_items:
                     try:
                         radius_km = float(orb_data.get('radius'))
                         # Assuming 0 inclination if not specified
                         orbit_obj = sim.add_orbit(radius_km, inclination=0)
                         orbit_map[orb_id] = orbit_obj
                     except (ValueError, TypeError, KeyError) as e:
                         print(f"Skipping invalid orbit {orb_id}: {e}")

            if not sim.orbits:
                 raise ValueError("No valid orbits configured.")

            # 4. Add Satellites to their respective orbits
            if 'satellites' in form_data:
                 for sat_id, sat_data in form_data['satellites'].items():
                    try:
                        orbit_id_ref = sat_data.get('orbitId')
                        if orbit_id_ref in orbit_map:
                            target_orbit_obj = orbit_map[orbit_id_ref]
                            # Assuming form angle is in degrees
                            angle_deg = float(sat_data.get('angle', 0.0))
                            # Algorithm calculates speed internally based on orbit radius
                            sim.add_satellite(target_orbit_obj, np.deg2rad(angle_deg))
                        else:
                             print(f"Warning: Satellite {sat_id} references unknown orbit ID {orbit_id_ref}")
                    except (ValueError, TypeError, KeyError) as e:
                        print(f"Skipping invalid satellite {sat_id}: {e}")
            # --- End Initialization ---

            # --- Run the Simulation ---
            print("Running simulate_mission()...")
            sim.simulate_mission() # Execute the main algorithm
            print("Simulation sequence complete.")

            # --- Store Results (Example: trajectory and events) ---
            # Limit trajectory size for session storage if necessary
            max_traj_points = 5000
            trajectory_data = sim.tanker_mission_trajectory
            if len(trajectory_data) > max_traj_points:
                 # Sample the trajectory to reduce size
                 step = len(trajectory_data) // max_traj_points
                 trajectory_data = trajectory_data[::step]


            simulation_results = {
                "trajectory": trajectory_data, # List of (time, x, y) tuples
                "events": sim.tanker.mission_events # List of (time, description) tuples
                # Add any other summary data you want here
            }
            print(f"Simulation results: {len(simulation_results['trajectory'])}")
            # Optionally store results back in session if needed by other pages/requests
            # session['simulation_results'] = simulation_results

        except ValueError as ve: # Catch specific configuration errors
             sim_error_message = f"Simulation setup error: {ve}"
             print(sim_error_message)
             status = 'error' # Update status for template
             message = sim_error_message
        except Exception as e: # Catch runtime errors during simulation
             sim_error_message = f"Error during simulation run: {e}"
             print(sim_error_message)
             # Optionally log traceback here
             # import traceback
             # traceback.print_exc()
             status = 'error' # Update status for template
             message = sim_error_message

    elif not ASTROALGO_AVAILABLE:
        status = 'error'
        message = 'Simulation algorithm module (astroalgo) could not be loaded.'
    elif not form_data:
         # This case might be hit if user navigates directly to /simulation
         status = 'warning'
         message = 'No configuration data loaded. Please submit the form first.'


    # Pass necessary data to the template
    return render_template('simulation.html',
                           form_data=form_data, # Pass original form data for display
                           status=status,
                           message=message,
                           simulation_results=simulation_results # Pass simulation output
                           )


# Error Handling Endpoints
@app.errorhandler(400)
def bad_request(e):
    return render_template('400.html'), 400

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


# API endpoints

@app.route('/api/form_data')
def get_form_data():
    # This endpoint remains useful for JavaScript to fetch data if needed
    form_data = session.get('form_data')
    return jsonify(form_data if form_data else {})

@app.route('/api/simulation_results')
def get_simulation_results():
    simulation_results = session.get('simulation_results')
    return jsonify(simulation_results if simulation_results else {})


if __name__ == '__main__':
    app.run(debug=True)
