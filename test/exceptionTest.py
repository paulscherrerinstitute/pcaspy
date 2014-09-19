#!/usr/bin/env python

from pcaspy import Driver, SimpleServer
import time

prefix = 'MTEST:'
pvdb = {
    'RAND' : {
        'prec' : 3,
        'count': 3,
    },
}

import threading
import numpy

class myDriver(Driver):
    def  __init__(self):
        super(myDriver, self).__init__()
        self.value = numpy.array([1,2,3])
        tid = threading.Thread(target = self.do)
        tid.setDaemon(True)
        tid.start()

    def read(self, reason):
        foo
        pass

    def write(self, reason, value):
        pass

    def do(self,):
        while True:
            self.value[1] += 1
            self.setParam('RAND', self.value)
            self.updatePVs()
            time.sleep(1)

if __name__ == '__main__':
    server = SimpleServer()
    server.createPV(prefix, pvdb)
    driver = myDriver()

    # process CA transactions
    while True:
        server.process(0.1)
