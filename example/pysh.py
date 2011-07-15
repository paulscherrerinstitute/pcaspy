#!/usr/bin/env python
import sys
import time
import thread
import subprocess
import tempfile
import shlex

from pcas import Driver, SimpleServer

class myDriver(Driver):
    def __init__(self, server):
        Driver.__init__(self, server)
        self.tid = None 

    def write(self, reason, value):
        status = True
        # take proper actions
        if reason == 'COMMAND':
            if not self.tid:
                command = value
                self.tid = thread.start_new_thread(self.runShell,(command,))
            else:
                status = False
        # store the values
        if status:
            self.setParam(reason, value)
        return status

    def runShell(self, command):
        print "DEBUG: Run ", command
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
        print "DEBUG: Finish ", command

if __name__ == '__main__':
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
    server = SimpleServer()
    server.createPVs(prefix, pvdb)
    server.createDriver(myDriver)

    while True:
        # process CA transactions
        server.process(0.01)
        # give other thread a chance
        time.sleep(0.01)
