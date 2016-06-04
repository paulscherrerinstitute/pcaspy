REM set EPICS_BASE=%PREFIX:\=/%/epics/

REM if %ARCH%==32 (
REM    set EPICS_HOST_ARCH=win32-x86
REM ) else if %ARCH%==64 (
REM     set EPICS_HOST_ARCH=windows-x64
REM )
echo Using EPICS_BASE=%EPICS_BASE%
echo Using EPICS_HOST_ARCH=%EPICS_HOST_ARCH%

"%PYTHON%" setup.py install
if errorlevel 1 exit 1
