#!/usr/bin/env python

"""
setup.py file for pcaspy
"""

try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    # 2.x
    from distutils.command.build_py import build_py

from distutils.core import setup, Extension
import os, platform, sys

if sys.version_info[0] > 2:
    raw_input = input

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
libraries = ['ca', 'Com', 'gdd','cas']
macros = []
cflags = []
# platform dependent libraries and macros
UNAME = platform.system()
if  UNAME.find('CYGWIN') == 0:
    UNAME = "cygwin32"
elif UNAME == 'Windows':
    UNAME = 'WIN32'
    libraries += ['ws2_32', 'msvcrt', 'user32', 'advapi32']
    macros += [('_CRT_SECURE_NO_WARNINGS', 'None')]
    cflags += ['/MT']
cas_module = Extension('pcaspy._cas',
                            sources  =[os.path.join('pcaspy','casdef.i'), 
                                       os.path.join('pcaspy','pv.cpp'),
                                       os.path.join('pcaspy','channel.cpp'),],
                            swig_opts=['-c++','-threads','-nodefaultdtor','-I%s'% os.path.join(EPICSBASE, 'include')],
                            extra_compile_args=cflags,
                            include_dirs = [ os.path.join(EPICSBASE, 'include'),
                                             os.path.join(EPICSBASE, 'include', 'os', UNAME),
                                           ],
                            library_dirs = [ os.path.join(EPICSBASE, 'lib', HOSTARCH),
                                           ],
                            libraries = libraries,
                            define_macros = macros,
                    )
# *NIX linker has runtime library path option
if UNAME != 'WIN32':
    cas_module.runtime_library_dirs += os.path.join(EPICSBASE, 'lib', HOSTARCH),

long_description = open('README').read()

setup (name = 'pcaspy',
       version = '0.3',
       description = """Portable Channel Access Server in Python""",
       long_description = long_description,
       author      = "Xiaoqiang Wang",
       author_email= "xiaoqiangwang@gmail.com",
       url         = "http://code.google.com/p/pcaspy/",
       ext_modules = [cas_module],
       packages    = ["pcaspy"],
       cmdclass    = {'build_py':build_py, 'build_ext':build_ext},
       license     = "GPLv3",
       platforms   = ["Windows","Linux", "Mac OS X"],
       classifiers = [
            'Development Status :: 4 - Beta',
            'Environment :: Console', 
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: C++',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 3',
           ],
       )

