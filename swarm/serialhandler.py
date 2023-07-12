from logging import Logger

import serial


class SerialHandler:
    def __init__(self, port: str, logger: Logger):
        self.logger = logger
        self.ser = serial.Serial(port, 115200, timeout=5)
        self.ser.set_buffer_size(rx_size=1024, tx_size=1024)

    def try_reboot(self):
        self.ser.write(b"reload\r\n")
        while self.ser.in_waiting <= 0:
            pass

        self.logger.info("Message from the ftSwarm")
        while True:
            message = self.ser.read_until(serial.LF)
            # noinspection PyBroadException
            try:
                self.logger.debug("- " + message.decode("UTF-8").removesuffix("\r\n"))
                if "@@@ ftSwarmOS CLI started" in message.decode("UTF-8").removesuffix("\r\n"):
                    break
            except:
                pass

        self.ser.read_all()
