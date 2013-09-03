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
if not EPICSBASE:
    while True:
        EPICSBASE = raw_input("Please define EPICS base path: ")
        if os.path.exists(EPICSBASE):
            break

HOSTARCH  = os.environ.get("EPICS_HOST_ARCH")
if not HOSTARCH:
    HOSTARCH = raw_input("Please define EPICS host arch: ")

# common libraries to link
libraries = ['ca', 'Com', 'gdd','cas', 'asIoc']
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
    libraries += ['ws2_32', 'msvcrt', 'user32', 'advapi32']
    macros += [('_CRT_SECURE_NO_WARNINGS', 'None')]
    cflags += ['/EHsc']
    lflags += ['/LTCG','/NODEFAULTLIB:libcmt.lib']
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

setup (name = 'pcaspy',
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
