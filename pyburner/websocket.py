import asyncio
import websockets
import json
import logging
from dataclasses import dataclass, field
from websockets import WebSocketClientProtocol


@dataclass
class WebSocket:
    endpoint: str
    _alive: bool = field(default=False, repr=False)
    _websocket: WebSocketClientProtocol = field(default=False, repr=False)
    _logger = logging.getLogger("pyBurner.websocket")
    _log_format = str = "[%(asctime)s][%(name)s][%(levelname)s] %(message)s"

    logging.basicConfig(
                **{
                    "format": _log_format,
                    "datefmt": "%m/%d/%Y %H:%M:%S",
                    "level": logging.INFO,
                    "filename": "./pyburner.log",
                    "filemode": "w",
                }
    )

    @staticmethod
    def _construct_uri(endpoint):
        uri: str = f"ws://{endpoint}"
        return uri

    async def connect(self, message_handler) -> None:
        uri = self._construct_uri(self.endpoint)
        try:
            self._websocket = await websockets.connect(uri, ping_interval=None)
            self._alive = True
            self._logger.info("Established websocket "
                              f"connection to {self.endpoint}")
            # run forever loop
            while self._alive:
                try:
                    await asyncio.wait_for(
                        self._process_messages(message_handler),
                        timeout=1.5
                    )
                except asyncio.TimeoutError:
                    await asyncio.sleep(3)
                    continue
                except websockets.ConnectionClosedError:
                    break
            self._alive = False
        except (OSError, websockets.WebSocketException) as e:
            self._logger.critical("Unable to open websocket "
                                  f"connection to {self.endpoint}. "
                                  f"The following error occurred: {e}")

    async def close_websocket(self) -> None:
        try:
            await self._websocket.close()
            self._alive = False
            self._logger.info("Websocket connection closed")
        except websockets.WebSocketException as e:
            self._logger.critical("A critical websocket exception occurred "
                                  "when attempting to close the websocket "
                                  f"connection: {e}")

    async def _process_messages(self, message_handler) -> None:
        async for message in self._websocket:
            await message_handler(message)

    async def send_to_websocket(self, query: dict) -> None:
        if self._alive:
            try:
                await self._websocket.send(json.dumps(query))
                self._logger.debug(f"Query sent: {query}")
            except websockets.WebSocketException as e:
                self._logger.critical("Unable to send the following JSON "
                                      f"query: {query}"
                                      f"Due to error: {e}")
        else:
            self._logger.critical(f"Failed to send the query: {query}. "
                                  f"The websocket is not currently open")
