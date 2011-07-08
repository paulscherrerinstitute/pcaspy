#!/usr/bin/env python
import sys
import time
import thread
import threading
import numpy

from pcas import Driver, SimpleServer

MAX_POINTS    = 1000
FREQUENCY     = 1000
NUM_DIVISIONS = 10
AMPLITUDE     = 1.0

class myDriver(Driver):
    def __init__(self, server):
        Driver.__init__(self, server)
        self.eid = threading.Event()
        self.tid = thread.start_new_thread(self.runSimScope, ()) 

    def write(self, reason, value):
        status = True
        # take proper actions
        if reason == 'UpdateTime':
            value = max(0.2, value)
        elif reason == 'Run':
            if value == 1:
                self.eid.set()
        # store the values
        if status:
            self.setParam(reason, value)
        return status

    def runSimScope(self):
        # simulate scope waveform
        while True:
            run = self.getParam('Run')
            updateTime = self.getParam('UpdateTime')
            if run:
                time.sleep(updateTime)
            else:
                self.eid.wait()
            run = self.getParam('Run')
            if not run: continue
            # retieve parameters
            noiseAmplitude    = self.getParam('NoiseAmplitude')
            timePerDivision   = self.getParam('TimePerDivision')
            voltsPerDivision  = self.getParam('VoltsPerDivision')
            triggerDelay      = self.getParam('TriggerDelay')
            voltOffset        = self.getParam('VoltOffset')
            # calculate the data wave based on timeWave scale 
            timeStart = triggerDelay
            timeStep  = timePerDivision * NUM_DIVISIONS / MAX_POINTS
            timeWave  = timeStart + numpy.arange(MAX_POINTS) * timeStep 
            noise  = noiseAmplitude * numpy.random.random(MAX_POINTS)
            data = AMPLITUDE * numpy.sin(timeWave * FREQUENCY * 2 * numpy.pi) + noise 
            # calculate statistics
            self.setParam('MinValue',  float(data.min()))
            self.setParam('MaxValue',  float(data.max()))
            self.setParam('MeanValue', float(data.mean()))
            # scale/offset
            yScale = 1.0 / voltsPerDivision
            data   = NUM_DIVISIONS/2.0 + yScale * (data + voltOffset)
            self.setParam('Waveform',  data.tolist())
            # do updates so clients see the changes
            self.updatePVs()

if __name__ == '__main__':
    server = SimpleServer()
    prefix = 'MTEST:'
    pvdb = {'Run'              : { 'type' : 'enum',
                                   'enums': ['STOP', 'RUN']    },
            'UpdateTime'       : { 'prec' : 3, 'value' : 1     },
            'TimePerDivision'  : { 'prec' : 5, 'value' : 0.001 },
            'TriggerDelay'     : { 'prec' : 5, 'value' : 0.0005},
            'VoltsPerDivision' : { 'prec' : 3, 'value' : 0.2   },
            'VoltOffset'       : { 'prec' : 3 },
            'NoiseAmplitude'   : { 'prec' : 3, 'value' : 0.2   },
            'Waveform'         : { 'count': MAX_POINTS,
                                   'prec' : 5 },
            'TimeBase'         : { 'count': MAX_POINTS,
                                   'prec' : 5,
                                   'value': list(numpy.arange(MAX_POINTS, dtype=float) * NUM_DIVISIONS / (MAX_POINTS -1))},
            'MinValue'         : { 'prec' : 4 },
            'MaxValue'         : { 'prec' : 4 },
            'MeanValue'        : { 'prec' : 4 },
           }
    for pvname in pvdb:
        info = pvdb[pvname]
        pv = server.createPV(prefix, pvname, info)
    server.createDriver(myDriver)

    while True:
        # process CA transactions
        server.process(0.01)
        # give other thread a chance
        time.sleep(0.01)