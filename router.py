from flask import Flask
from openbrokerapi import service_broker
from openbrokerapi.api import (
    BrokerCredentials,
    get_blueprint,
)
from openbrokerapi.log_util import basic_config


class Service(service_broker.Service):
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


def _add_service_id(response, service_id):
    if response.is_async:
        if response.operation is None:
            response.operation = service_id
        else:
            response.operation = ' '.join((service_id, response.operation))


class ServiceBrokerRouter(service_broker.ServiceBroker):
    def __init__(self):
        super().__init__()
        self.services = []

    def register_service(self, service):
        if not isinstance(service, Service):
            raise Exception('service should be of class Service')
        self.services.append(service)

    def _get_service_by_id(self, service_id):
        for service in self.services:
            if service.id == service_id:
                return service
        raise Exception('service not found')

    def catalog(self):
        return self.services

    def provision(self, instance_id, details, async_allowed):
        service = self._get_service_by_id(details.service_id)
        response = service.provision(instance_id, details, async_allowed)
        _add_service_id(response, details.service_id)
        return response

    def bind(self, instance_id, binding_id, details):
        service = self._get_service_by_id(details.service_id)
        return service.bind(instance_id, binding_id, details)

    def update(self, instance_id, details, async_allowed):
        service = self._get_service_by_id(details.service_id)
        response = service.update(instance_id, details, async_allowed)
        _add_service_id(response, details.service_id)
        return response

    def unbind(self, instance_id, binding_id, details):
        service = self._get_service_by_id(details.service_id)
        service.unbind(instance_id, binding_id, details)

    def deprovision(self, instance_id, details, async_allowed):
        service = self._get_service_by_id(details.service_id)
        response = service.deprovision(instance_id, details, async_allowed)
        _add_service_id(response, details.service_id)
        return response

    def last_operation(self, instance_id, operation_data):
        data = operation_data.split(' ', maxsplit=1)
        service_id = data[0]
        if len(data) == 2:
            operation_data = data[1]
        else:
            operation_data = None
        service = self._get_service_by_id(service_id)
        return service.last_operation(instance_id, operation_data)


def bootstrap(router, credentials, app=None):
    logger = basic_config()
    if app is None:
        app = Flask(__name__)
    app.register_blueprint(
        get_blueprint(
            router,
            BrokerCredentials(*credentials),
            logger,
        )
    )
    return app
