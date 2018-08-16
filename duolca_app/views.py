########################################################################################################
# DUOLCA 1.0.0 
# VIEWS.PY ROUTING FILE 
#
# VIEWS.PY is the main routing file, what the app does in different pages, for the Duolca Web Application 
# All routes are identified using the @... at the beginning of the view (function) related to it
# This file controls app authentication, token collection, deployment (using deployer class), and other pages
#
# August 17th, 2018 \\ Areena Akhter
########################################################################################################
 
# Import relevant libraries
from datetime import datetime
from flask import render_template, Flask, Response, request, session, redirect
import flask 
import requests
import adal
import os 
import json 
import uuid 
import os.path

# Import classes for deployment and management of Azure resources
from duolca_app.deployer import Deployer
from duolca_app.manager import Manager
from msrestazure.azure_active_directory import AdalAuthentication

from duolca_app import app
from duolca_app import config

# For deployment of the application, these variables must be set - in production, change the key and turn off debug
app.debug = True
app.secret_key = 'development'

# Global variables will be inputted into the login function
PORT = 5000  # A flask app by default runs on PORT 5000
AUTHORITY_URL = config.AUTHORITY_HOST_URL + '/' + config.TENANT
REDIRECT_URI = 'https://duolcaapp.azurewebsites.net/getAToken'
TEMPLATE_AUTHZ_URL = ('https://login.microsoftonline.com/{}/oauth2/authorize?' +
                      'response_type=code&client_id={}&redirect_uri={}&' +
                      'state={}&resource={}')
USERNAME = ""

# INDEX VIEW: routes user to the login URL 
@app.route('/')
def main():
    login_url = 'https://duolcaapp.azurewebsites.net/login'
    resp = flask.Response(status=307) 
    resp.headers['location'] = login_url
    return resp

# LOGIN VIEW: routes user to the external Azure Active Directory login for Nokia
@app.route("/login")
def login():
    auth_state = str(uuid.uuid4())
    flask.session['state'] = auth_state

    # Builds the authorization URL that the user is redirected to 
    authorization_url = TEMPLATE_AUTHZ_URL.format(
        config.TENANT,
        config.CLIENT_ID,
        REDIRECT_URI,
        auth_state,
        config.MANAGE_RESOURCE)
    resp = flask.Response(status=307)
    resp.headers['location'] = authorization_url
    return resp

# GETATOKEN VIEW: this is the callback (redirect URI) for the AD login, will run after login
@app.route("/getAToken", methods=['GET', 'POST'])
def auth():

    # Intialize the user-specific variables that will be used during run-time
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
    auth_token = context.acquire_token_with_authorization_code(code, REDIRECT_URI, resource, client_id, client_secret)
    flask.session['auth_access_token'] = auth_token['accessToken']
    AUTH_TOKEN = auth_token['accessToken']

    # GET THE AZURE RESOURCE MANAGEMENT ACCESS TOKEN (USED TO MAKE REST CALLS MANUALLY)
    resource = 'https://management.azure.com'
    context = adal.AuthenticationContext(AUTHORITY_URL)
    manage_token = context.acquire_token_with_authorization_code(code, REDIRECT_URI, resource, client_id, client_secret)
    flask.session['access_token'] = manage_token['accessToken']
    TOKEN = manage_token['accessToken']

    # GET THE AZURE RESOURCE MANAGEMENT CREDENTIALS (USED WITH SDK FOR PYTHON)
    CREDENTIALS = AdalAuthentication(
        context.acquire_token_with_client_credentials,
        config.MANAGE_RESOURCE,
        config.CLIENT_ID,
        config.CLIENT_SECRET
    )

    # MAKE A MANUAL REST CALL CALL TO THE GRAPH API TO GET USER INFO WHICH WILL ALWAYS BE USED!
    endpoint = config.AUTH_RESOURCE + '/' + config.API_VERSION + '/me/' # The specific endpoint for the 'Read User Info' rest call, look in Microsoft documentation for this
    http_headers = {'Authorization': flask.session.get('auth_access_token'), # Headers to be injected, include the authorization token
                    'User-Agent': 'duolca_app',
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'client-request-id': str(uuid.uuid4())}
    GRAPH_DATA = requests.get(endpoint, headers=http_headers, stream=False).json()

    flask.session['username'] = GRAPH_DATA['givenName']
    USERNAME = GRAPH_DATA['givenName']

    return flask.redirect('/home')

# HOME VIEW: renders the home template, which contains a form with deployment or management options for the user
@app.route('/home', methods=('GET', 'POST'))
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
        username=USERNAME
    ) 

# DEPLOY SUBMIT VIEW: When the user submits the form by clicking on the 'Deploy vLab' button, they're redirected here
@app.route('/DeploySubmit', methods=('GET', 'POST'))
def DeploySubmit():
    global COURSE_NAME
    global DEPLOY_NAME
    global RESOURCE_GROUP
    global LOCATION

    # UPON FORM BEING FILLED OUT BY USER: this sends info for deployment
    COURSE_NAME = request.form['course_name']
    RESOURCE_GROUP = request.form['resource_group']
    LOCATION = request.form['location']
    DEPLOY_NAME = request.form['deploy_name']

    # These variables are stored in the session (THEY'RE NOT ACTUALLY USED IN MY CODE, BUT AVAILABLE)
    flask.session['resource_group'] = RESOURCE_GROUP
    flask.session['course_name'] = COURSE_NAME

    return flask.redirect('/DeployTemplate')

# MANAGE SUBMIT VIEW: When the user submits the form by clicking on the 'Manage vLab' button, they're redirected here
@app.route('/ManageSubmit', methods=('GET', 'POST'))
def ManageSubmit():
    global COURSE_NAME
    global DEPLOY_NAME
    global RESOURCE_GROUP
    global LOCATION
    global DEPLOY_STATE
    global DEPLOYER

    # UPON FORM BEING FILLED OUT BY USER: this sends info for deployment
    COURSE_NAME = request.form['course_name']
    RESOURCE_GROUP = request.form['resource_group']
    LOCATION = request.form['location']
    DEPLOY_NAME = request.form['deploy_name']

    my_subscription_id = config.SUBSCRIPTION_ID   # your Azure Subscription Id
    public_ip = '/subscriptions/' + config.SUBSCRIPTION_ID + '/resourceGroups/' + RESOURCE_GROUP + '/providers/Microsoft.Network/publicIPAddresses/' +  COURSE_NAME + '-duolcatrialPublicIP'
    
    # Initializing the Deployer class with variables entered by user
    DEPLOYER = Deployer(config.SUBSCRIPTION_ID, RESOURCE_GROUP, CREDENTIALS, COURSE_NAME, public_ip, DEPLOY_NAME)
    DEPLOY_STATE = DEPLOYER.check_deployment()

    # Checking if the deployment exists (if NOT, won't let user into Management Screen)
    if DEPLOY_STATE == False:
        return flask.redirect('/')
    else:
        ip_data = DEPLOYER.ReturnIP() # Attains the IP Address of the machine
        
        return render_template(
            'manage.html', 
            deploy_name=DEPLOY_NAME,
            course_name=COURSE_NAME,
            resource_group=RESOURCE_GROUP,
            location='East US',
            deploy_state=DEPLOY_STATE, 
            ip_data = ip_data,
            username=USERNAME
        )

# DEPLOY TEMPLATE VIEW: Redirects from DeploySubmit, deploys the VM from template [using DEPLOY_NAME] 
@app.route('/DeployTemplate')
def DeployTemplate():
    global DEPLOYER
    global DEPLOY_STATE
    global RESOURCE_GROUP_EMPTY

    if 'access_token' not in flask.session:
        return flask.redirect('/')

    my_subscription_id = config.SUBSCRIPTION_ID   # your Azure Subscription Id
    resource_group = flask.session['resource_group']         # the resource group for deployment
    course_name = flask.session['course_name']
    public_ip = '/subscriptions/' + config.SUBSCRIPTION_ID + '/resourceGroups/' + RESOURCE_GROUP + '/providers/Microsoft.Network/publicIPAddresses/' +  course_name + '-duolcatrialPublicIP'

    if 'access_token' in flask.session:
        # Duolca initializes the Deployer class with values entered by user, and credentials generated in GetAToken
        DEPLOYER = Deployer(my_subscription_id, resource_group, CREDENTIALS, course_name, public_ip, DEPLOY_NAME)
        
        # Check if the deployment user wants to start has already been created or not 
        DEPLOY_STATE = DEPLOYER.check_deployment()
        post_deploy_state = False

        # If not deployed already, Duolca will deploy 
        if DEPLOY_STATE == False:
            # Begin by clearing the existing resource group
            DEPLOYER.DeleteResources()

            # Then run deployment from template, with deployer class having been initalized
            my_deployment = DEPLOYER.deploy()

            # Update the deploy_state to reflect new deployment
            DEPLOY_STATE = True
            post_deploy_state = True
        else:
            return flask.redirect('/')

        # Once Duolca has determined whether it's deployed or not, it'll render appropriate screen
        if DEPLOY_STATE == True: 
            if post_deploy_state == True:
                # Redirect to a management screen
                return flask.redirect('/manage')
            else:
                return flask.redirect('/')

# MANAGE VIEW: renders the management page after retrieving the management data (Public IP)
@app.route('/manage', methods=('GET', 'POST'))
def manage():
    ip_data = DEPLOYER.ReturnIP()

    return render_template(
            'manage.html', 
            deploy_name=DEPLOYER.deploy_name,
            course_name=DEPLOYER.course_name, 
            resource_group=DEPLOYER.resource_group,
            location='East US',
            deploy_state=DEPLOY_STATE, 
            ip_data = ip_data,
            username=USERNAME
        )

# # MANAGE_NEW VIEW: currently not in use, was an old redirect function
# @app.route('/manage_new')
# def manage_new():
#     ip_data = DEPLOYER.ReturnIP()

#     return render_template(
#             'manage.html', 
#             deploy_name=DEPLOYER.deploy_name,
#             course_name=DEPLOYER.course_name, 
#             resource_group=DEPLOYER.resource_group,
#             location='East US',
#             deploy_state=DEPLOY_STATE, 
#             ip_data = ip_data,
#             username=USERNAME
#     )

# DEALLOCATE VM VIEW: upon clicking on the 'Stop vLab' button, runs the Manager.DeallocateVM() function
@app.route('/DeallocateVM')
def DeallocateVM():

    # Initialize the Manager class 
    global MANAGER 
    MANAGER = Manager(config.SUBSCRIPTION_ID, RESOURCE_GROUP, CREDENTIALS, COURSE_NAME)

    # Run the deallocation function
    deallocate_vm = MANAGER.DeallocateVM()

    return flask.redirect('/')

# START VM VIEW: upon clicking on the 'Start vLab' button, runs the Manager.StartVM() function
@app.route('/StartVM')
def StartVM():
    # Initialize the Manager class 
    global MANAGER 
    MANAGER = Manager(config.SUBSCRIPTION_ID, RESOURCE_GROUP, CREDENTIALS, COURSE_NAME)

    # Run the start VM function 
    start_vm = MANAGER.StartVM()

    return flask.redirect('/')

# DELETE COURSE VIEW: upon clicking on the 'Delete Course' button, runs the Manager.DeleteCourse() function
@app.route('/DeleteCourse')
def DeleteCourse():
    Deployer.DeleteResources()
    return flask.redirect('/')

# CONTACT VIEW: renders the contact page
@app.route('/contact')
def contact():
    check_username(USERNAME)

    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact Us',
        year=datetime.now().year,
        message='Your contact page.',
        username=USERNAME
    )

# ABOUT VIEW: renders the documentation page 
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

# PROFILE VIEW: renders the user's profile page 
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

# LOGOUT VIEW: renders the logout page 
@app.route('/logout')
def logout():
    return 'Works'

def check_username(username):
    if USERNAME is None:
        return flask.redirect('/')
    