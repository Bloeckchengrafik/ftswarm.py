import logging
import asyncio

from .serialhandler import SerialHandler


class FtSwarm:
    def __init__(self, port: str, serial_handler_class=SerialHandler):
        self.logger = logging.getLogger(__name__)
        self.serial_handler = serial_handler_class(port, self.logger)
        self.serial_handler.try_reboot()
