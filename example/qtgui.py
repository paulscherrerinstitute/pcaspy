import sys
from PyQt4 import QtGui, QtCore

from pcaspy import SimpleServer, Driver
from pcaspy.tools import ServerThread

prefix = 'MTEST:'
pvdb   = {
        'RAND': {}
}

class myDriver(Driver):
    def __init__(self):
        super(myDriver,self).__init__()

class Display(QtGui.QWidget):
    def __init__(self):
        super(Display, self).__init__()
        layout = QtGui.QHBoxLayout()
        layout.addWidget(QtGui.QLabel('Value:'))
        input = QtGui.QDoubleSpinBox()
        layout.addWidget(input)
        self.setLayout(layout)
        self.connect(input, QtCore.SIGNAL('valueChanged(double)'), self.newValue)
        self.drv = myDriver()

    def newValue(self, value):
        self.drv.write('RAND', value)
        self.drv.updatePVs()

if __name__ == '__main__':
    # create pcas server
    server = SimpleServer()
    server.createPV(prefix, pvdb)
    
    # create qt gui
    app = QtGui.QApplication(sys.argv)
    win = Display()
    win.show()
    
    # create pcas server thread and shut down when app exits
    server_thread = ServerThread(server)
    QtCore.QObject.connect(app, QtCore.SIGNAL('lastWindowClosed()'), server_thread.stop)

    # start pcas and gui event loop
    server_thread.start()
    app.exec_()
