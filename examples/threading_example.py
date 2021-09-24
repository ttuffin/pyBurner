import asyncio
import pyburner
from threading import Thread

heater = pyburner.Client("111.222.333.444")
event_loop = asyncio.new_event_loop()


def background_loop(loop: asyncio.AbstractEventLoop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


def start_thread():
    t = Thread(target=background_loop, args=(event_loop,), daemon=True)
    t.start()


def init_websocket():
    asyncio.run_coroutine_threadsafe(
        heater.init_websocket(), event_loop)


def refresh_websocket():
    asyncio.run_coroutine_threadsafe(
        heater.refresh(), event_loop)


def close_websocket():
    asyncio.run_coroutine_threadsafe(
        heater.close_websocket(), event_loop)


def set_tempdesired(temperature: int):
    future = asyncio.run_coroutine_threadsafe(
        heater.set_tempdesired(temperature), event_loop)
    print(future.result())


def set_runmode(run_mode: int):
    future = asyncio.run_coroutine_threadsafe(
        heater.set_runmode(run_mode), event_loop)
    print(future.result())


def fetch_data(request):
    future = asyncio.run_coroutine_threadsafe(
        heater.fetch_data(request), event_loop)
    print(future.result())
