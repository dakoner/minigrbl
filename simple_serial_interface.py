import sys
import serial
import time
import threading
import queue

import termios, fcntl, sys, os, time
class SerialInterface(threading.Thread):
    
    def __init__(self, port="/dev/ttyUSB0", baud=115200):
        super().__init__()
        self.serialport = serial.serial_for_url(port, do_not_open=True)
        self.serialport.baudrate = baud
        self.serialport.parity = serial.PARITY_NONE
        self.serialport.stopbits=serial.STOPBITS_ONE
        self.serialport.bytesize=serial.EIGHTBITS
        self.serialport.dsrdtr=True
        self.serialport.dtr = True
        self.serialport.ctsrts=True
        self.serialport.rts = True


    def soft_reset(self):
        print("soft reset\r")
        self.serialport.write(b"\x18") # Ctrl-X

    def reset(self):
        print("reset\r")
        self.serialport.dtr = False
        time.sleep(1)
        self.serialport.dtr = True
       
    def break_(self):
        print("break\r")
        self.serialport.send_break()


    def run(self):
        try:
            self.serialport.open()
        except serial.SerialException as e:
            sys.stderr.write('Could not open serial port {}: {}\n'.format(ser.name, e))
            return

        while True:
            if self.serialport.in_waiting > 0:
                data = self.serialport.read(self.serialport.in_waiting)
                try:
                    sys.stdout.write(data.decode('utf-8'))
                except UnicodeDecodeError:
                    print("Failed to interpret: ", data)
                else:
                    sys.stdout.flush()

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
                    self.serialport.write(bytes(c, 'utf-8'))
                    self.serialport.flush()
            time.sleep(0.01)



def main():

    fd = sys.stdin.fileno()

    oldterm = termios.tcgetattr(fd)
    newattr = termios.tcgetattr(fd)
    import tty
    tty.setraw(sys.stdin)
    #newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
    #termios.tcsetattr(fd, termios.TCSANOW, newattr)

    oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

    s = SerialInterface()
    s.start()
    
    try:
        s.join()    
    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)

if __name__ == '__main__':
    main()