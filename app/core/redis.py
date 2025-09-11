import redis
from app.core.logger import logger
from app.core.config import settings

r = redis.Redis(
  host=settings.REDIS_HOST,
  port=settings.REDIS_PORT,
  password=settings.REDIS_PASSWORD,
)

try:
    response = r.ping()
    if response:
        logger.info("Successfully connected to redis")
    else:
        logger.info("Connecting to Redis failure")
except Exception as e:
    logger.error(f"Произошла ошибка: {e}")