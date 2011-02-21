copts = $(if $(findstring win32-x86-mingw,$(EPICS_HOST_ARCH)),-cmingw32)
all:
	python setup.py build_ext --swig-cpp -f ${copts} build
clean:
	python setup.py clean
