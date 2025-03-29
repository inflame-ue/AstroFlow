from flask import Flask, render_template, request, redirect, url_for, jsonify, session # type: ignore
from dotenv import load_dotenv
import json
import os

load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")  # add a secret key for session with .env

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        form_data = request.form.get('formData')
        if form_data:
            try:
                data = json.loads(form_data)
                print(data)
                session['form_data'] = data # store data in session for use in simulation
                return redirect(url_for('simulation'))
            except Exception as e:
                print("Error processing form data:", e)
        return redirect(url_for('simulation'))
    return render_template('form.html')

@app.route('/simulation')
def simulation():
    status = request.args.get('status')
    message = request.args.get('message')

    return render_template('simulation.html', 
                           status=status, 
                           message=message,
                           form_data=session.get('form_data')) # pass form data to simulation page

@app.route('/api/form_data')
def get_form_data():
    form_data = session.get('form_data')
    print("Form data:", form_data)
    return jsonify(form_data)


if __name__ == '__main__':
    app.run(debug=True)
