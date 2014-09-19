#!/usr/bin/env python
"""
This trivial program snoops all PV search requests and prints them out.
Its only purpose is to demonstrate how channel access disconvers PVs.
"""
import pcaspy.cas as cas
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s: %(message)s')

class SnooperServer(cas.caServer):
    def __init__(self):
        cas.caServer.__init__(self)

    def __del__(self):
        cas.asCaStop()

    def pvExistTest(self, context, addr, fullname):
        logging.debug('%s\t%s', addr.stringConvert(1024), fullname)
        return cas.pverDoesNotExistHere

    def pvAttach(self, context, fullname):
        return cas.S_casApp_pvNotFound

    def process(self, second):
        cas.process(second)

if __name__ == '__main__':
    snooper = SnooperServer()
    while True:
        snooper.process(0.1)
