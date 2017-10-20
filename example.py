from router import Service
from openbrokerapi import ServiceMetadata, ServicePlan


def gen_uuid(key):
    # consistently hash the key to a guid
    # users don't have to come up with a guid for all services and plans
    raise NotImplementedError


class ExampleService(Service):
    def __init__(self):
        plans = []
        plans.append(
            ServicePlan(
                 id=gen_uuid('my-unique-plan-sized-m-v0.1'),
                 name='m',
                 description='a medium sized cat, default color: black',
                 metadata=None,
                 free=False,
                 bindable=True,
            ),
            ServicePlan(
                 id=gen_uuid('my-unique-plan-sized-s-v0.1'),
                 name='s',
                 description='a small sized cat, default color: black',
                 metadata=None,
                 free=False,
                 bindable=True,
            ),
        )

        super.__init__(
            id=gen_uuid('my-very-unique-service'),
            name='exmple-service',
            description='Example Service does nothing',
            bindable=True,
            plans=plans,
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
        raise NotImplementedError
        # return ProvisionedServiceSpec()

    def bind(self, instance_id, binding_id, details):
        raise NotImplementedError
        # return Binding()

    def update(self, instance_id, details, async_allowed):
        raise NotImplementedError
        # return UpdateServiceSpec()

    def unbind(self, instance_id, binding_id, details):
        raise NotImplementedError

    def deprovision(self, instance_id, details, async_allowed):
        raise NotImplementedError
        # return DeprovisionServiceSpec()

    def last_operation(self, instance_id, operation_data):
        raise NotImplementedError
