"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, Flask, Response, request, session, redirect
import flask 
import requests
import adal
import os 
import json 
import uuid 

from duolca_app import app
from duolca_app import config
from duolca_app.db import get_db

app.debug = True
app.secret_key = 'development'

PORT = 5000  # A flask app by default runs on PORT 5000
AUTHORITY_URL = config.AUTHORITY_HOST_URL + '/' + config.TENANT
# REDIRECT_URI = 'http://localhost:{}/getAToken'.format(PORT)
REDIRECT_URI = 'https://duolcaapp.azurewebsites.net/getAToken'
TEMPLATE_AUTHZ_URL = ('https://login.microsoftonline.com/{}/oauth2/authorize?' +
                      'response_type=code&client_id={}&redirect_uri={}&' +
                      'state={}&resource={}')
TOKEN = ""
USERNAME = ""
# USERNAME_NEW="",
# VM_NAME="default",
# RESOURCE_GROUP="default",
# LOCATION="default"

@app.route('/home', methods=('GET', 'POST'))
def home():
    global USERNAME_NEW
    global VM_NAME 
    global RESOURCE_GROUP
    global LOCATION

    if request.method == 'POST':
        USERNAME_NEW = 'TEST'
        VM_NAME = request.form['vm_name']
        RESOURCE_GROUP = request.form['resource_group']
        LOCATION = request.form['location']
        # db = get_db()

        # db.execute(
        #         'INSERT INTO course (username, vm_name, resource_group, location) VALUES (?, ?, ?, ?)',
        #         (USERNAME_NEW, VM_NAME, RESOURCE_GROUP, LOCATION)  
        # )
        # db.commit()

        # return redirect(url_for('manage'))
        return flask.redirect('/manage')

    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
        username=USERNAME
    )   

@app.route('/manage', methods=('GET', 'POST'))
def manage():
        # db.execute(
        #         'INSERT INTO course (username, vm_name, resource_group, location) VALUES (?, ?, ?, ?)',
        #         (username, vm_name, resource_group, location)
        #     )
        #     db.commit()

        return render_template(
            'manage.html', 
            title='Management',
            message='Your VM Was Created and Logged!',
            username=USERNAME_NEW,
            vm_name=VM_NAME,
            resource_group=RESOURCE_GROUP,
            location=LOCATION
        )

@app.route('/')
def main():
    # login_url = 'http://localhost:{}/login'.format(PORT)
    login_url = 'https://duolcaapp.azurewebsites.net/login'
    resp = flask.Response(status=307) 
    resp.headers['location'] = login_url
    return resp

@app.route("/login")
def login():
    auth_state = str(uuid.uuid4())
    flask.session['state'] = auth_state
    authorization_url = TEMPLATE_AUTHZ_URL.format(
        config.TENANT,
        config.CLIENT_ID,
        REDIRECT_URI,
        auth_state,
        config.RESOURCE)
    resp = flask.Response(status=307)
    resp.headers['location'] = authorization_url
    return resp

@app.route("/getAToken", methods=['GET', 'POST'])
def auth():
    code = flask.request.args['code']
    state = flask.request.args['state']
   
    client_id = 'fb20d6fe-ce09-449a-b096-90f229943863'
    client_secret = '9bPMwvy7HztrwVkkCR08BOPMbPUb5Ze8MqMVZOwGTMQ='
    resource = 'https://graph.microsoft.com'
    
    context = adal.AuthenticationContext(AUTHORITY_URL)
    TOKEN = context.acquire_token_with_authorization_code(code, REDIRECT_URI, resource, client_id, client_secret)
    flask.session['access_token'] = TOKEN['accessToken']

    return flask.redirect('/graphcall')
   
@app.route('/graphcall')
def graphcall():
    if 'access_token' not in flask.session:
        return flask.redirect(flask.url_for('login'))

    endpoint = config.RESOURCE + '/' + config.API_VERSION + '/me/'
    http_headers = {'Authorization': flask.session.get('access_token'),
                    'User-Agent': 'duolca_app',
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'client-request-id': str(uuid.uuid4())}
    graph_data = requests.get(endpoint, headers=http_headers, stream=False).json()
    USERNAME = graph_data['givenName']

    return render_template(
        'auth.html', 
        title='Authorization',
        message='We Have Your Auth Info!',
        access_token=TOKEN, 
        graph_data=graph_data,
        username=USERNAME
    )

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact Us',
        #year=datetime.now().year,
        year=datetime.now().year,
        message='Your contact page.',
        username=USERNAME
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Duolca App Documentation.',
        username=USERNAME
    )

