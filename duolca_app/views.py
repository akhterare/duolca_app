"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, Flask, Response, request, session
import flask 
import requests
import adal
from duolca_app import app
from duolca_app import config
import os 
import json 

# SETTING VALUES USED FOR ACCESS TOKEN ACQUISITION
# PORT = 5000  # A flask app by default runs on PORT 5000
# AUTHORITY_URL = config.AUTHORITY_HOST_URL + '/' + config.TENANT
# REDIRECT_URI = 'http://localhost:{}/getAToken'.format(PORT)
# TEMPLATE_AUTHZ_URL = ('https://login.microsoftonline.com/{}/oauth2/authorize?' +
#                       'response_type=code&client_id={}&redirect_uri={}&' +
#                       'state={}&resource={}')

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )   

@app.route("/getAToken", methods=['GET', 'POST'])
def auth():
    URL = "https://duolcaapp.azurewebsites.net/.auth/me"
    r = requests.get(URL)
    right_header = r.headers

    tenant = "5d471751-9675-428d-917b-70f44f9630b0"
    authority_url = 'https://login.microsoftonline.com/' + tenant
    client_id = 'fb20d6fe-ce09-449a-b096-90f229943863'
    client_secret = '9bPMwvy7HztrwVkkCR08BOPMbPUb5Ze8MqMVZOwGTMQ='
    resource = 'https://management.azure.com'

    context = adal.AuthenticationContext(authority_url)
    token = context.acquire_token_with_client_credentials(resource, client_id, client_secret)
    access_token = token['accessToken']

    # access_token = flask.request.headers["X-MS-TOKEN-AAD-ACCESS-TOKEN"]
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
        title='Authorization',
        message='Your Token Was Successfully Retrieved!',
        access_token=access_token
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
        message='Duolca App Documentation.'
    )

