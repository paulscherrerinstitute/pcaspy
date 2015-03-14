Please refer [Documents Site](https://pcaspy.readthedocs.org/en/latest/api.html#pcaspy.SimpleServer.createPV) for a better version. **This page will be deleted in the future.**

PV database is defined by a Python dictionary.
```
pvdb = {
    'PVNAME' : {
        'field' : value
    }

}
```
The keys are PV base name and the values are pairs of 'field' : value. The possible fields are summarized in the table.

| **Field** | **Options** | **Default** | **Description** |
|:----------|:------------|:------------|:----------------|
| type | `enum`, `string`, `char`, `float` or `int` | `float` | PV data type |
| count | positive integer number | 1 | Number of elements |
| enums | string list | empty list `[]` | String representations when type is `enum` |
| states | list of severity state. Possible states are `Severity.NO_ALARM`,` Severity.MINOR_ALARM`, `Severity.MAJOR_ALARM`, `Severity.INVALID_ALARM` | empty list `[]` | Severity states when type is `enum` |
| prec | positive integer number | 0 | Precision when type is 'float' |
| unit  | string | empty string | Physical meaning of data |
| lolim | float number | 0.0 | Data low limit for graphics display|
| hilim | float number | 0.0 | Data high limit for graphics display|
| low | float number | 0.0 | Data low limit for alarm |
| high | float number | 0.0 | Dat high limit for alarm |
| lolo | float number | 0.0 | Data low low limit for alarm |
| hihi | float number | 0.0 | Data high high limit for alarm |
| scan  | float number | 0.0 | Data scan period. 0.0 means passive |
| asyn | boolean | False | PV data process finishes asynchronously or not |
| asg | string | empty string | Access security group name |
| value | python builtin data type | 0 or '' | Initial value |