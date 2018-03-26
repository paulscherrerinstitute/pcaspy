#!/usr/bin/env python

from pcaspy import Driver, SimpleServer, Alarm, Severity

prefix = 'MTEST:'
pvdb = {
    'RAND' : {
        'prec' : 3,
        'low' : -5, 'high': 5,
        'lolo': -10,'hihi': 10,
    },
    'ARRAY': {
        'count': 30,
        'value': 30*[1],
        'low': -5, 'high': 5,
        'lolo': -10, 'hihi': 10
    },
    'STATUS' : {
        'type' : 'enum',
        'enums':  ['OK', 'ERROR'],
        'states': [Severity.NO_ALARM, Severity.MAJOR_ALARM]
    },
    'MSG' : {
        'type' : 'str',
    }
}

class myDriver(Driver):
    def  __init__(self):
        super(myDriver, self).__init__()

    def write(self, reason, value):
        status = False
        if reason == 'MSG':
            status = True
            # store the value and this also resets alarm status and severity for string type
            self.setParam(reason, value)
            # set alarm status and severity
            if value != '':
                self.setParamStatus(reason, Alarm.COMM_ALARM, Severity.MINOR_ALARM)
            else:
                self.setParamStatus(reason, Alarm.NO_ALARM, Severity.NO_ALARM)
        else:
            status = True
            # store the value and this also resets alarm status and severity for string type
            self.setParam(reason, value)

        return status

if __name__ == '__main__':
    server = SimpleServer()
    server.createPV(prefix, pvdb)
    driver = myDriver()

    # process CA transactions
    while True:
        server.process(0.1)
