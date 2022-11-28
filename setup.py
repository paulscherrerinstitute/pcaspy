#!/usr/bin/env python

"""
setup.py file for pcaspy
"""
import os
import platform
import sys
import shutil
import subprocess
import filecmp

# Use setuptools to include build_sphinx, upload/sphinx commands
try:
    from setuptools import setup, Extension
    from setuptools.command.build_py import build_py as _build_py
except:
    from distutils.core import setup, Extension
    from distutils.command.build_py import build_py as _build_py

# build_py runs before build_ext so that swig generated module is not copied
# See http://bugs.python.org/issue7562
# This is a workaround to run build_ext ahead of build_py
class build_py(_build_py):
    def run(self):
        self.run_command('build_ext')
        _build_py.run(self)

# python 2/3 compatible way to load module from file
def load_module(name, location):
    if sys.hexversion < 0x03050000:
        import imp
        module = imp.load_source(name, location)
    else:
        import importlib.util
        spec = importlib.util.spec_from_file_location(name, location)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module

# check wether all paths exist
def paths_exist(paths):
    for path in paths:
        if not os.path.exists(path):
            return False
    return True

# define EPICS base path and host arch
EPICSBASE = os.environ.get("EPICS_BASE")
HOSTARCH = os.environ.get("EPICS_HOST_ARCH")
SHARED = os.environ.get("EPICS_SHARED")
# guess from EPICS root environment variable
if not EPICSBASE:
    EPICSROOT = os.environ.get("EPICS")
    if EPICSROOT:
        EPICSBASE = os.path.join(EPICSROOT, 'base')

if not EPICSBASE or not os.path.exists(EPICSBASE) or not HOSTARCH:
    raise IOError("Please define/validate EPICS_BASE and EPICS_HOST_ARCH environment variables")

# check EPICS version
PRE315 = True
if os.path.exists(os.path.join(EPICSBASE, 'include', 'compiler')):
    PRE315 = False

# common libraries to link
libraries = ['cas', 'ca', 'gdd', 'Com']
if PRE315:
    libraries.insert(0, 'asIoc')
else:
    libraries.insert(0, 'dbCore')
umacros = []
macros   = []
cflags = []
lflags = []
dlls = []
extra_objects = []
# platform dependent libraries and macros
UNAME = platform.system()
if  UNAME.find('CYGWIN') == 0:
    UNAME = "cygwin32"
    CMPL = 'gcc'
elif UNAME == 'Windows':
    UNAME = 'WIN32'
    # MSVC compiler
    static = False
    if HOSTARCH in ['win32-x86', 'windows-x64', 'win32-x86-debug', 'windows-x64-debug']:
        dlls = ['cas.dll', 'ca.dll', 'gdd.dll', 'Com.dll']
        if PRE315:
            dlls += ['dbIoc.dll', 'dbStaticIoc.dll', 'asIoc.dll']
        else:
            dlls += ['dbCore.dll']
        for dll in dlls:
            dllpath = os.path.join(EPICSBASE, 'bin', HOSTARCH, dll)
            if not os.path.exists(dllpath):
                static = True
                break
            dll_dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pcaspy', dll)
            if not os.path.exists(dll_dest) or not filecmp.cmp(dllpath, dll_dest):
                shutil.copy(dllpath, dll_dest)
        macros += [('_CRT_SECURE_NO_WARNINGS', 'None'), ('_CRT_NONSTDC_NO_DEPRECATE', 'None'), ('EPICS_CALL_DLL', '')]
        cflags += ['/Z7']
        CMPL = 'msvc'
    if HOSTARCH in ['win32-x86-static', 'windows-x64-static'] or static:
        libraries += ['ws2_32', 'user32', 'advapi32']
        macros += [('_CRT_SECURE_NO_WARNINGS', 'None'), ('_CRT_NONSTDC_NO_DEPRECATE', 'None'), ('EPICS_DLL_NO', '')]
        umacros+= ['_DLL']
        cflags += ['/EHsc', '/Z7']
        lflags += ['/LTCG']
        if HOSTARCH[-5:] == 'debug':
            libraries += ['msvcrtd']
            lflags += ['/NODEFAULTLIB:libcmtd.lib']
        else:
            libraries += ['msvcrt']
            lflags += ['/NODEFAULTLIB:libcmt.lib']
        CMPL = 'msvc'
    # GCC compiler
    if HOSTARCH in ['win32-x86-mingw', 'windows-x64-mingw']:
        macros += [('_MINGW', ''), ('EPICS_DLL_NO', '')]
        lflags += ['-static',]
        CMPL = 'gcc'
    if HOSTARCH == 'windows-x64-mingw':
        macros += [('MS_WIN64', '')]
        CMPL = 'gcc'
elif UNAME == 'Darwin':
    CMPL = 'clang'
    if not SHARED:
        extra_objects = [os.path.join(EPICSBASE, 'lib', HOSTARCH, 'lib%s.a'%lib) for lib in libraries]
        if paths_exist(extra_objects):
            libraries = []
        else:
            extra_objects = []
            SHARED = True
elif UNAME == 'Linux':
    if not SHARED:
        extra_objects = [os.path.join(EPICSBASE, 'lib', HOSTARCH, 'lib%s.a'%lib) for lib in libraries]
        if paths_exist(extra_objects):
            # necessary when EPICS is statically linked
            libraries = ['rt']
            if subprocess.call('nm -u %s | grep -q rl_' % os.path.join(EPICSBASE, 'lib', HOSTARCH, 'libCom.a'), shell=True) == 0:
                libraries += ['readline']
        else:
            extra_objects = []
            SHARED = True
    CMPL = 'gcc'
elif UNAME == 'SunOS':
    # OS_CLASS used by EPICS
    UNAME = 'solaris'
    CMPL = 'solStudio'
else:
    raise IOError("Unsupported OS {0}".format(UNAME))

cas_module = Extension('pcaspy._cas',
                       sources  =[os.path.join('pcaspy','casdef.i'),
                                  os.path.join('pcaspy','pv.cpp'),
                                  os.path.join('pcaspy','channel.cpp'),],
                       swig_opts=['-c++','-threads','-nodefaultdtor','-I%s'% os.path.join(EPICSBASE, 'include')],
                       extra_compile_args=cflags,
                       include_dirs = [ os.path.join(EPICSBASE, 'include'),
                                        os.path.join(EPICSBASE, 'include', 'os', UNAME),
                                        os.path.join(EPICSBASE, 'include', 'compiler', CMPL)],
                       library_dirs = [ os.path.join(EPICSBASE, 'lib', HOSTARCH),],
                       libraries = libraries,
                       extra_link_args = lflags,
                       extra_objects = extra_objects,
                       define_macros = macros,
                       undef_macros  = umacros,)
# use runtime library path option if linking share libraries on *NIX
if UNAME not in ['WIN32'] and SHARED:
    cas_module.runtime_library_dirs += [os.path.join(EPICSBASE, 'lib', HOSTARCH)]

long_description = open('README.rst').read()
_version = load_module('_version', 'pcaspy/_version.py')

dist = setup (name = 'pcaspy',
              version = _version.__version__,
              description = """Portable Channel Access Server in Python""",
              long_description = long_description,
              author      = "Xiaoqiang Wang",
              author_email= "xiaoqiangwang@gmail.com",
              url         = "https://pypi.python.org/pypi/pcaspy",
              ext_modules = [cas_module],
              packages    = ["pcaspy"],
              package_data={"pcaspy" : dlls},
              cmdclass    = {'build_py':build_py},
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
