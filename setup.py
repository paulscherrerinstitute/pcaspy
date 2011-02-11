#!/usr/bin/env python

"""
setup.py file for pyCAS
"""

from distutils.core import setup, Extension
import os, platform

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
cas_module = Extension('pcas._cas',
                            sources  =[os.path.join('pcas','casdef.i'), 
                                       os.path.join('pcas','pv.cpp'),],
                            swig_opts=['-c++','-nodefaultdtor','-I%s'% os.path.join(EPICSBASE, 'include')],
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

setup (name = 'pcas',
       version = '0.1',
       description = """python channel access server""",
       author      = "Xiaoqiang Wang",
       author_email= "xiaoqiangwang@gmail.com",
       url         = "http://code.google.com/p/pcas/",
       ext_modules = [cas_module],
       packages   = ["pcas"],
       )

