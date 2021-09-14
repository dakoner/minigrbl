import sys
import serial
import time
import threading
import queue
import paho.mqtt.client as mqtt

class SerialInterface(threading.Thread):
    
    def __init__(self, port="/dev/ttyUSB0", baud=115200):
        super().__init__()

        self.serialport = serial.serial_for_url(port, do_not_open=True)
        self.serialport.baudrate = baud
        self.serialport.parity = serial.PARITY_NONE
        self.serialport.stopbits=serial.STOPBITS_ONE
        self.serialport.bytesize=serial.EIGHTBITS
        self.serialport.dsrdtr= True
        self.serialport.ctsrts= True
        self.serialport.rts = False
        self.serialport.dtr = False
       

        self.client =  mqtt.Client("server")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.loop_start()
        self.client.connect("inspectionscope.local")

    def on_connect(self, client, userdata, flags, rc):
        self.client.subscribe("grblesp32/command")
        self.client.subscribe("grblesp32/reset")
        self.client.subscribe("grblesp32/cancel")

    def on_message(self, client, userdata, message):
        print(client, userdata, message)
        if message.topic == 'grblesp32/command':
            command = message.payload.decode('utf-8')
            print("Got command: ", command)
            self.write(command + "\n")
        elif message.topic == 'grblesp32/reset':
            if message.payload.decode('utf-8') == 'hard':
                self.reset()
            else:
                self.soft_reset()
        elif message.topic == 'grblesp32/cancel':
            self.write(0x85)

    def soft_reset(self):
        print("soft reset")
        self.write("\x18") # Ctrl-X

    def reset(self):
        print("reset\r")
        self.serialport.dtr = False
        time.sleep(.1)
        self.serialport.dtr = True
        self.serialport.rts = False
        time.sleep(.1)
        self.serialport.rts = True

    def run(self):
        try:
            self.serialport.open()
        except serial.SerialException as e:
            sys.stderr.write('Could not open serial port {}: {}\n'.format(ser.name, e))
            return
        self.reset()
        
        while True:
            if self.serialport.in_waiting > 0:
                data = self.serialport.read(self.serialport.in_waiting)
                print("read: ", data)
                sys.stdout.write(data.decode('utf-8'))
                self.client.publish("grblesp32/output", data)
            time.sleep(0.01)

    def write(self, data):
        print("writing: ", data)
        self.serialport.write(bytes(data,"utf-8"))
        self.serialport.flush()


def main():
    print("starting")
    s = SerialInterface()
    s.start()
    s.join()    

if __name__ == '__main__':
    main()