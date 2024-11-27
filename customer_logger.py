# custom_logger.py

from gunicorn.glogging import Logger
import logging

class CustomLogger(Logger):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.logger = logging.getLogger('gunicorn.access')
        formatter = logging.Formatter('[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S %z')
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        self.logger.setLevel(logging.INFO)

    def access(self, log_line):
        # Filter out access log entries for health checks
        if "GET /health" in log_line:
            return  # Don't log health checks
        super().access(log_line)  # Log other requests

