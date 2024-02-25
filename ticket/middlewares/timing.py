import time
import logging
from enum import Enum
from starlette.middleware.base import BaseHTTPMiddleware

_logger = logging.getLogger(__name__)
class LogType(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

class TimingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, log_type: LogType = LogType.INFO):
        super().__init__(app)
        self.log_type = log_type

    async def dispatch(self, request, call_next):
        now_time = time.time()
        response = await call_next(request)
        mesg = f"Response time : [{time.time() - now_time}] ms"
        match self.log_type:
            case LogType.DEBUG:
                _logger.debug(mesg)
            case LogType.INFO:
                _logger.info(mesg)
            case LogType.WARNING:
                _logger.warning(mesg)
            case LogType.ERROR:
                _logger.error(mesg)
        return response
