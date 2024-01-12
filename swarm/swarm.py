import logging
from enum import IntEnum


class Sensor(IntEnum):
    """All Sensor types known by the ftSwarm"""
    UNDEFINED = -1
    DIGITAL = 0
    ANALOG = 1
    SWITCH = 2
    REEDSWITCH = 3
    LIGHTBARRIER = 4
    VOLTMETER = 5
    OHMMETER = 6
    THERMOMETER = 7
    LDR = 8
    TRAILSENSOR = 9
    COLORSENSOR = 10
    ULTRASONIC = 11
    BUTTON = 12


class Actor(IntEnum):
    """All Actor types known by the ftSwarm"""
    UNDEFINDED = -1
    XMOTOR = 0
    XMMOTOR = 1
    TRACTOR = 2
    ENCODER = 3
    LAMP = 4
    VALVE = 5
    COMPRESSOR = 6
    BUZZER = 7


class MotionType(IntEnum):
    """How to move a motor"""
    COAST = 0
    BRAKE = 1
    ON = 2


class Toggle(IntEnum):
    """Toggle states"""
    NOTOGGLE = 0
    TOGGLEUP = 1
    TOGGLEDOWN = 2


class Align(IntEnum):
    """Text alignment for display"""
    ALIGNLEFT = 0
    ALIGNCENTER = 1
    ALIGNRIGHT = 2


class Trigger(IntEnum):
    """Trigger events"""
    TRIGGERUP = 0
    TRIGGERDOWN = 1
    TRIGGERVALUE = 2
    TRIGGERI2CREAD = 3
    TRIGGERI2CWRITE = 4


class FtSwarmBase:
    """Base class for all ftSwarm implementations"""

    def __init__(self) -> None:
        self.logger = logging.getLogger("swarm-base")

    async def send(self, port_name: str, command: str, *args: str | int | float) -> int | str | None:
        pass


class FtSwarmIO:
    """
    Base class for all ftSwarm interfaces

    Don't use this class at all
    """

    def __init__(self, swarm: FtSwarmBase, port_name: str) -> None:
        self._port_name = port_name
        self._swarm = swarm

    async def post_init(self) -> None:
        pass

    async def get_port_name(self) -> str:
        return self._port_name

    async def set_value(self, value: str) -> None:
        self._swarm.logger.warning(f"Received unexpected write to {self._port_name}: {value}")


class FtSwarmActorShim(FtSwarmIO):
    """
    Shim class for all ftSwarm actors for type annotations

    Don't use this class at all
    """

    def get_port_name(self) -> str:
        pass


class FtSwarmInput(FtSwarmIO):
    """
    Base class for all ftSwarm inputs

    Don't use this class at all
    """

    def __init__(self, swarm: FtSwarmBase, name: str, normally_open: bool = True, hysteresis: float = 0):
        super().__init__(swarm, name)
        self._normallyOpen = normally_open
        self._value = 0
        self._hysteresis = hysteresis

    async def post_init(self) -> None:
        await self._swarm.send(self._port_name, "setSensorType", await self.get_sensor_type(), self._normallyOpen)
        await self._swarm.send(self._port_name, "subscribe", self._hysteresis)
        self._value = await self._swarm.send(self._port_name, "getValue")

    async def get_sensor_type(self) -> Sensor:
        return Sensor.UNDEFINED

    async def on_trigger(self, trigger_event: Trigger, actor: FtSwarmActorShim, value: int | None = None) -> None:
        # The last parameter is optional, so we need to check if it is None
        await self._swarm.send(self._port_name, "onTrigger", trigger_event, actor.get_port_name(), *([value] or []))

    async def set_value(self, str_value: str) -> None:
        self._value = int(str_value)


class FtSwarmDigitalInput(FtSwarmInput):
    """
    Digital input

    Maps to ports A1...A4 on all controller types
    """

    def __init__(self, swarm: FtSwarmBase, name: str) -> None:
        super().__init__(swarm, name, True, 0)

    async def get_sensor_type(self) -> Sensor:
        return Sensor.DIGITAL

    async def get_toggle(self) -> Toggle:
        return Toggle(await self._swarm.send(self._port_name, "getToggle"))

    async def get_state(self) -> bool:
        return self._value != 0

    async def is_pressed(self) -> bool:
        return await self.get_state()

    async def is_released(self) -> bool:
        return not (await self.get_state())

    async def has_toggled_up(self) -> bool:
        return (await self.get_toggle()) == Toggle.TOGGLEUP

    async def has_toggled_down(self) -> bool:
        return (await self.get_toggle()) == Toggle.TOGGLEDOWN


class FtSwarmSwitch(FtSwarmDigitalInput):
    """
    Mechanical switch
    Maps to ports A1...A4 on all controller types
    Wiring for fischertechnik switches: 1-3 is normally open, 1-2 is normally closed
    """

    async def get_sensor_type(self) -> Sensor:
        return Sensor.SWITCH


class FtSwarmReedSwitch(FtSwarmDigitalInput):
    """
    Reed switch

    Maps to ports A1...A4 on all controller types
    """

    async def get_sensor_type(self) -> Sensor:
        return Sensor.REEDSWITCH


class FtSwarmLightBarrier(FtSwarmDigitalInput):
    """
    Light barrier

    Maps to ports A1...A4 on all controller types
    """

    async def get_sensor_type(self) -> Sensor:
        return Sensor.LIGHTBARRIER


class FtSwarmButton(FtSwarmDigitalInput):
    """
    Onboard button

    This input is only available on the ftSwarmControl
    """

    async def get_sensor_type(self) -> Sensor:
        return Sensor.BUTTON


class FtSwarmAnalogInput(FtSwarmInput):
    """
    General analog input

    Maps to ports A1...A6 on the ftSwarm specifically
    """

    async def get_sensor_type(self) -> Sensor:
        return Sensor.ANALOG

    async def get_value(self) -> int:
        return self._value


class FtSwarmVoltmeter(FtSwarmAnalogInput):
    """
    Voltmeter

    Maps to port A2 on the ftSwarm specifically
    """

    async def get_sensor_type(self) -> Sensor:
        return Sensor.VOLTMETER

    async def get_voltage(self) -> int:
        return await self._swarm.send(self._port_name, "getVoltage")


class FtSwarmOhmmeter(FtSwarmAnalogInput):
    """
    Ohmmeter

    Maps to ports A1...A6 on the ftSwarm specifically
    """

    async def get_sensor_type(self) -> Sensor:
        return Sensor.OHMMETER

    async def get_resistance(self) -> int:
        return await self._swarm.send(self._port_name, "getResistance")


class FtSwarmThermometer(FtSwarmAnalogInput):
    """
    Thermometer based on 1.5kOhm NTC

    Maps to ports A1...A6 on the ftSwarm specifically
    """

    async def get_sensor_type(self) -> Sensor:
        return Sensor.THERMOMETER

    async def get_celcius(self) -> int:
        return await self._swarm.send(self._port_name, "getCelcius")

    async def get_kelvin(self) -> int:
        return await self._swarm.send(self._port_name, "getKelvin")

    async def get_fahrenheit(self) -> int:
        return await self._swarm.send(self._port_name, "getFahrenheit")


class FtSwarmLDR(FtSwarmAnalogInput):
    """
    LDR

    Maps to ports A1...A6 on the ftSwarm specifically
    At FtSwarmControl you could use a LDR with a FtSwarmDigitalInput as well
    """

    async def get_sensor_type(self) -> Sensor:
        return Sensor.LDR


class FtSwarmActor(FtSwarmIO):
    """
    Base class for all actors

    Don't use this class directly, use one of the derived classes instead
    """

    def __init__(self, swarm: FtSwarmBase, port_name: str, high_precision: bool = False) -> None:
        super().__init__(swarm, port_name)
        self._high_precision = high_precision

    async def post_init(self) -> None:
        await self._swarm.send(self._port_name, "setActorType", await self.get_actor_type(), self._high_precision)

    async def get_actor_type(self) -> Actor:
        return Actor.UNDEFINDED


class FtSwarmMotor(FtSwarmActor):
    """
    General motor class, use this class for (old) gray motors, mini motors, XS motors

    M1..M2 all contollers - keep power budget in mind!
    """

    async def get_actor_type(self) -> Actor:
        return Actor.XMOTOR

    async def set_speed(self, speed) -> None:
        await self._swarm.send(self._port_name, "setSpeed", speed)

    async def get_speed(self) -> int:
        return await self._swarm.send(self._port_name, "getSpeed")


class FtSwarmTractorMotor(FtSwarmMotor):
    """
    Tractor & XM motor

    M1..M2 all contollers - keep power budget in mind!
    """

    async def get_actor_type(self) -> Actor:
        return Actor.TRACTOR

    async def set_motion_type(self, motion_type) -> None:
        """
        Set motion type of motor
        FtSwarmTractor has different options for stopping motor:

        :return: None
        """
        await self._swarm.send(self._port_name, "setMotionType", motion_type)

    async def get_motion_type(self) -> MotionType:
        return MotionType(await self._swarm.send(self._port_name, "getMotionType"))

    async def coast(self) -> None:
        await self.set_motion_type(MotionType.COAST)

    async def brake(self) -> None:
        await self.set_motion_type(MotionType.BRAKE)

    async def run(self) -> None:
        await self.set_motion_type(MotionType.ON)


class FtSwarmXMMotor(FtSwarmTractorMotor):
    """
    XM motor

    M1...M2 all contollers - keep power budget in mind!
    """

    async def get_actor_type(self) -> Actor:
        return Actor.XMMOTOR


# TODO: implement encoder input
class FtSwarmEncoderMotor(FtSwarmTractorMotor):
    """
    Encoder motor

    M1...M2 all contollers - keep power budget in mind!
    """

    async def get_actor_type(self) -> Actor:
        return Actor.ENCODER


class FtSwarmLamp(FtSwarmActor):
    """
    Classic lamp or LED

    M1...M2 all contollers - keep power budget in mind!
    """

    async def get_actor_type(self) -> Actor:
        return Actor.LAMP

    async def on(self, power=255) -> None:
        await self._swarm.send(self._port_name, "setSpeed", power)

    async def off(self) -> None:
        await self._swarm.send(self._port_name, "setSpeed", 0)


class FtSwarmBinaryActor(FtSwarmActor):
    """
    Base class for all binary actors

    Don't use this class directly, use one of the derived classes instead
    """

    async def on(self) -> None:
        await self._swarm.send(self._port_name, "setSpeed", 255)

    async def off(self) -> None:
        await self._swarm.send(self._port_name, "setSpeed", 0)


class FtSwarmValve(FtSwarmBinaryActor):
    """
    Electromagnetic Valve

    M1...M2 all contollers - keep power budget in mind!
    """

    async def get_actor_type(self) -> Actor:
        return Actor.VALVE


class FtSwarmCompressor(FtSwarmBinaryActor):
    """
    Compressor

    M1...M2 all contollers - keep power budget in mind!
    """

    async def get_actor_type(self) -> Actor:
        return Actor.COMPRESSOR


class FtSwarmBuzzer(FtSwarmBinaryActor):
    """
    Buzzer

    M1...M2 all contollers - keep power budget in mind!
    """

    async def get_actor_type(self) -> Actor:
        return Actor.BUZZER


class FtSwarmServo(FtSwarmIO):
    """
    Servo

    ftSwarm only

    A servo has 150mA typically, higher values with load. Keep power budget in mind!
    """

    def __init__(self, swarm, port_name) -> None:
        super().__init__(swarm, port_name)
        self._position = 0
        self._offset = 0

    async def post_init(self) -> None:
        self._offset = self._swarm.send(self._port_name, "getOffset")
        self._position = self._swarm.send(self._port_name, "getPositon")

    async def get_position(self) -> int:
        return self._position

    async def set_position(self, position) -> None:
        self._position = position
        await self._swarm.send(self._port_name, "setPosition", position)

    async def get_offset(self) -> int:
        return self._offset

    async def set_offset(self, offset) -> None:
        self._offset = offset
        await self._swarm.send(self._port_name, "setOffset", offset)


class FtSwarmJoystick(FtSwarmIO):
    """
    Joystick

    ftSwarmControl only
    """

    def __init__(self, swarm, port_name, hysteresis) -> None:
        super().__init__(swarm, port_name)
        self._lr = 0
        self._fb = 0
        self._hysteresis = hysteresis

    async def post_init(self) -> None:
        await self._swarm.send(self._port_name, "subscribe", self._hysteresis)

    async def get_fb(self) -> int:
        return self._fb

    async def get_lr(self) -> int:
        return self._lr

    async def on_trigger_lr(self, trigger_event, actor, p1=None) -> None:
        await self._swarm.send(self._port_name, "onTriggerLR", trigger_event, actor, *(p1 or []))

    async def on_trigger_fb(self, trigger_event, actor, p1=None) -> None:
        await self._swarm.send(self._port_name, "onTriggerFB", trigger_event, actor, *(p1 or []))


class FtSwarmPixel(FtSwarmIO):
    """
    RGB LED

    ftSwarm only
    One LED takes up to 60mA, keep power budget in mind!
    """

    def __init__(self, swarm, port_name) -> None:
        super().__init__(swarm, port_name)
        self._brightness = 0
        self._color = 0

    async def post_init(self) -> None:
        self._brightness = await self._swarm.send(self._port_name, "getBrightness")
        self._color = await self._swarm.send(self._port_name, "getColor")

    async def get_brightness(self) -> int:
        """
        Get the brightness of the LED
        :return:  brightness 0..255
        """
        return self._brightness

    async def set_brightness(self, brightness) -> None:
        self._brightness = brightness
        await self._swarm.send(self._port_name, "setBrightness", brightness)

    async def get_color(self) -> int:
        return self._color

    async def set_color(self, color) -> None:
        # If color is a tuple, reformat it as hex
        if isinstance(color, tuple) or isinstance(color, list):
            color = (color[0] << 16) + (color[1] << 8) + color[2]
        self._color = color
        await self._swarm.send(self._port_name, "setColor", color)


class FtSwarmI2C(FtSwarmIO):
    """
    I2C slave with 4 registers
    """

    def __init__(self, swarm, port_name) -> None:
        super().__init__(swarm, port_name)
        self.__register = [0, 0, 0, 0, 0, 0, 0, 0]

    async def post_init(self) -> None:
        for i in range(8):
            self.__register[i] = await self._swarm.send(self._port_name, "getRegister", i)
        await self._swarm.send(self._port_name, "subscribe")

    async def get_register(self, reg) -> int:
        return self.__register[reg]

    async def set_register(self, reg, value) -> None:
        self.__register[reg] = value
        await self._swarm.send(self._port_name, "setRegister", reg, value)

    async def on_trigger(self, trigger_event, actor, p1) -> None:
        await self._swarm.send(self._port_name, "onTrigger", trigger_event, actor.get_port_name(), p1)
