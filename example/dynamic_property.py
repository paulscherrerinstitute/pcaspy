#!/usr/bin/env python

from pcaspy import Driver, SimpleServer, Severity

prefix = 'MTEST:'
pvdb = {
    'ENUM' : {
        'type' : 'enum',
        'enums': ['ONE', 'TWO']
    },
    'RAND' : {
    },
    'CHANGE' : {
        'type' : 'int',
        'value': 2,
    }
}

enums = ['ZERO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE',
         'SIX', 'SEVEN', 'EIGHT', 'NINE', 'TEN']

class myDriver(Driver):
    def  __init__(self):
        super(myDriver, self).__init__()

    def write(self, reason, value):
        status = True
        if reason == 'CHANGE':
            num_states = value
            if num_states >= 1 and num_states <= 11:
                status = True
                self.setParamEnums('ENUM', enums[:num_states])
            info = {'hihi':value, 'unit': 'eV'}
            self.setParamInfo('RAND', info)
        if status:
            self.setParam(reason, value)
        return status

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)

    server = SimpleServer()
    server.createPV(prefix, pvdb)
    driver = myDriver()

    # process CA transactions
    while True:
        server.process(0.1)
