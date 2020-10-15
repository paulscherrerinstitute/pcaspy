Summary: Portable Channel Access Server in Python
Name: python-pcaspy
Version: 0.7.3
Release: 1%{?dist}
Source0: https://pypi.io/packages/source/p/pcaspy/pcaspy-%{version}.tar.gz
License: BSD
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
Vendor: Xiaoqiang Wang <xiaoqiangwang@gmail.com>
Url: https://pypi.python.org/pypi/pcaspy

BuildRequires: python-devel python-setuptools swig

# Do not check .so files in the python_sitearch directory
# or any files in the application's directory for provides
%global __provides_exclude_from ^%{python_sitearch}/.*\\.so$

# If EPICS_BASE is defined from environment, then epics-base package is not required
%if "%{?getenv:EPICS_BASE}"==""
BuildRequires: epics-base
%endif

%description
PCASpy
======

PCASpy provides not only the low level python binding to EPICS Portable Channel Access Server
but also the necessary high level abstraction to ease the server tool programming.

Check out `PCASpy documents <https://pcaspy.readthedocs.org>`_ to get started.

%prep
%setup -n pcaspy-%{version}

%build
env CFLAGS="$RPM_OPT_FLAGS" python setup.py build

%install
python setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
