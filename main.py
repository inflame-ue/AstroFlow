from flask import Flask, render_template, request, redirect, url_for, jsonify, session # type: ignore
from dotenv import load_dotenv
from utils.parser import normalize_form_data
import json
import os
import numpy as np # needed for deg2rad


try:
    from astroalgo.algorithm import SimulateMission, Tanker, LaunchPad, Orbit, Satellite, EARTH_RADIUS
    ASTROALGO_AVAILABLE = True
except ImportError as e:
    print(f"WARNING: Could not import astroalgo. Simulation will not run. Error: {e}")
    ASTROALGO_AVAILABLE = False
    # define dummy classes if import fails, so the rest of the Flask app doesn't crash
    class SimulateMission: pass
    class Tanker: pass
    class LaunchPad: pass
    class Orbit: pass
    class Satellite: pass
    EARTH_RADIUS = 6378.137

load_dotenv()
app = Flask(__name__)
# secret key for session
app.secret_key = os.environ.get("SECRET_KEY")  # without it the app will not work

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        form_data = request.form.get('formData')
        session.pop('form_data', None) # clear previous data first
        session.pop('simulation_results', None) # clear previous results

        if form_data:
            try:
                data = json.loads(form_data)
                # normalize the orbit data
                data_normalized = normalize_form_data(data)
                if data_normalized: # check if normalization didn't return None/empty
                    print("Normalized form data:", json.dumps(data_normalized, indent=2))
                    session['form_data'] = data_normalized # store data in session
                    return redirect(url_for('simulation', status='success'))
                else:
                    print("Normalization failed or returned empty data.")
                    return redirect(url_for('simulation', status='error', message='Form data normalization failed.'))

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON form data: {e}")
                return redirect(url_for('simulation', status='error', message='Invalid form data format.'))
            except Exception as e:
                print(f"Error processing form data: {e}")
                return redirect(url_for('simulation', status='error', message='Could not process form data.'))
        else:
             print("No form data received in POST request.")
             return redirect(url_for('simulation', status='warning', message='No configuration data submitted.'))

    # For GET requests, clear old data and render the form
    session.pop('form_data', None)
    session.pop('simulation_results', None)
    return render_template('form.html')

@app.route('/simulation')
def simulation():
    form_data = session.get('form_data', None)
    status = request.args.get('status')
    message = request.args.get('message')
    simulation_results = None # initialize results variable
    sim_error_message = None # specific error during simulation run

    print(f"ASTROALGO_AVAILABLE: {ASTROALGO_AVAILABLE}")
    if form_data and ASTROALGO_AVAILABLE:
        print("Attempting to initialize and run simulation...")
        try:
            # tanker starts at Earth radius, angle will be set by launchpad choice
            tanker = Tanker(EARTH_RADIUS, 0, 0)
            sim = SimulateMission(EARTH_RADIUS, tanker)

            if 'launchpads' in form_data:
                for lp_id, lp_data in form_data['launchpads'].items():
                    try:
                        angle_deg = float(lp_data.get('angle1', 0.0))
                        sim.add_launch_pad(LaunchPad(EARTH_RADIUS, np.deg2rad(angle_deg)))
                    except (ValueError, TypeError, KeyError) as e:
                        print(f"Skipping invalid launchpad {lp_id}: {e}")

            if not sim.launch_pads:
                 raise ValueError("No valid launch pads configured.")

            orbit_map = {}
            if 'orbits' in form_data:
                 # sort by radius to ensure algorithm processes them correctly if needed
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

            if 'satellites' in form_data:
                 for sat_id, sat_data in form_data['satellites'].items():
                    try:
                        orbit_id_ref = sat_data.get('orbitId')
                        if orbit_id_ref in orbit_map:
                            target_orbit_obj = orbit_map[orbit_id_ref]
                            angle_deg = float(sat_data.get('angle', 0.0))
                            sim.add_satellite(target_orbit_obj, np.deg2rad(angle_deg))
                        else:
                             print(f"Warning: Satellite {sat_id} references unknown orbit ID {orbit_id_ref}")
                    except (ValueError, TypeError, KeyError) as e:
                        print(f"Skipping invalid satellite {sat_id}: {e}")
            
            print("Running simulate_mission()...")
            sim.simulate_mission()
            print("Simulation sequence complete.")

            # limit trajectory size for session storage if necessary
            max_traj_points = 5000
            trajectory_data = sim.tanker_mission_trajectory
            if len(trajectory_data) > max_traj_points:
                 # sample the trajectory to reduce size
                 step = len(trajectory_data) // max_traj_points
                 trajectory_data = trajectory_data[::step]


            simulation_results = {
                "trajectory": trajectory_data, # List of (time, x, y) tuples
                "events": sim.tanker.mission_events # List of (time, description) tuples
            }

            # write simulation results to file
            with open('simulation_results.json', 'w') as f:
                json.dump(simulation_results, f)

        except ValueError as ve: # catch specific configuration errors
             sim_error_message = f"Simulation setup error: {ve}"
             print(sim_error_message)
             status = 'error'
             message = sim_error_message
        except Exception as e: # catch runtime errors during simulation
             sim_error_message = f"Error during simulation run: {e}"
             print(sim_error_message)
             status = 'error'
             message = sim_error_message
    elif not ASTROALGO_AVAILABLE:
        status = 'error'
        message = 'Simulation algorithm module (astroalgo) could not be loaded.'
    elif not form_data:
         status = 'warning'
         message = 'No configuration data loaded. Please submit the form first.'


    return render_template('simulation.html',
                           form_data=form_data, # pass original form data for display
                           status=status,
                           message=message,
                           simulation_results=simulation_results # pass simulation output
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
    form_data = session.get('form_data')
    return jsonify(form_data if form_data else {})

@app.route('/api/simulation_results')
def get_simulation_results():
    with open('simulation_results.json', 'r') as f:
        simulation_results = json.load(f)
    return jsonify(simulation_results if simulation_results else {})


if __name__ == '__main__':
    app.run(debug=True)
