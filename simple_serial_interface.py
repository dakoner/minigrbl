import sys
import serial
import time
import threading
import queue
import tty

import termios, fcntl, sys, os, time
from serial_interface import SerialInterface

def main():
    s = SerialInterface()

    fd = sys.stdin.fileno()

    oldterm = termios.tcgetattr(fd)
    newattr = termios.tcgetattr(fd)
    tty.setraw(sys.stdin)
    #newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
    #termios.tcsetattr(fd, termios.TCSANOW, newattr)

    oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)
   
    s.start()
    try:
        while True:
            c = sys.stdin.read(1)
            if c:
                if ord(c) == 18:
                    self.reset()
                elif ord(c) == 24:
                    self.soft_reset()
                elif ord(c) == 3:
                    return
                else:
                    if ord(c) < 32:
                        sys.stdout.write("Send control char: %d\r\n" % ord(c))
                        sys.stdout.flush()
                    else:
                        sys.stdout.write(c)
                        sys.stdout.flush()
                    s.write(c)
            time.sleep(0.01)
        s.join()    
    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)

if __name__ == '__main__':
    main()