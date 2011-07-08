#!/usr/bin/env python

from pcas import SimpleServer, Driver
import time
import random

prefix = 'MTEST:'
db = {
    'RAND' : {
        'prec' : 3,
        'scan' : 1,
        'count': 10,
    },
}
class myDriver(Driver):
    def __init__(self, server):
        Driver.__init__(self, server)

    def read(self, reason):
        if reason == 'RAND':
            value = [random.random() for i in range(10)]
        else:
            value = self.getParam(reason)
        return value

if __name__ == '__main__':
    server = SimpleServer()
    for pvname in db:
        info = db[pvname]
        pv = server.createPV(prefix, pvname, info)
    server.createDriver(myDriver)

    while True:
        # process CA transactions
        server.process(0.01)
        # give other thread a chance
        time.sleep(0.01)
