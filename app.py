#!/usr/bin/env python3
import os
from router import bootstrap, ServiceBrokerRouter

from example import ExampleService

router = ServiceBrokerRouter()

router.register_service(ExampleService())

app = bootstrap(
    router,
    (os.environ['BROKER_USER'], os.environ['BROKER_PASSWORD']),
)
