

# Introduction #

The portable channel access server in EPICS base consists of several C++ classes to be implemented by server tools. Here is a description of these classes and their respective Python binding.


# gdd #
The C++ document is at http://www.aps.anl.gov/epics/EpicsDocumentation/EpicsGeneral/gdd.html.
In short gdd is used between server tool and server library to exchange data. gdd is a general data container for most data types. In addition, it contains the properties of the data, e.g. dimension, timestamp, unit, limits.
## Reference Count ##
**C++**: gdd can only be created on heap and is reference counted. When a gdd value is passed in as function argument, if user needs to keep it for later use, user needs to reference it first and unreference it after use.
When a gdd value is created, it is automatically referenced once.

**Python**: when the python proxy object is deleted, it unreferences the underlying C++ object.

## put/get Methods ##
### `put` ###
It accepts and the following data types,
  * int, float, bool, long, str
  * numpy basic data types
  * sequence of the above data types
If primitiveType is aitEnumInvalid, numeric data are stored as aitEnumFloat64 and string data are stored as aitEnumString.
Otherwise the input data is converted to primitiveType.

### `get` ###
  * Scalar:
    * aitEnumFloat32 and aitEnumFloat64: float
    * aitEnumString and aitEnumFixedString: str
    * aitEnumUint8 and aitEnumInt8: str (of one character)
    * Others: int
  * Array:
    * aitEnumUint8 and aitEnumInt8: str
    * Others: a list based on the above rules.

# casServer #
Two methods must be implemented:
  * `pvExistTest`: check PV existence.
  * `pvAttach`: return existing PV.

## Python Only Methods ##
  * `createPV (prefix, pvdb)`: create PVs from `prefix` and `pvdb` dictionary.
  * `process (time)`: process request for given `time`.

# casPV #
The orignal `casPV` class does not provide gdd read functions. A `PV` C++ class is created to use gddAppTable function table to provide gdd read methods. The following methods need to be implemented depending on PV type.
  * `write`
  * `getValue`
  * `getUnits`
  * `getHighLimit`
  * `getLowLimit`
  * `getEnums`
  * `getPrecision`
  * `bestExternalType`
  * `getName`
In the Python side, this `PV` class shadows the original `casPV` class.