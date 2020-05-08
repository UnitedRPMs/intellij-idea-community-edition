#!/usr/bin/sh

# WARNING:
# Running IntelliJ IDEA with java other than java 11
# may cause various problems, such as Graddle import not working
if [ -z "$IDEA_JDK" ] ; then
  jvm_path=$(ls -1F /usr/lib/jvm/ | grep -i "/" | sed -e 's|/||g' | grep -e "java-1.8.")
  IDEA_JDK=/usr/lib/jvm/$jvm_path
fi
exec env IDEA_JDK="$IDEA_JDK" /usr/share/java/idea/bin/idea.sh "$@"

