from flask import Flask, render_template, request, redirect, url_for, jsonify, session
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
    
    return render_template('simulation.html', 
                           form_data=form_data, 
                           status=status, 
                           message=message)

if __name__ == '__main__':
    app.run(debug=True)
