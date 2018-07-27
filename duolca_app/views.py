"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, Flask, Response, request, session
import flask 
from adal import AuthenticationContext
from duolca_app import app
from duolca_app import config

# SETTING VALUES USED FOR ACCESS TOKEN ACQUISITION
PORT = 5000  # A flask app by default runs on PORT 5000
AUTHORITY_URL = config.AUTHORITY_HOST_URL + '/' + config.TENANT
REDIRECT_URI = 'http://localhost:{}/getAToken'.format(PORT)
TEMPLATE_AUTHZ_URL = ('https://login.microsoftonline.com/{}/oauth2/authorize?' +
                      'response_type=code&client_id={}&redirect_uri={}&' +
                      'state={}&resource={}')


@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )   

@app.route("/getAToken")
def auth():
    # code = flask.request.args['code']
    # state = flask.request.args['state']
    # if state != Flask.flask.session['state']:
    #     raise ValueError("State does not match")
    # auth_context = adal.AuthenticationContext(AUTHORITY_URL)
    # token_response = auth_context.acquire_token_with_authorization_code(code, REDIRECT_URI, config.RESOURCE,
    #                                                                     config.CLIENT_ID, config.CLIENT_SECRET)
    # # # It is recommended to save this to a database when using a production app.
    # flask.session['access_token'] = token_response['accessToken']

    return render_template(
        'auth.html', 
        title='Authorization'
        message='Your Token'
    )

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact Us',
        #year=datetime.now().year,
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )

