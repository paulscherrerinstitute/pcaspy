#!/usr/bin/env python
import sys
import time
import thread
import subprocess
import tempfile
import shlex

from pcas import Driver, SimpleServer

class myDriver(Driver):
    def __init__(self):
        Driver.__init__(self)
        self.tid = None 

    def write(self, reason, value):
        status = True
        # store the values
        self.setParam(reason, value)
        # take proper actions
        if reason == 'COMMAND' and not self.tid:
            command = value
            self.tid = thread.start_new_thread(self.runShell,(command,))
        return status

    def runShell(self, command):
        # set status BUSY
        self.setParam('STATUS', 1)
        self.updatePVs()
        # run shell
        proc = subprocess.Popen(shlex.split(command), stdout = subprocess.PIPE)
        self.setParam('OUTPUT', proc.stdout.read().rstrip())
        self.callbackPV('COMMAND')
        # set status DONE
        self.setParam('STATUS', 0)
        self.updatePVs()
        self.tid = None

if __name__ == '__main__':
    driver = myDriver()
    server = SimpleServer()
    prefix = 'MTEST:'
    pvdb = { 'COMMAND' : 
             {
                 'type' : 'string',
                 'asyn' : True
             },
             'OUTPUT'  :
             {
                 'type' : 'string',
             },
             'STATUS'   :
             {   'type' : 'enum',
                 'enums': ['DONE', 'BUSY']
             }
           }
    for pvname in pvdb:
        info = pvdb[pvname]
        pv = server.createPV(prefix, pvname, info, driver)
        driver.registerPV(pv)

    while True:
        # process CA transactions
        server.process(0.01)
        # give other thread a chance
        time.sleep(0.01)
