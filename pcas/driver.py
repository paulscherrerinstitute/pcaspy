import cas
import thread
import time

class Driver(object):
    def __init__(self, server):
        self.pvData  = {}
        self.pvFlag  = {}
        # init pvData with pv instance
        self.server = server
        for reason, pv in server.getPV().items():
            self.setParam(reason, pv.info.value)

    def read(self, reason):
        """driver reimplemente this method to PV read request"""
        return self.getParam(reason)

    def write(self, reason, value):
        """driver reimplemente this method to PV write request
        return False if the value is not accepted.
        """
        self.setParam(reason, value)
        return True

    def setParam(self, reason, value):
        """set PV value and request update"""
        if self.pvData.get(reason) != value:
            self.pvData[reason] = value
            self.pvFlag[reason] = True

    def getParam(self, reason):
        """retrieve PV value"""
        return self.pvData[reason]

    def callbackPV(self, reason):
        """inform asynchronous write completion"""
        pv = self.server.getPV(reason)
        if pv.info.asyn:
            pv.endAsyncWrite(cas.S_casApp_success)

    def updatePVs(self):
        """post update event on changed values"""
        for reason, pv in self.server.getPV().items():
            if self.pvFlag[reason] and pv.info.scan == 0:
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
        # initialize from info dict with defaults
        self.count = info.get('count', 1)
        self.type  = _ait_d[info.get('type', 'float')]
        self.enums = info.get('enums', [])
        self.prec  = info.get('prec', 0.0)
        self.unit  = info.get('unit', '')
        self.lolim = info.get('lolim', 0.0)
        self.hilim = info.get('hilim', 0.0)
        self.scan  = info.get('scan', 0)
        self.asyn  = info.get('asyn', False)
        self.reason= ''
        # initialize value based on type and count
        if self.type in [cas.aitEnumString, cas.aitEnumFixedString,]:
            value = ''
        else:
            value = 0
        if self.count > 1:
            value = [value] * self.count
        self.value = info.get('value', value)

class SimplePV(cas.casPV):
    def __init__(self, name, info, server):
        cas.casPV.__init__(self)
        self.name = name
        self.info = info
        self.server  = server
        self.interest = False
        self.active   = False
        if self.info.scan > 0:
            thread.start_new_thread(self.scan,())

    def scan(self):
        while True:
            driver = self.server.getDriver()
            if not driver: continue
            value = driver.read(self.info.reason)
            self.updateValue(value)
            time.sleep(self.info.scan)

    def interestRegister(self):
        self.interest = True
        return cas.S_casApp_success

    def interestDelete(self):
        self.interest = False

    def write(self, context, value):
        # get driver object
        driver = self.server.getDriver()
        if not driver: return
        # call out driver support 
        success = driver.write(self.info.reason, value.get())
        self.updateValue(driver.getParam(self.info.reason))
        if self.info.asyn:
            if success:
                # async write will finish later
                self.startAsyncWrite(context)
                return cas.S_casApp_asyncCompletion
            else:
                return  cas.S_casApp_postponeAsyncIO
        else:
            return cas.S_casApp_success

    def updateValue(self, value):
        if (self.interest):
            if type(value) != cas.gdd:
                gddValue = cas.gdd()
                gddValue.put(value)
                value = gddValue
            self.postEvent(value);
        
    def getValue(self, value):
        # get driver object
        driver = self.server.getDriver()
        if not driver: return
        # create gdd value
        value.setPrimType(self.info.type)
        newValue = driver.read(self.info.reason)
        value.put(newValue)
        self.updateValue(newValue)
        return cas.S_casApp_success

    def getPrecision(self, prec):
        prec.put(self.info.prec)
        return cas.S_casApp_success

    def getUnits(self, unit):
        unit.put(self.info.unit)
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
        self.pvs_s = {}
        self.pvs_f = {}
        self.driver = None

    def pvExistTest(self, context, addr, fullname):
        if fullname in self.pvs_f.keys():
            return cas.pverExistsHere
        else:
            return cas.pverDoesNotExistHere

    def pvAttach(self, context, fullname):
        if fullname in self.pvs_f.keys():
            return self.pvs_f[fullname]
        else:
            return cas.S_casApp_pvNotFound

    def createPV(self, prefix, name, info):
        pvinfo = PVInfo(info)
        pvinfo.reason = name
        fullname = prefix + name
        pv = SimplePV(fullname, pvinfo, self)
        self.pvs_f[fullname] = pv
        self.pvs_s[name] = pv
        return pv
    def getPV(self, name=None):
        if name == None:
            return self.pvs_s
        else:
            return self.pvs_s[name]

    def createDriver(self, driver_class):
        self.driver = driver_class(self)
    def getDriver(self):
        return self.driver

    def process(self, time):
        cas.process(time)
