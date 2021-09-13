import sys
import serial
import time
import threading
import queue
import paho.mqtt.client as mqtt

class SerialInterface(threading.Thread):
    
    def __init__(self, port="/dev/ttyUSB0", baud=115200):
        super().__init__()

        self.serialport = serial.Serial(port, baud,
                                        parity=serial.PARITY_NONE, 
                                        stopbits=serial.STOPBITS_ONE,
                                        bytesize=serial.EIGHTBITS,
                                        dsrdtr=True)
        self.serialport.flushInput()
        self.serialport.flushOutput()

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
        self.serialport.write("\x18") # Ctrl-X

    def reset(self):
        print("reset")
        self.serialport.dtr = True
        time.sleep(0.5)
        self.serialport.dtr = False

    def run(self):
        while True:
            if self.serialport.in_waiting > 0:
                data = self.serialport.read(self.serialport.in_waiting)
                print("read: ", data)
                sys.stdout.write(data.decode('utf-8'))
                self.client.publish("grblesp32/output", data)
            time.sleep(0.01)

    def stop(self):
        self.serialport.flushInput()
        self.serialport.flushOutput()
        self.serialport.close()
        
    def write(self, data):
        print("writing: ", data)
        self.serialport.write(bytes(data,"utf-8"))


def main():
    print("starting")
    s = SerialInterface()
    s.start()
    s.join()    

if __name__ == '__main__':
    main()