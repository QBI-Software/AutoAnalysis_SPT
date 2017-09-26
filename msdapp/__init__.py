from flask import Flask, render_template

app = Flask(__name__)
app.config.from_object("config")
app.secret_key = app.config['CSRF_SESSION_KEY']
app.static_folder = app.config['UPLOAD_FOLDER']
print("config:debug=", app.config['DEBUG'])

from msdapp.msd.controllers import simple_page

app.register_blueprint(simple_page)