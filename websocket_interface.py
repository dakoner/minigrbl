import sys
import serial
import time
import threading
import queue
import paho.mqtt.client as mqtt


import websocket
import threading

MQTT_SERVER="gork.local"
WEBSOCKET_SERVER=sys.argv[1]
#WEBSOCKET_SERVER="microscope-6pack.local"
#WEBSOCKET_SERVER="inspection-6pack.local"

class WebSocketInterface(threading.Thread):
    
    def on_ws_connect(self, ws):
        print(">>>>>OPENED")

        self.client =  mqtt.Client("server")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.loop_start()
        self.client.connect(MQTT_SERVER)

    def on_ws_message(self, ws, message):
        try:
            if isinstance(message, str):
                if message.startswith("CURRENT_ID"):
                    self.current_id = message.split(':')[1]
                elif message.startswith("ACTIVE_ID"):
                    active_id = message.split(':')[1]
                    if self.current_id != active_id:
                        print("Warning: different active id.")
                elif message.startswith("PING"):
                    ping_id = message.split(":")[1]
                    if ping_id != self.current_id:
                        print("Warning: ping different active id.")
            else:
                message = str(message, 'ascii')
                for m in message.split("\n"):
                    if m != '':
                        print("Read:", m)
                        self.client.publish(f"{WEBSOCKET_SERVER}/output", m)
        except Exception as e:
            print("Caught exception", e)
            
    def on_ws_close(self, ws, close_status_code, close_msg):
        print(">>>>>>CLOSED")
    

    def __init__(self):
        super().__init__()

        self.wsapp = websocket.WebSocketApp(
            f"ws://{WEBSOCKET_SERVER}:81", 
            on_open=self.on_ws_connect, 
            on_message=self.on_ws_message, 
            on_close=self.on_ws_close)

    def on_connect(self, client, userdata, flags, rc):
        self.client.subscribe(f"{WEBSOCKET_SERVER}/command")
        self.client.subscribe(f"{WEBSOCKET_SERVER}/reset")
        self.client.subscribe(f"{WEBSOCKET_SERVER}/cancel")

    def on_message(self, client, userdata, message):
        print("Message:", message.topic, message.payload)
        if message.topic == f"{WEBSOCKET_SERVER}/command":
            command = message.payload.decode('utf-8')
            if command == '?':
                self.write(command)
            else:
                self.write(command + "\n")
        elif message.topic == f"{WEBSOCKET_SERVER}/reset":
            if message.payload.decode('utf-8') == 'hard':
                self.reset()
            else:
                self.soft_reset()
        elif message.topic == f"{WEBSOCKET_SERVER}/cancel":
            print("Cancel")
            self.write(chr(0x85))
            
    def soft_reset(self):
        self.write("\x18") # Ctrl-X

    def reset(self):
        pass

    def run(self):
        self.wsapp.run_forever()
        
    def write(self, data):
        self.wsapp.send(data)

def main():
    s = WebSocketInterface()
    s.start()
    s.join()    

if __name__ == '__main__':
    main()
