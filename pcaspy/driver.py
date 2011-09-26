import cas
import thread
import time

class Manager(object):
    pvs = {}    # PV dict using port name as key and {pv base name: pv instance} as value
    pvf = {}    # PV dict using PV full name as key
    driver = {} # Driver dict

manager = Manager()


# decorator to register driver
def registerDriver(driver_init_func):
    def wrap(*args, **kargs):
        driver_instance = args[0]
        port = driver_instance.port
        driver_init_func(*args, **kargs)
        manager.driver[port] = driver_instance
    return wrap

# Driver metaclass to decorate subclass.__init__ to
# register subclass object 
class DriverType(type):
    def __init__(self, name, bases, dct):
        if name != 'Driver':
            self.__init__ = registerDriver(self.__init__)
        return type.__init__(self, name, bases, dct)

class Driver(object):
    port = 'default'

    __metaclass__ = DriverType
    def __init__(self):
        self.pvData  = {}
        self.pvFlag  = {}
        # init pvData with pv instance
        for reason, pv in manager.pvs[self.port].items():
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
        same = self.pvData.get(reason) == value
        if type(same) == bool and not same or hasattr(same, 'all') and not same.all():
            self.pvData[reason] = value
            self.pvFlag[reason] = True

    def getParam(self, reason):
        """retrieve PV value"""
        return self.pvData[reason]

    def callbackPV(self, reason):
        """inform asynchronous write completion"""
        pv = manager.pvs[self.port][reason]
        if pv.info.asyn:
            pv.endAsyncWrite(cas.S_casApp_success)

    def updatePVs(self):
        """post update event on changed values"""
        for reason, pv in manager.pvs[self.port].items():
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
        self.asg   = info.get('asg', '')
        self.reason= ''
        self.port  = info.get('port', 'default')
        # initialize value based on type and count
        if self.type in [cas.aitEnumString, cas.aitEnumFixedString,]:
            value = ''
        else:
            value = 0
        if self.count > 1:
            value = [value] * self.count
        self.value = info.get('value', value)

class SimplePV(cas.casPV):
    def __init__(self, name, info):
        cas.casPV.__init__(self)
        self.name = name
        self.info = info
        self.interest = False
        if info.asg:
            self.setAccessSecurityGroup(info.asg)
        if self.info.scan > 0:
            thread.start_new_thread(self.scan,())

    def scan(self):
        while True:
            driver = manager.driver.get(self.info.port)
            if driver:
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
        driver = manager.driver.get(self.info.port)
        if not driver: return S_casApp_undefined
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
                gddValue.setPrimType(self.info.type)
                gddValue.put(value)
                gddValue.setTimeStamp()
                value = gddValue
            self.postEvent(value);
        
    def getValue(self, value):
        # get driver object
        driver = manager.driver.get(self.info.port)
        if not driver: return S_casApp_undefined
        # create gdd value
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

    def pvExistTest(self, context, addr, fullname):
        if fullname in manager.pvf:
            return cas.pverExistsHere
        else:
            return cas.pverDoesNotExistHere

    def pvAttach(self, context, fullname):
        return manager.pvf.get(fullname, cas.S_casApp_pvNotFound)

    def createPV(self, prefix, pvdb):
        for basename, pvinfo in pvdb.items():
            pvinfo = PVInfo(pvinfo)
            pvinfo.reason = basename
            pvinfo.name   = prefix + basename
            pv = SimplePV(pvinfo.name, pvinfo)
            manager.pvf[pvinfo.name] = pv
            if pvinfo.port not in manager.pvs: manager.pvs[pvinfo.port]={}
            manager.pvs[pvinfo.port][basename] = pv

    def initAccessSecurityFile(self, filename, subst):
        cas.asInitFile(filename, subst)
        cas.asCaStart()

    def process(self, time):
        cas.process(time)
