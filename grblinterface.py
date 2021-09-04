#!/usr/bin/python3
import time
import sys
from queue import Queue
import threading
import paho.mqtt.client as mqtt
from interface import Interface

class GRBL:
    def _onread(self):
        while True:
            line = self._queue.get()
            if line.startswith('<'):
                self.client.publish("grblesp32/status", line)
            else:
                self.client.publish("grblesp32/output", line)
            print(line)

    def _poll_state(self):
        while True:
            self._iface.write("?")
            time.sleep(1)

    def write(self, data):
        self._iface.write(data)

    def soft_reset(self):
        self._iface.write("\x18") # Ctrl-X

    def reset(self):
        self._iface.serialport.dtr = True
        time.sleep(0.5)
        self._iface.serialport.dtr = False

    def __init__(self):
        self._queue = Queue()
        self._iface = Interface("iface", "/dev/ttyUSB0", 115200)
        self._iface.start(self._queue)

        self._thread_read_iface = threading.Thread(target=self._onread)
        self._thread_read_iface.start()
        self._thread_polling = threading.Thread(target=self._poll_state)
        self._thread_polling.start()

        self.client =  mqtt.Client("server")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.loop_start()
        self.client.connect("inspectionscope.local")

    def on_connect(self, client, userdata, flags, rc):
        self.client.subscribe("grblesp32/command")
        self.client.subscribe("grblesp32/reset")

    def on_message(self, client, userdata, message):
        if message.topic == 'grblesp32/command':
            command = message.payload.decode('utf-8')
            self.write(command + "\n")
        elif message.topic == 'grblesp32/reset':
            self.reset()
        elif message.topic == 'grblesp32/cancel':
            self.write(0x85)

    def run(self):
        try:
            self._thread_read_iface.join()
        except KeyboardInterrupt:
            print("Exiting")
            sys.exit(0)
 
g = GRBL()
g.run()