%define _legacy_common_support 1
%global __jar_repack %{nil}
%define debug_package %{nil}

# Put only the same build id with the commit in all sources
%global build_id 201.7223.91

# intellij-community
%global commit0 40e5005d02df57f58ac2d498867446c43d61101f
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

# JetBrains-android
%global commit1 8933ebe1a49d4f96d69431442f518be2d448b1e5
%global shortcommit1 %(c=%{commit1}; echo ${c:0:7})

# adt-tools-base
# See commits here http://git.jetbrains.org/?p=idea/adt-tools-base.git;a=summary
# You can make the tarball "./intellij-idea-community-snapshot -c your_commit_here
%global commit2 17e9c8b666cac0b974b1efc5e1e4c33404f72904 
%global shortcommit2 %(c=%{commit2}; echo ${c:0:7})

Summary:	Intelligent Java IDE
Name:		intellij-idea-community-edition
Version:	2020.1.1
Release:	1%{?dist}
License:	ASL 2.0
Group:          Development/Languages
Url:		https://www.jetbrains.com/idea/

Source0:	https://github.com/JetBrains/intellij-community/archive/%{commit0}.zip#/%{name}-%{shortcommit0}.tar.gz
Source1:	https://github.com/JetBrains/android/archive/%{commit1}.zip#/JetBrains-android-%{shortcommit1}.tar.gz
Source2:	adt-tools-base-17e9c8b.tar.gz	
Source3:	idea.desktop
Source4:	idea.sh

BuildRequires:	ant
BuildRequires:	java-1.8.0-openjdk-devel
BuildRequires:	java-1.8.0-openjdk-openjfx java-1.8.0-openjdk-openjfx-devel
BuildRequires:	openjfx openjfx-devel
BuildRequires:	git
BuildRequires:	python3-devel
#-------------------------------------------------------------------------------
Requires:	java-1.8.0-openjdk
Requires:	openjfx
Requires:	java-1.8.0-openjdk-openjfx	

%description
IntelliJ IDEA analyzes your code, looking for connections between symbols
across all project files and languages.  Using this information it provides
indepth coding assistance, quick navigation, clever error analysis, and, of
course, refactorings.

%prep
%setup -n intellij-community-%{commit0} -a1 -a2
  # build system doesn't like symlinks
  mv -f android-%{commit1} android
  mv -f adt-tools-base-%{shortcommit2} android/tools-base
  

sed '/def targetOs =/c def targetOs = "linux"' -i build/dependencies/setupJbre.gradle
  sed '/String targetOS/c   String targetOS = OS_LINUX' -i platform/build-scripts/groovy/org/jetbrains/intellij/build/BuildOptions.groovy
  sed -E 's|(<sysproperty key="jna.nosys")|<sysproperty key="intellij.build.target.os" value="linux" />\1|' -i build.xml
  sed -E 's/-Xmx[0-9]+m/-XX:-UseGCOverheadLimit/' -i build.xml
  echo %{build_id} > build.txt

# python fixes  
  find -depth -type f -writable -name "*.py" -exec sed -iE '1s=^#! */usr/bin/\(python\|env python\)[23]\?=#!%{__python3}=' {} +

%build

  unset _JAVA_OPTIONS
  jvm_path=$(ls -1F /usr/lib/jvm/ | grep -i "/" | sed -e 's|/||g' | grep -e "java-1.8.")
  export JAVA_HOME=/usr/lib/jvm/$jvm_path  
  export PATH="${JAVA_HOME}/bin:${PATH}"
  ant build
  
  tar -xf "out/idea-ce/artifacts/ideaIC-%{build_id}-no-jbr.tar.gz" -C $PWD

%install

pushd idea-IC-%{build_id}

  sed -i 's/lcd/on/' bin/*.vmoptions

  rm -rf bin/fsnotifier-arm lib/libpty/linux/x86

  install -dm 755 %{buildroot}/usr/share/{licenses,pixmaps,icons/hicolor/scalable/apps}
  install -dm 755 %{buildroot}/%{_javadir}/idea/
  mv -f {bin,lib,plugins,redist} %{buildroot}/%{_javadir}/idea/
  cp -dr --no-preserve='ownership' license %{buildroot}/usr/share/licenses/idea
  ln -s /%{_javadir}/idea/bin/idea.png %{buildroot}/usr/share/pixmaps/
  ln -s /%{_javadir}/idea/bin/idea.svg %{buildroot}/usr/share/icons/hicolor/scalable/apps/
  install -Dm 644 %{S:3} -t %{buildroot}/usr/share/applications/
  install -Dm 755 %{S:4} %{buildroot}/usr/bin/idea
  install -Dm 644 build.txt -t %{buildroot}/%{_javadir}/idea
popd


#mangling

sed -i 's|/bin/sh|/usr/bin/sh|g' %{buildroot}/%{_javadir}/idea/bin/idea.sh 
sed -i 's|/bin/sh|/usr/bin/sh|g' %{buildroot}/%{_javadir}/idea/bin/format.sh 
sed -i 's|/bin/sh|/usr/bin/sh|g' %{buildroot}/%{_javadir}/idea/bin/inspect.sh 

sed -i 's|/usr/bin/env bash|/usr/bin/bash|g' %{buildroot}/%{_javadir}/idea/plugins/Kotlin/kotlinc/bin/kotlin 
sed -i 's|/usr/bin/env bash|/usr/bin/bash|g' %{buildroot}/%{_javadir}/idea/plugins/Kotlin/kotlinc/bin/kotlinc-jvm 
sed -i 's|/usr/bin/env bash|/usr/bin/bash|g' %{buildroot}/%{_javadir}/idea/plugins/Kotlin/kotlinc/bin/kotlinc-js 
sed -i 's|/usr/bin/env bash|/usr/bin/bash|g' %{buildroot}/%{_javadir}/idea/plugins/Kotlin/kotlinc/bin/kotlin-dce-js 
sed -i 's|/usr/bin/env bash|/usr/bin/bash|g' %{buildroot}/%{_javadir}/idea/plugins/Kotlin/kotlinc/bin/kotlinc 
 

%files
%{_bindir}/idea
%{_datadir}/applications/idea.desktop
%{_datadir}/icons/hicolor/scalable/apps/idea.svg
%{_datadir}/pixmaps/idea.png
%{_javadir}/idea/
%{_datadir}/licenses/idea/


%changelog

* Tue May 05 2020 Unitedrpms Project <unitedrpms AT protonmail DOT com> - 2020.1.1-1
- Initial build
