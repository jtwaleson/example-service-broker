from flask import Flask
from openbrokerapi import service_broker
from openbrokerapi.api import (
    ProvisionedServiceSpec,
    UpdateServiceSpec,
    Binding,
    DeprovisionServiceSpec,
    LastOperation,
    BrokerCredentials,
    get_blueprint,
)
from openbrokerapi.log_util import log_util


class Service(service_broker.Service):
    def has_instance_id(self, instance_id):
        raise NotImplementedError

    def provision(self, instance_id, service_details, async_allowed):
        raise NotImplementedError
        # return ProvisionedServiceSpec()
        # :raises ErrInstanceAlreadyExists: If instance already exists
        # :raises ErrAsyncRequired: If async is required but not supported

    def bind(self, instance_id, binding_id, details):
        raise NotImplementedError
        # return Binding()
        # :raises ErrBindingAlreadyExists: If binding already exists
        # :raises ErrAppGuidNotProvided: If AppGuid is required but not provided

    def update(self, instance_id, details, async_allowed):
        raise NotImplementedError
        # return UpdateServiceSpec()
        # :raises ErrAsyncRequired: If async is required but not supported

    def unbind(self, instance_id, binding_id, details):
        raise NotImplementedError
        # :raises ErrBindingAlreadyExists: If binding already exists

    def deprovision(self, instance_id, details, async_allowed):
        raise NotImplementedError
        # return DeprovisionServiceSpec()
        # :raises ErrInstanceDoesNotExist: If instance does not exists
        # :raises ErrAsyncRequired: If async is required but not supported

    def last_operation(self, instance_id, operation_data):
        raise NotImplementedError
        # return LastOperation()


class ServiceBrokerRouter(service_broker.ServiceBroker):
    def __init__(self):
        super.__init__()
        self.services = []

    def register_service(self, service):
        if not isinstance(service, Service):
            raise Exception('service should be of class Service')
        if len(self.services) > 0:
            raise NotImplementedError(
                'support for multiple services is not yet there '
                'as it requires looking up service instance -> service lookups'
            )
        self.services.append(service)

    def _get_owning_service(self, instance_id):
        for service in self.services:
            if service.has_instance_id(instance_id):
                return service
        raise Exception('no owning service found for this instance')

    def _get_service_by_id(self, service_id):
        for service in self.services:
            if service.id == service_id:
                return service
        raise Exception('service not found')

    def catalog(self):
        return self.services

    def provision(self, instance_id, service_details, async_allowed):
        service = self._get_service_by_id(service_details.service_id)
        return service.provision(instance_id, service_details, async_allowed)

    def bind(self, instance_id, binding_id, details):
        service = self._get_owning_service(instance_id)
        return service.bind(instance_id, binding_id, details)

    def update(self, instance_id, details, async_allowed):
        service = self._get_owning_service(instance_id)
        return service.update(instance_id, details, async_allowed)

    def unbind(self, instance_id, binding_id, details):
        service = self._get_owning_service(instance_id)
        service.unbind(instance_id, binding_id, details)

    def deprovision(self, instance_id, details, async_allowed):
        service = self._get_owning_service(instance_id)
        return service.deprovision(instance_id, details, async_allowed)

    def last_operation(self, instance_id, operation_data):
        service = self._get_owning_service(instance_id)
        return service.last_operation(instance_id, operation_data)


def bootstrap(router, credentials, app=None):
    logger = log_util.basic_config()
    if app is None:
        app = Flask(__name__)
    app.register_blueprint(
        get_blueprint(
            router,
            BrokerCredentials(credentials),
            logger,
        )
    )
    return app
