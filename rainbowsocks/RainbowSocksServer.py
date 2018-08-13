import asyncio
import json
import threading
import websockets
import secrets
import time

from .utils import sockit

class RainbowSocksServer():
    
    def __init__(self):
        self.registered_events = {}
        self.connected_clients = set()

    async def _service(self, websocket, path):
        websocket.id = secrets.token_hex(16)
        self.connected_clients.add(websocket)
        #print(dir(websocket))
        #print(f"{websocket.id} connected.")
        websocket.send({"status": "connected"})
        try:
            while True:
                message = await websocket.messages.get()
                #print(message)
                event = json.loads(message)
                socketmod = await self.socket_mod(websocket, event.get("eventid", None))
                if event['trigger'] in self.registered_events:
                    await self.registered_events[event['trigger']](socketmod, event['data'])
                else:
                    await socketmod.send(sockit({"status": "error", "data": "No event."}))


        finally:
            #print(f"{websocket.id} disconnected.")
            self.connected_clients.remove(websocket)

    async def socket_mod(self, socket, eventid):
        async def respond(data):
            response = {"status": "reply", "data": data}
            if eventid:
                response['eventid'] = eventid
            await socket.send(sockit(response))

        async def broadcast(data, channel=None):
            response = {"status": "broadcast", "data": data}
            if eventid:
                response['eventid'] = eventid
            if channel:
                response['trigger'] = channel
            for client in [x for x in self.connected_clients]:
                try:
                    await client.send(sockit(response))
                except:
                    print(f"'{client.id}' is not responding, removing...")
                    self.connected_clients.remove(client)

        socket.respond = respond
        socket.broadcast = broadcast
        return socket


    def event(self, trigger, **kwargs):
        def register(f):
            if not asyncio.iscoroutinefunction(f):
                raise Exception('"{0.__name__}" must be a coroutine'.format(f))

            self.registered_events[trigger] = f
            return f

        return register


    def run(self, host='0.0.0.0', port=1020):
        print(f"Running on 'ws://{host}:{port}'")
        asyncio.get_event_loop().run_until_complete(
        websockets.serve(self._service, host, port))
        asyncio.get_event_loop().run_forever()