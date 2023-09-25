BuildArch:      noarch
Name:           cert-gen
Version:        1.7.0
Release:        1
License:        GPLv3
Group:          Unspecified
Summary:        A RPM package that generates upon installing a self signed certificate
Distribution:   PhotonPonyOS

URL:            https://gitlab.bbn.apsensing.com/infrastructure/ppos/dib/-/tree/ppos38
Vendor:         AP Sensing
Packager:       AP Sensing
Provides:       cert-gen = %{version}-%{release}

Requires:       openssl
Requires:       systemd
Requires:       aps-nginx
Requires:       aps-dts-user

Requires(pre):  shadow-utils
Requires(post): policycoreutils
Requires(postun): policycoreutils

%{?systemd_requires}

Source0:        %{_sourcedir}/aps-cert-gen
Source2:        %{_sourcedir}/README.md
Source3:        %{_sourcedir}/aps-cert-ln
Source4:        %{_sourcedir}/aps-cert-ln.service
Source5:        %{_sourcedir}/42-aps-cert-ln.preset

%description
A RPM package that generates a self signed certificate upon installing.

%prep

%build

%pre
getent group dts_cert > /dev/null || groupadd -r dts_cert
usermod -aG dts_cert nginx
usermod -aG dts_cert dts

%post
pushd /usr/share/aps/dts/cert
rm -rf dts.crt
rm -rf dts.key

aps-cert-gen

chmod 640 dts.key
chown nginx:dts_cert dts.key
chmod 640 dts.crt
chown nginx:dts_cert dts.crt
popd

# SELinux RPM instructions: https://fedoraproject.org/wiki/PackagingDrafts/SELinux#File_contexts
semanage fcontext -a -t httpd_sys_content_t '/opt/cert(/.*)?' 2>/dev/null || :
semanage fcontext -a -t httpd_sys_content_t '/usr/share/aps/dts/cert(/.*)?' 2>/dev/null || :
# restorecon -R /opt/cert/ || : # Don't do this 
restorecon -R /usr/share/aps/dts/cert || :

# Run after creating certs to avoid conflicts
%systemd_post aps-cert-ln.service

%postun
if [ $1 -eq 0 ] ; then
    semanage fcontext -d -t httpd_sys_content_t '/opt/cert(/.*)?' 2>/dev/null || :
    semanage fcontext -d -t httpd_sys_content_t '/usr/share/aps/dts/cert(/.*)?' 2>/dev/null || :
fi

# Run after applying cert SELinux rules to avoid conflicts 
%systemd_postun_with_restart aps-cert-ln.service

%preun
%systemd_preun aps-cert-ln.service

%install
install -d -m 755 $RPM_BUILD_ROOT/usr/share/aps/dts/cert
install -m 644 %{_sourcedir}/README.md $RPM_BUILD_ROOT/usr/share/aps/dts/cert/README.md

install -d -m 755 $RPM_BUILD_ROOT/usr/bin/
install -m 755 %{_sourcedir}/aps-cert-gen $RPM_BUILD_ROOT/usr/bin
install -m 755 %{_sourcedir}/aps-cert-ln $RPM_BUILD_ROOT/usr/bin

install -d -m 755 $RPM_BUILD_ROOT/usr/lib/systemd/system
install -m 644 %{_sourcedir}/aps-cert-ln.service $RPM_BUILD_ROOT/usr/lib/systemd/system

install -d -m 755 $RPM_BUILD_ROOT/usr/lib/systemd/system-preset
install -m 644 %{_sourcedir}/42-aps-cert-ln.preset $RPM_BUILD_ROOT/usr/lib/systemd/system-preset

%files
%dir %attr(755, nginx, dts_cert) /usr/share/aps/dts/cert
%attr(644, nginx, dts_cert) /usr/share/aps/dts/cert/README.md

%attr(755, root, root) /usr/bin/aps-cert-gen
%attr(755, root, root) /usr/bin/aps-cert-ln

%attr(644, root, root) /usr/lib/systemd/system/aps-cert-ln.service

%attr(644, root, root) /usr/lib/systemd/system-preset/42-aps-cert-ln.preset

%changelog
* Mon Sep 25 2023 Fabian Sauter <fabian.sauter+rpm@apsensing.com> - 1.7.0-1
- SELinux adding the httpd_sys_content_t label to /opt/cert

* Mon Sep 25 2023 Fabian Sauter <fabian.sauter+rpm@apsensing.com> - 1.6.0-1
- Using the aps-dts-user RPM package for the dts user

* Thu Aug 24 2023 Fabian Sauter <fabian.sauter+rpm@apsensing.com> - 1.5.0-1
- Certs are now stored inside '/usr/share/aps/dts/cert'.
- '/opt/cert' contains proper replacement certificates or softlinks to the contents of '/usr/share/aps/dts/cert'.
- Systemd onshot service for creating symlinks to the cert and key file in '/opt/cert'.

* Wed Aug 23 2023 Fabian Sauter <fabian.sauter+rpm@apsensing.com> - 1.4.0-1
- Allowing login to the dts user

* Tue Aug 22 2023 Fabian Sauter <fabian.sauter+rpm@apsensing.com> - 1.3.0-1
- Creating a home directory for the dts user on creation

* Mon Aug 21 2023 Fabian Sauter <fabian.sauter+rpm@apsensing.com> - 1.2.0-1
- Requiring aps-nginx instead of nginx 

* Tue Aug 15 2023 Fabian Sauter <fabian.sauter+rpm@apsensing.com> - 1.0.0-1
- Initial release