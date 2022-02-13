import websockets
import json
from websockets import WebSocketServer
from dataclasses import dataclass, field


@dataclass()
class WSServer:
    _websocket: WebSocketServer = field(default=False, init=False)
    heater_data: dict = field(default_factory=dict, init=False)

    def __post_init__(self):
        self.heater_data: dict = {"TempCurrent": 10, "TempDesired": 21,
                                  "RunState": 0, "PumpMin": 1.6,
                                  "PumpMax": 5.5, "PumpCal": 0.022,
                                  "PumpCount": 7239, "LowVoltCutout": 11.5,
                                  "FanMin": 1680, "FanMax": 4500,
                                  "FrostOn": 0, "FrostRise": 5
                                  }

    async def handler(self, websocket, path):
        async for message in websocket:
            try:
                message = json.loads(message)
                if message == {"Refresh": 1}:
                    await websocket.send(json.dumps(self.heater_data))
                elif message == {"Run": 1}:
                    self.heater_data.update({"RunState": 9})
                else:
                    self.heater_data.update(message)
            except json.decoder.JSONDecodeError:
                response = "Payload must be in dictionary format"
                await websocket.send(response)

    async def start_server(self):
        self._websocket = await websockets.serve(
            self.handler, "localhost", 8889)
        return True

    async def stop_server(self):
        self._websocket.close()
        await self._websocket.wait_closed()
