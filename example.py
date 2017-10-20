import uuid
from router import Service
from openbrokerapi.catalog import ServiceMetadata, ServicePlan
import logging
from openbrokerapi.api import (
    ProvisionedServiceSpec,
    OperationState,
    LastOperation,
    DeprovisionServiceSpec,
    Binding,
    UpdateServiceSpec,
)


def gen_uuid(key):
    # consistently hash the key to a guid
    # users don't have to come up with a guid for all services and plans
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, key))


plans = {
    'm': ServicePlan(
        id=gen_uuid('my-unique-plan-sized-m-v0.1'),
        name='m',
        description='a medium sized cat, default color: black',
        metadata=None,
        free=False,
        bindable=True,
    ),
    's': ServicePlan(
        id=gen_uuid('my-unique-plan-sized-s-v0.1'),
        name='s',
        description='a small sized cat, default color: black',
        metadata=None,
        free=False,
        bindable=True,
    ),
}


def get_plan_by_id(plan_id):
    for key, plan in plans.items():
        if plan.id == plan_id:
            return key, plan
    raise KeyError('plan {} not found'.format(plan_id))


class ExampleService(Service):
    def __init__(self):
        super().__init__(
            id=gen_uuid('my-very-unique-service'),
            name='example-service',
            description='Example Service does nothing',
            bindable=True,
            plans=plans.keys(),
            tags=['example', 'service'],
            requires=None,
            metadata=ServiceMetadata(
                displayName='Example Service',
                imageUrl=None,
                longDescription=None,
                providerDisplayName=None,
                documentationUrl=None,
                supportUrl=None,
            ),
            dashboard_client=None,
            plan_updateable=True,
        )

    def has_instance_id(self, instance_id):
        return True  # for now the ServiceBrokerRouter only supports one service

    def provision(self, instance_id, service_details, async_allowed):
        if service_details.parameters is None:
            service_details.parameters = {}
        key, plan = get_plan_by_id(service_details.plan_id)
        if key == 'm' and 'hello' not in service_details.parameters:
            raise Exception('parameter "hello" is required for plan "m"')
        logging.info(
            'creating plan: {} - {} - {}'.format(
                key,
                str(plan),
                str(service_details.parameters)
            )
        )
        return ProvisionedServiceSpec(
            is_async=True, dashboard_url=None, operation='create',
        )
        # :raises ErrInstanceAlreadyExists: If instance already exists
        # :raises ErrAsyncRequired: If async is required but not supported
        # raise NotImplementedError('sorry, not yet implemented')

    def bind(self, instance_id, binding_id, details):
        if details.parameters is None:
            details.parameters = {}

        key, plan = get_plan_by_id(details.plan_id)
        logging.info('binding plan: {} - {}'.format(key, str(plan)))

        if key == 'm' and 'hello' not in details.parameters:
            raise Exception('parameter "hello" is required to blind plan "m"')

        return Binding(
            credentials={
                'plan': key,
                'plan_name': plan.name,
                'plan_description': plan.description,
                'parameters': str(details.parameters),
            },
        )
        # :raises ErrBindingAlreadyExists: If binding already exists
        # :raises ErrAppGuidNotProvided: If AppGuid is required but not provided
        # return Binding()

    def update(self, instance_id, details, async_allowed):
        raise NotImplementedError
        # cases:
        # - can not update: plan incompatible
        # - can not update: backed returned error
        # - no params: send current status and supported methods??
        # - success
        # :raises ErrAsyncRequired: If async is required but not supported
        return UpdateServiceSpec(is_async=True, operation='update')

    def unbind(self, instance_id, binding_id, details):
        pass

    def deprovision(self, instance_id, details, async_allowed):
        if True:  # async
            return DeprovisionServiceSpec(is_async=True, operation='delete')
        else:
            return DeprovisionServiceSpec(is_async=False)

    def last_operation(self, instance_id, operation_data):
        if operation_data == 'create':
            # check if creation was successful
            return LastOperation(OperationState.SUCCEEDED, 'created')
        elif operation_data == 'delete':
            # check if deletion was successful
            return LastOperation(OperationState.SUCCEEDED, 'deleted')
        elif operation_data == 'update':
            # check if deletion was successful
            return LastOperation(OperationState.SUCCEEDED, 'updated')
        else:
            return LastOperation(OperationState.FAILED, 'failed, no valid operation id found')
