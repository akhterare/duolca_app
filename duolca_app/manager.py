"""A deployer class to deploy a template on Azure"""
import os.path
from duolca_app import config
import json
from haikunator import Haikunator
from azure.mgmt.resource import ResourceManagementClient 
from azure.mgmt.resource.resources.models import DeploymentMode, DeploymentProperties, TemplateLink, ParametersLink 
from msrestazure.azure_active_directory import AdalAuthentication
from azure.mgmt.compute import ComputeManagementClient
import flask

class Manager(object):
    name_generator = Haikunator()

# INITALIZE THE CLASS WITH THE USER INPUTS
    def __init__(self, subscription_id, resource_group, credentials, course_name):
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.vm_name = course_name
        self.credentials = credentials

        self.client = ComputeManagementClient(credentials, subscription_id)

    def DeallocateVM(self):
        deallocate_async_operation = self.client.virtual_machines.deallocate(self.resource_group, self.vm_name)
        # deallocate_async_operation.wait()

    def StartVM(self):
        start_async_operation = self.client.virtual_machines.start(self.resource_group, self.vm_name)
        # start_async_operation.wait()
    


