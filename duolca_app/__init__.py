"""
The flask application package.
"""

import adal 
import duolca_app.config 
import uuid 
import requests
import flask
from flask import Flask
from os import environ
# from applicationinsights.requests import WSGIApplication
app = Flask(__name__)
# app.wsgi_app = WSGIApplication(environ.get('APPINSIGHTS_INSTRUMENTATIONKEY'), app.wsgi_app)
app.config.from_pyfile('config.py')

from . import db
db.init_app(app)

import duolca_app.views



