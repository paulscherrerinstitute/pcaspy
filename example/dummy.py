#!/usr/bin/env python

from pcas import Driver, SimpleServer
import time

if __name__ == '__main__':
    driver = Driver()
    server = SimpleServer()
    from db import pvdb, prefix
    for pvname in pvdb:
        info = pvdb[pvname]
        pv = server.createPV(prefix, pvname, info, driver)
        driver.registerPV(pv)

    while True:
        # process CA transactions
        server.process(0.01)
        # give other thread a chance
        time.sleep(0.01)
