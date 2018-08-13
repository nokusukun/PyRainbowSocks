import asyncio
import json
import threading
import websockets
import secrets
import time
import queue


from .utils import sockit
from .websocket_client import websocket as wsclient

class RainbowSocksClient(object):
    """docstring for RainbowSocksClient"""
    def __init__(self, server):
        self.server = server
        self.returns = {}
        self.connection = None
        self.service_thread = None

        self.registered_events = {}

    def _service(self):
        while True:
            try:
                raw_data = self.connection.recv()
                #print(f"Recv Message: {raw_data}")
                #try:
                data = json.loads(raw_data)
                eventid = data['eventid']
                if data['status'] == "reply":
                    if eventid in self.returns:
                        self.returns[eventid].put(data['data'])

                if data['status'] == "broadcast":
                    if eventid in self.returns:
                        self.returns[eventid].put(data['data'])
                    if "trigger" in data:
                        if data['trigger'] in self.registered_events:
                            self.registered_events[data['trigger']](self.connection, data['data'])
                    if "broadcast" in self.registered_events:
                        self.registered_events["broadcast"](self.connection, data['data'])

            except:
                print(f"Parse Failed: '{raw_data}'")
                break

            time.sleep(0.5)

    def request(self, trigger, data, nowait=False):
        eventid = secrets.token_hex()
        payload = {"trigger": trigger, "data": data, "eventid": eventid}
        self.returns[eventid] = queue.Queue()
        self.connection.send(json.dumps(payload))
        if nowait:
            return None
        else:
            return self.returns[eventid].get()


    def event(self, trigger, **kwargs):
        def register(f):
            self.registered_events[trigger] = f
            return f
        return register

    def connect(self):
        self.connection = wsclient.create_connection(self.server)
        self.service_thread = threading.Thread(target=self._service)
        self.service_thread.start()


