import sys
import signal
from PyQt5 import QtGui, QtCore, QtWidgets
from simple_pyspin import Camera
import paho.mqtt.client as mqtt
import cv2

XY_STEP_SIZE=10
Z_STEP_SIZE=10

class PySpinCameraReader(QtCore.QThread):
    signal = QtCore.pyqtSignal(QtGui.QImage)
    def __init__(self):
        super(PySpinCameraReader, self).__init__()
        self.cam = Camera()
        self.cam.init()

    def run(self):         
        self.cam.start()
        while True:
            img = self.cam.get_array()
            image = QtGui.QImage(img, self.cam.Width, self.cam.Height, QtGui.QImage.Format_Grayscale8)
            self.signal.emit(image)


class Cv2CameraReader(QtCore.QThread):
    signal = QtCore.pyqtSignal(QtGui.QImage)
    def __init__(self):
        super(Cv2CameraReader, self).__init__()
        self.cam = cv2.VideoCapture(0)
        self.width = self.cam.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def run(self):
        while True:
            ret, img = self.cam.read()
            print(ret)
            if ret:
                image = QtGui.QImage(img.data, self.width, self.height, QtGui.QImage.Format_RGB888)
                self.signal.emit(image)

class Window(QtWidgets.QWidget):

    def __init__(self):
        super(Window, self).__init__()

        self.central_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.central_layout)
        self.image_widget = QtWidgets.QLabel(self)
        self.central_layout.addWidget(self.image_widget)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.setFocus()

        self.camera = Cv2CameraReader()
        self.camera.start()
        self.camera.signal.connect(self.imageTo)

        self.client =  mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.connect_async("awow.local")
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print("connected")
    def on_disconnect(self, client, userdata, flags, rc):
        print("disconnected")

    def keyPressEvent(self, event):
        cmd = None
        if event.key() == QtCore.Qt.Key_Q:
            cmd = "$J=G91 F10000 Z-%f" % Z_STEP_SIZE
        elif event.key() == QtCore.Qt.Key_Z:
            cmd = "$J=G91 F10000 Z%f" % Z_STEP_SIZE
        elif event.key() == QtCore.Qt.Key_A:
            cmd = "$J=G91 F10000 Y-%f" % XY_STEP_SIZE
        elif event.key() == QtCore.Qt.Key_D:
            cmd = "$J=G91 F10000 Y%f" % XY_STEP_SIZE
        elif event.key() == QtCore.Qt.Key_W:
            cmd = "$J=G91 F10000 X%f" % XY_STEP_SIZE
        elif event.key() == QtCore.Qt.Key_S:
            cmd = "$J=G91 F10000 X-%f" % XY_STEP_SIZE
        elif event.key() == QtCore.Qt.Key_X:
            QtWidgets.qApp.quit()
        if cmd:
            self.client.publish("grblesp32/command", cmd)


    def imageTo(self, image): 
        image = QtGui.QPixmap.fromImage(image).scaled(QtWidgets.QApplication.instance().primaryScreen().size())
        self.image_widget.setPixmap(image)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.showFullScreen()

    app.exec_()
