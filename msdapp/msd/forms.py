from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import Form, BooleanField, StringField, validators, FileField, IntegerField,SubmitField
from wtforms.csrf.session import SessionCSRF

class FilterMSDForm(Form):
    # class Meta:
    #     csrf = True  # Enable CSRF
    #     csrf_class = SessionCSRF  # Set the CSRF implementation
    #     csrf_secret = b'foobar'  # Some implementations need a secret key.

    datafile = FileField('Initial datafile (AllROI-D.txt)', validators=[FileRequired()])
    datafile_msd = FileField('Initial MSD datafile (AllROI-MSD.txt)', validators=[FileRequired()])
    minlimit = IntegerField('Min limit', [validators.NumberRange(min=-10, max=10)])
    maxlimit = IntegerField('Max limit', [validators.NumberRange(min=-10, max=10)])
    submit = SubmitField('Run Script')


