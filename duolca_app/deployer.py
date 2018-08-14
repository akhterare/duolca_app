"""A deployer class to deploy a template on Azure"""
import os.path
from duolca_app import config
import json
from haikunator import Haikunator
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient 
from azure.mgmt.resource.resources.models import DeploymentMode, DeploymentProperties, TemplateLink, ParametersLink 
from msrestazure.azure_active_directory import AdalAuthentication
import flask

class Deployer(object):
    """ Initialize the deployer class with subscription, resource group and public key.
    :raises IOError: If the public key path cannot be read (access or not exists)
    :raises KeyError: If AZURE_CLIENT_ID, AZURE_CLIENT_SECRET or AZURE_TENANT_ID env
        variables or not defined
    """
    name_generator = Haikunator()

# INITALIZE THE CLASS WITH THE USER INPUTS
    def __init__(self, subscription_id, resource_group, credentials, course_name, public_ip, deploy_name):
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.course_name = course_name
        self.credentials = credentials
        self.client = ResourceManagementClient(self.credentials, self.subscription_id)
        self.public_ip = public_ip
        self.deploy_name = deploy_name

# CHECK WHETHER OR NOT A DEPLOYMENT EXISTS
    def check_deployment(self):
        deployed = self.client.deployments.check_existence(
            self.resource_group,
            self.deploy_name
        ) 
        return deployed

# DEPLOY THE VIRTUAL MACHINE ACCORDING TO VALUES YOU SET FOR YOURSELF WHEN YOU CALLED THE CLASS
    def deploy(self):
        template_path = os.path.join(os.path.dirname(__file__), 'templates', self.course_name + '.json')
        with open(template_path, 'r') as template_file_fd:
            template = json.load(template_file_fd)

        parameters = {
            'vmName': self.course_name,
        }
        parameters = {k: {'value': v} for k, v in parameters.items()}

        deployment_prop = DeploymentProperties(
            mode='Complete',
            template=template,
            parameters=parameters
        )

        deployment_async_operation = self.client.deployments.create_or_update(
            self.resource_group,
            self.deploy_name,
            deployment_prop
        )

        # result = deployment_async_operation.result()
        deployment_async_operation.wait()

# COLLECT INFORMATION ABOUT THE DEPLOYMENT 
    def ReturnIP(self):
        created_public_ip = self.client.resources.get_by_id(
            self.public_ip,
            '2018-07-01'
        )
        return created_public_ip.properties['ipAddress']

# DELETE ALL RESOURCES IN THE DEPLOYMENT
    def DeleteResources(self):
        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'clearResources.json')
        with open(template_path, 'r') as template_file_fd:
            template = json.load(template_file_fd)

        parameters = {}
        # parameters = {k: {'value': v} for k, v in parameters.items()}

        deployment_prop = DeploymentProperties(
            mode='Complete',
            template=template,
            parameters=parameters
        )

        deployment_async_operation = self.client.deployments.create_or_update(
            self.resource_group,
            self.deploy_name + 'DeleteResources',
            deployment_prop
        )

        # result = deployment_async_operation.result()
        deployment_async_operation.wait()

        # resource_list=[]
        # for item in client.resource_groups.list_resources(GROUP_NAME):
        #     resource_list.append(item)
        # return resource_list
    