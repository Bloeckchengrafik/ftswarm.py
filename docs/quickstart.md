# Quickstart

If you already got the hardware with the newest firmware, you're already
done with the c++ part. Just connect the ftSwarm to your computer and
install the python library:

```bash
pip install ftswarm.py
```

If you want to build the firmware on your own, you can find the source
code at [github](https://github.com/elektrofuzzis/ftSwarm).

## Getting Started

After building a swarm and connecting one of the ftSwarm devices to your
computer, you can start to control it with python. First, you have to
import the library and create a swarm object as well as get asyncio running:

```python
import swarm
import asyncio


async def main():
    ftswarm = swarm.FtSwarm(port="/dev/ttyUSB0")  # or "COM1" (or similar) on windows
    # do something with the ftSwarm


if __name__ == '__main__':
    asyncio.run(main())
```

The port has to be set to the serial port where the ftSwarm is connected.
If you use windows, you can find the port in the device manager.

## About aliases

A swarm can become quite complex fast. To make it easier to
control the hardware, you can use aliases. An alias is a name for a
specific hardware. For example, you can create an alias for the first
motor in the cli. More information on this topic can be found in the
[official config documentation](https://ftswarm.elektrofuzzis.dev/de/advanced/Configuration/).

All IO Ports can be called by their alias name or their controller hostname + number, e.g. "ftswarm1.A1" or "
ftswarm1.M2".

Now you can finally control some hardware.

## Example: Reading a switch

For this example, we will read the state of a switch. The switch is
connected to a digital input called `myswitch`.

```python
import swarm
import asyncio

async def main():
    ftswarm = swarm.FtSwarm(port="/dev/ttyUSB0")  # Enter your port here
    switch = await ftswarm.get_switch("myswitch")
    while True:
        print("Switch state:", await switch.get_state())
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
```

## Example: Writing to a motor

For this example, we will write a value to a motor. The motor is
connected to a digital output called `mymotor`.

```python
import swarm
import asyncio

async def main():
    ftswarm = swarm.FtSwarm(port="/dev/ttyUSB0")  # Enter your port here
    motor = await ftswarm.get_motor("mymotor")
    while True:
        await motor.set_speed(255)
        await asyncio.sleep(1)
        await motor.set_speed(-255)
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
```