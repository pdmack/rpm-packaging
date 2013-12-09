Name:           metrics
Version:        3.0.1
Release:        1%{?dist}
Summary:        metrics library for Java
License:        ASL 2.0
URL:            http://metrics.codahale.com
Source0:        https://github.com/codahale/metrics/archive/v%{version}.tar.gz
Patch0:		metrics-3.0.1-plugins.patch
BuildArch:      noarch

BuildRequires:  maven-local
BuildRequires:  mvn(ch.qos.logback:logback-classic) 
BuildRequires:  mvn(com.fasterxml.jackson.core:jackson-databind) 
BuildRequires:  mvn(com.sun.jersey:jersey-server) 
BuildRequires:  mvn(log4j:log4j) 
BuildRequires:  mvn(net.sf.ehcache:ehcache-core) 
BuildRequires:  mvn(org.apache.httpcomponents:httpclient) 
BuildRequires:  mvn(org.eclipse.jetty:jetty-server) 
BuildRequires:  mvn(org.slf4j:slf4j-api)

%description

Metrics provides a powerful toolkit of ways to measure the behavior of
critical components in your production environment.

With modules for common libraries and reporting backends, Metrics
provides you with full-stack visibility.

%package javadoc
Summary:        API documentation for %{name}

%description javadoc
This package provides %{summary}.

%prep
%setup -q
%patch0 -p1
# this is kind of a blunt instrument, but we're missing some test dependencies for now
find . -type d -name test | xargs rm -rf

%build
%mvn_build -f

%install
%mvn_install

%files -f .mfiles
%doc README.md
%doc LICENSE NOTICE
%dir %{_javadir}/%{name}

%files javadoc -f .mfiles-javadoc
%doc LICENSE NOTICE

%changelog
* Fri Nov 29 2013 William Benton <willb@redhat.com> - 3.0.1-1
- Initial packaging
