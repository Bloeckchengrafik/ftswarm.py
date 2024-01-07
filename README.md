# 📚 Client library for the ftSwarm Serial API

This library provides a simple interface to the ftSwarm Serial API in a python 3 way.

## ⚙️ Installation

To install the latest version of the library, run the following command:
```bash
pip install ftswarm-py
```

## 🚲 Usage

The library provides a simple interface to the ftSwarm Serial API. The following example shows how to connect to the ftSwarm and read a button named "button1" from the ftSwarm.

```python
import asyncio
from swarm import FtSwarm


async def read_button():
    swarm = FtSwarm("/dev/ttyUSB0")  # Change this to your serial port
    button = await swarm.get_button("button1")

    print(button.get_state())

asyncio.run(read_button())
```

Let's just go over the code above. The following steps are performed:
- Creating an async context
- Creating a FtSwarm object with the serial port as parameter
- Getting the button named "button1" from the ftSwarm
- Printing the state of the button

Quite simple, right? 

Another simple example can be found at the quickstart section of the [documentation](https://bloeckchengrafik.de/ftswarm.py/quickstart/).

## 📝 Documentation

The library is documented using docstrings. You can also find the documentation on [my website](https://bloeckchengrafik.de/ftswarm.py/).

## 🙆 Contributing

If you want to contribute to the project, feel free to open a pull request. I will review it as soon as possible.
Before adding large features, please open an issue first to discuss the feature, so that you don't waste your time.

## ⚖️ License

This project is licensed under the MIT license. You can find the license in the [LICENSE](LICENSE) file.