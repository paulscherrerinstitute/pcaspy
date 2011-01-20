from pcas import Driver, SimpleServer, PVInfo
import random
import time
import math
import thread

class FSCalc(object):
    def __init__(self):
        pass

    def calc(self, max=1200):
        a = 1
        b = 1
        while self.run:
            time.sleep(0.2)
            a = b
            b = a + b 
            if b > max:
                break

class myDriver(Driver):
    def __init__(self):
        Driver.__init__(self)
        thread.start_new_thread(self.poll,())   

    def write(self, reason, value):
        # store the values
        self.setParam(reason, value)
        # take proper actions
        if reason == 'SHUFFLE':
            if value == 1:
                data = self.getParam('WAVE')
                random.shuffle(data)
                self.setParam('WAVE', data)
            else:
                self.setParam('WAVE', list(range(12)))
        elif reason == 'START':
            if value == 1:
                if not self.run:
                    self.run = True
                    thread.start_new_thread(self.calcFS,())
            else:
                self.run = False
        return True

    def poll(self):
        while True:
            self.setParam('START', 0)
            self.updatePVs()
            self.callbackPV('START')

if __name__ == '__main__':
    driver = myDriver()
    server = SimpleServer()
    from db import pvdb, prefix
    for pvname in pvdb:
        info = PVInfo(pvdb[pvname])
        info.reason = pvname
        pv = server.createPV(prefix+pvname, info, driver)
        driver.registerPV(pv)

    while True:
        # process CA transactions
        server.process(0.01)
        # give other thread a chance
        time.sleep(0.01)
