import asyncio
from logging import Logger
from asyncio.locks import Lock
import serial


class SerialHandler:
    def __init__(self, port: str, logger: Logger):
        self.logger = logger
        self.ser = serial.Serial(port, 115200, timeout=5)
        # self.ser.set_buffer_size(rx_size=1024, tx_size=1024)
        self.lock = Lock()
        self.message_queue = asyncio.Queue()

    def try_reboot(self):
        self.ser.write(b"startCLI\r\n")
        while self.ser.in_waiting <= 0:
            pass

        self.logger.info("Message from the ftSwarm")
        while True:
            message = self.ser.read_until(serial.LF)
            # noinspection PyBroadException
            try:
                self.logger.info("- " + message.decode("UTF-8").removesuffix("\n".removesuffix("\r")))
                if "@@@ ftSwarmOS CLI started" in message.decode("UTF-8").removesuffix("\n").removesuffix("\r"):
                    break
            except:
                pass

        self.ser.read_all()

    async def send_and_wait(self, cmd: str, wait_for_return=True):
        async with self.lock:
            return await self._send_and_wait(cmd, wait_for_return)

    async def _send_and_wait(self, cmd: str, wait_for_return):
        if not self.ser.is_open:
            raise serial.SerialException("Serial port is not open")

        self.logger.debug("Swarm <- " + cmd)
        self.ser.write(cmd.encode("UTF-8") + b"\r\n")

        if not wait_for_return:
            return

        while True:
            message = await self._get_message(queue=False)  # Queueing is only for building the cli backlog
            if message is None:
                await asyncio.sleep(0.01)
                continue

            if message.startswith("R: "):
                return message[3:]
            else:
                self.message_queue.put_nowait(message)

    async def get_message(self) -> str | None:
        async with self.lock:
            return await self._get_message()

    async def _get_message(self, queue=True) -> str | None:
        if not self.ser.is_open:
            raise serial.SerialException("Serial port is not open")

        if self.message_queue.qsize() > 0 and queue:
            return self.message_queue.get_nowait()  # Prioritize queue

        if self.ser.in_waiting <= 0:
            return

        # Get message
        rest = self.ser.read_until(serial.LF)
        message = rest.removesuffix(b"\n").removesuffix(b"\r").decode("UTF-8")
        self.logger.debug("Swarm -> " + message)

        return message

    def close(self):
        self.ser.close()
