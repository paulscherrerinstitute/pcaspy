#!/usr/bin/env python

from pcas import Driver, SimpleServer
import time

prefix = 'MTEST:'
db = {
    'RAND' : {
        'prec' : 3,
    },
}

if __name__ == '__main__':
    server = SimpleServer()
    for pvname in db:
        info = db[pvname]
        pv = server.createPV(prefix, pvname, info)
    server.createDriver(Driver)

    while True:
        # process CA transactions
        server.process(0.01)
        # give other thread a chance
        time.sleep(0.01)
