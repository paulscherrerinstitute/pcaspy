#!/usr/bin/env python

from pcaspy import Driver, SimpleServer

prefix = 'MTEST:'
pvdb = {
    'LEVEL': {
    },
    'FILL' : {
        'prec' : 3,
        'asg'  : 'fill',
    },
}

class myDriver(Driver):
    def  __init__(self):
        super(myDriver, self).__init__()

if __name__ == '__main__':
    server = SimpleServer()
    server.initAccessSecurityFile('test.as', P=prefix)
    server.createPV(prefix, pvdb)
    driver = myDriver()
    # process CA transactions
    while True:
        server.process(0.1)
