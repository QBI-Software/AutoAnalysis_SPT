# Run a test server.
#from msdapp import app
from flask import Flask, render_template
from msdapp.msd.controllers import simple_page

app = Flask(__name__)
app.config.from_object("config")
app.secret_key = app.config['CSRF_SESSION_KEY']
app.static_folder = app.config['UPLOAD_FOLDER']
print("config:debug=", app.config['DEBUG'])
app.register_blueprint(simple_page)

app.run(debug=True, port=8085)