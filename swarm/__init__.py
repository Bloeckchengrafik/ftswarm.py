import asyncio
from swarm.swarm import *

from .serialhandler import SerialHandler


class FtSwarm(FtSwarmBase):
    def __init__(self, port: str, serial_handler_class=SerialHandler):
        super().__init__()
        self.logger = logging.getLogger("swarm")
        self.serial_handler = serial_handler_class(port, self.logger)
        self.serial_handler.try_reboot()
        self.objects = {}

        asyncio.create_task(self.input_loop())

    async def send(self, port_name: str, command: str, *args: str | int | float) -> int | str | None:
        cmd = self._build_command(port_name, command, args)
        result = await self.serial_handler.send_and_wait(cmd, command != "subscribe")

        if result is None:
            return None

        try:
            return int(result)
        except ValueError:
            return result

    async def queue_use(self):
        message = await self.serial_handler.get_message()  # With caching
        if message is None:
            return

        if not message.startswith("S: "):
            self.logger.warning("Unexpected message: " + message)
            return

        message = message[3:]
        port_name, value = message.split(" ", 1)
        if port_name not in self.objects:
            self.logger.warning("Received message for unknown port: " + message)
            return

        port = self.objects[port_name]
        await port.set_value(value)

    async def input_loop(self):
        while True:
            await self.queue_use()
            await asyncio.sleep(0.2)

    @staticmethod
    def _stringify_param(param):
        if hasattr(param, "value"):
            return str(param.value)
        return str(param)

    def _build_command(self, port_name, command, params):
        return f"{port_name}.{command}({','.join(map(self._stringify_param, params))})"

    async def _get_object(self, port_name: str, clazz: type, *args):
        if port_name in self.objects:
            return self.objects[port_name]

        obj = clazz(self, port_name, *args)
        await obj.post_init()
        self.objects[port_name] = obj
        return obj

    async def get_digital_input(self, port_name: str) -> FtSwarmDigitalInput:
        return await self._get_object(port_name, FtSwarmDigitalInput)

    async def get_switch(self, port_name: str) -> FtSwarmSwitch:
        return await self._get_object(port_name, FtSwarmSwitch)

    async def get_reed_switch(self, port_name: str) -> FtSwarmReedSwitch:
        return await self._get_object(port_name, FtSwarmReedSwitch)

    async def get_light_barrier(self, port_name: str) -> FtSwarmLightBarrier:
        return await self._get_object(port_name, FtSwarmLightBarrier)

    async def get_button(self, port_name: str) -> FtSwarmButton:
        return await self._get_object(port_name, FtSwarmButton)

    async def get_analog_input(self, port_name: str) -> FtSwarmAnalogInput:
        return await self._get_object(port_name, FtSwarmAnalogInput)

    async def get_voltmeter(self, port_name: str) -> FtSwarmVoltmeter:
        return await self._get_object(port_name, FtSwarmVoltmeter)

    async def get_ohmmeter(self, port_name: str) -> FtSwarmOhmmeter:
        return await self._get_object(port_name, FtSwarmOhmmeter)

    async def get_thermometer(self, port_name: str) -> FtSwarmThermometer:
        return await self._get_object(port_name, FtSwarmThermometer)

    async def get_ldr(self, port_name: str) -> FtSwarmLDR:
        return await self._get_object(port_name, FtSwarmLDR)

    async def get_motor(self, port_name: str, high_precision: bool = False) -> FtSwarmMotor:
        return await self._get_object(port_name, FtSwarmMotor, high_precision)

    async def get_tractor_motor(self, port_name: str, high_precision: bool = False) -> FtSwarmTractorMotor:
        return await self._get_object(port_name, FtSwarmTractorMotor, high_precision)

    async def get_xm_motor(self, port_name: str, high_precision: bool = False) -> FtSwarmXMMotor:
        return await self._get_object(port_name, FtSwarmXMMotor, high_precision)

    async def get_encoder_motor(self, port_name: str, high_precision: bool = False) -> FtSwarmEncoderMotor:
        return await self._get_object(port_name, FtSwarmEncoderMotor, high_precision)

    async def get_lamp(self, port_name: str, high_precision: bool = False) -> FtSwarmLamp:
        return await self._get_object(port_name, FtSwarmLamp, high_precision)

    async def get_valve(self, port_name: str) -> FtSwarmValve:
        return await self._get_object(port_name, FtSwarmValve)

    async def get_buzzer(self, port_name: str) -> FtSwarmBuzzer:
        return await self._get_object(port_name, FtSwarmBuzzer)

    async def get_servo(self, port_name: str) -> FtSwarmServo:
        return await self._get_object(port_name, FtSwarmServo)

    async def get_joystick(self, port_name: str) -> FtSwarmJoystick:
        return await self._get_object(port_name, FtSwarmJoystick)

    async def get_pixel(self, port_name: str) -> FtSwarmPixel:
        return await self._get_object(port_name, FtSwarmPixel)

    async def get_i2c(self, port_name: str) -> FtSwarmI2C:
        return await self._get_object(port_name, FtSwarmI2C)
