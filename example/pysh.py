#!/usr/bin/env python
import time
import sys
import threading
import subprocess
import shlex

from pcaspy import Driver, SimpleServer

prefix = 'MTEST:'
pvdb = { 
    'COMMAND' : {
        'type' : 'char',
        'count': 128,
        'asyn' : True
    },
    'OUTPUT'  : {
        'type' : 'char',
        'count': 500,
    },
    'STATUS'  : {
        'type' : 'enum',
        'enums': ['DONE', 'BUSY']
    },
    'ERROR'   : {
        'type' : 'string',
    },
}
import math
class myDriver(Driver):
    def __init__(self):
        Driver.__init__(self)
        self.tid = None 

    def write(self, reason, value):
        status = True
        # take proper actions
        if reason == 'COMMAND':
            if not self.tid:
                command = value
                if command:
                    self.tid = threading.Thread(target=self.runShell,args=(command,))
                    self.tid.start()
            else:
                status = False
        else:
            status = False
        # store the values
        if status:
            self.setParam(reason, value)
        return status

    def runShell(self, command):
        print("DEBUG: Run ", command)
        # set status BUSY
        self.setParam('STATUS', 1)
        self.updatePVs()
        # run shell
        try:
            time.sleep(0.01)
            proc = subprocess.Popen(shlex.split(command), 
                    stdout = subprocess.PIPE, 
                    stderr = subprocess.PIPE)
            proc.wait()
        except OSError:
            self.setParam('ERROR', str(sys.exc_info()[1]))
            self.setParam('OUTPUT', '')
        else:
            self.setParam('ERROR', proc.stderr.read().rstrip())
            self.setParam('OUTPUT', proc.stdout.read().rstrip())
        self.callbackPV('COMMAND')
        # set status DONE
        self.setParam('STATUS', 0)
        self.updatePVs()
        self.tid = None
        print("DEBUG: Finish ", command)

if __name__ == '__main__':
    server = SimpleServer()
    server.createPV(prefix, pvdb)
    driver = myDriver()

    while True:
        # process CA transactions
        server.process(0.1)
