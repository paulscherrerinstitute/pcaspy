#!/usr/bin/env python

from pcaspy import Driver, SimpleServer, Severity

prefix = 'MTEST:'
pvdb = {
    'RAND' : {
        'prec' : 3,
        'low' : -5, 'high': 5,
        'lolo': -10,'hihi': 10,
    },
    'STATUS' : {
        'type' : 'enum',
        'enums':  ['OK', 'ERROR'],
        'states': [Severity.NO_ALARM, Severity.MAJOR_ALARM]
    },
    'MSG' : []
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
