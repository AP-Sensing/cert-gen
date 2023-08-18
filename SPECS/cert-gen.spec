BuildArch:      noarch
Name:           cert-gen
Version:        1.1.0
Release:        2
License:        GPLv3
Group:          Unspecified
Summary:        A RPM package that generates upon installing a self signed certificate
Distribution:   PhotonPonyOS

URL:            https://gitlab.bbn.apsensing.com/infrastructure/ppos/dib/-/tree/ppos38
Vendor:         AP Sensing
Packager:       AP Sensing
Provides:       cert-gen = %{version}-%{release}

Requires:       openssl
Requires:       nginx

Requires(pre):  shadow-utils
Requires(post): policycoreutils
Requires(postun): policycoreutils

Source0:        %{_sourcedir}/cert-gen

%description
A RPM package that generates upon installing a self signed certificate.

%prep

%build

%pre
getent group dts_cert >/dev/null || groupadd -r dts_cert
getent passwd dts >/dev/null || useradd -r -g dts_cert -d /home/dts -s /sbin/nologin -c "Main dts user account" dts
usermod -aG dts_cert nginx
usermod -aG dts_cert dts

%post
pushd /opt/cert
# Generate a new certificate only if there is not already one.
# This is usefull to allow the user to replace the cert later and we do not change it then.
if [[ ! -f "dts.key" && ! -f "dts.crt" ]]; then
    cert-gen
    chmod 640 dts.key
    chmod 640 dts.crt
fi
popd

chown -R nginx:dts_cert /opt/cert/

# SELinux RPM instructions: https://fedoraproject.org/wiki/PackagingDrafts/SELinux#File_contexts
semanage fcontext -a -t httpd_sys_content_t '/opt/cert(/.*)?' 2>/dev/null || :
restorecon -R /opt/cert || :

%postun
if [ $1 -eq 0 ] ; then
    semanage fcontext -d -t httpd_sys_content_t '/opt/cert(/.*)?' 2>/dev/null || :
fi

%install
install -d -m 755 $RPM_BUILD_ROOT/opt/cert/

install -d -m 755 $RPM_BUILD_ROOT/usr/bin/
install -m 755 %{_sourcedir}/cert-gen $RPM_BUILD_ROOT/usr/bin

%files
%attr(755, nginx, dts_cert) /opt/cert/

%attr(755, root, root) /usr/bin/cert-gen

%changelog
* Tue Aug 15 2023 Fabian Sauter <fabian.sauter+rpm@apsensing.com> - 1.0.0-1
- Initial release