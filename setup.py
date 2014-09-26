#!/usr/bin/env python

"""
setup.py file for pcaspy
"""
# Use setuptools to include build_sphinx, upload/sphinx commands
try:
    from setuptools import setup
except:
    pass

# Use 2to3 to support Python 3
try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    # 2.x
    from distutils.command.build_py import build_py

from distutils.core import setup, Extension
import os
import platform
import sys
import imp

# raw_input is renamed to input in Python 3
if sys.version_info[0] > 2:
    raw_input = input

# Python 2.4 below does not check the -c++ option in setup
# This is a workaound.
from distutils.command.build_ext import build_ext as _build_ext
if sys.hexversion < 0x02050000:
    class build_ext(_build_ext):
        def initialize_options (self):
            _build_ext.initialize_options(self)
            self.swig_cpp = True
else:
    build_ext = _build_ext

# define EPICS base path and host arch
EPICSBASE = os.environ.get("EPICS_BASE")
if not EPICSBASE:
    EPICSROOT = os.environ.get("EPICS")
    if EPICSROOT:
        EPICSBASE = os.path.join(EPICSROOT, 'base')
if not EPICSBASE or not os.path.exists(EPICSBASE):
    raise IOError("Please define EPICS_BASE environment variable")

HOSTARCH  = os.environ.get("EPICS_HOST_ARCH")
if not HOSTARCH:
    raise IOError("Please define EPICS_HOST_ARCH environment variable")

# common libraries to link
libraries = ['asIoc', 'cas', 'ca', 'gdd', 'Com']
umacros = []
macros   = []
cflags = []
lflags = []
# platform dependent libraries and macros
UNAME = platform.system()
if  UNAME.find('CYGWIN') == 0:
    UNAME = "cygwin32"
elif UNAME == 'Windows':
    UNAME = 'WIN32'
    libraries += ['ws2_32', 'user32', 'advapi32']
    # MSVC compiler
    if HOSTARCH in ['win32-x86', 'windows-x64', 'win32-x86-debug', 'windows-x64-debug']:
        macros += [('_CRT_SECURE_NO_WARNINGS', 'None'), ('EPICS_DLL_NO', '')]
        cflags += ['/EHsc']
        lflags += ['/LTCG']
        if HOSTARCH[-5:] == 'debug':
            libraries += ['msvcrtd']
            lflags += ['/NODEFAULTLIB:libcmtd.lib']
        else:
            libraries += ['msvcrt']
            lflags += ['/NODEFAULTLIB:libcmt.lib']
    # GCC compiler
    if HOSTARCH in ['win32-x86-mingw', 'windows-x64-mingw']:
        macros += [('_MINGW', ''), ('EPICS_DLL_NO', '')]
        lflags += ['-static',]
    if HOSTARCH == 'windows-x64-mingw':
        macros += [('MS_WIN64', '')]
    umacros+= ['_DLL']
cas_module = Extension('pcaspy._cas',
                       sources  =[os.path.join('pcaspy','casdef.i'),
                                  os.path.join('pcaspy','pv.cpp'),
                                  os.path.join('pcaspy','channel.cpp'),],
                       swig_opts=['-c++','-threads','-nodefaultdtor','-I%s'% os.path.join(EPICSBASE, 'include')],
                       extra_compile_args=cflags,
                       include_dirs = [ os.path.join(EPICSBASE, 'include'),
                                        os.path.join(EPICSBASE, 'include', 'os', UNAME),],
                       library_dirs = [ os.path.join(EPICSBASE, 'lib', HOSTARCH),],
                       libraries = libraries,
                       extra_link_args = lflags,
                       define_macros = macros,
                       undef_macros  = umacros,)
# *NIX linker has runtime library path option
if UNAME != 'WIN32':
    cas_module.runtime_library_dirs += os.path.join(EPICSBASE, 'lib', HOSTARCH),

long_description = open('README').read()
_version = imp.load_source('_version','pcaspy/_version.py')

dist = setup (name = 'pcaspy',
       version = _version.__version__,
       description = """Portable Channel Access Server in Python""",
       long_description = long_description,
       author      = "Xiaoqiang Wang",
       author_email= "xiaoqiangwang@gmail.com",
       url         = "http://code.google.com/p/pcaspy/",
       ext_modules = [cas_module],
       packages    = ["pcaspy"],
       cmdclass    = {'build_py':build_py, 'build_ext':build_ext},
       license     = "BSD",
       platforms   = ["Windows","Linux", "Mac OS X"],
       classifiers = ['Development Status :: 4 - Beta',
                      'Environment :: Console',
                      'Intended Audience :: Developers',
                      'License :: OSI Approved :: BSD License',
                      'Programming Language :: C++',
                      'Programming Language :: Python :: 2',
                      'Programming Language :: Python :: 3',
                      ],
       )

# Re-run the build_py to ensure that swig generated py files are also copied
build_py = build_py(dist)
build_py.ensure_finalized()
build_py.run()
