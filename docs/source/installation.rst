.. _installation-label:

Installation
============

Binary Installers
-----------------
PCASpy has binary installers that has EPICS 3.14.12 libraries statically builtin for Windows and OS X.
Refer to the project `download page <https://code.google.com/p/pcaspy/downloads/list>`_ for installers.

We also provide *wheel* packages. Make sure you have ``pip`` and ``wheel`` package installed, and run::

    # (OS X)
    $ [sudo] pip install pcaspy
    # (Windows)
    > C:\Python27\Scripts\pip.exe install pcaspy

If we do not have a *wheel* for your system. then pip will try to build from source. And then you would need
to have EPICS base installed, see :ref:`getting-epics`.

Source
------
You can get the current source tarball from project download page,

The mercurial repository is at https://code.google.com/p/pcaspy/. You can download the current development
version as a zip package, or clone the repository::

    $ hg clone https://code.google.com/p/pcaspy/

Build
-----

.. _getting-epics:

Getting EPICS
~~~~~~~~~~~~~
In general please follow `the official installation instruction <http://www.aps.anl.gov/epics/base/R3-14/12-docs/README.html>`_.
Here is a short guide,

- Get the source tarball from http://www.aps.anl.gov/epics/base/R3-14/12.php.
- Unpack it to a proper path.
- Set the following environment variables:

  - EPICS_BASE : the path containing the EPICS base source tree.
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

- It is suggested to build EPICS libraries statically on Windows. Change these two lines in ``EPICS_BASE/configure/CONFIG_SITE``::

    SHARED_LIBRARIES=NO
    STATIC_BUILD=YES

- Run ``make``.

Note: On windows, one has to use the same version of Visual Studio as the one used to build Python.

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

Windows
~~~~~~~
- Python 2.4+ including 3.x (http://www.python.org/download/)
- SWIG 1.3.29+ is required. Get it from http://www.swig.org/download.html and unpack to ``C:\Program Files (x86)\SWIG\``.

Download the most recent source tarball, uncompress and run::

    > set PATH=%PATH%;C:\Program Files (x86)\SWIG\
    > C:\Python27\python.exe setup.py build install


Linux / OS X
~~~~~~~~~~~~~~
- Python 2.4+ including 3.x
- Python headers (package name "python-dev" or similar)
- SWIG 1.3.29+

Download the most recent source tarball, uncompress and run::

    $ python setup.py build
    $ [sudo] python setup.py install

