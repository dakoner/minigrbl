#!/usr/bin/python3
import time
import paho.mqtt.client as mqtt

from inputs import devices
from inputs import get_gamepad
import threading
from queue import Queue
import math

STEP_SIZE=0.5

class Driver:
    def __init__(self):
        self.client =  mqtt.Client("client")
        self.client.loop_start()
        self.client.connect("gork.local")

        self.lastTime = time.time()
        self.lastValue = 0
        self.move_x = False
        self.last_x = 0
        self.move_y = False
        self.last_y = 0
        
        self.queue = Queue()

        self._thread = threading.Thread(target=self.gamepad)
        self._thread.start()

    def gamepad(self):
        while True:
            events = get_gamepad()
            self.queue.put(events)
 
    def do_status(self):
        if self.move_x or self.move_y:
            cmd = "$J=G91"
            if self.move_x:
                if self.last_x > 0:
                    step = -STEP_SIZE
                else:
                    step = STEP_SIZE
                cmd += " Y%f" % step
            if self.move_y:
                if self.last_y > 0:
                    step = -STEP_SIZE
                else:
                    step = STEP_SIZE

                cmd += " X%f" % step
            feed = int(math.sqrt((self.last_x * self.last_x) + (self.last_y * self.last_y))/250.)
            cmd += " F%d" % feed
            print("send command", cmd)
            self.client.publish("grblesp32/command", cmd)

    def run(self):
        while True:
            time.sleep(0.1)
            self.do_status()
            try:
                while True:
                    events = self.queue.get_nowait()
                    for event in events:
                        type_, code, state = event.ev_type, event.code, event.state 
                        if type_ == 'Key':
                            if code == 'BTN_TL' and state == 1:
                                    cmd = "$J=G91 F200 Z-%f" % STEP_SIZE
                                    self.client.publish("grblesp32/command", cmd)
                            elif code == 'BTN_TR' and state == 1:
                                    cmd = "$J=G91 F200 Z%f" % STEP_SIZE
                                    self.client.publish("grblesp32/command", cmd)
                            elif code == 'BTN_SELECT' and state == 1:
                                    cmd = "M5"
                                    self.client.publish("grblesp32/command", cmd)
                            elif code == 'BTN_START' and state == 1:
                                    if self.led_state < 4:
                                        self.led_state += 1
                                    else:
                                        self.led_state = 0
                                    strength = (self.led_state)*1024
                                    if strength == 0:
                                        strength = 100
                                    cmd = "M3 S%d" % strength
                                    self.client.publish("grblesp32/command", cmd)
                        elif type_ == 'Absolute':
                            if code in ('ABS_HAT0X', 'ABS_HAT0Y'):
                                if state in (-1, 1):
                                    move = STEP_SIZE * state
                                    dir_ = 'X'
                                    if code == 'ABS_HAT0X':
                                        dir_ = 'Y'
                                    cmd = "$J=G91 F200 %s%f" % (dir_, move)
                                    self.client.publish("grblesp32/command", cmd)
                            elif code == 'ABS_X':
                                if abs(state) > 100:
                                    print("start x move")
                                    self.move_x = True
                                    self.last_x = state
                                else:
                                    print("cancel x move")
                                    self.move_x = False
                                    self.last_x = 0
                                    if not self.move_y:
                                        self.client.publish("grblesp32/cancel", "")
                            elif code == 'ABS_Y':
                                if abs(state) > 100:
                                    print("start y move")
                                    self.move_y = True
                                    self.last_y = state
                                else:
                                    print("cancel y move")
                                    self.move_y = False
                                    self.last_y = 0
                                    if not self.move_x:
                                        self.client.publish("grblesp32/cancel", "")
            except:
                pass            
    
d = Driver()
d.run()
 
