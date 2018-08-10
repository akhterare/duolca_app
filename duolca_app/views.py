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
import os.path
from duolca_app.deployer import Deployer
from msrestazure.azure_active_directory import AdalAuthentication

from duolca_app import app
from duolca_app import config
from duolca_app.db import get_db

app.debug = True
app.secret_key = 'development'

PORT = 5000  # A flask app by default runs on PORT 5000
AUTHORITY_URL = config.AUTHORITY_HOST_URL + '/' + config.TENANT
REDIRECT_URI = 'https://duolcaapp.azurewebsites.net/getAToken'
TEMPLATE_AUTHZ_URL = ('https://login.microsoftonline.com/{}/oauth2/authorize?' +
                      'response_type=code&client_id={}&redirect_uri={}&' +
                      'state={}&resource={}')
# TOKEN = ""
# AUTH_TOKEN = ""
# CREDENTIALS = ""
USERNAME = ""

@app.route('/')
def main():
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
        config.MANAGE_RESOURCE)
    resp = flask.Response(status=307)
    resp.headers['location'] = authorization_url
    return resp

@app.route("/getAToken", methods=['GET', 'POST'])
def auth():
    global CREDENTIALS
    global USERNAME
    global GRAPH_DATA
    global TOKEN
    global AUTH_TOKEN

    code = flask.request.args['code']
    state = flask.request.args['state']
   
    client_id = 'fb20d6fe-ce09-449a-b096-90f229943863'
    client_secret = '9bPMwvy7HztrwVkkCR08BOPMbPUb5Ze8MqMVZOwGTMQ='
    
    # GET THE MICROSOFT GRAPH ACCESS TOKEN
    resource = 'https://graph.microsoft.com'
    context = adal.AuthenticationContext(AUTHORITY_URL)
    AUTH_TOKEN = context.acquire_token_with_authorization_code(code, REDIRECT_URI, resource, client_id, client_secret)
    flask.session['auth_access_token'] = AUTH_TOKEN['accessToken']

    # GET THE AZURE RESOURCE MANAGEMENT ACCESS TOKEN
    resource = 'https://management.azure.com'
    context = adal.AuthenticationContext(AUTHORITY_URL)
    TOKEN = context.acquire_token_with_authorization_code(code, REDIRECT_URI, resource, client_id, client_secret)
    flask.session['access_token'] = TOKEN['accessToken']

    CREDENTIALS = AdalAuthentication(
        context.acquire_token_with_client_credentials,
        config.MANAGE_RESOURCE,
        config.CLIENT_ID,
        config.CLIENT_SECRET
    )

    # MAKE A CALL TO THE GRAPH API TO GET USER INFO WHICH WILL ALWAYS BE USED!
    endpoint = config.AUTH_RESOURCE + '/' + config.API_VERSION + '/me/'
    http_headers = {'Authorization': flask.session.get('auth_access_token'),
                    'User-Agent': 'duolca_app',
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'client-request-id': str(uuid.uuid4())}
    GRAPH_DATA = requests.get(endpoint, headers=http_headers, stream=False).json()

    flask.session['username'] = GRAPH_DATA['givenName']
    USERNAME = GRAPH_DATA['givenName']

    return flask.redirect('/home')
    
    #     return render_template(
    #         'manage.html', 
    #         title='Management',
    #         message='Your VM Was Successfully Deployed!',
    #         vm_name='input test vm', 
    #         resource_group=deployer.resource_group,
    #         location='East US',
    #         credentials=CREDENTIALS

    # )
    # return render_template(
    #     'auth.html', 
    #     title='Authorization',
    #     message='We Have Your Auth Info!',
    #     access_token=TOKEN, 
    #     credentials=CREDENTIALS
    #     # graph_data=graph_data,
    #     # username=USERNAME
    # )

@app.route('/home', methods=('GET', 'POST'))
def home():
    global VM_NAME 
    global RESOURCE_GROUP
    global LOCATION

    # UPON FORM BEING FILLED OUT BY USER: this sends info for deployment
    if request.method == 'POST':
        VM_NAME = request.form['vm_name']
        RESOURCE_GROUP = request.form['resource_group']
        LOCATION = request.form['location']

        flask.session['resource_group'] = RESOURCE_GROUP
        flask.session['vm_name'] = VM_NAME

        # db = get_db()

        # db.execute(
        #         'INSERT INTO course (username, vm_name, resource_group, location) VALUES (?, ?, ?, ?)',
        #         (USERNAME_NEW, VM_NAME, RESOURCE_GROUP, LOCATION)  
        # )
        # db.commit()

        # return redirect(url_for('manage'))
        return flask.redirect('/DeployTemplate')

    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
        username=USERNAME
    ) 

@app.route('/DeployTemplate')
def DeployTemplate():
    global DEPLOYER
    global DEPLOY_STATE

    if 'access_token' not in flask.session:
        return flask.redirect(flask.url_for('login'))

    my_subscription_id = config.SUBSCRIPTION_ID   # your Azure Subscription Id
    resource_group = flask.session['resource_group']         # the resource group for deployment
    
    if 'access_token' in flask.session:
        # Duolca initializes the Deployer class with values entered by user, and credentials generated in GetAToken
        vm_name = flask.session['vm_name']
        DEPLOYER = Deployer(my_subscription_id, resource_group, CREDENTIALS, vm_name)
        
        # Check if the deployment user wants to start has already been created or not 
        DEPLOY_STATE = DEPLOYER.check_deployment()

        # If not deployed already, Duolca will deploy 
        if DEPLOY_STATE == False:
            my_deployment = DEPLOYER.deploy()
        
        # Regardless, Duolca redirects to the VM management screen 
        return flask.redirect('/manage')
    else: 
        return flask.redirect('/')

@app.route('/manage', methods=('GET', 'POST'))
def manage():
    if 'access_token' not in flask.session:
        return flask.redirect(flask.url_for('login'))

    # resources_delete_state = False

    # Collect information about the deployed VM 
    # if request.method=='POST':
    #     DEPLOYER.DeleteResources(DEPLOYER.resource_group)
    #     resources_delete_state = True

    endpoint = config.AUTH_RESOURCE + '/' + config.API_VERSION + '/me/'
    http_headers = {'Authorization': AUTH_TOKEN,
                    'User-Agent': 'duolca_app',
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'client-request-id': str(uuid.uuid4())}
    IP_ADDRESS_DATA = requests.get(endpoint, headers=http_headers, stream=False).json()
    # endpoint = config.MANAGE_RESOURCE + '/subscriptions/' + config.SUBSCRIPTION_ID + '/resourceGroups/' + RESOURCE_GROUP + '/providers/Microsoft.Network/publicIPAddresses/' + DEPLOYER.vm_name + '-duolcasampPublicIP?api-version=2018-04-01' 
    # http_headers = {'Authorization': flask.session.get('access_token'),
    #                 'User-Agent': 'duolca_app',
    #                 'Accept': 'application/json',
    #                 'Content-Type': 'application/json',
    #                 'client-request-id': str(uuid.uuid4())}
    # IP_ADDRESS_DATA = requests.get(endpoint, headers=http_headers, stream=False).json()

    return render_template(
            'manage.html', 
            title='Management',
            message='Your VM Was Successfully Deployed!',
            vm_name=DEPLOYER.vm_name, 
            resource_group=DEPLOYER.resource_group,
            location='East US',
            deploy_state=DEPLOY_STATE, 
            # resources_delete_state=resources_delete_state,
            ip_data = IP_ADDRESS_DATA,
            username=USERNAME
        )

@app.route('/contact')
def contact():
    check_username(USERNAME)

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
    check_username(USERNAME)

    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Duolca App Documentation.',
        username=USERNAME
    )

@app.route('/profile')
def profile():
    check_username(USERNAME)

    """Renders the about page."""
    return render_template(
        'profile.html',
        title='Your Profile',
        year=datetime.now().year,
        username=USERNAME,
        graph_data=GRAPH_DATA
    )

def check_username(username):
    if USERNAME is None:
        return flask.redirect('/')
    