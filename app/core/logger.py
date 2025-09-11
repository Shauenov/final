import logging
import logging_loki
from app.core.config import settings
from multiprocessing import Queue

logger = logging.getLogger()

if settings.LOKI_URL and settings.ENVIRONMENT != "local":
  handler = logging_loki.LokiQueueHandler(
    queue=Queue(-1),
    url=settings.LOKI_URL,
    tags={"application": "juie-app"},
    version="1",
  )
  logger.addHandler(handler)