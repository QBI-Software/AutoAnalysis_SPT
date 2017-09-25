from flask import Flask, render_template

app = Flask(__name__)
app.config.from_object("config")
UPLOAD_PATH = app.config['UPLOAD_FOLDER']
SECRET_KEY = app.config['CSRF_SESSION_KEY']

from msdapp.msd.controllers import simple_page

app.register_blueprint(simple_page)