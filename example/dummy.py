#!/usr/bin/env python

from pcaspy import Driver, SimpleServer
import time

prefix = 'MTEST:'
pvdb = {
    'RAND' : {
        'prec' : 3,
    },
}

if __name__ == '__main__':
    server = SimpleServer()
    server.createPV(prefix, pvdb)
    driver = Driver()

    while True:
        # process CA transactions
        server.process(0.01)
        # give other thread a chance
        time.sleep(0.01)
