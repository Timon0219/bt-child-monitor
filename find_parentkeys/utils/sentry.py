import sentry_sdk
import logging
from sentry_sdk.integrations.logging import LoggingIntegration

def init_sentry(sentry_dsn):
    """Initialize Sentry for error tracking."""
    sentry_logging = LoggingIntegration(
    level=logging.INFO,        # Capture info and above as breadcrumbs
    event_level=logging.ERROR  # Send errors as events
    )

    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            traces_sample_rate=1.0,
            integrations=[sentry_logging]
        )
        logging.info("Sentry initialized successfully.")
    else:
        logging.warning("SENTRY_DSN not found. Sentry initialization skipped.")
