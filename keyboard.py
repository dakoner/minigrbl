#!/usr/bin/python3
import time
import paho.mqtt.client as mqtt
from inputs import devices, get_key
STEP_SIZE=.1

class Driver:
    def __init__(self):
        self.client =  mqtt.Client("client")
        self.client.loop_start()
        self.client.connect("inspectionscope.local")

        keyboard = devices.keyboards[1]
        print("wait")
        while True:
            events = keyboard.read()
            for event in events:
                type_, code, state = event.ev_type, event.code, event.state
                if type_ == 'Key':
                    print(type_, code, state)
                    if code == 'KEY_Q' and state == 1:
                        cmd = "$J=G91 F10000 Z-%f" % STEP_SIZE
                        self.client.publish("grblesp32/command", cmd )
                    elif code == 'KEY_Z' and state == 1:
                        cmd = "$J=G91 F10000 Z%f" % STEP_SIZE
                        self.client.publish("grblesp32/command", cmd )
                    elif code == 'KEY_A' and state == 1:
                        cmd = "$J=G91 F10000 X-%f" % STEP_SIZE
                        self.client.publish("grblesp32/command", cmd )
                    elif code == 'KEY_D' and state == 1:
                        cmd = "$J=G91 F10000 X%f" % STEP_SIZE
                        self.client.publish("grblesp32/command", cmd )
                    elif code == 'KEY_W' and state == 1:
                        cmd = "$J=G91 F10000 Y%f" % STEP_SIZE
                        self.client.publish("grblesp32/command", cmd )
                    elif code == 'KEY_S' and state == 1:
                        cmd = "$J=G91 F10000 Y-%f" % STEP_SIZE
                        self.client.publish("grblesp32/command", cmd )   
print("start")
d = Driver()
d.run()
 
