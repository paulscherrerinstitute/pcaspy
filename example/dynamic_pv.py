from pcaspy import Driver, SimpleServer
import pcaspy.cas as cas

import re

prefix = 'MTEST:'
pvdb = { 'STATIC' : {} }

# keep reference to dynamic spectra pvs
spvs = {}

class SpectrumSimulator(object):
    """
    An object to produce spectrum on request.
    """
    def get(self, index):
        """
        :param int index: the spectrum id
        :return: a list of 100 integers
        """
        return [index] * 100

class SpectrumPV(cas.casPV):
    def __init__(self, name):
        cas.casPV.__init__(self)
        self.name = name
        self.index = int(re.match('MTEST:SPECTRUM(\d+)', name).group(1))

    def getValue(self, value):
        value.put([self.index]*100)
        return cas.S_casApp_success

    def maxDimension(self):
        return 1

    def maxBound(self, dims):
        return 100


# The driver serves normal static PVs
class myDriver(Driver):
    def __init__(self):
        Driver.__init__(self)


class myServer(SimpleServer):

    def __init__(self):
        SimpleServer.__init__(self)

    def pvExistTest(self, context, addr, fullname):
        if fullname.startswith('MTEST:SPECTRUM'):
            return cas.pverExistsHere
        else:
            return SimpleServer.pvExistTest(self, context, addr, fullname)

    def pvAttach(self, context, fullname):
        if fullname.startswith('MTEST:SPECTRUM'):
            if fullname not in spvs:
                pv = SpectrumPV(fullname)
                spvs[fullname] = pv
            return spvs[fullname]
        else:
            return SimpleServer.pvAttach(self, context, fullname)


if __name__ == '__main__':
    server = myServer()
    server.createPV(prefix, pvdb)
    driver = myDriver()

    while True:
        server.process(1)
