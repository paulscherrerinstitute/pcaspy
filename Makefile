copts = $(if $(findstring win32-x86-mingw,$(EPICS_HOST_ARCH)),-cmingw32)
all:
	python setup.py build_ext --swig-cpp --inplace -f ${copts}  build
bdist:
	python setup.py build_ext --swig-cpp -f ${copts}  bdist
sdist:
	python setup.py sdist
clean:
	python setup.py clean
