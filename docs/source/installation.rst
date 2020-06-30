.. _installation-label:

Installation
============

Binary Installers
-----------------

Anaconda
~~~~~~~~
Packages for Anaconda can be installed via::

    conda install -c paulscherrerinstitute pcaspy

Wheel
~~~~~
The binary packages are distributed at `PyPI <https://pypi.python.org/pypi/pcaspy>`_.
They have EPICS 3.14.12.6 libraries statically builtin. Make sure you have `pip <https://pypi.python.org/pypi/pip>`_ and
`wheel <https://pypi.python.org/pypi/wheel>`_  installed, and run::

    $ sudo pip install pcaspy # macOS
    > C:\Python27\Scripts\pip.exe install pcaspy :: Windows


.. note:: On Windows, if you see error message "The program can't start because MSVCRxxx.dll is missing from your computer." when importing pcaspy, you might need to install the proper `Visual C++ Redistributable <https://support.microsoft.com/en-us/help/2977003/the-latest-supported-visual-c-downloads>`_.

Egg
~~~
PyPI does not allow upload linux-specific wheels package, yet (as of 2014).
The old *egg* format is used then::

    $ sudo easy_install pcaspy

Or install only for the current user::

    $ easy_install --user pcaspy


Source
------
If no binary package is available for your system, you can build from source.
And then you would need EPICS base installed, see :ref:`getting-epics`.

The source can be downloaded in various ways:

  * The released source tarballs can be found at `PyPI <https://pypi.python.org/pypi/pcaspy>`_.
  * From the `git repository <https://github.com/paulscherrerinstitute/pcaspy/releases>`_,
    each release can be downloaded as a zip package.
  * Clone the repository if you feel adventurous::

    $ git clone https://github.com/paulscherrerinstitute/pcaspy.git


.. _getting-epics:

Getting EPICS
~~~~~~~~~~~~~
In general please follow `the official installation instruction <http://www.aps.anl.gov/epics/base/R3-14/12-docs/README.html>`_.
Here is a short guide,

- Get the source tarball from http://www.aps.anl.gov/epics/base/R3-14/12.php.
- Unpack it to a proper path.
- Set the following environment variables:

  - EPICS_BASE : the path containing the EPICS base source tree.
  - EPICS_HOST_ARCH : EPICS is built into static libraries on Windows.

    +---------+-------+--------------------+
    |    OS   | Arch  | EPICS_HOST_ARCH    |
    +=========+=======+====================+
    |         | 32bit | linux-x86          |
    | Linux   +-------+--------------------+
    |         | 64bit | linux-x86_64       |
    +---------+-------+--------------------+
    |         | 32bit | win32-x86-static   |
    | Windows +-------+--------------------+
    |         | 64bit | windows-x64-static |
    +---------+-------+--------------------+
    |         | PPC   | darwin-ppcx86      |
    |  OS X   +-------+--------------------+
    |         | Intel | darwin-x86         |
    +---------+-------+--------------------+

- From EPICS 7 onwards, PCAS library is not any more distributed in EPICS base. In the official document, it
  suggests building PCAS as epics module. However to simplify the build process, you are suggested to still
  build PCAS library together with EPICS base.

  - Download source from https://github.com/epics-modules/pcas/releases
  - Unpack its contents to <EPICS_BASE>/modules/pcas
  - Create <EPICS_BASE>/modules/Makefile.local, with the following contents::
  
        SUBMODULES += pcas
        pcas_DEPEND_DIRS = libcom

  - As long as v4.13.2 is the latest release of pcas, add ``-include $(TOP)/../RELEASE.$(EPICS_HOST_ARCH).local``
    to the end of <EPICS_BASE>/modules/pcas/configure/RELEASE.
- Run ``make``.

.. note:: On windows, the Visual Studio version has to match that used to build Python.

          +------------------+-----------------------+
          | Python Version   | Visual Studio Version |
          +==================+=======================+
          | 2.6 - 2.7,       |                       |
          | 3.0 - 3.2        |  2008                 |
          +------------------+-----------------------+
          | 3.3 - 3.4        |  2010                 |
          +------------------+-----------------------+
          | 3.5 - 3.6        |  2015                 |
          +------------------+-----------------------+

          Mismatching may cause crashes!

Windows
~~~~~~~
- Python 2.6+ including 3.x (http://www.python.org/download/)
- SWIG 1.3.29+ is required. Get it from http://www.swig.org/download.html and unpack to ``C:\Program Files (x86)\SWIG\``.

Download the most recent source tarball, uncompress and run::

    > set PATH=%PATH%;C:\Program Files (x86)\SWIG\
    > C:\Python27\python.exe setup.py build install


Linux
~~~~~
- Python 2.6+ including 3.x
- Python headers (package name "python-dev" or similar)
- SWIG 1.3.29+ (package name "swig")

In the source directory, run::

    $ sudo python setup.py install

or install only for the current user::

    $ python setup.py build install --user

.. note:: You might need to pass *-E* flag to sudo to preserve the EPICS environment variables. If your user account
          is not allowed to do so, a normal procedure should be followed, ::

              $ su -
              # export EPICS_BASE=<epics base path>
              # export EPICS_HOST_ARCH=<epics host arch>
              # python setup.py install
            
macOS
~~~~~
- SWIG (MacPorts package "swig-python")

In the source directory, run::

    $ sudo python setup.py install


Package
-------
After the build succeeds, you may want to create a package for distribution.

Anaconda
~~~~~~~~
Conda recipe is included::

    $ conda build -c paulscherrerinstitute conda-recipe

Wheel
~~~~~
::

    $ python setup.py bdist_wheel

RPM
^^^
The spec file *python-pcaspy.spec* is included. Get the source tarball either from PyPI or create it by
``python setup.py sdist``, and run::

    $ rpmbuild -ta pcaspy-0.6.3.tar.gz

The binary and source RPM will be created. The package name is *python-pcaspy*.
