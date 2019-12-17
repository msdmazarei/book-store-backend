from raven.base import Raven
from sentry_sdk import init, capture_message, capture_exception
from sentry_sdk.integrations.bottle import BottleIntegration

import logging
from sentry_sdk.integrations.logging import LoggingIntegration

# All of this is already happening by default!
sentry_logging = LoggingIntegration(
    level=logging.INFO,        # Capture info and above as breadcrumbs
    event_level=logging.ERROR  # Send errors as events
)


sentry_client = init(dsn='http://501e3ca35149498f803316b86a05bbe6@sentry.mazarei.id.ir/2',
    integrations=[BottleIntegration(),sentry_logging])





capture_message("Hello World")  # Will create an event.

capture_exception(Exception("This is an example of an error message."))