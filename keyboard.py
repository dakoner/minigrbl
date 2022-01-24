#!/usr/bin/python3
import os
import termios
import sys
import time
import paho.mqtt.client as mqtt
import tty
import fcntl

XY_STEP_SIZE=100
Z_STEP_SIZE=10

class Driver:
    def __init__(self):
        self.client =  mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.connect_async("awow.local")
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print("connected")
    def on_disconnect(self, client, userdata, flags, rc):
        print("disconnected")

    def run(self):
        while True:
            c = sys.stdin.read(1)
            if c:
                print(c)
                cmd = None
                if c == '/':
                    return
                if c == 'q':
                    cmd = "$J=G91 F10000 Z-%f" % Z_STEP_SIZE
                elif c == 'z':
                    cmd = "$J=G91 F10000 Z%f" % Z_STEP_SIZE
                elif c == 'a':
                    cmd = "$J=G91 F10000 Y%f" % XY_STEP_SIZE
                elif c == 'd':
                    cmd = "$J=G91 F10000 Y-%f" % XY_STEP_SIZE
                elif c == 'w':
                    cmd = "$J=G91 F10000 X%f" % XY_STEP_SIZE
                elif c == 's':
                    cmd = "$J=G91 F10000 X-%f" % XY_STEP_SIZE
                elif c == 'r':
                    self.client.publish("grblesp32/reset", "hard")
                if cmd:
                    self.client.publish("grblesp32/command", cmd)

def main():
    fd = sys.stdin.fileno()

    oldterm = termios.tcgetattr(fd)
    newattr = termios.tcgetattr(fd)
    tty.setraw(sys.stdin)
   

    oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)
    
    d = Driver()
    try:
        d.run()
    except:
        termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
        raise
    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
   
if __name__ == '__main__':
     main()
