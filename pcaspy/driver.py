import cas
import threading
import time

from alarm import Severity, Alarm

class Manager(object):
    pvs = {}    # PV dict using port name as key and {pv base name: pv instance} as value
    pvf = {}    # PV dict using PV full name as key
    driver = {} # Driver dict

# Yes, this is a global instance
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

class Data(object):
    def __init__(self):
        self.value = 0
        self.flag  = False
        self.severity  = Severity.INVALID_ALARM
        self.alarm = Alarm.UDF_ALARM
        self.time  = cas.epicsTimeStamp()

    def __repr__(self):
        return "Value: %s\nAlarm: %s\nSeverity: %s\nTime: %s" % (self.value, self.alarm, self.severity, self.time)

class Driver(object):
    port = 'default'

    __metaclass__ = DriverType
    def __init__(self):
        self.pvDB    = {}
        # init pvData with pv instance
        for reason, pv in manager.pvs[self.port].items():
            data = Data()
            data.value = pv.info.value
            self.pvDB[reason] = data

    def read(self, reason):
        """
        Return PV current value

        Parameters
        ----------
        reason : str
            PV base name
        Return
        ------
            PV current value
        Note
        ----
        driver reimplemente this method to PV read request

        """
        return self.getParam(reason)

    def write(self, reason, value):
        """
        Write PV new value

        Parameters
        ----------
        reason : str
            PV base name
        value :
            PV new value
        Return
        ------
            True if the new value is accepted
            False if the new value is rejected
        Note
        ----
        driver reimplemente this method to PV write request

        """
        self.setParam(reason, value)
        return True

    def setParam(self, reason, value):
        """set PV value and request update"""
        same = self.pvDB[reason].value == value
        if (type(same) == bool and not same) or (hasattr(same, 'all') and not same.all()):
            self.pvDB[reason].value = value
            self.pvDB[reason].flag  = True
            self.pvDB[reason].time = cas.epicsTimeStamp()
            alarm, severity = self._checkAlarm(reason, value)
            if alarm is not None: self.pvDB[reason].alarm = alarm
            if severity is not None: self.pvDB[reason].severity = severity

    def setParamStatus(self, reason, alarm=None, severity=None):
        """set PV status and serverity and request update"""
        if alarm is not None:
            self.pvDB[reason].alarm = alarm
        if severity is not None:
            self.pvDB[reason].severity = severity
        self.pvDB[reason].flag  = True

    def getParam(self, reason):
        """retrieve PV value"""
        return self.pvDB[reason].value

    def getParamDB(self, reason):
        return self.pvDB[reason]

    def callbackPV(self, reason):
        """inform asynchronous write completion"""
        pv = manager.pvs[self.port][reason]
        if pv.info.asyn:
            pv.endAsyncWrite(cas.S_casApp_success)

    def updatePVs(self):
        """post update event on changed values"""
        for reason, pv in manager.pvs[self.port].items():
            if self.pvDB[reason].flag and pv.info.scan == 0:
                pv.updateValue(self.pvDB[reason])
                self.pvDB[reason].flag = False

    def _checkAlarm(self, reason, value):
        info =  manager.pvs[self.port][reason].info
        if info.type == cas.aitEnumEnum16:
            return self._checkEnumAlarm(info, value)
        elif info.type in [cas.aitEnumFloat64, cas.aitEnumInt32]:
            return self._checkNumericAlarm(info, value)
        elif  info.type in [cas.aitEnumString, cas.aitEnumFixedString, cas.aitEnumUint8]:
            return Alarm.NO_ALARM,Severity.NO_ALARM
        else:
            return None,None

    def _checkNumericAlarm(self, info, value):
        severity = Severity.NO_ALARM
        alarm = Alarm.NO_ALARM
        lolo = info.lolo
        hihi = info.hihi
        low  = info.low
        high = info.high

        if lolo >= hihi:
            valid_lolo_hihi = False
        else:
            valid_lolo_hihi = True

        if low >= high:
            valid_low_high = False
        else:
            valid_low_high = True

        if valid_low_high and value <= low:
            alarm = Alarm.LOW_ALARM
            severity = Severity.MINOR_ALARM

        if valid_lolo_hihi and value <= lolo:
            alarm = Alarm.LOLO_ALARM
            severity = Severity.MAJOR_ALARM

        if valid_low_high and value >= high:
            alarm = Alarm.HIGH_ALARM
            severity = Severity.MINOR_ALARM

        if valid_lolo_hihi and value >= hihi:
            alarm = Alarm.HIHI_ALARM
            severity = Severity.MAJOR_ALARM

        return alarm, severity


    def _checkEnumAlarm(self, info, value):
        severity = Severity.NO_ALARM
        alarm = Alarm.NO_ALARM

        states = info.states

        if value>=0 and value < len(states):
            severity = states[value]
            if severity != Severity.NO_ALARM:
                alarm = Alarm.STATE_ALARM
        else:
            severity = Severity.MAJOR_ALARM
            alarm = Alarm.STATE_ALARM

        return alarm, severity


# map aitType to string representation
_ait_d = {'enum'   : cas.aitEnumEnum16,
          'str'    : cas.aitEnumString,
          'string' : cas.aitEnumString,
          'float'  : cas.aitEnumFloat64,
          'int'    : cas.aitEnumInt32,
          'char'   : cas.aitEnumUint8,
          }
class PVInfo(object):
    def __init__(self, info):
        # initialize from info dict with defaults
        self.count = info.get('count', 1)
        self.type  = _ait_d[info.get('type', 'float')]
        self.enums = info.get('enums', [])
        self.states= info.get('states',[])
        # initialize enum severity states if not specified
        if not self.states:
            self.states = len(self.enums) * [Severity.NO_ALARM]
        self.prec  = info.get('prec', 0.0)
        self.unit  = info.get('unit', '')
        self.lolim = info.get('lolim', 0.0)
        self.hilim = info.get('hilim', 0.0)
        self.hihi  = info.get('hihi', 0.0)
        self.lolo  = info.get('lolo', 0.0)
        self.high  = info.get('high', 0.0)
        self.low   = info.get('low',  0.0)
        self.scan  = info.get('scan', 0)
        self.asyn  = info.get('asyn', False)
        self.asg   = info.get('asg', '')
        self.reason= ''
        self.port  = info.get('port', 'default')
        # initialize value based on type and count
        if self.type in [cas.aitEnumString, cas.aitEnumFixedString, cas.aitEnumUint8]:
            value = ''
        else:
            value = 0
        if self.count > 1 and self.type is not cas.aitEnumUint8:
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
        # scan thread
        if self.info.scan > 0:
            self.tid = threading.Thread(target=self.scan)
            self.tid.setDaemon(True)
            self.tid.start()

    def scan(self):
        while True:
            driver = manager.driver.get(self.info.port)
            if driver:
                gddValue = cas.gdd()
                self.getValue(gddValue)
                gddValue.setTimeStamp()
                self.updateValue(gddValue)
            time.sleep(self.info.scan)

    def interestRegister(self):
        self.interest = True
        return cas.S_casApp_success

    def interestDelete(self):
        self.interest = False

    def writeValue(self, value):
        # get driver object
        driver = manager.driver.get(self.info.port)
        if not driver: return cas.S_casApp_undefined
        # call out driver support
        success = driver.write(self.info.reason, value.get())
        value = driver.getParamDB(self.info.reason)
        if not success:
            value.severity = Severity.INVALID_ALARM
            value.alarm    = Alarm.WRITE_ALARM
        self.updateValue(value)
        return success

    def write(self, context, value):
        # delegate asynchronous to python writeNotify method
        # only if writeNotify not present in C++ library
        if not cas.EPICS_HAS_WRITENOTIFY and self.info.asyn:
            return self.writeNotify(context, value)
        else:
            self.writeValue(value)
            return cas.S_casApp_success

    def writeNotify(self, context, value):
        success = self.writeValue(value)
        # do asynchronous only if PV supports
        if success and self.info.asyn:
            # async write will finish later
            self.startAsyncWrite(context)
            return cas.S_casApp_asyncCompletion
        elif self.hasAsyncWrite():
            return  cas.S_casApp_postponeAsyncIO
        else:
            return cas.S_casApp_success

    def updateValue(self, value):
        if (self.interest):
            if type(value) != cas.gdd:
                gddValue = cas.gdd()
                gddValue.setPrimType(self.info.type)
                gddValue.put(value.value)
                gddValue.setTimeStamp(value.time)
                gddValue.setStatSevr(value.alarm, value.severity)
                value = gddValue
            self.postEvent(value)

    def getValue(self, value):
        # get driver object
        driver = manager.driver.get(self.info.port)
        if not driver: return cas.S_casApp_undefined
        # set gdd type if necessary
        if value.primitiveType() == cas.aitEnumInvalid:
            value.setPrimType(self.info.type)
        # set gdd value
        newValue = driver.read(self.info.reason)
        value.put(newValue)
        # set gdd info
        dbValue = driver.getParamDB(self.info.reason)
        value.setStatSevr(dbValue.alarm, dbValue.severity)
        value.setTimeStamp(dbValue.time)
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

    def __del__(self):
        cas.asCaStop()

    def pvExistTest(self, context, addr, fullname):
        if fullname in manager.pvf:
            return cas.pverExistsHere
        else:
            return cas.pverDoesNotExistHere

    def pvAttach(self, context, fullname):
        return manager.pvf.get(fullname, cas.S_casApp_pvNotFound)

    def createPV(self, prefix, pvdb):
        """
        Create PV based on prefix and database definition

        Parameters
        ----------
        prefix : str
            Name prefixing the basename
        pvdb : dict
            PV database definition::

                {
                    'PVNAME' : {
                        'field' : value
                    }
                    ...
                }
        """
        for basename, pvinfo in pvdb.items():
            pvinfo = PVInfo(pvinfo)
            pvinfo.reason = basename
            pvinfo.name   = prefix + basename
            pv = SimplePV(pvinfo.name, pvinfo)
            manager.pvf[pvinfo.name] = pv
            if pvinfo.port not in manager.pvs: manager.pvs[pvinfo.port]={}
            manager.pvs[pvinfo.port][basename] = pv

    def initAccessSecurityFile(self, filename, **subst):
        """
        Load access security configuration file

        Parameters
        ----------
        filename : str
            Name of the access security configuration file
        **subst : dict
            Substitute macros

        """
        macro = ','.join(['%s=%s'%(k,v) for k,v in subst.items()])
        cas.asInitFile(filename, macro)
        cas.asCaStart()

    def process(self, time):
        cas.process(time)
