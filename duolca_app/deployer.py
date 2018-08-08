"""A deployer class to deploy a template on Azure"""
import os.path
from duolca_app import config
import json
from haikunator import Haikunator
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import DeploymentMode
from msrestazure.azure_active_directory import AdalAuthentication
import flask

class Deployer(object):
    """ Initialize the deployer class with subscription, resource group and public key.
    :raises IOError: If the public key path cannot be read (access or not exists)
    :raises KeyError: If AZURE_CLIENT_ID, AZURE_CLIENT_SECRET or AZURE_TENANT_ID env
        variables or not defined
    """
    name_generator = Haikunator()

# INITALIZE THE CLASS WITH THE SUBSCRIPTION ID AND RESOURCE GROUP INPUTTED
    def __init__(self, subscription_id, resource_group):
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.dns_label_prefix = self.name_generator.haikunate()

        # pub_ssh_key_path = os.path.expanduser(pub_ssh_key_path)
        # # Will raise if file not exists or not enough permission
        # with open(pub_ssh_key_path, 'r') as pub_ssh_file_fd:
        #     self.pub_ssh_key = pub_ssh_file_fd.read()

        # self.credentials = AdalAuthentication(
        #     flask.session['access_token'],
        #     config.MANAGE_RESOURCE,
        #     config.CLIENT_ID,
        #     config.CLIENT_SECRET
        # )
        self.credentials = views.CREDENTIALS
        self.client = ResourceManagementClient(self.credentials, self.subscription_id)

    def deploy(self):
    # Deploy your template to your desired resource group 

        self.client.resource_groups.create_or_update(
            self.resource_group,
            {
                'location':'westeurope'
            }
        )

        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'template.json')
        with open(template_path, 'r') as template_file_fd:
            template = json.load(template_file_fd)

        parameters = {
            # 'sshKeyData': self.pub_ssh_key,
            'vmName': 'test-vm',
            'dnsLabelPrefix': self.dns_label_prefix
        }
        parameters = {k: {'value': v} for k, v in parameters.items()}

        deployment_properties = {
            'mode': DeploymentMode.incremental,
            'template': template,
            'parameters': parameters
        }

        deployment_async_operation = self.client.deployments.create_or_update(
            self.resource_group,
            'test-vm',
            deployment_properties
        )
        deployment_async_operation.wait()
