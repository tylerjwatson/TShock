%global tshock_group NyxStudios
%global tshock_proj TShock
%global tsapi_group Deathmax
%global tsapi_dir TerrariaServerAPI
%global tsapi_proj TerrariaAPI-Server

%global tsapi_commit a44d46af2f7b54110707b6f09875fdcf32365544
%global tshock_commit 1228acbbc864515497da7c12f88b3af0bf209420

%global tshock_version 4.3201

##
# Package doesn't contain any libc/unmanaged code so debuginfo searching
# here is going to be pretty useless.
##
%define 	debug_package %{nil}
%define 	user tsapi
%define 	group tsapi

%define		install_dir %{buildroot}%{_datadir}/terraria
%define		lib_dir %{buildroot}%{_libdir}/tsapi

Name:		tshock
Version:        %{tshock_version}
Release:        1%{?dist}
Summary:        A server modification for Terraria that adds features everyone loves.

Packager:	Tyler Watson <tyler@tw.id.au>
License:        GPLv2+
URL:            http://tshock.co/xf

Source0:        https://github.com/%{tshock_group}/%{tshock_proj}/archive/%{tshock_commit}/%{tshock_proj}-%{tshock_commit}.tar.gz
Source1:	https://github.com/%{tsapi_group}/%{tsapi_proj}/archive/%{tsapi_commit}/%{tsapi_proj}-%{tsapi_commit}.tar.gz

##
# Fixes CS1065 errors on TSAPI
##
Patch1:		0001-fix-cs1065.patch
Patch2:		0002-TSAPI-reference.patch	
Patch4:		0004-tsapi-solution-output.patch
Patch5:		0005-disable-test-solution.patch

BuildRequires:  gcc
BuildRequires:	libmono-2_0-devel >= 3.10
BuildRequires:	mono-devel >= 3.10
AutoReqProv:	no

Requires:		mono-complete >= 3.10      
Requires(pre): 		/usr/sbin/useradd, /usr/bin/getent
Requires(postun): 	/usr/sbin/userdel

Provides:	tshock

%description

A server modification for Terraria that adds features everyone loves.


%prep

%setup -b 1 -T -n %{tsapi_proj}-%{tsapi_commit}
%patch1 -p0
%patch4 -p0

%setup -n %{tshock_proj}-%{tshock_commit}
%patch2 -p0
%patch5 -p0

%pre

/usr/bin/getent passwd %{user} || /usr/sbin/useradd -r -d %{_datadir}/terraria -s /sbin/nologin %{user} 

%postun

/usr/sbin/userdel -f %{user} 

%build

pushd ../%{tsapi_proj}-%{tsapi_commit}
xbuild
popd

pushd ../%{tshock_proj}-%{tshock_commit}
xbuild TShock.sln
cp -rdf TShockAPI/bin/Debug/*.dll ../build 
popd

pushd ../build
mkbundle -o TerrariaServer --deps TerrariaServer.exe 

# step: AOT all .NET assemblies
mono --aot=full TShockAPI.dll
mono --aot=full HttpServer.dll
mono --aot=full Newtonsoft.Json.dll
mono --aot=full TerrariaServer.exe

popd

%install

install -d -m755 %{install_dir} 
install -d -m755 %{lib_dir}
install -d -m755 %{buildroot}%{_sysconfdir}/tsapi
install -d -m755 %{buildroot}%{_sysconfdir}/tsapi/instances.d

pushd ../build

install -m755 TerrariaServer %{install_dir}/TerrariaServer
install -m755 TShockAPI.dll %{lib_dir}/TShockAPI.dll 
install -m755 TShockAPI.dll.so %{lib_dir}/TShockAPI.dll.so 

install -m755 HttpServer.dll %{lib_dir}/HttpServer.dll 
install -m755 HttpServer.dll.so %{lib_dir}/HttpServer.dll.so 

install -m755 Newtonsoft.Json.dll %{lib_dir}/Newtonsoft.Json.dll
install -m755 Newtonsoft.Json.dll.so %{lib_dir}/Newtonsoft.Json.dll.so

install -m755 Mono.Data.Sqlite.dll %{lib_dir}/Mono.Data.Sqlite.dll
install -m755 Mono.Data.Sqlite.dll.so %{lib_dir}/Mono.Data.Sqlite.dll.so

install -m755 MySql.Data.dll %{lib_dir}/MySql.Data.dll

mkdir -p %{buildroot}%{_sysconfdir}/systemd/user


echo <<EOF >%{buildroot}%{_sysconfdir}/tsapi/instances.conf
# Sample instances file

[DEFAULT]
port = 7777

EOF

echo <<EOF >%{buildroot}%{_sysconfdir}/systemd/user/tsapi.service
[Unit]
Description=TSAPI Terraria Server
After=network.target
Requires=network.target


[Service]
ExecStart=%{_bindir}/tsapi start %i


[Install]
WantedBy=multi-user.target

EOF

# Symlink section
mkdir ${RPM_BUILD_ROOT}/%{_bindir}

##
# I'm pretty sure this is the dirtiest shit ever, fix this if it
# becomes a problem.
##
ln -sf ../../%{_datadir}/terraria/TerrariaServer ${RPM_BUILD_ROOT}/%{_bindir}/TerrariaServer
ln -sf ../../../tsapi %{install_dir}/serverplugins 

popd
# rm -rf $RPM_BUILD_ROOT


%files
%defattr(744,%{user},%{group},-)

%attr(775,%{user},%{group}) %{_datarootdir}/terraria
%attr(755,%{user},%{group}) %{_datarootdir}/terraria/TerrariaServer
%attr(775,%{user},%{group}) %{_sysconfdir}/tsapi
%attr(775,%{user},%{group}) %{_sysconfdir}/tsapi/instances.d

%attr(775,%{user},%{group}) %config %{_sysconfdir}/tsapi/instances.conf

%{_sysconfdir}/systemd/user/tsapi.service

%{_libdir}/tsapi
%{_libdir}/tsapi/TShockAPI.dll
%{_libdir}/tsapi/TShockAPI.dll.so
%{_libdir}/tsapi/HttpServer.dll
%{_libdir}/tsapi/HttpServer.dll.so

%{_bindir}/TerrariaServer

%post
# %doc



%changelog
* Wed Dec 24 2014 Tyler Watson <tyler@tw.id.au> 4.2301.0-1
- Initial specfile and SRPM package
