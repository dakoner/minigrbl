#!/usr/bin/python3
import time
import paho.mqtt.client as mqtt
import curses
from line_processor import Processor

class Driver:
    def __init__(self, stdscr):
        self.processor = Processor()

        self.stdscr = stdscr
        self.stdscr.box()
        self.stdscr.nodelay(1)

        self.command_win = self.stdscr.subwin(3, 10, 3, 3)
        self.command_win.box()
        self.command_win.refresh()


        self.state_win = self.stdscr.subwin(3, 80, 6, 3)
        self.state_win.box()
        self.state_win.refresh()

        self.log_win = self.stdscr.subwin(30, 80, 13, 3)
        self.log_win.scrollok(True)
        self.log_win.box()
        self.log_win.refresh()
        
        self.info_win = self.stdscr.subwin(3, 15, 10, 6)
        self.info_win.box()
        self.info_win.refresh()

        self.stdscr.refresh()

        self.client =  mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.connect("awow.local")

        self.time = time.time()
        self.client.loop_start()


    def publish(self, topic, payload):
        self.client.publish(topic, payload)

    def on_connect(self, client, userdata, flags, rc):
        self.info_win.addstr(1, 2, "connect")
        self.info_win.clrtoeol()
        self.info_win.box()
        self.info_win.refresh()
        self.client.subscribe("grblesp32/status")
        self.client.subscribe("grblesp32/output")

    def on_message(self, client, userdata, message):
        try:
            processed_lines = self.processor.run(message.payload.decode('utf-8'))
            for line in processed_lines:
                if line.startswith("<"):
                    self.state_win.addstr(1, 2, line)
                    self.state_win.clrtoeol()
                elif line.startswith("ok"):
                    pass
                elif line.strip() == '':
                    pass
                else:
                    self.log_win.addstr(29, 1, line)
                    self.log_win.clrtoeol()
                    self.log_win.scroll()
            self.log_win.box()
            self.log_win.refresh()
            self.state_win.box()
            self.state_win.refresh()
            self.stdscr.refresh()
        except:
            raise RuntimeError

    def on_disconnect(self, *args):
        self.info_win.addstr(1, 2, "disconnect")
        self.info_win.clrtoeol()
        self.info_win.refresh()

    def run(self):
        while True:
            t = time.time()
            if t - self.time > 1:
                self.client.publish("grblesp32/command", "?")
                self.time = t
            ch = self.stdscr.getch()
            
            refresh_required = True
            #if ch == ord('q'):
            #    raise RuntimeError
            if ch == ord('r'):
                self.command_win.addstr(1, 2, "reset")
                self.client.publish("grblesp32/reset", "")
            elif ch == ord(' '):
                self.command_win.addstr(1, 2, "unlock")
                self.client.publish("grblesp32/command", "$X")
            elif ch == ord('q'):
                self.command_win.addstr(1, 2, "up")
                self.client.publish("grblesp32/command", "$J=G91 F10000 Z-10")
            elif ch == ord('z'):
                self.command_win.addstr(1, 2, "down")
                self.client.publish("grblesp32/command", "$J=G91 F10000 Z10")
            elif ch == ord('w'):
                self.command_win.addstr(1, 2, "forward")
                self.client.publish("grblesp32/command", "$J=G91 F10000 X10")
            elif ch == ord('s'):
                self.command_win.addstr(1, 2, "back")
                self.client.publish("grblesp32/command", "$J=G91 F10000 X-10")
            elif ch == ord('a'):
                self.command_win.addstr(1, 2, "left")
                self.client.publish("grblesp32/command", "$J=G91 F10000 Y10")
            elif ch == ord('d'):
                self.command_win.addstr(1, 2, "right")
                self.client.publish("grblesp32/command", "$J=G91 F10000 Y-10")
            else:
                refresh_required = False

            if refresh_required:
                self.command_win.clrtoeol()
                self.command_win.box()
                self.command_win.refresh()
                self.stdscr.refresh()

def main(stdscr):
    d = Driver(stdscr)
    d.run()
 
if __name__=='__main__':
    curses.wrapper(main)
