#!/usr/bin/env python

from pcaspy import SimpleServer, Driver
import time
import random

class myDriver(Driver):
    def __init__(self):
        Driver.__init__(self)

    def read(self, reason):
        if reason == 'RAND':
            value = [random.random() for i in range(10)]
        else:
            value = self.getParam(reason)
        return value

if __name__ == '__main__':
    prefix = 'MTEST:'
    pvdb = {
        'RAND' : {
            'prec' : 3,
            'scan' : 1,
            'count': 10,
        },
    }

    server = SimpleServer()
    server.createPV(prefix, pvdb)
    driver = myDriver()

    while True:
        # process CA transactions
        server.process(0.01)
        # give other thread a chance
        time.sleep(0.01)
