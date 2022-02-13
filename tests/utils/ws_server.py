import websockets
import json
from websockets import WebSocketServer
from dataclasses import dataclass, field


@dataclass()
class TestWSServer:
    _websocket: WebSocketServer = field(default=False, init=False)
    heater_data: dict = field(default_factory=dict, init=False)

    def __post_init__(self):
        self.heater_data: dict = {"TempCurrent": 10.1, "TempDesired": 21,
                                  "RunState": 7, "PumpMin": 1.6,
                                  "PumpMax": 5.5, "PumpCal": 0.022,
                                  "PumpCount": 0, "LowVoltCutout": 11.5,
                                  "FanMin": 1680, "FanMax": 4500,
                                  "FrostOn": 0, "FrostRise": 5
                                  }

    async def handler(self, websocket, path):
        async for message in websocket:
            try:
                message = json.loads(message)
                if message == {"Refresh": 1}:
                    await websocket.send(str(self.heater_data))
                else:
                    self.heater_data.update(message)
            except json.decoder.JSONDecodeError:
                response = "Payload must be in dictionary format"
                await websocket.send(response)

    async def start_server(self):
        self._websocket = await websockets.serve(
            self.handler, "localhost", 8889)

    async def stop_server(self):
        await self._websocket.close()
