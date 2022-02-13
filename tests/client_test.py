import asyncio
import pytest
import pyburner
from .utils.ws_server import WSServer

heater = pyburner.Client("127.0.0.1:8889")


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.stop()
    loop.close()


@pytest.fixture(scope="session")
async def async_ws_server():
    server = WSServer()
    result = await server.start_server()
    yield result
    await server.stop_server()


@pytest.fixture(scope="session")
async def async_init_heater(async_ws_server):
    result = await heater.init_websocket()
    yield result
    await heater.close_websocket()


@pytest.mark.asyncio
async def test_init_ws(event_loop, async_init_heater):
    assert async_init_heater is True


@pytest.mark.asyncio
async def test_refresh(event_loop):
    await heater.refresh()
    assert bool(heater.heater_data)


@pytest.mark.asyncio
async def test_settemp(event_loop):
    result = await heater.set_tempdesired(19)
    assert result is True


@pytest.mark.asyncio
async def test_setrunmode(event_loop):
    result = await heater.set_runmode(1)
    assert result is True


@pytest.mark.asyncio
async def test_setfanmin(event_loop):
    result = await heater.set_fanmin(1750)
    assert result is True


@pytest.mark.asyncio
async def test_setfanmax(event_loop):
    result = await heater.set_fanmax(5500)
    assert result is True


@pytest.mark.asyncio
async def test_pumpreset(event_loop):
    result = await heater.set_pumpreset()
    assert result is True


@pytest.mark.asyncio
async def test_pumpmin(event_loop):
    result = await heater.set_pumpmin(1.8)
    assert result is True


@pytest.mark.asyncio
async def test_pumpmax(event_loop):
    result = await heater.set_pumpmax(5.9)
    assert result is True


@pytest.mark.asyncio
async def test_pumpcal(event_loop):
    result = await heater.set_pumpcal(0.035)
    assert result is True


@pytest.mark.asyncio
async def test_lowvoltagecutout(event_loop):
    result = await heater.set_lowvoltcutout(11.2)
    assert result is True


@pytest.mark.asyncio
async def test_froston(event_loop):
    result = await heater.set_froston(1.1)
    assert result is True


@pytest.mark.asyncio
async def test_frostrise(event_loop):
    result = await heater.set_frostrise(3)
    assert result is True
