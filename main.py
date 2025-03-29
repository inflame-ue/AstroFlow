from flask import Flask, render_template
from flask import request, redirect, url_for

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return redirect(url_for('simulation.index')) 
    return render_template('form.html')

if __name__ == '__main__':
    app.run(debug=True)
