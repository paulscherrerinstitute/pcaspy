set EPICS_BASE=%PREFIX%\epics

if %ARCH%==32 (
   set EPICS_HOST_ARCH=win32-x86-static
) else if %ARCH%==64 (
    set EPICS_HOST_ARCH=windows-x64-static
)
echo Using EPICS_BASE=%EPICS_BASE%
echo Using EPICS_HOST_ARCH=%EPICS_HOST_ARCH%

for /f "delims=" %%i in ('conda info --root') do set OUTPUT_PATH=%%i\conda-bld\win-%ARCH%

"%PYTHON%" setup.py install bdist_wheel
copy dist\*.whl %OUTPUT_PATH%
if errorlevel 1 exit 1
