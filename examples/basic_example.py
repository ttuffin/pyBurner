import pyburner
import asyncio

heater = pyburner.Client("111.222.333.444")
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
