#!/usr/bin/env python

from pcaspy import Driver, SimpleServer

prefix = 'MTEST:'
pvdb = {
    'RAND' : {
        'prec' : 3,
    },
}

class myDriver(Driver):
    def  __init__(self):
        super(myDriver, self).__init__()

if __name__ == '__main__':
    server = SimpleServer()
    server.createPV(prefix, pvdb)
    driver = myDriver()

    # process CA transactions
    while True:
        server.process(0.1)
