
.. py:currentmodule:: pcaspy

Development
===========

The PCAS library is part of EPICS base. In version 3.14 it is found at `src/gdd` and `src/cas`.
In version 3.15 it is found at `src/ca/legacy/gdd` and `src/ca/legacy/cas`.
The library implements the channel access protocol. A server application could respond
to the CA requests, when it implements the following interfaces.

caServer
--------

.. cpp:class:: caServer


The virtual methods are,

    .. cpp:function:: pvExistReturn pvExistTest(const casCtx & ctx, const caNetAddr & clientAddress, const char * pPVAliasName)

       This function is called by the server library when it needs to determine if a named PV exists (or could be created)
       in the server application.
       This method should return *pverExistsHere* if server has this PV or *pverDoesNotExistHere* otherwise.

    .. cpp:function:: pvAttachReturn pvAttach ( const casCtx &ctx, const char *pPVAliasName )

       This function is called **every** time that a client attaches to the PV. It should return a :cpp:class:`PV` pointer
       on success, S_casApp_pvNotFound if this PV does not exist here.

The Python class :class:`SimpleServer` implements this interface.

casPV
-----

This is the basic entity representing a piece of data, with associated information like units, limits, alarm, timestamp etc.
The C++ class `casPV` abstracts the interface to access the PV value. :cpp:class:`PV` derives from `casPV` and further defines
the interface to access the PV associated information. In addition it adds helper functions for asynchronous write.

.. cpp:class:: PV

Virtual methods
~~~~~~~~~~~~~~~

    .. cpp:function:: const char * getName()

       Return the canonical (full) name for the PV.

    .. cpp:function:: unsigned maxDimension()
    .. cpp:function:: aitIndex maxBound(unsigned dimension)

       =========      ============  ========
       Type           maxDimension  maxBound
       =========      ============  ========
       Scalar         0             1
       1D Array       1             number of elements in array
       =========      ============  ========

    .. cpp:function:: caStatus getValue(gdd & value)

       The PV value.

    .. cpp:function:: caStatus getPrecision(gdd & value)

       The PV precision.

    .. cpp:function:: caStatus getUnits(gdd & value)

      The PV units.

    .. cpp:function:: caStatus getEnums(gdd & value)

      The PV enumerated states.

    .. cpp:function:: caStatus getLowLimit(gdd & value)
    .. cpp:function:: caStatus getHighLimit(gdd & value)

      The PV display/control limit

    .. cpp:function:: caStatus getLowAlarmLimit(gdd & value)
    .. cpp:function:: caStatus getHighAlarmLimit(gdd & value)

      The PV alarm limit

    .. cpp:function:: caStatus getLowWarnLimit(gdd & value)
    .. cpp:function:: caStatus getHighWarnLimit(gdd & value)

      The PV warning limit

    .. cpp:function:: caStatus write(const casCtx & ctx, const gdd & value)
    .. cpp:function:: caStatus writeNotify(const casCtx & ctx, const gdd & value)

      The write interface is called when the server receives
      ca_put request and the writeNotify interface is called
      when the server receives ca_put_callback request.

      A writeNotify request is considered complete and therefore
      ready for asynchronous completion notification when any
      action that it initiates, and any cascaded actions, complete.

      Return S_casApp_postponeAsyncIO if too many simultaneous
      asynchronous IO operations are pending against the PV.
      The server library will retry the request whenever an
      asynchronous IO operation (read or write) completes
      against the PV.

    .. cpp:function:: caStatus interestRegister()

      Called by the server library each time that it wishes to
      subscribe for PV change notification from the server
      tool via :cpp:func:`postEvent`.

    .. cpp:function:: caStatus interestDelete()

      Called by the server library each time that it wishes to
      remove its subscription for PV value change events.

Helper methods
~~~~~~~~~~~~~~
    .. cpp:function:: caStatus postEvent(int mask, const gdd & event)

      Server application calls this function to post a PV event.
      The event mask can be any combination of *DBE_VALUE*,  *DBE_LOG*, *DBE_ALARM*, *DBE_PROPERTY*.

    .. cpp:function:: void startAsyncWrite()

      Server application calls this function to initiate asynchronous write operation.
      This must be matched by a call to :cpp:func:`endAsyncWrite`.

    .. cpp:function:: void endAsyncWrite()

      Server application calls this function to end asynchronous write operation.

    .. cpp:function:: bool hasAsyncWrite()

      Return true if one asynchronous write is in progress.

    .. cpp:function:: bool setAccessSecurityGroup(const char * asgName)

      Server application calls this function to set the access security group name.



The Python class :class:`SimplePV` implements this interface.

casChannel
----------

This class could be used to finely control read/write access based on the client or other conditions.
In C++ class `Channel`, the control access is implemented using Access Security Group.
Library user does not need to instantiate this class, it is done inside `PV::createChannel`.
As such this class is not exposed to Python.


.. py:currentmodule:: pcaspy.cas

:class:`gdd`
------------

.. py:class:: gdd

gdd stands for `General Data Descriptor <http://www.aps.anl.gov/epics/EpicsDocumentation/EpicsGeneral/gdd.html>`_.
It is a generic, descriptive data container. Although designed to be generic, its usage in EPICS is limited to
Portable Channel Access Server programming, more specifically in the getters of :class:`pcaspy.SimplePV`.

    .. py:classmethod:: gdd.get()

        Retrieve the data. The gdd primitive types are up cast to Python types.

        +---------------------+---------+
        | gdd                 | Python  |
        +=====================+=========+
        | aitEnumString       |         |
        | aitEnumFixedString  | str     |
        +---------------------+---------+
        | aitEnumFloat32      |         |
        | aitEnumFloat64      | float   |
        +---------------------+---------+
        | aitEnumInt8         |         |
        | aitEnumUint8        | str     |
        +---------------------+---------+
        | aitEnumInt16        |         |
        | aitEnumUint16       |         |
        | aitEnumEnum16       | int     |
        | aitEnumInt32        |         |
        | aitEnumUint32       |         |
        +---------------------+---------+

        .. note:: aitEnumInt8 and aitEnumUint8 are used to store char arrays.

    .. classmethod:: gdd.put(value)

        Store the data. The conversion table.

        +--------------+---------------------------------------------+
        |              |               gdd                           |
        |              +-------------------+-------------------------+
        |              |      Scalar       |      Atomic             |
        |   Input      +---------+---------+----------+--------------+
        |              | numeric | string  | numeric  | string       |
        +==============+=========+=========+==========+==============+
        | gdd          | copy dimension/bound info, then putDD       |
        +--------------+---------------------------------------------+
        | numeric      | putConvertNumeric | putNumericArray(size=1) |
        +--------------+-------------------+-------------------------+
        | string       | putConvertString  | convert to char array   |
        |              |                   | then putCharArray       |
        +------+-------+-------------------+-------------------------+
        | numpy| scalar|          putConvertNumeric                  |
        |      +-------+---------------------------------------------+
        |      | array | putXXXDataBuffer                            |
        +------+-------+---------------------------------------------+
        | sequence     |  setup gdd dimension/bound, then            |
        |              |  put(F)StringArray/putNumericArray          |
        +--------------+---------------------------------------------+

    .. classmethod:: gdd.setPrimType(type)

        Force the GDD to change the primitive type of the data it describes.
        Changing the primitive type code is generally an unnatural thing to do.
        Force a GDD to change the application type, which effectively changes the high-level meaning of the data held within the GDD.

    .. classmethod:: gdd.setStatSevr(status, severity)

        Manipulate the status field of a GDD as a combination status and severity field.

    .. classmethod:: gdd.setTimeStamp()

        Manipulate the time stamp field of the GDD to the current time.

