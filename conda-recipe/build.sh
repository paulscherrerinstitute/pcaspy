#echo $PREFIX
export EPICS_BASE=$PREFIX/epics
export EPICS_HOST_ARCH=darwin-x86 # echo $(uname | tr '[:upper:]' '[:lower:]')-$(uname -m)
#$PYTHON setup.py build     # Python command to install the script
$PYTHON setup.py install     # Python command to install the script
