.. _reference-label:

Reference
=========

.. module:: pcaspy

:class:`SimpleServer`
---------------------
.. autoclass:: SimpleServer

    .. automethod:: createPV(prefix, pvdb)

    .. automethod:: initAccessSecurityFile(asfile, macro)

    .. automethod:: process(time)

:class:`Driver`
---------------
.. autoclass:: Driver

    .. automethod:: __init__()

    .. automethod:: read(reason)

    .. automethod:: write(reason, value)

    .. automethod:: getParam(reason)

    .. automethod:: setParam(reason)

    .. automethod:: setParamStatus(reason, alarm, severity)

    .. automethod:: callbackPV(reason)

    .. automethod:: updatePVs()

:class:`SimplePV`
-----------------
.. autoclass:: SimplePV

.. module:: pcaspy.tools

:class:`ServerThread`
---------------------
.. autoclass:: ServerThread

    .. automethod:: __init__(server)

    .. automethod:: start()

    .. automethod:: stop()


.. py:currentmodule:: pcaspy

Implementation Details
----------------------

The PCAS library is part of EPICS base. In version 3.14 it is found at `src/cas`.
In version 3.15 it is found at `src/ca/legacy/gdd` `src/ca/legacy/cas`.
The library implements the channel access protocol. A server application could respond
to the CA requests, when it implements the following interfaces.

caServer
~~~~~~~~

The virtual methods are,
    * `pvExistTest`: return whether a PV exists in this sever.
    * `pvAttach`:  return a PV instance.

The Python class :class:`SimpleServer` implements this interface.

casPV
~~~~~

This is the basic entity representing a piece of data, with associated information like units, limits, alarm, timestamp etc.
The C++ class `casPV` abstracts the interface to access the PV value. Class `PV` derives from `casPV` and further defines
the interface to access the PV associated information. In addition it adds helper functions for asynchronous write.

The virtual methods are,
    * `getName`: PV fullname
    * `maxBound`: number of elements
    * `maxDimension`: number of dimension. 0 for scalar, 1 for waveform.
    * `getValue`: return the PV value.
    * `getPrevision`: return the PV precision
    * `getUnits`: return the PV units
    * `getEnums`: return the enum PV's states
    * `getLowLimit`: return the PV low limit
    * `getHighLimit`: return the PV high limit
    * `write`: write new value to the PV
    * `interestRegister`: monitor the PV change
    * `interestDelete`: unmonitor the PV change

The helper methods are,
    * `startAsyncWrite`: initiate asynchronous write operation
    * `endAsyncWrite`: end asynchronous write operation

The Python class :class:`SimplePV` implements this interface.

casChannel
~~~~~~~~~~

This class could be used to finely control read/write access based on the client or other conditions.
In C++ class `Channel`, the control access is implemented using Access Security Group.
Library user does not need to instantiate this class, it is done inside `PV::createChannel`.
As such this class is not exposed to Python.