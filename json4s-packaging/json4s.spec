%global json4s_version 3.2.7
%global scala_version 2.10

# we don't want scalaz support atm
%global want_scalaz 0

Name:           json4s
Version:        %{json4s_version}
Release:        1%{?dist}
Summary:        Common AST for Scala JSON parsers.

License:        ASL 2.0
URL:            https://github.com/json4s/json4s
Source0:        https://github.com/json4s/json4s/archive/v%{json4s_version}_%{scala_version}.tar.gz
Source1:	https://raw.github.com/willb/climbing-nemesis/master/climbing-nemesis.py

BuildArch:	noarch
BuildRequires:  sbt
BuildRequires:  scala
BuildRequires:	python
BuildRequires:	maven-local
BuildRequires:	javapackages-tools
Requires:	javapackages-tools
Requires:       scala

%description

json4s is a common AST for Scala JSON parsers.

%package javadoc
Summary:        Javadoc for %{name}

%description javadoc
Javadoc for %{name}.

%prep
%setup -q

sed -i -e 's/2[.]10[.][012]/2.10.3/g' project/*

sed -i -e 's/0[.]13[.]0/0.13.1/g' project/build.properties || echo sbt.version=0.13.1 > project/build.properties

sed -i -e '/lift build/d'  project/Dependencies.scala
sed -i -e '/def crossMapped/,+1d'  project/Dependencies.scala


# not used in Fedora
sed -i -e '/net.liftweb/d' project/Dependencies.scala

# only needed by liftweb
sed -i -e '/commons-codec/d' project/Dependencies.scala

# only needed by examples and benchmarks
sed -i -e '/jackson-module-scala/d' project/Dependencies.scala

sed -i -e 's/cross crossMapped.*//' project/Dependencies.scala



%if %{want_scalaz} == 0
sed -i -e '/scalaz/d' project/Dependencies.scala
sed -i -e 's/scalazExt(, )?//' project/build.scala
sed -i -e '/lazy val scalazExt/,/dependsOn/d' project/build.scala
%endif

sed -i -e '/lazy val examples = Project/,/lazy val.*= Project/{//;p;d}' project/build.scala

for target in json4stests benchmark mongo ; do
sed -i -e '/lazy val '$target'/,/dependsOn/d' project/build.scala
sed -i -e 's/'$target'(, )?//' project/build.scala
done

sed -i -e 's/[+][+] buildInfoSettings//' project/build.scala
sed -i -e '/buildInfo/d' project/build.scala

rm -f project/plugins.sbt

cp -r /usr/share/java/sbt/ivy-local .
mkdir boot

cp %{SOURCE1} .

chmod 755 climbing-nemesis.py

./climbing-nemesis.py --jarfile /usr/share/java/scalacheck.jar org.scalacheck scalacheck ivy-local --version 1.11.0 --scala %{scala_version}


%build

export SBT_BOOT_DIR=boot
export SBT_IVY_DIR=ivy-local
sbt package deliverLocal publishM2Configuration

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/%{_javadir}
mkdir -p %{buildroot}/%{_mavenpomdir}

mkdir -p %{buildroot}/%{_javadocdir}/%{name}

cp core/target/scala-%{scala_version}/%{name}_%{scala_version}-%{version}.jar %{buildroot}/%{_javadir}/%{name}.jar
cp core/target/scala-%{scala_version}/%{name}_%{scala_version}-%{version}.pom %{buildroot}/%{_mavenpomdir}/JPP-%{name}.pom

cp -rp core/target/scala-%{scala_version}/api/* %{buildroot}/%{_javadocdir}/%{name}

%add_maven_depmap JPP-%{name}.pom %{name}.jar

%files
%{_javadir}/%{name}.jar
%{_mavenpomdir}/JPP-%{name}.pom
%{_mavendepmapfragdir}/%{name}

%doc LICENSE README

%files javadoc
%{_javadocdir}/%{name}


%changelog

* Wed Feb 19 2014 William Benton <willb@redhat.com> - 3.2.7-1
- initial package
