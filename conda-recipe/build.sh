#echo $PREFIX
export EPICS_BASE=$PREFIX/epics

PLATFORM=$(uname | tr '[:upper:]' '[:lower:]')
if [ $PLATFORM == "linux" ] ; then
  export EPICS_HOST_ARCH=$(uname | tr '[:upper:]' '[:lower:]')-$(uname -m)
elif [ $PLATFORM == "darwin" ] ; then
  export EPICS_HOST_ARCH=darwin-x86
fi

echo Using EPICS_BASE=$EPICS_BASE
echo Using EPICS_HOST_ARCH=$EPICS_HOST_ARCH

 # echo $(uname | tr '[:upper:]' '[:lower:]')-$(uname -m)
#$PYTHON setup.py build     # Python command to install the script
$PYTHON setup.py install     # Python command to install the script
