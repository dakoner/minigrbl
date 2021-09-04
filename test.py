#!/usr/bin/python3
import time
from queue import Queue
import threading
import paho.mqtt.client as mqtt
import curses

from interface import Interface
class GRBL:
    def _onread(self):
        while True:
            line = self._queue.get()
            self.win.scroll()
            self.win.addstr(38,2, line)
            self.win.clrtoeol()
            self.win.refresh()

    def __init__(self, win):
        self.win = win
        self.win.scrollok(True)
        self.win.setscrreg(2,38)

        self._queue = Queue()
        self._iface = Interface("iface", "/dev/ttyUSB0", 115200)
        self._iface.start(self._queue)

        self._iface_read_do = True
        self._thread_read_iface = threading.Thread(target=self._onread)
        self._thread_read_iface.start()
        self._thread_polling = threading.Thread(target=self._poll_state)
        self._thread_polling.start()


    def _poll_state(self):
        while True:
            self._iface.write("?")
            time.sleep(1)
        
class Driver:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.stdscr.box()
        self.stdscr.nodelay(1)
        self.stdscr.border(0)

        grblwin = self.stdscr.subwin(40, 120, 10, 3)
        grblwin.box()
        grblwin.refresh()
        self.g = GRBL(grblwin)

        self.win = self.stdscr.subwin(3, 10, 3, 3)
        self.win.box()

        self.win.refresh()
        self.stdscr.refresh()


    def run(self):
        while True:
            ch = self.stdscr.getch()
            
            refresh_required = True
            if ch == ord('q'):
                raise RuntimeError
            elif ch == ord('r'):
                self.g._iface.write("\x18") # Ctrl-X
                self.win.addstr(1, 2, "reset")
                self.win.clrtoeol()
            elif ch == ord('u'):
                self.g._iface.write("$X\n") # Ctrl-X
                self.win.addstr(1, 2, "unlock")
                self.win.clrtoeol()
            elif ch == ord('b'):
                self.g._iface.serialport.dtr = True
                time.sleep(0.1)
                self.g._iface.serialport.dtr = False

            elif ch == ord('a'):
                self.g._iface.write("G91 G0 Z1\n")
                self.win.addstr(1, 2, "forward")
                self.win.clrtoeol()
            elif ch == ord('z'):
                self.g._iface.write("G91 G0 Z-1\n")
                self.win.addstr(1, 2, "back")
                self.win.clrtoeol()
            elif ch == curses.KEY_UP:
                self.g._iface.write("G91 G0 X10\n")
                self.win.addstr(1, 2, "up")
                self.win.clrtoeol()
            elif ch == curses.KEY_DOWN:
                self.g._iface.write("G91 G0 X-10\n")
                self.win.addstr(1, 2, "down")
                self.win.clrtoeol()
            elif ch == curses.KEY_LEFT:
                self.g._iface.write("G91 G0 Y-10\n")
                self.win.addstr(1, 2, "left")
                self.win.clrtoeol()
            elif ch == curses.KEY_RIGHT:
                self.g._iface.write("G91 G0 Y10\n")
                self.win.addstr(1, 2, "right")
                self.win.clrtoeol()
            else:
                refresh_required = False

            if refresh_required:
                self.win.refresh()
                self.stdscr.refresh()

def main(stdscr):
    d = Driver(stdscr)
    d.run()
 

if __name__=='__main__':
    curses.wrapper(main)

    
