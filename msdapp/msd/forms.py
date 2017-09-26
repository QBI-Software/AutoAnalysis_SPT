from wtforms import Form, BooleanField, StringField, validators, FileField, IntegerField,SubmitField
from wtforms.csrf.session import SessionCSRF
from flask import session
from datetime import timedelta
from msdapp import app

SECRET_KEY = app.config['CSRF_SESSION_KEY']

class MSDBaseForm(Form):
    class Meta:
        csrf = True
        csrf_class = SessionCSRF
        csrf_secret = SECRET_KEY

        @property
        def csrf_context(self):
            return session

class FilterMSDForm(MSDBaseForm):
    datafile = FileField('Initial datafile (AllROI-D.txt)')
    datafile_msd = FileField('Initial MSD datafile (AllROI-MSD.txt)')
    minlimit = IntegerField('Min limit', validators=[validators.NumberRange(min=-10, max=10)])
    maxlimit = IntegerField('Max limit', validators=[validators.NumberRange(min=-10, max=10)])
    submit = SubmitField('Run Script')



