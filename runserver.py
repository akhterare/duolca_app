"""
This script runs the python_webapp_flask application using a development server.
"""

from os import environ
from duolca_app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0')
