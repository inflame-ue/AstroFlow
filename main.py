from flask import Flask, render_template, request, redirect, url_for, jsonify
import json

app = Flask(__name__)

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
                # Process the data as needed
            except Exception as e:
                print("Error processing form data:", e)
        
        # Redirect to simulation page
        return redirect(url_for('simulation'))
    
    # For GET requests, render the form
    return render_template('form.html')

@app.route('/simulation')
def simulation():
    return render_template('simulation.html')

if __name__ == '__main__':
    app.run(debug=True)
