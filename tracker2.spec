%define build_doc	1

#gw libtracker-common is in the main package and not provided
%global __requires_exclude devel\\(libtracker-common|devel\\(libtracker-data

%define oname tracker

# ovitters 1.12.0 is broken
%define _disable_ld_as_needed 1
%define _disable_ld_no_undefined 1

%define api		2.0
%define major		0
%define girmajor	2.0

%define libname		%mklibname %{name} %{api} %{major}
%define develname	%mklibname %{name} -d
%define girname         %mklibname %{name}-gir %{girmajor}

%define url_ver		%(echo %{version} | cut -d. -f1,2)

Summary:	Desktop-neutral metadata-based search framework
Name:		tracker2
Version:	2.3.6
Release:	3
License:	GPLv2+ and LGPLv2+
Group:		Graphical desktop/GNOME
URL:		https://wiki.gnome.org/Projects/Tracker
Source0:	https://download.gnome.org/sources/%{oname}/%{url_ver}/%{oname}-%{version}.tar.xz
Source1:	30-tracker.conf

BuildRequires:	dbus-daemon
BuildRequires:	intltool
BuildRequires:	gettext-devel
BuildRequires:	icu-devel
BuildRequires:	gnome-common
BuildRequires:	meson
BuildRequires:	pkgconfig(gobject-introspection-1.0)
BuildRequires:	pkgconfig(flac)
BuildRequires:	pkgconfig(gdk-pixbuf-2.0)
BuildRequires:	pkgconfig(gio-unix-2.0)
BuildRequires:	pkgconfig(glib-2.0)
BuildRequires:	pkgconfig(gmodule-2.0)
BuildRequires:	pkgconfig(gnome-desktop-3.0)
BuildRequires:	pkgconfig(gthread-2.0)
BuildRequires:	pkgconfig(libgxps)
BuildRequires:	pkgconfig(libnm)
BuildRequires:	pkgconfig(libxml-2.0)
BuildRequires:	pkgconfig(pango)
BuildRequires:	pkgconfig(rest-0.7)
BuildRequires:	libstemmer-devel
BuildRequires:	pkgconfig(sqlite3)
BuildRequires:	pkgconfig(uuid)
BuildRequires:	pkgconfig(vapigen)
BuildRequires:	pkgconfig(json-glib-1.0)
BuildRequires:	vala
BuildRequires:  locales
Requires:	odt2txt

Recommends:	tracker2-miners


%description
Tracker is a framework designed to extract information and metadata about your
personal data so that it can be searched easily and quickly. Tracker is
desktop-neutral, fast and resource efficient.

%package -n %{libname}
Group:		System/Libraries
Summary:	Shared library of Tracker
# ovitters: library needs the gschema, further, they need the indexing (mga#20300)
#           best solution is to require the main package
Requires:	%{name}

%description -n %{libname}
Tracker is a tool designed to extract information and metadata about your
personal data so that it can be searched easily and quickly. Tracker is
desktop-neutral, fast and resource efficient.

%package -n %{develname}
Group:		Development/C
Summary:	Development library of Tracker
Requires:	%{libname} = %{version}-%{release}
Requires:	%{girname} = %{version}-%{release}
Requires:	%{name}-vala
Provides:	%{name}-devel = %{version}-%{release}
Provides:	lib%{name}-devel = %{version}-%{release}

%description -n %{develname}
Tracker is a tool designed to extract information and metadata about your
personal data so that it can be searched easily and quickly. Tracker is
desktop-neutral, fast and resource efficient.

%package -n %{girname}
Summary:        GObject Introspection interface description for %{name}
Group:          System/Libraries
Requires:       %{libname} = %{version}-%{release}

%description -n %{girname}
GObject Introspection interface description for %{name}.

%package vala
Summary:	Vala bindings for %{name}
Group:		Development/Other
BuildArch:	noarch
Requires:	%{name}-devel >= %{version}-%{release}
Requires:	vala

%description vala
This package contains vala bindings for development %{name}.

%if %{build_doc}
%package docs
Summary:	Documentations for tracker
Group:		Documentation
BuildArch:	noarch
BuildRequires:  pkgconfig(gtk-doc)
BuildRequires:	graphviz

%description docs
This package contains the documentation for tracker.
%endif

%prep
%setup -q -n %oname-%version
# remove generated code, we want to build from the actual source files
for i in `find . -name '*.vala'`; do rm -f ${i%.vala}.c; done
%autopatch -p1

%build
export LC_ALL=UTF-8 CPATH+=":/usr/include/libstemmer/"
%meson \
%if %{build_doc}
	-Ddocs=true \
%endif
	-Dfunctional_tests=false \
	-Dsystemd_user_services=%{_userunitdir}

%meson_build

%install
%meson_install

%{__install} -D -p -m 0644 %{SOURCE1} %{buildroot}%{_prefix}/lib/sysctl.d/30-%{name}.conf

%find_lang %{oname}

rm -rf %{buildroot}%{_datadir}/tracker-tests

rm -f %{buildroot}%{_libdir}/tracker-2.0/libtracker-common.a
rm -rf %{buildroot}%{_libdir}/tracker-2.0/trackertestutils

%files -f %{oname}.lang
%doc README.md NEWS AUTHORS
%{_bindir}/%{oname}
%{_datadir}/%{oname}/
%{_libexecdir}/%{oname}-store
%{_prefix}/lib/sysctl.d/30-%{name}.conf
%{_datadir}/bash-completion/completions/tracker
%{_datadir}/dbus-1/services/org.freedesktop.Tracker1.service
%{_mandir}/man1/tracker*.1*
%{_datadir}/glib-2.0/schemas/org.freedesktop.Tracker.*
%{_userunitdir}/tracker-store.service

%files vala
%{_datadir}/vala/vapi/%{oname}-control-%{api}.vapi
%{_datadir}/vala/vapi/%{oname}-control-%{api}.deps
%{_datadir}/vala/vapi/%{oname}-sparql-%{api}.vapi
%{_datadir}/vala/vapi/%{oname}-sparql-%{api}.deps
%{_datadir}/vala/vapi/%{oname}-miner-%{api}.vapi
%{_datadir}/vala/vapi/%{oname}-miner-%{api}.deps

%files -n %{libname}
%{_libdir}/lib%{oname}-control-%{api}.so.%{major}{,.*}
%{_libdir}/lib%{oname}-miner-%{api}.so.%{major}{,.*}
%{_libdir}/lib%{oname}-sparql-%{api}.so.%{major}{,.*}
%dir %{_libdir}/%{oname}-%{api}/
%{_libdir}/%{oname}-%{api}/libtracker-*.so

%files -n %{girname}
%{_libdir}/girepository-1.0/Tracker-%{girmajor}.typelib
%{_libdir}/girepository-1.0/TrackerControl-%{girmajor}.typelib
%{_libdir}/girepository-1.0/TrackerMiner-%{girmajor}.typelib

%files -n %{develname}
%{_libdir}/lib%{oname}-control-%{api}.so
%{_libdir}/lib%{oname}-miner-%{api}.so
%{_libdir}/lib%{oname}-sparql-%{api}.so
%{_libdir}/%{oname}-%{api}/libtracker-*.so
%{_includedir}/*
%{_libdir}/pkgconfig/%{oname}-control-%{api}.pc
%{_libdir}/pkgconfig/%{oname}-miner-%{api}.pc
%{_libdir}/pkgconfig/%{oname}-sparql-%{api}.pc
%{_datadir}/gir-1.0/Tracker-%{girmajor}.gir
%{_datadir}/gir-1.0/TrackerControl-%{girmajor}.gir
%{_datadir}/gir-1.0/TrackerMiner-%{girmajor}.gir

%if %{build_doc}
%files docs
%{_datadir}/gtk-doc/html/lib%{oname}-control
%{_datadir}/gtk-doc/html/lib%{oname}-miner
%{_datadir}/gtk-doc/html/lib%{oname}-sparql
%{_datadir}/gtk-doc/html/ontology
%endif
