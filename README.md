## Description

A Python library for interacting with the [Afterburner](http://www.mrjones.id.au/afterburner/); an
aftermarket, extensible controller for diesel heaters. Please refer to the 
[Afterburner Manual](http://www.mrjones.id.au/afterburner/assets/files/UserManual-V3.2.pdf) for information on what
types of diesel heaters are compatible with the Afterburner.

**pyBurner** leverages [asyncio](https://docs.python.org/3/library/asyncio.html) 
for concurrent operations and the [websockets](https://websockets.readthedocs.io/en/stable/) library for communicating 
with the Afterburner. By utilising pyBurner you can fetch runtime information and statistics from the Afterburner and
send commands to adjust the operations of the heater, such as turning it on/off and setting the desired temperature.

### Compatibility
pyBurner has been verified with the following versions of Python and the Afterburner firmware.

| Afterburner | Python |
|-------------|--------|
|    v3.4.4   |  v3.9  |

## Installation

~~~bash
$ pip install pyburner
~~~

## Usage

Since pyBurner utilises Python's built-in asyncio library, you will first need to ensure an event loop is running.
Calling `asyncio.get_event_loop()` will attempt to retrieve the current event loop, and if one is not found it 
will create one automatically. Please refer to the 
[asyncio Event Loop docs](https://docs.python.org/3/library/asyncio-eventloop.html) for more information.

You can then instantiate the `pyburner.Client()` class and pass the Afterburner's IP address as the only parameter:
`heater = pyburner.client("192.168.0.9")`

Next, a websocket connection should be established using `heater.init_websocket()`, followed by the commands you wish
to send. A full list of available commands can be found further down.

Below is a simple, standalone application that uses pyBurner to fetch temperature 
information from the Afterburner.
~~~python
import pyburner
import asyncio

heater = pyburner.Client("<afterburner_ip_address>")
loop = asyncio.get_event_loop()


async def main():
    asyncio.create_task(heater.init_websocket())
    # allow time for websocket to connect
    await asyncio.sleep(1.5)
    tasks = await asyncio.gather(
        heater.fetch_data("TempCurrent"),
        heater.fetch_data("TempBody")
    )
    print(f"The ambient temperature is {tasks[0]} degrees.\n"
          f"The heater body temperature is {tasks[1]} degrees.")
    await asyncio.create_task(heater.close_websocket())

asyncio.run(main())
~~~

If you wish to run the asyncio event loop in a separate thread, see 
[examples/threading_example.py](https://github.com/ttuffin/pyBurner/blob/dev/examples/threading_example.py) as a 
reference. One example of running the code in `threading_example.py`:
~~~
>>> import threading_example
>>> threading_example.start_thread()
>>> threading_example.init_websocket()
>>> threading_example.set_tempdesired(22)
True
~~~

When establishing the initial websocket connection, the Afterburner will send all current data to pyBurner which is then
stored in a dictionary called `heater_data`. You may then directly access the values in the dictionary. For example:

**Full dictionary**: `heater.heater_data`

**Specific key**: `heater.heater_data["TempCurrent"]`

Note that while a websocket connection is open, the Afterburner will only send updates when a value is changed, and only
that specific value will be updated in `heater_data`.
It is possible to trigger a refresh of the entire `heater_data` dictionary by sending the `refresh()` command. Note 
that the `fetch_data()` by default does not execute a full refresh of the `heater_data` dictionary. If you need to 
ensure that up-to-date information is retrieved, parse `refresh=True` in the `fetch_data()` call.

### Commands

~~~
fetch_data(request: str, refresh: bool = False)
~~~
Fetch a specific parameter from the Afterburner. The refresh option controls whether a full refresh of the websocket 
data will be executed before returning the value of the requested parameter. Please refer to the 
[Afterburner Manual](http://www.mrjones.id.au/afterburner/assets/files/UserManual-V3.2.pdf) for a list of available 
parameters.

Example: `fetch_data("TempCurrent", refresh=True)`

~~~
set_tempdesired(temperature: int)
~~~
Set the desired ambient temperature.

Example: `set_tempdesired(21)`

~~~
set_runmode(runmode: int)
~~~
Instruct the Afterburner to turn the heater on or off.


Valid runmodes are 0 (off) or 1 (on).

Example: `set_runmode(1)`

~~~
set_fanmin(fan_min: int)
~~~
Set fan RPM for lowest heating power

Example: `set_fanmin(1680)`
~~~
set_fanmax(fan_max: int)
~~~
Set fan RPM for highest heating power

Example: `set_fanmax(4500)`
~~~
set_pumpreset()
~~~
Reset the accumulated number of pump cycles (fuel gauge)

Example: `set_pumpreset()`

~~~
set_pumpmin(pump_min: float)
~~~
Set pump rate for lowest heating power (in Hz)

Example: `set_pumpmin(1.6)`

~~~
set_pumpmax(pump_max: float)
~~~
Pump rate for highest heating power (in Hz)

Example: `set_pumpmax(5.5)`

~~~
set_pumpcal(pump_cal: float)
~~~
Volume of fuel in mL / stroke of pump

Example: `set_pumpcal(0.022)`

~~~
set_lowvoltcutout(low_volt_cutout: float)
~~~
Threshold for low voltage shutdown (unloaded)

Example: `set_lowvoltcutout(11.5)`