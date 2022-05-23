from . import cas
from .alarm import Severity, Alarm
try:
    from collections.abc import Iterable
except ImportError:  # python < 3
    from collections import Iterable
import operator
import threading
import time
import sys
import logging
if sys.hexversion >= 0x02070000:
    from logging import NullHandler
else:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger('pcaspy').addHandler(NullHandler())


class Manager(object):
    pvs = {}     #: PV dict using port name as key and {pv base name: pv instance} as value
    pvf = {}     #: PV dict using PV full name as key
    driver = {}  #: Driver dict

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
    def __init__(cls, name, bases, dct):
        if name != 'Driver':
            cls.__init__ = registerDriver(cls.__init__)
        type.__init__(cls, name, bases, dct)


class Data(object):
    def __init__(self):
        self.value = 0
        self.flag = False
        self.severity = Severity.INVALID_ALARM
        self.alarm = Alarm.UDF_ALARM
        self.udf = True
        self.mask = 0
        self.time = cas.epicsTimeStamp()

    def __repr__(self):
        return "value=%s alarm=%s severity=%s flag=%s mask=%s time=%s" % \
               (self.value, Alarm.nameOf(self.alarm), Severity.nameOf(self.severity), self.flag, self.mask, self.time)

# Define empty DriverBase using metaclass syntax compatible with both Python 2 and Python 3
DriverBase = DriverType(str('DriverBase'), (), {
    '__doc__': 'Driver base class'
})


class Driver(DriverBase):
    """
    This class reacts to PV's read/write requests. The default behavior is to accept any value of a write request
    and return it to a read request, an echo alike.

    To specify the behavior, override methods :meth:`read` and :meth:`write` in a derived class.
    """
    port = 'default'

    def __init__(self):
        """
        Initialize parameters database. This method must be called by subclasses in the first place.
        """
        self.pvDB = {}
        # init pvData with pv instance
        for reason, pv in manager.pvs[self.port].items():
            data = Data()
            data.value = pv.info.value
            self.pvDB[reason] = data

    def read(self, reason):
        """
        Read PV current value

        :param str reason: PV base name
        :return: PV current value

        This method is invoked by server library when clients issue read access to a PV.
        By default it returns the value stored in the parameter library by calling :meth:`getParam`.

        The derived class might leave this method untouched and update the PV values from
        a separate polling thread. See :ref:`shell-command-example`, :ref:`simscope-example`.

        .. note:: This method is called by the server library main thread. Time consuming tasks
                  should not be performed here. It is suggested to work in an auxiliary thread.
        """
        return self.getParam(reason)

    def write(self, reason, value):
        """
        Write PV new value

        :param str reason: PV base name
        :param value: PV new value
        :return: True if the new value is accepted, False if rejected.

        This method is invoked by server library when clients write to a PV.
        By default it stores the value in the parameter library by calling :meth:`setParam`.

        .. note:: This method is called by the server library main thread. Time consuming tasks
                  should not be performed here. It is suggested to work in an auxiliary thread.

        """
        self.setParam(reason, value)
        return True

    def setParam(self, reason, value, timestamp=None):
        """set PV value and request update

        :param str reason: PV base name
        :param value: PV new value
        :param pcaspy.cas.epicsTimeStamp timestamp: PV time stamp

        Store the PV's new value if it is indeed different from the old.
        For list and numpy array, a copy will be made.
        This new value will be pushed to registered client the next time when :meth:`updatePVs` is called.
        The PV's modification time will be updated to *timestamp*. If *timestamp* is omitted, the current
        time is applied.

        Alarm and severity status are updated as well. For numeric type, the alarm/severity is determined as the
        following:

            ========================    ============  ============
            value                       alarm         severity
            ========================    ============  ============
            value < *lolo*              LOLO_ALARM    MAJOR_ALARM
            *lolo* < value < *low*      LOW_ALARM     MINOR_ALARM
            *low* < value < *high*      NO_ALARM      NO_ALARM
            *high* < value < *hihi*     HIGH_ALARM    MINOR_ALARM
            value > *hihi*              HIHI_ALARM    MAJOR_ALARM
            ========================    ============  ============

        For enumerate type, the alarm severity is defined by field *states*. And if severity is other than NO_ALARM,
        the alarm status is STATE_ALARM.

        .. note:: The *timestamp*, if given, must be of :class:`pcaspy.cas.epicsTimeStamp` type.

        """
        # make a copy of mutable objects, list, numpy.ndarray
        if isinstance(value, list):
            value = value[:]
        elif 'numpy.ndarray' in str(type(value)):
            value = value.copy()
        # check whether value update is needed
        pv = manager.pvs[self.port][reason]
        self.pvDB[reason].mask |= pv.info.checkValue(value)
        self.pvDB[reason].value = value
        if timestamp is None:
            timestamp = cas.epicsTimeStamp()
        self.pvDB[reason].time = timestamp
        if self.pvDB[reason].mask:
            self.pvDB[reason].flag = True
        # check whether alarm/severity update is needed
        alarm, severity = pv.info.checkAlarm(value)
        self.setParamStatus(reason, alarm, severity)
        logging.getLogger('pcaspy.Driver.setParam')\
            .debug('%s: %s', reason, self.pvDB[reason])

    def setParamStatus(self, reason, alarm=None, severity=None):
        """set PV status and severity and request update

        :param str reason: PV base name
        :param alarm: alarm state
        :param severity: severity state

        The PVs' alarm status and severity are automatically set in :meth:`setParam`.
        If the status and severity need to be set explicitly to override the defaults, :meth:`setParamStatus` must
        be called *after* :meth:`setParam`.

        The new alarm status/severity will be pushed to registered clients the next time when :meth:`updatePVs` is called.
        """
        if alarm is not None and self.pvDB[reason].alarm != alarm:
            self.pvDB[reason].alarm = alarm
            self.pvDB[reason].mask |= cas.DBE_ALARM
            self.pvDB[reason].flag = True
        if severity is not None and self.pvDB[reason].severity != severity:
            self.pvDB[reason].severity = severity
            self.pvDB[reason].mask |= cas.DBE_ALARM
            self.pvDB[reason].flag = True

    def setParamEnums(self, reason, enums, states=None):
        """ set PV enumerate strings and severity states

        :param str reason: PV base name
        :param list enums: string representation of the enumerate states
        :param list states: alarm severity of the enumerate states.

        The number of elements in *states* must match that of *enums*.
        If *None* is given, the list is populated with *Severity.NO_ALARM*.

        The new enumerate strings will be pushed to registered clients the next time when :meth:`updatePVs` is called.

        .. note:: The monitoring client needs to use *DBR_GR_XXX* or *DBR_CTRL_XXX* request type and *DBE_PROPERTY*
                  event mask when issuing the subscription. This requires EPICS base 3.14.12.6+.
        """
        if states is None:
            states = [Alarm.NO_ALARM] * len(enums)
        if len(enums) != len(states):
            raise ValueError('enums and states must have the same length')
        pv = manager.pvs[self.port][reason]
        if pv.info.enums != enums:
            pv.info.enums = enums
            pv.info.states = states
            self.pvDB[reason].mask |= cas.DBE_PROPERTY
            self.pvDB[reason].flag = True

    def setParamInfo(self, reason, info):
        """
        set PV meta info, limits, precision, limits, units.

        :param str reason: PV base name
        :param dict info: information dictionary, same as used in :meth:`SimpleServer.createPV`.

        The new meta information will be pushed to registered clients the next time when :meth:`updatePVs` is called.

        .. note:: The monitoring client needs to use *DBR_GR_XXX* or *DBR_CTRL_XXX* request type and *DBE_PROPERTY*
                  event mask when issuing the subscription. This requires EPICS base 3.14.12.6+.
        """
        # copy new information
        pv = manager.pvs[self.port][reason]
        for k, v in info.items():
            if hasattr(pv.info, k):
                setattr(pv.info, k, v)
        pv.info.validateLimit()

        # recheck alarm
        alarm, severity = pv.info.checkAlarm(self.pvDB[reason].value)
        self.setParamStatus(reason, alarm, severity)

        # mark event mask and flag
        self.pvDB[reason].mask |= cas.DBE_PROPERTY
        self.pvDB[reason].flag = True

    def getParam(self, reason):
        """retrieve PV value

        :param str reason: PV base name
        :return: PV current value

        """
        return self.pvDB[reason].value

    def getParamDB(self, reason):
        """
        Return the PV data information

        :param str reason: PV base name
        :return: PV current data information
        :rtype: :class:`Data`

        """

        return self.pvDB[reason]

    def getParamInfo(self, reason, info_keys=None):
        """
        Get PV info fields. This function returns a dictionary with info/value pairs,
        where each entry of the info_keys-parameter results in a dictionary entry if
        the PVInfo-object has such an attribute. Attributes that do not exist are ignored.
        Valid attributes are the same as used in :meth:`SimpleServer.createPV`.

        If no info_keys are specified, all PV info keys are returned.

        :param str reason: PV base name
        :param list info_keys: List of keys for what information to obtain
        :return: Dictionary with PV info fields and their current values
        :rtype: dict
        """
        pv = manager.pvs[self.port][reason]

        if info_keys is None:
            info_keys = ['states', 'prec', 'unit', 'lolim', 'hilim',
                         'hihi', 'lolo', 'high', 'low', 'scan', 'asyn', 'adel', 'mdel',
                         'asg', 'port', 'enums', 'count', 'type', 'value']

        info_dict = {}
        for key in info_keys:
            if hasattr(pv.info, key):
                info_dict[key] = getattr(pv.info, key)

        return info_dict

    def callbackPV(self, reason):
        """Inform asynchronous write completion

        :param str reason: PV base name

        """
        pv = manager.pvs[self.port][reason]
        if pv.info.asyn:
            pv.endAsyncWrite(cas.S_casApp_success)

    def updatePVs(self):
        """Post update events on all PVs with value, alarm status or metadata changed"""
        for reason in self.pvDB:
            self.updatePV(reason)

    def updatePV(self, reason):
        """Post update event on the PV if value, alarm status or metadata changes

        :param str reason: PV base name
        """
        pv = manager.pvs[self.port][reason]
        if self.pvDB[reason].flag and pv.info.scan == 0:
            self.pvDB[reason].flag = False
            pv.updateValue(self.pvDB[reason])
            self.pvDB[reason].mask = 0


# map aitType to string representation
_ait_d = {'enum':   cas.aitEnumEnum16,
          'str':    cas.aitEnumString,
          'string': cas.aitEnumString,
          'float':  cas.aitEnumFloat64,
          'int':    cas.aitEnumInt32,
          'short':  cas.aitEnumInt16,
          'char':   cas.aitEnumUint8,
          }

# map aitType to gddAppType_dbr_ctrl_xxx
_dbr_d = {
    cas.aitEnumUint8:   32,
    cas.aitEnumInt16:   29,
    cas.aitEnumInt32:   33,
    cas.aitEnumFloat64: 34,
}


class PVInfo(object):
    def __init__(self, info):
        # initialize from info dict with defaults
        self.count = info.get('count', 1)
        self.type = _ait_d[info.get('type', 'float')]
        # check the number of enum states and
        # the state string do not exceed the maximum
        enums = info.get('enums', [])
        if len(enums) > cas.MAX_ENUM_STATES:
            sys.stderr.write('enums exceeds the maximum allowed states %d\n' % cas.MAX_ENUM_STATES)
            enums = enums[:cas.MAX_ENUM_STATES]
        self.enums = []
        for enum in enums:
            if len(enum) >= cas.MAX_ENUM_STRING_SIZE:
                sys.stderr.write('enums state "%s" exceeds the maximum length %d\n'
                                 % (enum, cas.MAX_ENUM_STRING_SIZE-1))
                enum = enum[:cas.MAX_ENUM_STRING_SIZE-1]
            self.enums.append(enum)
        self.states = info.get('states', [])
        # initialize enum severity states if not specified
        if not self.states:
            self.states = len(self.enums) * [Severity.NO_ALARM]
        self.prec = info.get('prec', 0.0)
        self.unit = info.get('unit', '')
        self.lolim = info.get('lolim', 0.0)
        self.hilim = info.get('hilim', 0.0)
        self.hihi = info.get('hihi', 0.0)
        self.lolo = info.get('lolo', 0.0)
        self.high = info.get('high', 0.0)
        self.low = info.get('low',  0.0)
        self.adel = info.get('adel', 0.0)
        self.mdel = info.get('mdel', 0.0)
        self.scan = info.get('scan', 0)
        self.asyn = info.get('asyn', False)
        self.asg = info.get('asg', '')
        self.reason = ''
        self.port = info.get('port', 'default')
        # validate alarm limit
        self.valid_low_high = False
        self.valid_lolo_hihi = False
        self.validateLimit()

        # initialize value based on type and count
        if self.type in [cas.aitEnumString, cas.aitEnumFixedString, cas.aitEnumUint8]:
            value = ''
        else:
            value = 0
        if self.count > 1 and self.type is not cas.aitEnumUint8:
            value = [value] * self.count
        self.value = info.get('value', value)
        # initialize last monitor/archive value
        self.mlst = self.value
        self.alst = self.value

    def validateLimit(self):
        # validate alarm limit
        if self.lolo >= self.hihi:
            self.valid_lolo_hihi = False
        else:
            self.valid_lolo_hihi = True

        if self.low >= self.high:
            self.valid_low_high = False
        else:
            self.valid_low_high = True

    def checkValue(self, newValue):
        """Check value change event"""
        mask = 0
        # array type always gets notified
        if self.count > 1:
            mask = (cas.DBE_LOG | cas.DBE_VALUE)
        # string type's equality is checked
        elif self.type in [cas.aitEnumString, cas.aitEnumFixedString]:
            if self.mlst != newValue:
                mask |= cas.DBE_VALUE
                self.mlst = newValue
            if self.alst != newValue:
                mask |= cas.DBE_LOG
                self.alst = newValue
        # scalar numeric type is checked against archive and monitor deadband
        else:
            if abs(self.mlst - newValue) > self.mdel:
                mask |= cas.DBE_VALUE
                self.mlst = newValue
            if abs(self.alst - newValue) > self.adel:
                mask |= cas.DBE_LOG
                self.alst = newValue
        return mask

    def checkAlarm(self, value):
        if self.type == cas.aitEnumEnum16:
            return self._checkEnumAlarm(value)
        elif self.type in [cas.aitEnumFloat64, cas.aitEnumInt32, cas.aitEnumInt16]:
            return self._checkNumericAlarm(value)
        elif self.type in [cas.aitEnumString, cas.aitEnumFixedString, cas.aitEnumUint8]:
            return Alarm.NO_ALARM, Severity.NO_ALARM
        else:
            return None, None

    def _checkNumericAlarm(self, value):
        severity = Severity.NO_ALARM
        alarm = Alarm.NO_ALARM

        if self.valid_low_high:
            if self._compareNumeric(value, self.low, operator.le):
                alarm = Alarm.LOW_ALARM
                severity = Severity.MINOR_ALARM
            elif self._compareNumeric(value, self.high, operator.ge):
                alarm = Alarm.HIGH_ALARM
                severity = Severity.MINOR_ALARM

        if self.valid_lolo_hihi:
            if self._compareNumeric(value, self.lolo, operator.le):
                alarm = Alarm.LOLO_ALARM
                severity = Severity.MAJOR_ALARM
            elif self._compareNumeric(value, self.hihi, operator.ge):
                alarm = Alarm.HIHI_ALARM
                severity = Severity.MAJOR_ALARM

        return alarm, severity

    def _checkEnumAlarm(self, value):
        if 0 <= value < len(self.states):
            severity = self.states[value]
            if severity == Severity.NO_ALARM:
                alarm = Alarm.NO_ALARM
            else:
                alarm = Alarm.STATE_ALARM
        else:
            severity = Severity.MAJOR_ALARM
            alarm = Alarm.STATE_ALARM

        return alarm, severity

    def _compareNumeric(self, value, limit, op):
        """
        Compare value and limit with comparison operator.

        :param value: numeric scalar or sequence
        :param limit: numeric scalar
        :param op: comparision operators, le, ge etc
        """
        if isinstance(value, Iterable):
            return any(op(v, limit) for v in value)
        else:
            return op(value, limit)


class SimplePV(cas.casPV):
    """
    This class represent the PV entity and its associated attributes.

    It is to be created by server application on startup.
    It derives from :cpp:class:`PV` and implements the virtual methods.

    .. note:: This is considered an internal class and should not be referenced by module users.
    """
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
                # read value from driver and write to driver's param database
                newValue = driver.read(self.info.reason)
                driver.setParam(self.info.reason, newValue)
                # post update events if necessary
                dbValue = driver.getParamDB(self.info.reason)
                if dbValue.flag:
                    dbValue.flag = False
                    self.updateValue(dbValue)
                    dbValue.mask = 0
            time.sleep(self.info.scan)

    def interestRegister(self):
        self.interest = True
        return cas.S_casApp_success

    def interestDelete(self):
        self.interest = False

    def writeValue(self, gddValue):
        # get driver object
        driver = manager.driver.get(self.info.port)
        if not driver:
            logging.getLogger('pcaspy.SimplePV.writeValue').\
                warning('%s: No driver is registered for port %s', self.info.reason, self.info.port)
            return cas.S_casApp_undefined
        # call out driver support
        success = driver.write(self.info.reason, gddValue.get())
        if success is False:
            logging.getLogger('pcaspy.SimplePV.writeValue').\
                warning('%s: Driver rejects value %s', self.info.reason, gddValue.get())
            driver.setParamStatus(self.info.reason, Alarm.WRITE_ALARM, Severity.INVALID_ALARM)
        driver.updatePV(self.info.reason)
        return success

    def write(self, context, value):
        # delegate asynchronous write to python writeNotify method
        # only if writeNotify not present in C++ library
        if not cas.EPICS_HAS_WRITENOTIFY and self.info.asyn:
            return self.writeNotify(context, value)
        else:
            self.writeValue(value)
            return cas.S_casApp_success

    def writeNotify(self, context, value):
        # postpone request if one already in process
        if self.hasAsyncWrite():
            return cas.S_casApp_postponeAsyncIO

        # do asynchronous only if PV supports
        if self.info.asyn:
            # register async write io
            self.startAsyncWrite(context)
            # call out driver
            success = self.writeValue(value)
            # if not successful, clean the async write io
            # pass status S_cas_success instead of cas.S_casApp_canceledAsyncIO
            # so that client wont see error message.
            if not success:
                self.endAsyncWrite(cas.S_cas_success)
            # server library expects status S_casApp_asynCompletion if async write io has been initiated.
            return cas.S_casApp_asyncCompletion
        else:
            # call out driver
            success = self.writeValue(value)
            return cas.S_casApp_success

    def updateValue(self, dbValue):
        if not self.interest:
            return

        gddValue = cas.gdd(16, self.info.type)  # gddAppType_value
        if self.info.count > 1:
            gddValue.setDimension(1)
            gddValue.setBound(0, 0, self.info.count)
        gddValue.put(dbValue.value)
        gddValue.setTimeStamp(dbValue.time)
        gddValue.setStatSevr(dbValue.alarm, dbValue.severity)

        if self.info.type == cas.aitEnumEnum16:
            gddCtrl = cas.gdd.createDD(31)  # gddAppType_dbr_ctrl_enum
            gddCtrl[1].put(gddValue)
            gddCtrl[2].put(self.info.enums)
        elif self.info.type == cas.aitEnumString:  # string type has no control info
            gddCtrl = gddValue
        else:
            gddCtrl = cas.gdd.createDD(_dbr_d[self.info.type])  # gddAppType_dbr_ctrl_xxx
            gddCtrl[1].put(self.info.unit)
            gddCtrl[2].put(self.info.low)
            gddCtrl[3].put(self.info.high)
            gddCtrl[4].put(self.info.lolo)
            gddCtrl[5].put(self.info.hihi)
            gddCtrl[6].put(self.info.lolim)
            gddCtrl[7].put(self.info.hilim)
            gddCtrl[8].put(self.info.lolim)
            gddCtrl[9].put(self.info.hilim)
            if self.info.type == cas.aitEnumFloat64:
                gddCtrl[10].put(self.info.prec)
                gddCtrl[11].put(gddValue)
            else:
                gddCtrl[10].put(gddValue)

        self.postEvent(dbValue.mask, gddCtrl)

    def getValue(self, value):
        # get driver object
        driver = manager.driver.get(self.info.port)
        if not driver:
            logging.getLogger('pcaspy.SimplePV.getValue')\
                .warning('%s: No driver is registered for port %s', self.info.reason, self.info.port)
            return cas.S_casApp_undefined
        # set gdd type if necessary
        if value.primitiveType() == cas.aitEnumInvalid:
            value.setPrimType(self.info.type)
        # set gdd value
        if self.info.scan > 0:
            newValue = driver.getParam(self.info.reason)
        else:
            newValue = driver.read(self.info.reason)
        if newValue is None:
            logging.getLogger('pcaspy.SimplePV.getValue')\
                .warning('%s: Driver returns None', self.info.reason)
            return cas.S_casApp_undefined
        logging.getLogger('pcaspy.SimplePV.getValue')\
            .debug('%s: Read value %s', self.info.reason, newValue)
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
        if self.info.enums:
            enums.put(self.info.enums)
        return cas.S_casApp_success

    def getHighLimit(self, hilim):
        hilim.put(self.info.hilim)
        return cas.S_casApp_success

    def getLowLimit(self, lolim):
        lolim.put(self.info.lolim)
        return cas.S_casApp_success

    def getHighAlarmLimit(self, hilim):
        hilim.put(self.info.hihi)
        return cas.S_casApp_success

    def getLowAlarmLimit(self, lolim):
        lolim.put(self.info.lolo)
        return cas.S_casApp_success

    def getHighWarnLimit(self, hilim):
        hilim.put(self.info.high)
        return cas.S_casApp_success

    def getLowWarnLimit(self, lolim):
        lolim.put(self.info.low)
        return cas.S_casApp_success

    def bestExternalType(self):
        return self.info.type

    def maxDimension(self):
        if self.info.count > 1:
            return 1
        else:
            return 0

    def maxBound(self, dims):
        if dims == 0:
            return self.info.count
        else:
            return 0

    def getName(self):
        return self.name


class SimpleServer(cas.caServer):
    """
    This class encapsulates transactions performed by channel access server.
    It stands between the channel access client and the driver object.
    It answers the basic channel access discover requests and forwards the
    read/write requests to driver object.

    It derives from :cpp:class:`caServer`. In addition to implement the virtual methods,
    it adds method :meth:`createPV` to create the PVs and :meth:`process` to process server requests.
    ::

        server = SimpleServer()
        server.createPV(prefix, pvdb)
        while True:
            server.process(0.1)

    """
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

    @staticmethod
    def createPV(prefix, pvdb):
        """
        Create PV based on prefix and database definition pvdb

        :param str prefix:          Name prefixing the *base_name* defined in *pvdb*
        :param dict pvdb:           PV database configuration

        pvdb is a Python *dict* assuming the following format,
        ::

          pvdb = {
            'base_name' : {
              'field_name' : value,
            },
          }

        The base_name is unique and will be prefixed to create PV full name.
        This PV configuration is expressed again in a dict. The *field_name*
        is used to configure the PV properties.

        .. _database-field-definition:
        .. table:: Database Field Definition

          ========  =======    ===============================================
          Field     Default    Description
          ========  =======    ===============================================
          type      'float'    PV data type. enum, string, char, float or int
          count     1          Number of elements
          enums     []         String representations of the enumerate states
          states    []         Severity values of the enumerate states.
                               Any of the following, Severity.NO_ALARM, Severity.MINOR_ALARM,
                               Severity.MAJOR_ALARM, Severity.INVALID_ALARM
          prec      0          Data precision
          unit      ''         Physical meaning of data
          lolim     0          Data low limit for graphics display
          hilim     0          Data high limit for graphics display
          low       0          Data low limit for alarm
          high      0          Data high limit for alarm
          lolo      0          Data low low limit for alarm
          hihi      0          Data high high limit for alarm
          adel      0          Archive deadband
          mdel      0          Monitor, value change deadband
          scan      0          Scan period in second. 0 means passive
          asyn      False      Process finishes asynchronously if True
          asg       ''         Access security group name
          value     0 or ''    Data initial value
          ========  =======    ===============================================

        The data type supported has been greatly reduced from C++ PCAS to match Python native types.
        Numeric types are 'float' and 'int', corresponding to DBF_DOUBLE and DBF_LONG of EPICS IOC.
        The display limits are defined by *lolim* abd *hilim*.
        The alarm limits are defined by *low*, *high*, *lolo*, *hihi*.

        Fixed width string, 40 characters as of EPICS 3.14, is of type 'string'.
        Long string is supported using 'char' type and specify the *count* field large enough.
        'enum' type defines a list of choices by *enums* field, and optional associated severity by *states*.

        The *adel* and *mdel* fields specify the deadbands to trigger an archive and value change event respectively.

        *asyn* if set to be True. Any channel access client write with callback option, i.e. calling `ca_put_callback`,
        will be noticed only when :meth:`Driver.callbackPV` being called.

        """
        for basename, pvinfo in pvdb.items():
            pvinfo = PVInfo(pvinfo)
            pvinfo.reason = basename
            pvinfo.name = prefix + basename
            pv = SimplePV(pvinfo.name, pvinfo)
            manager.pvf[pvinfo.name] = pv
            if pvinfo.port not in manager.pvs:
                manager.pvs[pvinfo.port] = {}
            manager.pvs[pvinfo.port][basename] = pv

    @staticmethod
    def initAccessSecurityFile(filename, **subst):
        """
        Load access security configuration file

        :param str filename:    Name of the access security configuration file
        :param subst:           Substitute macros specified by keyword arguments

        .. note::
            This must be called before :meth:`createPV`.

        """
        macro = ','.join(['%s=%s' % (k, v) for k, v in subst.items()])
        cas.asInitFile(filename, macro)
        cas.asCaStart()

    @staticmethod
    def process(delay):
        """
        Process server transactions.

        :param float delay: Processing time in second

        This method should be called so frequent so that the incoming channel access
        requests are answered in time. Normally called in the loop::

            server = SimpleServer()
            ...
            while True:
                server.process(0.1)


        """
        cas.process(delay)
