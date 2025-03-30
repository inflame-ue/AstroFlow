from flask import Flask, render_template, request, redirect, url_for, jsonify, session # type: ignore
from dotenv import load_dotenv
from utils.parser import normalize_form_data
import json
import os


load_dotenv()
app = Flask(__name__)

# secret key for session
app.secret_key = os.environ.get("SECRET_KEY")  # without it the app will not work

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        form_data = request.form.get('formData')
        if form_data:
            try:
                data = json.loads(form_data)
                data = normalize_form_data(data)
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
    form_data = session.get('form_data')

    if not form_data:
        return redirect(url_for('bad_request'))

    return render_template('simulation.html', 
                           status=status, 
                           message=message,
                           form_data=form_data) # pass form data to simulation page


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
    return jsonify(form_data)


if __name__ == '__main__':
    app.run(debug=True)
