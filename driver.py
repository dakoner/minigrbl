#!/usr/bin/python3
import time
import paho.mqtt.client as mqtt
import curses
        
class Driver:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.stdscr.box()
        self.stdscr.nodelay(1)
        self.stdscr.border(0)

        self.command_win = self.stdscr.subwin(3, 10, 3, 3)
        self.command_win.box()
        self.command_win.refresh()

        self.log_win = self.stdscr.subwin(40, 120, 13, 3)
        self.log_win.box()
        self.log_win.refresh()
        
        self.info_win = self.stdscr.subwin(3, 15, 10, 6)
        self.info_win.box()
        self.info_win.refresh()

        self.stdscr.refresh()

        self.client =  mqtt.Client("client")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.loop_start()
        self.client.connect("inspectionscope.local")


    def publish(self, topic, payload):
        self.client.publish(topic, payload)

    def on_connect(self, client, userdata, flags, rc):
        self.info_win.addstr(1, 2, "connect")
        self.info_win.clrtoeol()
        self.info_win.box()
        self.info_win.refresh()
        self.client.subscribe("grblesp32/command")

    def on_message(self, client, userdata, message):
        try:
            self.log_win.addstr(3,2, message.payload.decode('utf-8'))
            #self.log_win.scroll()
            self.log_win.refresh()
            self.stdscr.refresh()
        except:
            raise RuntimeError

    def on_disconnect(self, *args):
        self.info_win.addstr(1, 2, "disconnect")
        self.info_win.clrtoeol()
        self.info_win.refresh()

    def run(self):
        while True:
            ch = self.stdscr.getch()
            
            refresh_required = True
            if ch == ord('q'):
                raise RuntimeError
            elif ch == ord('r'):
                self.command_win.addstr(1, 2, "reset")
                
            elif ch == ord('u'):
                self.command_win.addstr(1, 2, "unlock")
               
            elif ch == ord('a'):
                self.command_win.addstr(1, 2, "forward")
               
            elif ch == ord('z'):
                self.command_win.addstr(1, 2, "back")
               
            elif ch == curses.KEY_UP:
                self.command_win.addstr(1, 2, "up")
             
            elif ch == curses.KEY_DOWN:
                self.command_win.addstr(1, 2, "down")
              
            elif ch == curses.KEY_LEFT:
                self.command_win.addstr(1, 2, "left")
              
            elif ch == curses.KEY_RIGHT:
                self.command_win.addstr(1, 2, "right")
              
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