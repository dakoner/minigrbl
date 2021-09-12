#!/usr/bin/python3
import time
import paho.mqtt.client as mqtt
from inputs import get_key
STEP_SIZE=.1

class Driver:
    def __init__(self):
        self.client =  mqtt.Client("client")
        self.client.loop_start()
        self.client.connect("inspectionscope.local")


        while True:
            events = get_key()
            for event in events:
                type_, code, state = event.ev_type, event.code, event.state 
                if type_ == 'Key':
                    if code == 'q':
                        cmd = "$J=G91 F10000 Z-%f" % STEP_SIZE
                        self.client.publish("grblesp32/command", cmd)
                    elif code == 'z':
                        cmd = "$J=G91 F10000 Z%f" % STEP_SIZE
                        self.client.publish("grblesp32/command", cmd)
                    elif code == 'a':
                        cmd = "$J=G91 F10000 X-%f" % STEP_SIZE
                        self.client.publish("grblesp32/command", cmd)
                    elif code == 'd':
                        cmd = "$J=G91 F10000 X%f" % STEP_SIZE
                        self.client.publish("grblesp32/command", cmd)
                    elif code == 'w':
                        cmd = "$J=G91 F10000 Y%f" % STEP_SIZE
                        self.client.publish("grblesp32/command", cmd)
                    elif code == 's':
                        cmd = "$J=G91 F10000 Y-%f" % STEP_SIZE
                        self.client.publish("grblesp32/command", cmd)   

d = Driver()
d.run()
 