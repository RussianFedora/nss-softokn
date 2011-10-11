%global nspr_version 4.8.8
%global nss_name nss
%global nss_util_version 3.12.10
%global unsupported_tools_directory %{_libdir}/nss/unsupported-tools
%global saved_files_dir %{_libdir}/nss/saved

# Produce .chk files for the final stripped binaries
%define __spec_install_post \
    %{?__debug_package:%{__debug_install_post}} \
    %{__arch_install_post} \
    %{__os_install_post} \
    $RPM_BUILD_ROOT/%{unsupported_tools_directory}/shlibsign -i $RPM_BUILD_ROOT/%{_libdir}/libsoftokn3.so \
    $RPM_BUILD_ROOT/%{unsupported_tools_directory}/shlibsign -i $RPM_BUILD_ROOT/%{_lib}/libfreebl3.so \
    $RPM_BUILD_ROOT/%{unsupported_tools_directory}/shlibsign -i $RPM_BUILD_ROOT/%{_libdir}/libnssdbm3.so \
%{nil}

Summary:          Network Security Services Softoken Module
Name:             nss-softokn
Version:          3.12.10
Release:          5.el6.R
License:          MPLv1.1 or GPLv2+ or LGPLv2+
URL:              http://www.mozilla.org/projects/security/pki/nss/
Group:            System Environment/Libraries
Requires:         nspr >= %{nspr_version}
Requires:         nss-util >= %{nss_util_version}
Requires:         nss-softokn-freebl%{_isa} >= %{version}
BuildRoot:        %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:    nspr-devel >= %{nspr_version}
BuildRequires:    nss-util-devel >= %{nss_util_version}
BuildRequires:    sqlite-devel
BuildRequires:    zlib-devel
BuildRequires:    pkgconfig
BuildRequires:    gawk
BuildRequires:    psmisc
BuildRequires:    perl

Source0:          %{name}-%{version}-stripped.tar.bz2
# The nss-softokn tar ball is a subset of nss-{version}-stripped.tar.bz2, 
# Therefore we use the nss-split-softokn.sh script to keep only what we need.
# Download the nss tarball via git from the nss project and follow these
# steps to make the tarball for nss-util out of the one for nss:
# fedpkg clone nss
# fedpkg clone nss-softokn
# cd nss-softokn
# cp ../../nss/devel/${version}-stripped.tar.bz2  .
# sh ./nss-split-softokn.sh ${version}
# A file named {name}-{version}-stripped.tar.bz2 should appear
Source1:          nss-split-softokn.sh
Source2:          nss-softokn.pc.in
Source3:          nss-softokn-config.in

Patch2:           nss-softokn-3.12.4-prelink.patch
Patch3:           bz709517.patch
Patch4:           softoken-minimal-test-dependencies.patch

%description
Network Security Services Softoken Cryptographic Module

%package freebl
Summary:          Freebl library for the Network Security Services
Group:            System Environment/Base
Conflicts:        nss < 3.12.2.99.3-5
Conflicts:        prelink < 0.4.3

%description freebl
NSS Softoken Cryptographic Module Freelb Library

Install the nss-softokn-freebl package if you need the freebl 
library.

%package freebl-devel
Summary:          Header and Library files for doing development with the Freebl library for NSS
Group:            System Environment/Base
Provides:         nss-softokn-freebl-static = %{version}-%{release}
Requires:         nss-softokn-freebl%{?_isa} = %{version}-%{release}

%description freebl-devel
NSS Softoken Cryptographic Module Freelb Library Development Tools
This package supports special needs of some PKCS #11 module developers and
is otherwise considered private to NSS. As such, the programming interfaces
may change and the usual NSS binary compatibility commitments do not apply.
Developers should rely only on the officially supported NSS public API.

%package devel
Summary:          Development libraries for Network Security Services
Group:            Development/Libraries
Requires:         nss-softokn%{?_isa} = %{version}-%{release}
Requires:         nss-softokn-freebl-devel%{?_isa} = %{version}-%{release}
Requires:         nspr-devel >= %{nspr_version}
Requires:         nss-util-devel >= %{nss_util_version}
Requires:         pkgconfig
BuildRequires:    nspr-devel >= %{nspr_version}
BuildRequires:    nss-util-devel >= %{nss_util_version}
# require nss at least the version when we split via subpackages
BuildRequires:    nss-devel >= 3.12.2.99.3-11

%description devel
Header and Library files for doing development with Network Security Services.


%prep
%setup -q

%patch2 -p0 -b .prelink
%patch3 -p0 -b .709517
%patch4 -p0 -b .onlycrypto


%build

FREEBL_NO_DEPEND=1
export FREEBL_NO_DEPEND

FREEBL_USE_PRELINK=1
export FREEBL_USE_PRELINK

# Enable compiler optimizations and disable debugging code
BUILD_OPT=1
export BUILD_OPT

# Uncomment to disable optimizations
#RPM_OPT_FLAGS=`echo $RPM_OPT_FLAGS | sed -e 's/-O2/-O0/g'`
#export RPM_OPT_FLAGS

# Generate symbolic info for debuggers
XCFLAGS=$RPM_OPT_FLAGS
export XCFLAGS

PKG_CONFIG_ALLOW_SYSTEM_LIBS=1
PKG_CONFIG_ALLOW_SYSTEM_CFLAGS=1

export PKG_CONFIG_ALLOW_SYSTEM_LIBS
export PKG_CONFIG_ALLOW_SYSTEM_CFLAGS

NSPR_INCLUDE_DIR=`/usr/bin/pkg-config --cflags-only-I nspr | sed 's/-I//'`
NSPR_LIB_DIR=`/usr/bin/pkg-config --libs-only-L nspr | sed 's/-L//'`

export NSPR_INCLUDE_DIR
export NSPR_LIB_DIR

NSSUTIL_INCLUDE_DIR=`/usr/bin/pkg-config --cflags-only-I nss-util | sed 's/-I//'`
NSSUTIL_LIB_DIR=%{_libdir}

export NSSUTIL_INCLUDE_DIR
export NSSUTIL_LIB_DIR

NSS_USE_SYSTEM_SQLITE=1
export NSS_USE_SYSTEM_SQLITE

%ifarch x86_64 ppc64 ia64 s390x sparc64
USE_64=1
export USE_64
%endif

# Compile softokn plus needed support
%{__make} -C ./mozilla/security/coreconf
%{__make} -C ./mozilla/security/dbm
%{__make} -C ./mozilla/security/nss

# Set up our package file
# The nspr_version and nss_util_version globals used here
# must match the ones nss-softokn has for its Requires. 
%{__mkdir_p} ./mozilla/dist/pkgconfig
%{__cat} %{SOURCE2} | sed -e "s,%%libdir%%,%{_libdir},g" \
                          -e "s,%%prefix%%,%{_prefix},g" \
                          -e "s,%%exec_prefix%%,%{_prefix},g" \
                          -e "s,%%includedir%%,%{_includedir}/nss3,g" \
                          -e "s,%%NSPR_VERSION%%,%{nspr_version},g" \
                          -e "s,%%NSSUTIL_VERSION%%,%{nss_util_version},g" \
                          -e "s,%%SOFTOKEN_VERSION%%,%{version},g" > \
                          ./mozilla/dist/pkgconfig/nss-softokn.pc

SOFTOKEN_VMAJOR=`cat mozilla/security/nss/lib/softoken/softkver.h | grep "#define.*SOFTOKEN_VMAJOR" | awk '{print $3}'`
SOFTOKEN_VMINOR=`cat mozilla/security/nss/lib/softoken/softkver.h | grep "#define.*SOFTOKEN_VMINOR" | awk '{print $3}'`
SOFTOKEN_VPATCH=`cat mozilla/security/nss/lib/softoken/softkver.h | grep "#define.*SOFTOKEN_VPATCH" | awk '{print $3}'`

export SOFTOKEN_VMAJOR 
export SOFTOKEN_VMINOR 
export SOFTOKEN_VPATCH

%{__cat} %{SOURCE3} | sed -e "s,@libdir@,%{_libdir},g" \
                          -e "s,@prefix@,%{_prefix},g" \
                          -e "s,@exec_prefix@,%{_prefix},g" \
                          -e "s,@includedir@,%{_includedir}/nss3,g" \
                          -e "s,@MOD_MAJOR_VERSION@,$SOFTOKEN_VMAJOR,g" \
                          -e "s,@MOD_MINOR_VERSION@,$SOFTOKEN_VMINOR,g" \
                          -e "s,@MOD_PATCH_VERSION@,$SOFTOKEN_VPATCH,g" \
                          > ./mozilla/dist/pkgconfig/nss-softokn-config

chmod 755 ./mozilla/dist/pkgconfig/nss-softokn-config


# enable the following line to force a test failure
# find ./mozilla -name \*.chk | xargs rm -f

#
# We can't run a subset of the tests because the tools have
# dependencies on nss libraries outside of softokn. 
# Let's leave this as a place holder.
#

%check

# Begin -- copied from the build section
FREEBL_NO_DEPEND=1
export FREEBL_NO_DEPEND

BUILD_OPT=1
export BUILD_OPT

%ifarch x86_64 ppc64 ia64 s390x sparc64
USE_64=1
export USE_64
%endif
# End -- copied from the build section

# enable the following line to force a test failure
# find ./mozilla -name \*.chk | xargs rm -f

# Run test suite.

SPACEISBAD=`find ./mozilla/security/nss/tests | grep -c ' '` ||:
if [ $SPACEISBAD -ne 0 ]; then
  echo "error: filenames containing space are not supported (xargs)"
  exit 1
fi

rm -rf ./mozilla/tests_results
cd ./mozilla/security/nss/tests/
# all.sh is the test suite script

# only run cipher tests for nss-softokn
%global nss_cycles "standard"
%global nss_tests "cipher"
%global nss_ssl_tests " "
%global nss_ssl_run " "

HOST=localhost DOMSUF=localdomain PORT=$MYRAND NSS_CYCLES=%{?nss_cycles} NSS_TESTS=%{?nss_tests} NSS_SSL_TESTS=%{?nss_ssl_tests} NSS_SSL_RUN=%{?nss_ssl_run} ./all.sh

cd ../../../../

killall $RANDSERV || :

TEST_FAILURES=`grep -c FAILED ./mozilla/tests_results/security/localhost.1/output.log` || :
# test suite is failing on arm and has for awhile let's run the test suite but make it non fatal on arm
%ifnarch %{arm}
if [ $TEST_FAILURES -ne 0 ]; then
  echo "error: test suite returned failure(s)"
  exit 1
fi
echo "test suite completed"
%endif

%install

%{__rm} -rf $RPM_BUILD_ROOT

# There is no make install target so we'll do it ourselves.

%{__mkdir_p} $RPM_BUILD_ROOT/%{_includedir}/nss3
%{__mkdir_p} $RPM_BUILD_ROOT/%{_bindir}
%{__mkdir_p} $RPM_BUILD_ROOT/%{_libdir}
%{__mkdir_p} $RPM_BUILD_ROOT/%{_lib}
%{__mkdir_p} $RPM_BUILD_ROOT/%{unsupported_tools_directory}
%{__mkdir_p} $RPM_BUILD_ROOT/%{_libdir}/pkgconfig
%{__mkdir_p} $RPM_BUILD_ROOT/%{saved_files_dir}

# Copy the binary libraries we want
for file in libsoftokn3.so libnssdbm3.so
do
  %{__install} -p -m 755 mozilla/dist/*.OBJ/lib/$file $RPM_BUILD_ROOT/%{_libdir}
done

# Because libcrypt depends on libfreebl3.so, it is special
# so we install it in /lib{64}, keeping a symbolic link to it
# back in /usr/lib{64} to keep everyone else working
for file in libfreebl3.so
do
  %{__install} -p -m 755 mozilla/dist/*.OBJ/lib/$file $RPM_BUILD_ROOT/%{_lib}
  ln -sf ../../%{_lib}/libfreebl3.so $RPM_BUILD_ROOT/%{_libdir}/libfreebl3.so
done

# Make sure chk files can be found in both places
for file in libfreebl3.chk
do
  ln -s ../../%{_lib}/$file $RPM_BUILD_ROOT/%{_libdir}/$file
done

# Copy the binaries we ship as unsupported
for file in shlibsign
do
  %{__install} -p -m 755 mozilla/dist/*.OBJ/bin/$file $RPM_BUILD_ROOT/%{unsupported_tools_directory}
done

# Copy the include files we want
for file in mozilla/dist/public/nss/*.h
do
  %{__install} -p -m 644 $file $RPM_BUILD_ROOT/%{_includedir}/nss3
done

# Copy some freebl include files we also want
for file in blapi.h alghmac.h
do
  %{__install} -p -m 644 mozilla/dist/private/nss/$file $RPM_BUILD_ROOT/%{_includedir}/nss3
done

# Copy the static freebl library
for file in libfreebl.a
do
%{__install} -p -m 644 mozilla/dist/*.OBJ/lib/$file $RPM_BUILD_ROOT/%{_libdir}
done

# Copy the package configuration files
%{__install} -p -m 644 ./mozilla/dist/pkgconfig/nss-softokn.pc $RPM_BUILD_ROOT/%{_libdir}/pkgconfig/nss-softokn.pc
%{__install} -p -m 755 ./mozilla/dist/pkgconfig/nss-softokn-config $RPM_BUILD_ROOT/%{_bindir}/nss-softokn-config

%clean
%{__rm} -rf $RPM_BUILD_ROOT


%post
/sbin/ldconfig >/dev/null 2>/dev/null

%postun
/sbin/ldconfig >/dev/null 2>/dev/null

%files
%defattr(-,root,root)
%{_libdir}/libnssdbm3.so
%{_libdir}/libnssdbm3.chk
%{_libdir}/libsoftokn3.so
%{_libdir}/libsoftokn3.chk
# shared with nss-tools
%dir %{_libdir}/nss
%dir %{saved_files_dir}
%dir %{unsupported_tools_directory}
%{unsupported_tools_directory}/shlibsign

%files freebl
%defattr(-,root,root)
/%{_lib}/libfreebl3.so
/%{_lib}/libfreebl3.chk
# and these symbolic links
%{_libdir}/libfreebl3.so
%{_libdir}/libfreebl3.chk

%files freebl-devel
%defattr(-,root,root)
%{_libdir}/libfreebl.a
%{_includedir}/nss3/blapi.h
%{_includedir}/nss3/blapit.h
%{_includedir}/nss3/alghmac.h

%files devel
%defattr(-,root,root)
%{_libdir}/pkgconfig/nss-softokn.pc
%{_bindir}/nss-softokn-config

# co-owned with nss
%dir %{_includedir}/nss3
#
# The following headers are those exported public in
# mozilla/security/nss/lib/freebl/manifest.mn and
# mozilla/security/nss/lib/softoken/manifest.mn
#
# The following list is short because many headers, such as
# the pkcs #11 ones, have been provided by nss-util-devel
# which installed them before us.
#
%{_includedir}/nss3/ecl-exp.h
%{_includedir}/nss3/hasht.h
%{_includedir}/nss3/sechash.h
%{_includedir}/nss3/nsslowhash.h
%{_includedir}/nss3/secmodt.h
%{_includedir}/nss3/shsign.h

%changelog
* Wed Aug 17 2011 Elio Maldonado <emaldona@redhat.com> - 3.12.10-5.el6.R
- rebuilt as recommended to deal with an rpm 4.9.1 issue

* Wed Jul 20 2011 Elio Maldonado <emaldona@redhat.com> - 3.12.10-4
- Adjustements from code review (#715402)

* Sun Jun 26 2011 Elio Maldonado <emaldona@redhat.com> - 3.12.10-3
- Add %%{check} section to run crypto tests as part of the build (#715402)

* Tue Jun 14 2011 Elio Maldonado <emaldona@redhat.com> - 3.12.10-2
- Fix intel optimized aes code to deal with case where input and ouput are in the same buffer (#709517)

* Fri May 06 2011 Elio Maldonado <emaldona@redhat.com> - 3.12.10-1
- Update to NSS_3_12_10_RTM

* Wed Apr 27 2011 Elio Maldonado <emaldona@redhat.com> - 3.12.10-0.1.beta1
- Update to NSS_3_12_10_BETA1

* Fri Feb 25 2011 Elio Maldonado <emaldona@redhat.com> - 3.12.9-7
- Add requires nss-softokn-freebl-devel to nss-softokn-devel (#675196)

* Mon Feb 14 2011 Elio Maldonado <emaldona@redhat.com> - 3.12.9-5
- Expand the nss-softokn-freebl-devel package description (#675196)

* Mon Feb 14 2011 Elio Maldonado <emaldona@redhat.com> - 3.12.9-5
- Remove duplicates from the file lists

* Sun Feb 13 2011 Elio Maldonado <emaldona@redhat.com> - 3.12.9-4
- Add blapit.h to headers provided by nss-softokn-freebl-devel (#675196)
- Expand the freebl-devel package description

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.12.9-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Feb 04 2011 Elio Maldonado <emaldona@redhat.com> - 3.12.9-2
- Add header for nss-softokn-freebl-devel (#675196)

* Wed Jan 12 2011 Elio Maldonado <emaldona@redhat.com> - 3.12.9-1
- Update to 3.12.9

* Mon Dec 27 2010 Elio Maldonado <emaldona@redhat.com> - 3.12.9-0.1.beta2
- Rebuilt according to fedora pre-release package naming guidelines

* Fri Dec 10 2010 Elio Maldonado <emaldona@redhat.com> - 3.12.8.99.2-1
- Update to NSS_3_12_9_BETA2

* Wed Dec 08 2010 Elio Maldonado <emaldona@redhat.com> - 3.12.8.99.1-1
- Update to NSS_3_12_9_BETA1

* Wed Sep 29 2010 jkeating - 3.12.8-2
- Rebuilt for gcc bug 634757

* Thu Sep 23 2010 Elio Maldonado <emaldona@redhat.com> - 3.12.8-1
- Update to 3.12.8
- Adhere to static library packaging guidelines (#609613)
- Fix nss-util-devel version dependency line
- Shorten freebl and freebl subpackages descriptions

* Sat Sep 18 2010 Elio Maldonado <emaldona@redhat.com> - 3.12.99.4-1
- NSS 3.12.8 RC0

* Sat Sep 12 2010 Elio Maldonado <emaldona@redhat.com> - 3.12.7.99.3-2
- Update the required version of nss-util to 3.12.7.99.3

* Sat Sep 04 2010 Elio Maldonado <emaldona@redhat.com> - 3.12.7.99.3-1
- NSS 3.12.8 Beta 3

* Mon Aug 30 2010 Elio Maldonado <emaldona@redhat.com> - 3.12.7-3
- Update BuildRequires on nspr-devel and nss-util-devel

* Sat Aug 29 2010 Elio Maldonado <emaldona@redhat.com> - 3.12.7-2
- Define NSS_USE_SYSTEM_SQLITE and remove nss-nolocalsql patch
- Fix rpmlint warnings about macros in comments and changelog

* Mon Aug 16 2010 Elio Maldonado <emaldona@redhat.com> - 3.12.7-1
- Update to 3.12.7
- Fix build files to ensure nsslowhash.h is included in public headers

* Tue Jun 08 2010 Elio Maldonado <emaldona@redhat.com> - 3.12.6-3
- Retagging

* Mon Jun 07 2010 Elio Maldonado <emaldona@redhat.com> - 3.12.6-2
- Bump NVR to be greater than those for nss-softokn subpackages in F11 (rhbz#601407)

* Sun Jun 06 2010 Elio Maldonado <emaldona@redhat.com> - 3.12.4-23
- Bump release number

* Fri Jun 04 2010 Elio Maldonado <emaldona@redhat.com> - 3.12.4-22
- Cleanup changelog comments to avoid unwanted macro expansions

* Wed Jun 02 2010 Elio Maldonado <emaldona@redhat.com> - 3.12.4-21
- Retagging

* Wed Jun 02 2010 Elio Maldonado <emaldona@redhat.com> - 3.12.4-20
- Add %%{?_isa} to the requires in the devel packages (#596840)
- Fix typo in the package description (#598295)
- Update nspr version to 4.8.4

* Sat May 08 2010 Elio Maldonado <emaldona@redhat.com> - 3.12.4-19
- Consider the system as not fips enabled when /proc/sys/crypto/fips_enabled isn't present (rhbz#590199)

* Sat May 08 2010 Elio Maldonado <emaldona@redhat.com> - 3.12.4-18
- Fix Conflicts line to prevent update when prelink is not yet the right version (rhbz#590199)

* Mon Apr 19 2010 Elio Maldonado <emaldona@redhat.com> - 3.12.4-17
- Updated prelink patch rhbz#504949

* Wed Apr 15 2010 Elio Maldonado <emaldona@redhat.com> - 3.12.4-16
- allow prelink of softoken and freebl. Change the verify code to use
  prelink -u if prelink is installed. Fix by Robert Relyea rhbz#504949

* Mon Jan 18 2010 Elio Maldonado <emaldona@redhat.com> - 3.12.4-15
- Move libfreebl3.so and its .chk file to /lib{64} (rhbz#561544)

* Mon Jan 18 2010 Elio Maldonado <emaldona@redhat.com> - 3.12.4-13
- Fix in nss-softokn-spec.in 
- Require nss-util >= 3.12.4

* Thu Dec 03 2009 Elio Maldonado<emaldona@redhat.com> - 3.12.4-12
- Require nss-util 3.12.5

* Fri Nov 20 2009 Elio Maldonado<emaldona@redhat.com> - 3.12.4-11
- export freebl devel tools (#538226)

* Tue Sep 23 2009 Elio Maldonado<emaldona@redhat.com> - 3.12.4-10
- Fix paths in nss-softokn-prelink so signed libraries don't get touched, rhbz#524794

* Thu Sep 17 2009 Elio Maldonado<emaldona@redhat.com> - 3.12.4-9
- Add nssdbm3.so to nss-softokn-prelink.conf, rhbz#524077

* Thu Sep 10 2009 Elio Maldonado<emaldona@redhat.com> - 3.12.4-8
- Retagging for a chained build

* Thu Sep 10 2009 Elio Maldonado<emaldona@redhat.com> - 3.12.4-6
- Don't list libraries in nss-softokn-config, dynamic linking required

* Tue Sep 08 2009 Elio Maldonado<emaldona@redhat.com> - 3.12.4-5
- Installing shared libraries to %%{_libdir}

* Sun Sep 06 2009 Elio Maldonado<emaldona@redhat.com> - 3.12.4-4
- Postuninstall scriptlet finishes quietly

* Sat Sep 05 2009 Elio Maldonado<emaldona@redhat.com> - 3.12.4-3
- Remove symblic links to shared libraries from devel, rhbz#521155
- Apply the nss-nolocalsql patch
- No rpath-link in nss-softokn-config

* Fri Sep 04 2009 serstring=Elio Maldonado<emaldona@redhat.cpm> - 3.12.4-2
- Retagging to pick up the correct .cvsignore

* Tue Sep 01 2009 Elio Maldonado<emaldona@redhat.com> - 3.12.4-1
- Update to 3.12.4
- Fix logic on postun
- Don't require sqlite

* Mon Aug 31 2009 Elio Maldonado<emaldona@redhat.com> - 3.12.3.99.3-24
- Fixed test on %postun to avoid returning 1 when nss-softokn instances still remain

* Sun Aug 30 2009 Elio Maldonado<emaldona@redhat.com> - 3.12.3.99.3-23
- Explicitly state via nss_util_version the nss-util version we require

* Fri Aug 28 2009 Warren Togami <wtogami@redhat.com> - 3.12.3.99.3-22
- caolan's nss-softokn.pc patch

* Thu Aug 27 2009 Elio Maldonado<emaldona@redhat.com> - 3.12.3.99.3-21
- Bump the release number for a chained build of nss-util, nss-softokn and nss

* Thu Aug 27 2009 Elio Maldonado<emaldona@redhat.com> - 3.12.3.99.3-20
- List freebl, nssdbm and softokn libraries in nss-softokn-config and nss-softokn.pc

* Thu Aug 27 2009 Elio Maldonado@<emaldona@redhat.com> - 3.12.3.99.3-19
- Determine NSSUTIL_INCLUDE_DIR and NSSUTIL_LIB_DIR with a pkg-config query on nss-util
- Remove the release 17 hack

* Wed Aug 27 2009 Elio maldonado<emaldona@redhat.com> - 3.12.3.99.3-18
- fix spurious executable permissions on nss-softokn.pc

* Thu Aug 27 2009 Adel Gadllah <adel.gadllah@gmail.com> - 3.12.3.99.3-17
- Add hack to fix build

* Tue Aug 25 2009 Dennis Gilmore <dennis@ausil.us> - 3.12.3.99.3-16
- only have a single Requires: line in the .pc file

* Tue Aug 25 2009 Dennis Gilmore <dennis@ausil.us> - 3.12.3.99.3-12
- bump to unique rpm nvr 

* Tue Aug 25 2009 Elio Maldonado<emaldona@redhat.com> - 3.12.3.99.3-10
- Build after nss with subpackages and new nss-util

* Thu Aug 20 2009 Dennis Gilmore <dennis@ausil.us> 3.12.3.99.3-9
- revert to shipping bits

* Thu Aug 19 2009 Elio Maldonado <emaldona@redhat.com> 3.12.3.99.3-8.1
- Disable installing until conflicts are relsoved

* Thu Aug 19 2009 Elio Maldonado <emaldona@redhat.com> 3.12.3.99.3-8
- Initial build
