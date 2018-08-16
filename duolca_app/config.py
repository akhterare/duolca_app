########################################################################################################
# DUOLCA 1.0.0 
# CONFIG.PY Variables File
#
# CONFIG.PY is a storage file that contains the variable needed by Duolca to run
# The developer will have to intialize certain variables themselves when their app is created
#
# August 17th, 2018 \\ Areena Akhter
########################################################################################################
 

AUTH_RESOURCE = "https://graph.microsoft.com"  # Add the resource you want the access token for
MANAGE_RESOURCE = "https://management.azure.com"
TENANT = "nokia.onmicrosoft.com"  # Enter tenant name, e.g. contoso.onmicrosoft.com
AUTHORITY_HOST_URL = "https://login.microsoftonline.com"
API_VERSION = 'v1.0'

# TO BE CHANGED BY THE USER UPON APP REGISTRATION
CLIENT_ID = "fb20d6fe-ce09-449a-b096-90f229943863"  # copy the Application ID of your app from your Azure portal
CLIENT_SECRET = "9bPMwvy7HztrwVkkCR08BOPMbPUb5Ze8MqMVZOwGTMQ="  # copy the value of key you generated when setting up the application

# TO BE ENTERED BY USER UPON APP CREATION
SUBSCRIPTION_ID = '66e8f030-dbe5-4677-bd29-06b963faa0ac'