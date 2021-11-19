import json
import asyncio
from dataclasses import dataclass, field
from websockets import WebSocketClientProtocol
from pyburner.websocket import WebSocket


@dataclass()
class Client:
    afterburner_ip: str
    _websocket: WebSocketClientProtocol = field(default=False, init=False)
    heater_data: dict = field(default_factory=dict, init=False)

    def __post_init__(self):
        self._websocket = WebSocket(self.afterburner_ip)

    async def init_websocket(self) -> bool:
        if await self._websocket.connect():
            asyncio.create_task(self._websocket.run_loop(self.handler))
            return True

    async def close_websocket(self) -> bool:
        if await self._websocket.close_websocket():
            return True

    async def handler(self, messages: dict) -> None:
        output = json.loads(messages)
        self.heater_data.update(output)

    async def refresh(self) -> None:
        await self._websocket.send_to_websocket({"Refresh": 1})
        await asyncio.sleep(2.5)  # allow time for AB to send data

    async def _set_config(self, json_input: dict) -> bool:
        await self._websocket.send_to_websocket(json_input)
        for key in json_input:
            if str(key) == "Run":
                # AB does not contain a "Run" dict key, so we
                # can't look for that to verify the exec of Run
                # was successful. Instead we check "RunState"
                # Wait 5s for RunState status to change on AB.
                await asyncio.sleep(5)
                await self.fetch_data("RunState", refresh=True)
                run_state = self.heater_data["RunState"]
                # AB sends the start-up command
                if (json_input[key] == 1) and (run_state == 9):
                    return True
                # AB sends the shutdown command
                elif (json_input[key] == 0) and (run_state == 7):
                    return True
            else:
                fetch_result = await self.fetch_data(key, refresh=True)
                if str(json_input[key]) == fetch_result:
                    return True

    async def fetch_data(self, request: str, refresh: bool = False) -> str:
        if refresh:
            await self.refresh()
        for key in self.heater_data:
            if key == request:
                return str(self.heater_data[key])

    async def set_tempdesired(self, temperature: int) -> bool:
        return await self._set_config({"TempDesired": temperature})

    async def set_runmode(self, runmode: int) -> bool:
        if runmode not in (0, 1):
            raise ValueError("Incorrect run mode specified")
        else:
            return await self._set_config({"Run": runmode})

    async def set_fanmin(self, fan_min: int) -> bool:
        return await self._set_config({"FanMin": fan_min})

    async def set_fanmax(self, fan_max: int) -> bool:
        return await self._set_config({"FanMax": fan_max})

    async def set_pumpreset(self) -> bool:
        return await self._set_config({"PumpCount": 0})

    async def set_pumpmin(self, pump_min: float) -> bool:
        return await self._set_config({"PumpMin": pump_min})

    async def set_pumpmax(self, pump_max: float) -> bool:
        return await self._set_config({"PumpMax": pump_max})

    async def set_pumpcal(self, pump_cal: float) -> bool:
        return await self._set_config({"PumpCal": pump_cal})

    async def set_lowvoltcutout(self, low_volt_cutout: float) -> bool:
        return await self._set_config({"LowVoltCutout": low_volt_cutout})

    async def set_froston(self, start_temp: float) -> bool:
        if not min(-1, 31) < start_temp < max(-1, 31):
            raise ValueError("Invalid FrostOn value specified. "
                             "Only values between 0 to 30 "
                             "are valid.")
        else:
            return await self._set_config({"FrostOn": start_temp})

    async def set_frostrise(self, temp_rise: float) -> bool:
        if not min(-30, 31) < temp_rise < max(-30, 31):
            raise ValueError("Invalid FrostRise value specified. "
                             "Only values between -30 to +30 "
                             "are valid.")
        else:
            return await self._set_config({"FrostRise": temp_rise})
