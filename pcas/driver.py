import cas
import thread
import time

class Driver(object):
    def __init__(self):
        self.pvData  = {}
        self.pvFlag  = {}
        self.pvs = {}

    def read(self, reason):
        return self.getParam(reason)

    def write(self, reason, value):
        self.setParam(reason, value)
        return True

    def setParam(self, reason, value):
        if self.pvData.get(reason) != value:
            self.pvData[reason] = value
            self.pvFlag[reason] = True

    def getParam(self, reason):
        return self.pvData[reason]

    def registerPV(self, pv):
        self.pvs[pv.info.reason] = pv
        # initialize value based on type and count
        type = pv.info.type
        # empty for string types
        if type in [cas.aitEnumString, cas.aitEnumFixedString,]:
            value = ''
        # zero for numeric types
        else:
            value = 0
        count = pv.info.count
        if count > 1:
            value = [value] * count
        self.setParam(pv.info.reason, value)

    def callbackPV(self, reason):
        pv = self.pvs[reason]
        if pv.info.asyn:
            pv.writeComplete()

    def updatePVs(self):
        reasons = self.pvData.keys()
        for pv in self.pvs.values():
            reason = pv.info.reason
            if reason in reasons:
                if self.pvFlag[reason]:
                    pv.updateValue(self.pvData[reason])
                    self.pvFlag[reason] = False

# map aitType to string representation
_ait_d = {'enum'   : cas.aitEnumEnum16,
          'str'    : cas.aitEnumString,
          'string' : cas.aitEnumString,
          'float'  : cas.aitEnumFloat64,
          'int'    : cas.aitEnumInt32,
          }
class PVInfo(object):
    def __init__(self, info):
        # initialize default
        self.count = 1
        self.type  = cas.aitEnumFloat64
        self.enums = []
        self.prec  = 0.0
        self.units = ''
        self.lolim = 0.0
        self.hilim = 0.0
        self.scan  = 0
        self.reason= ''
        self.asyn  = False
        # override with given dict
        for key in info:
            value = info.get(key)
            if key == 'type':
                self.type = _ait_d[value]
            else:
                setattr(self, key, value) 

class SimplePV(cas.casPV):
    def __init__(self, name, info, drv):
        cas.casPV.__init__(self)
        self.name = name
        self.info = info
        self.drv  = drv
        self.interest = False
        self.active   = False
        self.asyn = None
        if self.info.scan > 0:
            thread.start_new_thread(self.scan,())

    def scan(self):
        while True:
            value = self.drv.read(self.info.reason)
            self.updateValue(value)
            time.sleep(self.info.scan)

    def interestRegister(self):
        self.interest = True
        return cas.S_casApp_success

    def interestDelete(self):
        self.interest = False

    def write(self, context, value):
        # call out driver support 
        success = self.drv.write(self.info.reason, value.get())
        # post event for monitors
        if success:
            self.updateValue(value)
            # async write will finish later
            if self.info.asyn:
                self.asyn = cas.casAsyncWriteIO(context)
                return cas.S_casApp_asyncCompletion
        else:
            return cas.S_casApp_success

    def writeComplete(self):
        if self.asyn:
            self.asyn.postIOCompletion(cas.S_casApp_success)
            self.asyn = None

    def updateValue(self, value):
        if type(value) != cas.gdd:
            gddValue = cas.gdd()
            gddValue.put(value)
            value = gddValue
        if (self.interest):
            self.postEvent(value);
        
    def getValue(self, value):
        value.setPrimType(self.info.type)
        newValue = self.drv.read(self.info.reason)
        value.put(newValue)
        return cas.S_casApp_success

    def getPrecision(self, prec):
        prec.put(self.info.prec)
        return cas.S_casApp_success

    def getUnits(self, units):
        units.put(self.info.units)
        return cas.S_casApp_success

    def getEnums(self, enums):
        if (self.info.enums):
            enums.put(self.info.enums)
        return cas.S_casApp_success

    def getHighLimit(self, hilim):
        hilim.put(self.info.hilim)
        return cas.S_casApp_success

    def getLowLimit(self, lolim):
        lolim.put(self.info.lolim)
        return cas.S_casApp_success

    def bestExternalType(self):
        return self.info.type
   
    def maxDimension(self):
        if self.info.count > 1:
            return 1
        else:
            return 0

    def maxBound(self, dims):
        return self.info.count

    def getName(self):
        return self.name

class SimpleServer(cas.caServer):
    def __init__(self):
        cas.caServer.__init__(self)
        self.pvs = {}

    def pvExistTest(self, context, addr, name):
        if name in self.pvs.keys():
            return cas.pverExistsHere
        else:
            return cas.pverDoesNotExistHere

    def pvAttach(self, context, name):
        if name in self.pvs.keys():
            return self.pvs[name]
        else:
            return cas.S_casApp_pvNotFound

    def createPV(self, prefix, name, info, drv):
        # create PCInfo from dict
        pvinfo = PVInfo(info)
        pvinfo.reason = name
        # create and store SimplePV instance
        fullname = prefix + name
        pv = SimplePV(fullname, pvinfo, drv)
        self.pvs[fullname] = pv
        return pv

   
    def process(self, time):
        cas.process(time)
