%global json4s_version 3.2.7
%global scala_version 2.10

%global remap_version_to_installed() sed -i -e 's/"%{1}" %% "%{2}" %% "[^"]*"/"%{1}" %% "%{2}" %% "'$(rpm -q --qf "%%%%{version}" $(rpm -q --whatprovides "mvn(%{1}:%{2})" ))'"/g' %{3}

# we don't want scalaz support atm
%global want_scalaz 0

Name:		json4s
Version:	%{json4s_version}
Release:	1%{?dist}
Summary:	Common AST for Scala JSON parsers

License:	ASL 2.0
URL:		https://github.com/json4s/json4s
Source0:	https://github.com/json4s/json4s/archive/v%{json4s_version}_%{scala_version}.tar.gz
Source1:	https://raw.github.com/willb/climbing-nemesis/master/climbing-nemesis.py

BuildArch:	noarch
BuildRequires:	sbt
BuildRequires:	scala
BuildRequires:	python
BuildRequires:	maven-local
BuildRequires:	javapackages-tools
Requires:	javapackages-tools
Requires:	scala

Requires:	mvn(com.thoughtworks.paranamer:paranamer)
Requires:	mvn(org.scala-lang:scalap)
Requires:	mvn(com.fasterxml.jackson.core:jackson-databind)
Requires:	mvn(com.fasterxml.jackson.core:jackson-core)
Requires:	mvn(com.fasterxml.jackson.core:jackson-annotations)
Requires:	mvn(joda-time:joda-time)
Requires:	mvn(org.joda:joda-convert)

BuildRequires:	mvn(com.thoughtworks.paranamer:paranamer)
BuildRequires:	mvn(org.scala-lang:scalap)
BuildRequires:	mvn(com.fasterxml.jackson.core:jackson-databind)
BuildRequires:	mvn(com.fasterxml.jackson.core:jackson-core)
BuildRequires:	mvn(com.fasterxml.jackson.core:jackson-annotations)
BuildRequires:	mvn(joda-time:joda-time)
BuildRequires:	mvn(org.joda:joda-convert)

%description

json4s is a common AST for Scala JSON parsers.

%package javadoc
Summary:	Javadoc for %{name}

%description javadoc
Javadoc for %{name}.

%prep
%setup -q -n %{name}-%{version}_%{scala_version}

# eliminate lift codeOB
rm -rf native-lift

# work around buildinfo absence
sed -i -e 's/BuildInfo.organization/"org.json4s"/' jackson/src/main/scala/org/json4s/jackson/Json4sScalaModule.scala
sed -i -e 's/BuildInfo.name/"json4s"/' jackson/src/main/scala/org/json4s/jackson/Json4sScalaModule.scala
sed -i -e 's/BuildInfo.version/"%{version}"/' jackson/src/main/scala/org/json4s/jackson/Json4sScalaModule.scala

sed -i -e 's/2[.]10[.][012]/2.10.3/g' project/*

sed -i -e 's/0[.]13[.]0/0.13.1/g' project/build.properties || echo sbt.version=0.13.1 > project/build.properties

sed -i -e '/lift build/d'  project/Dependencies.scala
sed -i -e '/def crossMapped/,+1d'  project/Dependencies.scala

%remap_version_to_installed com.fasterxml.jackson.core jackson-databind project/Dependencies.scala

# not used in Fedora
sed -i -e '/net.liftweb/d' project/Dependencies.scala

# only needed by liftweb
sed -i -e '/commons-codec/d' project/Dependencies.scala

# only needed by examples and benchmarks
sed -i -e '/jackson-module-scala/d' project/Dependencies.scala

sed -i -e 's/cross crossMapped.*//' project/Dependencies.scala

sed -i -i '/com.typesafe/d' project/build.scala

sed -i -e '/lazy val examples = Project/,/lazy val.*= Project/{/.*/d}' project/build.scala
sed -i -e '/^[/][/].*/d' project/build.scala

%if %{want_scalaz} == 0
sed -i -e '/scalaz/d' project/Dependencies.scala
sed -i -e 's/scalazExt,//' project/build.scala
sed -i -e '/lazy val scalazExt/,/dependsOn/d' project/build.scala
%endif

for target in json4sTests benchmark mongo ; do
sed -i -e '/lazy val '$target'/,/dependsOn/d' project/build.scala
sed -i -e 's/'$target',//' project/build.scala
done

sed -i -e 's/[+][+] buildInfoSettings//' project/build.scala
sed -i -e '/buildInfo/d' project/build.scala
sed -i -e '/sbtbuildinfo/d' project/build.scala

# munge publishSettings
sed -i 's/^\(.*val publishSetting =.*\)$/PUBLISH_SETTING_HERE\n\1/' project/build.scala
sed -i '/val publishSetting =/,/^[[:space:]]*[}][[:space:]]*$/d' project/build.scala
sed -i 's|PUBLISH_SETTING_HERE|val publishSetting = publishTo <<= (version) { version: String =>\nval cwd = java.lang.System.getProperty("user.dir")\nSome(Resolver.file("published", file("published"))(Resolver.ivyStylePatterns) ivys s"$cwd/published/[organization]/[module]/[revision]/ivy.xml" artifacts s"$cwd/published/[organization]/[module]/[revision]/[artifact]-[revision].[ext]")\n}|' project/build.scala

rm -f project/plugins.sbt

cp -r /usr/share/sbt/ivy-local .
mkdir boot

cp %{SOURCE1} .

chmod 755 climbing-nemesis.py

./climbing-nemesis.py com.thoughtworks.paranamer paranamer ivy-local --version 2.6
./climbing-nemesis.py org.scala-lang scalap ivy-local --version 2.10.3
./climbing-nemesis.py com.fasterxml.jackson.core jackson-databind ivy-local --ignore maven-scm-provider-gitexe
./climbing-nemesis.py com.fasterxml.jackson.core jackson-core ivy-local --ignore maven-scm-provider-gitexe
./climbing-nemesis.py com.fasterxml.jackson.core jackson-annotations ivy-local --ignore maven-scm-provider-gitexe
./climbing-nemesis.py joda-time joda-time ivy-local --version 2.3
./climbing-nemesis.py org.joda joda-convert ivy-local --version 1.6

%build

export SBT_BOOT_DIR=boot
export SBT_IVY_DIR=ivy-local

sbt package "set publishTo in Global := Some(Resolver.file(\"published\", file(\"published\"))(Resolver.ivyStylePatterns) ivys \"$(pwd)/published/[organization]/[module]/[revision]/ivy.xml\" artifacts \"$(pwd)/published/[organization]/[module]/[revision]/[artifact]-[revision].[ext]\")" publish makePom

# XXX: this is a hack; we seem to get correct metadata but bogus JARs
# from "sbt publish" for some reason
for f in $(find published -name \*.jar ) ; do
  find . -ipath \*target\* -and -name $(basename $f) -exec cp '{}' $f \;
done

%install
mkdir -p %{buildroot}/%{_javadir}/%{name}
mkdir -p %{buildroot}/%{_mavenpomdir}

mkdir -p %{buildroot}/%{_javadocdir}/%{name}
for apidir in $(find . -name api -type d) ; do
  pushd $apidir
  cp -rp . %{buildroot}/%{_javadocdir}/%{name}
  popd
done

for jar in $(find published -name \*.jar | grep -v %{name}_%{scala_version}-%{version}.jar) ; do
  install -m 644 $jar %{buildroot}/%{_javadir}/%{name}/$(echo $jar | cut -f5 -d/ | cut -f1 -d_).jar
done

declare -a shortnames

for pom in $(find published -name \*.pom | grep -v %{name}_%{scala_version}-%{version}.pom ) ; do 
  shortname=$(echo $pom | cut -f5 -d/ | cut -f1 -d_)
  echo installing POM $pom to %{_mavenpomdir}/JPP.%{name}-${shortname}.pom
  install -pm 644 $pom %{buildroot}/%{_mavenpomdir}/JPP.%{name}-${shortname}.pom
  echo %{_mavenpomdir}/JPP.%{name}-${shortname}.pom >> .rpm_pomfiles
  shortnames=( "${shortnames[@]}" $shortname )
done

for sub in ${shortnames[@]} ; do
  echo running add_maven_depmap JPP.%{name}-${sub}.pom %{name}/${sub}.jar
  %add_maven_depmap JPP.%{name}-${sub}.pom %{name}/${sub}.jar
done

%files -f .mfiles
%dir %{_javadir}/%{name}

%doc LICENSE README.md

%files javadoc
%{_javadocdir}/%{name}
%doc LICENSE


%changelog

* Wed Feb 19 2014 William Benton <willb@redhat.com> - 3.2.7-1
- initial package
