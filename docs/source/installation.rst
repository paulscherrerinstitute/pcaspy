Installation
============

Getting EPICS
-------------
In general please follow http://www.aps.anl.gov/epics/base/R3-14/12-docs/README.html.

On Windows, EPICS libraies are already built in the installer. 
If you need to build from source, it is suggested to  build EPICS libraries 
statically by changeing these two lines in ``EPICS_BASE/configure/CONFIG_SITE``::

    SHARED_LIBRARIES=NO
    STATIC_BUILD=YES

And one has to use same version Visual Studio as the one used to build Python.

+------------------+-----------------------+
| Python Version   | Visual Studio Version |
+==================+=======================+
| 2.4 - 2.5        |  2003                 |
+------------------+-----------------------+
| 2.6 - 2.7,       |                       |
| 3.0 - 3.2        |  2008                 |
+------------------+-----------------------+
| 3.3 - 3.4        |  2010                 |
+------------------+-----------------------+

Mismatching may cause crashes!


Here is a short guide,

- Get the source tarball from http://www.aps.anl.gov/epics/base/R3-14/12.php.
- Unpack it to a proper path.
- Set the following environment variables:

  - EPICS_BASE : the path containing the EPICS base installation. 
  - EPICS_HOST_ARCH :

    +---------+-------+-----------------+
    |    OS   | Arch  | EPICS_HOST_ARCH |
    +=========+=======+=================+
    |         | 32bit | linux-x86       |
    | Linux   +-------+-----------------+
    |         | 64bit | linux-x86_64    |
    +---------+-------+-----------------+
    |         | 32bit | win32-x86       |
    | Windows +-------+-----------------+
    |         | 64bit | windows-x64     |
    +---------+-------+-----------------+
    |         | PPC   | darwin-ppcx86   |
    |  OS X   +-------+-----------------+
    |         | Intel | darwin-x86      |
    +---------+-------+-----------------+

- Run ``make``.

Windows
-------
- Python 2.4+ including 3.x (http://www.python.org/download/)

The installer from project page installs PCASpy with EPICS libraries statically builtin.

To build from source, SWIG 1.3.29+ is required. Get it from 
http://www.swig.org/download.html and unpack to ``C:\Program Files (x86)\SWIG\``.

Download the most recent source tarball, uncompress and run::

    > set PATH=%PATH%;C:\Program Files (x86)\SWIG\
    > C:\Python27\python.exe setup.py build


Linux/Mac OS X
--------------
- Python 2.4+ including 3.x
- Python headers (package name "python-dev" or similar)
- SWIG 1.3.29+
- EPICS 3.14.8+

Download the most recent source tarball, uncompress and run::

    $ python setup.py build
    $ [sudo] python setup.py install
