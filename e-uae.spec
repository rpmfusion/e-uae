Name:           e-uae
Version:        0.8.29
Release:        0.14.wip4%{?dist}
Summary:        A powerful Amiga Emulator, based on UAE
Group:          Applications/Emulators
License:        GPLv2+
URL:            http://www.rcdrummond.net/uae/
Source0:        http://www.rcdrummond.net/uae/%{name}-%{version}-WIP4/%{name}-%{version}-WIP4.tar.bz2
Source1:        %{name}.png
Patch0:         %{name}-0.8.29-irqfixes.patch
Patch1:         %{name}-0.8.29-hardfilefixes.patch
# patch from upstream not to require an executable stack
Patch2:         %{name}-0.8.29-execstack.patch
# patch from upstream to fix a 64bit gtk+ bug
Patch3:         %{name}-0.8.29-gtk_64bit.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  desktop-file-utils
BuildRequires:  gtk2-devel => 2.0.0
BuildRequires:  libICE-devel
BuildRequires:  ncurses-devel
BuildRequires:  pkgconfig
BuildRequires:  SDL-devel => 1.2.0
BuildRequires:  zlib-devel
%ifarch %{ix86} x86_64 ppc 
BuildRequires:  libcapsimage-devel => 2.0.0
%endif
Requires:       hicolor-icon-theme
Requires:       policycoreutils


%description
E-UAE is an Amiga Emulator based on UAE which attempts to bring all the
features of WinUAE to non Windows platforms. E-UAE includes almost
complete emulation of the custom chips, including AGA, bsdsocket
emulation, JIT compilation for X86 processors, emulation of the 68000 to
the 68060 as well as the FPUs.


%prep
%setup -q -n %{name}-%{version}-WIP4
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

# Encoding fixes
iconv -f iso8859-1 ChangeLog -t utf8 > ChangeLog.conv && /bin/mv -f ChangeLog.conv ChangeLog

# Permission fixes
chmod -x src/crc32.c


%build
# Flag notes
# --enable-jit : Defaults to enabled on X86
# --enable-natmem : Defaults to enabled on Linux/X86
# --enable-autoconfig : Defaults to enabled if threading available (should be)
# --enable-aga : Defaults to true
# --enable-cdtv : Defaults to true if SCSI is enabled.
# --enable-cd32 : Defaults to true if AGA and SCSI is enabled
# --enable-action-replay : Defaults to true
# --enable-cycle-exact-cpu : Defaults to true
# --enable-compatible-cpu : Defaults to true
# --enable-natmem : Defaults to yes on Linux
# --enable-autoconfig : Defaults to yes if threads enabled (they should be)
# --enable-fdi : Defaults to on
%ifarch %{ix86} x86_64 ppc
# Fix for libcaps support
export LDFLAGS=-lstdc++
%configure --enable-bsdsock-new \
           --enable-ui \
           --enable-audio \
           --with-sdl \
           --with-sdl-gfx \
           --with-sdl-sound \
           --with-caps \
           --with-caps-prefix=/usr 
%else
%configure --enable-bsdsock-new \
           --enable-ui \
           --enable-audio \
           --with-sdl \
           --with-sdl-gfx \
           --with-sdl-sound
%endif

# Don't use parallel building (%%{?_smp_mflags}) seems broken in some cases
make

# Build desktop icon
cat >%{name}.desktop <<EOF
[Desktop Entry]
Encoding=UTF-8
Name=E-UAE
GenericName=Amiga Emulator
Comment=UNIX Amiga Emulator
Exec=uae
Icon=%{name}
Terminal=false
Type=Application
Categories=Game;Emulator;
EOF


%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/48x48/apps
install -pm0644 %{SOURCE1} %{buildroot}%{_datadir}/icons/hicolor/48x48/apps/%{name}.png

desktop-file-install --vendor dribble \
                     --dir %{buildroot}%{_datadir}/applications \
                     %{name}.desktop


%clean
rm -rf %{buildroot}


%post
touch --no-create %{_datadir}/icons/hicolor
if [ -x %{_bindir}/gtk-update-icon-cache ]; then
   %{_bindir}/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor || :
fi

# SELinux support
%ifarch %{ix86}
semanage fcontext -a -t java_exec_t %{_bindir}/uae >/dev/null 2>&1 || :
restorecon -R %{_bindir}/uae
%endif


%postun
touch --no-create %{_datadir}/icons/hicolor
if [ -x %{_bindir}/gtk-update-icon-cache ]; then
   %{_bindir}/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor || :
fi

# SELinux support
%ifarch %{ix86}
if [ "$1" -eq "0" ]; then
    semanage fcontext -d -t java_exec_t %{_bindir}/uae >/dev/null 2>&1 || :
fi
%endif


%files
%defattr(-,root,root,-)
%{_bindir}/uae
%{_bindir}/readdisk
%{_datadir}/applications/dribble-e-uae.desktop
%{_datadir}/icons/hicolor/48x48/apps/%{name}.png
%doc docs/* ChangeLog COPYING README


%changelog
* Sun Nov 15 2009 Ian Chapman <packages[AT]amiga-hardware.com> 0.8.29-0.14.wip4
- Work around fix for libcaps support

* Sun Oct 18 2009 Andrea Musuruane <musuruan@gmail.com> 0.8.29-0.13.wip4
- fixed a 64bit gtk+ bug causing a segfault (BZ #850)

* Sun Mar 29 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 0.8.29-0.12.wip4
- rebuild for new F11 features

* Sun Oct 19 2008 Andrea Musuruane <musuruan@gmail.com> 0.8.29-0.11.wip4
- fix libcapsimage support (available only for i686, x86_64 and ppc)

* Sun Oct 05 2008 Andrea Musuruane <musuruan@gmail.com> 0.8.29-0.10.wip4
- addedd a patch from upstream not to require an executable stack
- added an SELinux context because uae requires an executable heap

* Fri Mar 21 2008 Ian Chapman <packages[AT]amiga-hardware.com> 0.8.29-0.9.wip4
- Add support for libcapsimage to x86_64
- Added patch for various IRQ handling fixes
- Added patch for fixing hardfile related race condition
- Convert ChangeLog to UTF8
- License change due to new guidelines

* Sat Mar 31 2007 Ian Chapman <packages[AT]amiga-hardware.com> 0.8.29-0.8.wip4
- Upgrade to 0.8.29-WIP4

* Tue Mar 13 2007 Ian Chapman <packages[AT]amiga-hardware.com> 0.8.29-0.7.wip3
- Dropped dribble-menus requirement, due to be obsoleted
- Changed .desktop category to Game;Emulator;

* Thu Jan 25 2007 Ian Chapman <packages[AT]amiga-hardware.com> 0.8.29-0.6.wip3
- Various spec cleanups
- Dropped support for FC4
- Renamed icon and .desktop file

* Wed Aug 02 2006 Ian Chapman <packages[AT]amiga-hardware.com> 0.8.29-0.5.wip3
- Upgraded to 0.8.29-WIP3

* Sun Jul 09 2006 Ian Chapman <packages[AT]amiga-hardware.com> 0.8.29-0.4.wip2
- Moved icon installation to make it freedesktop compliant
- Added %%post and %%postun sections to update icon cache at installation

* Sat Jun 24 2006 Ian Chapman <packages[AT]amiga-hardware.com> 0.8.29-0.3.wip2
- Cosmetic fixes for the Dribble repository
- Rebuilt ensuring libICE support
- Moved .desktop file creation to build section

* Wed May 31 2006 Ian Chapman <packages[AT]amiga-hardware.com> 0.8.29-0.2.wip2
- Corrected release name format to 0.%%{X}.%%{alphatag} from 0.%%{alphatag}.%%{X}
- Added %%{version}-%%{release} to provides field
- Dropped gawk as a buildrequire. Doesn't seem to be needed.
- Dropped xorg-x11-devel as a buildrequire. SDL-devel should pull in needed X
  headers and this should make it compatible with both modular/non-modular X
- Added ncurses-devel as a buildrequire
- Added pkgconfig as a buildrequire
- Disabled parallel make as it currently seems to be broken.
- Cosmetic changes to the configure section. Makes it less verbose.

* Sat May 06 2006 Ian Chapman <packages[AT]amiga-hardware.com> 0.8.29-0.WIP2.1.iss
- Upgraded to 0.8.29-WIP2
- Spec file changed to more closely follow Fedora packaging guidelines
- Amiga specific tools removed
- Added gawk, xorg-x11-devel, desktop-file-utils buildrequires
- Removed file from buildrequires as per packaging guidelines
- Added x86_64 support, minus caps stuff as it's not available for x86_64

* Mon Oct 24 2005 Ian Chapman <packages[AT]amiga-hardware.com> 0.8.28-1.iss
- Upgraded to 0.8.28
- Fixes for deprecated fields no longer supported by the latest rpmbuild
- Now compiled against SDL as the FC2 arts/SDL bug appears fixed.
- Compiled on PPC
- SCSI emulation removed.

* Sun Jan 23 2005 Ian Chapman <packages[AT]amiga-hardware.com> 0.8.27-2.iss
- Upgraded to the final version of 0.8.27 instead of RC2
- Now compiled against alsa as it supports it natively.
- Added scsi emulation support.
- CD32 emulation now enabled as it required scsi-emulation support
- CDTV emulation now enabled as it required scsi-emulation support

* Tue Nov 30 2004 Ian Chapman <packages[AT]amiga-hardware.com> 0.8.27-1.iss
- Initial Release
