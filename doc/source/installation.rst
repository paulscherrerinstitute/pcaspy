Installation
============

Getting EPICS
-------------
On Windows, EPICS libraies are statically builtin.

On Linux and Mac OS X you need to follow http://www.aps.anl.gov/epics/base/R3-14/12-docs/README.html.
Here is a short guide,

- Get the source tarball from http://www.aps.anl.gov/epics/base/R3-14/12.php.
- Unpack it to a proper path.
- Set the following environment variables:

  - EPICS_BASE : the path containing the EPICS base installation. 
  - EPICS_HOST_ARCH :

    - linux-x86 on 32bit Linux
    - linux-x86_64 on 64bit Linux.
    - darwin-x86 on Mac OS X

- Run "make".

Windows
-------
- Python 2.4+ including 3.x

Download the installer from project page and run it. 
This installs PCASpy with EPICS libraries statically builtin.

Linux/Mac OS X
--------------
- Python 2.4+ including 3.x
- Python headers (package name "python-dev" or similar)
- Swig 1.3.29+
- EPICS 3.14.8+

Download the most recent source tarball, uncompress and run::

    $ python setup.py build
    $ [sudo] python setup.py install
