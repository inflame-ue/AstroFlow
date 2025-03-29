from flask import Flask, render_template, request, redirect, url_for, jsonify, session # type: ignore
import json

app = Flask(__name__)
app.secret_key = 'astroflow_secret_key'  # Add a secret key for session

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if we have form data
        form_data = request.form.get('formData')
        if form_data:
            try:
                # Parse the JSON data
                data = json.loads(form_data)
                print("Received form data:", data)
                # Store data in session for use in simulation
                session['form_data'] = data

                # Redirect to simulation page
                return redirect(url_for('simulation'))
            except Exception as e:
                print("Error processing form data:", e)
        
        # Redirect to simulation page
        return redirect(url_for('simulation'))
    
    # For GET requests, render the form
    return render_template('form.html')

@app.route('/simulation')
def simulation():
    # Get data from session if available
    form_data = session.get('form_data', None)
    
    # Get status parameters
    status = request.args.get('status')
    message = request.args.get('message')
    
    # Extract station angles from form_data
    station_angles = [] # Default to empty list
    try:
        if form_data and 'launchpads' in form_data:
            for key, launchpad_data in form_data['launchpads'].items():
                angle = float(launchpad_data.get('angle1', 0)) # Get angle1 for each launchpad
                station_angles.append(angle)
    except Exception as e:
        print(f"Error extracting station angles: {e}")
        station_angles = [] # Fallback to empty list
        
    return render_template('simulation.html', 
                           form_data=form_data, 
                           status=status, 
                           message=message,
                           # Pass angles as a list (will be converted to JSON in template)
                           station_angles=station_angles)

if __name__ == '__main__':
    app.run(debug=True)
