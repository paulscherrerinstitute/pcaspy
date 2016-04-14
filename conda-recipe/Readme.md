# Overview
Conda package recipe.

# Usage
```bash
conda install -c https://conda.anaconda.org/paulscherrerinstitute pcaspy
```

# Development

To build the package use:

```bash
conda build -c https://conda.anaconda.org/paulscherrerinstitute conda-recipe
```

__Note:__ The __-c__ option is required as pcaspy is dependent on epics-base that is available on the  https://conda.anaconda.org/paulscherrerinstitute package channel.

## Hints
While packaging pcaspy you might want to test the package in an ipython shell. Make sure that you are not in the pcaspy source folder when you do so. Otherwise you will hit following error:

```
In [2]: import pcaspy
---------------------------------------------------------------------------
ImportError                               Traceback (most recent call last)
<ipython-input-2-a3e041eefa63> in <module>()
----> 1 import pcaspy

/Users/ebner/Git/pcaspy/pcaspy/__init__.py in <module>()
----> 1 from driver import Driver, SimpleServer, PVInfo, SimplePV
      2 from _version import __version__, version_info
      3 from alarm import Severity, Alarm

ImportError: No module named 'driver'
```
