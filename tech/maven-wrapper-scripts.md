# The Maven wrapper scripts (mvnw and mvnw.cmd), line by line

## What it is

The Maven wrapper is two small programs that start Maven without Maven being installed. `java/mvnw` is a **shell script** (`bash.md`) for macOS and Linux. `java/mvnw.cmd` is a **batch file** for Windows that also contains a **PowerShell** program: one file, two languages. Both come from the Apache Maven Wrapper project (version 3.3.4), are licensed under Apache 2.0 and are not edited here.

## Why this repository uses it

The Java half has to build the same way on any machine. The wrapper downloads the exact Maven version named in `.mvn/wrapper/maven-wrapper.properties` the first time and keeps it under `~/.m2/wrapper`, so `./mvnw test` just works (`maven.md`).

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `java/mvnw` | The POSIX shell script. |
| `java/mvnw.cmd` | The Windows batch and PowerShell script. |
| `java/.mvn/wrapper/maven-wrapper.properties` | Names the Maven download address. |


## How it works underneath

Both scripts do the same eight things: (1) find the Java installation; (2) read `distributionUrl` from the properties file; (3) work out the folder where this Maven version lives, named after the version and a hash of the address; (4) if the folder exists, run Maven from there; (5) otherwise download the zip (with `wget`, `curl` or, as a last resort, a tiny Java program), (6) optionally check its SHA-256 (`sha-256.md`), (7) unpack it into a temporary folder and move it into place, and (8) run Maven with the arguments you gave. A temporary folder is always removed at the end, even after an error.

## Walkthrough of this repository's use

### java/mvnw (shell)

The script is explained in groups of lines. Words such as *variable*, *function*, *exit status* and *standard error* are explained at their first use, and `bash.md` has the general ideas.

`java/mvnw`

```bash
#!/bin/sh
# ----------------------------------------------------------------------------
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
```

- `#!/bin/sh`: a comment written by the author; the tool ignores it. It explains the lines below.
- `# ----------------------------------------------------------------------------`: a comment written by the author; the tool ignores it. It explains the lines below.
- `# Licensed to the Apache Software Foundation (ASF) under one`: a comment written by the author; the tool ignores it. It explains the lines below.
- `# or more contributor license agreements.  See the NOTICE file`: a comment written by the author; the tool ignores it. It explains the lines below.
- `# distributed with this work for additional information`: a comment written by the author; the tool ignores it. It explains the lines below.
- `# regarding copyright ownership.  The ASF licenses this file`: a comment written by the author; the tool ignores it. It explains the lines below.
- `# to you under the Apache License, Version 2.0 (the`: a comment written by the author; the tool ignores it. It explains the lines below.
- `# "License"); you may not use this file except in compliance`: a comment written by the author; the tool ignores it. It explains the lines below.
- `# with the License.  You may obtain a copy of the License at`: a comment written by the author; the tool ignores it. It explains the lines below.
- `#`: a comment written by the author; the tool ignores it. It explains the lines below.

```bash
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
# ----------------------------------------------------------------------------
```

- `#    http://www.apache.org/licenses/LICENSE-2.0`: a comment written by the author; the tool ignores it. It explains the lines below.
- `#`: a comment written by the author; the tool ignores it. It explains the lines below.
- `# Unless required by applicable law or agreed to in writing,`: a comment written by the author; the tool ignores it. It explains the lines below.
- `# software distributed under the License is distributed on an`: a comment written by the author; the tool ignores it. It explains the lines below.
- `# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY`: a comment written by the author; the tool ignores it. It explains the lines below.
- `# KIND, either express or implied.  See the License for the`: a comment written by the author; the tool ignores it. It explains the lines below.
- `# specific language governing permissions and limitations`: a comment written by the author; the tool ignores it. It explains the lines below.
- `# under the License.`: a comment written by the author; the tool ignores it. It explains the lines below.
- `# ----------------------------------------------------------------------------`: a comment written by the author; the tool ignores it. It explains the lines below.

```bash
# ----------------------------------------------------------------------------
# Apache Maven Wrapper startup batch script, version 3.3.4
#
# Optional ENV vars
# -----------------
#   JAVA_HOME - location of a JDK home dir, required when download maven via java source
#   MVNW_REPOURL - repo url base for downloading maven distribution
#   MVNW_USERNAME/MVNW_PASSWORD - user and password for downloading maven
#   MVNW_VERBOSE - true: enable verbose log; debug: trace the mvnw script; others: silence the output
# ----------------------------------------------------------------------------
```

- `# ----------------------------------------------------------------------------`: a comment written by the author; the tool ignores it. It explains the lines below.
- `# Apache Maven Wrapper startup batch script, version 3.3.4`: a comment written by the author; the tool ignores it. It explains the lines below.
- `#`: a comment written by the author; the tool ignores it. It explains the lines below.
- `# Optional ENV vars`: a comment written by the author; the tool ignores it. It explains the lines below.
- `# -----------------`: a comment written by the author; the tool ignores it. It explains the lines below.
- `#   JAVA_HOME - location of a JDK home dir, required when download maven via java source`: a comment written by the author; the tool ignores it. It explains the lines below.
- `#   MVNW_REPOURL - repo url base for downloading maven distribution`: a comment written by the author; the tool ignores it. It explains the lines below.
- `#   MVNW_USERNAME/MVNW_PASSWORD - user and password for downloading maven`: a comment written by the author; the tool ignores it. It explains the lines below.
- `#   MVNW_VERBOSE - true: enable verbose log; debug: trace the mvnw script; others: silence the outpu`: a comment written by the author; the tool ignores it. It explains the lines below.
- `# ----------------------------------------------------------------------------`: a comment written by the author; the tool ignores it. It explains the lines below.

```bash
set -euf
[ "${MVNW_VERBOSE-}" != debug ] || set -x
```

- `set -euf`: Three safety switches. `-e`: stop at the first failing command. `-u`: treat an unset variable as an error. `-f`: switch off *globbing* (the expansion of `*` into file names) so text with `*` is not rewritten by accident.
- `[ "${MVNW_VERBOSE-}" != debug ] || set -x`: `[ A != B ] || cmd` runs `cmd` only when the test fails, i.e. when `MVNW_VERBOSE` is `debug`. `${MVNW_VERBOSE-}` reads the variable, giving empty text if it is unset. `set -x` makes the shell print every command before running it (a trace).

```bash
# OS specific support.
native_path() { printf %s\\n "$1"; }
case "$(uname)" in
CYGWIN* | MINGW*)
  [ -z "${JAVA_HOME-}" ] || JAVA_HOME="$(cygpath --unix "$JAVA_HOME")"
  native_path() { cygpath --path --windows "$1"; }
  ;;
esac
```

- `# OS specific support.`: a comment written by the author; the tool ignores it. It explains the lines below.
- `native_path() { printf %s\\n "$1"; }`: Defines a **shell function** `native_path` that prints its first argument (`$1`) followed by a newline. `printf %s\\n` is the portable way to print text exactly. On Windows-like shells the function is replaced below.
- `case "$(uname)" in`: `case` compares one value against patterns. `$(uname)` is the output of the program `uname`, the name of the operating system.
- `CYGWIN* | MINGW*)`: The pattern for the Windows-on-Unix environments Cygwin and MinGW (`|` means or, `*` means anything).
- `[ -z "${JAVA_HOME-}" ] || JAVA_HOME="$(cygpath --unix "$JAVA_HOME")"`: If `JAVA_HOME` is not empty, converts it with `cygpath --unix` into a Unix-style path.
- `native_path() { cygpath --path --windows "$1"; }`: On Cygwin/MinGW, redefines `native_path` to convert a path to Windows form with `cygpath`, because Java there wants Windows paths.
- `;;`: `;;` ends one branch of a `case`.
- `esac`: `esac` (`case` backwards) ends the `case` statement.

```bash
# set JAVACMD and JAVACCMD
set_java_home() {
  # For Cygwin and MinGW, ensure paths are in Unix format before anything is touched
  if [ -n "${JAVA_HOME-}" ]; then
    if [ -x "$JAVA_HOME/jre/sh/java" ]; then
      # IBM's JDK on AIX uses strange locations for the executables
      JAVACMD="$JAVA_HOME/jre/sh/java"
      JAVACCMD="$JAVA_HOME/jre/sh/javac"
    else
      JAVACMD="$JAVA_HOME/bin/java"
```

- `# set JAVACMD and JAVACCMD`: a comment written by the author; the tool ignores it. It explains the lines below.
- `set_java_home() {`: Defines the function `set_java_home`, which finds the Java programs and sets `JAVACMD` (the `java` launcher) and `JAVACCMD` (the `javac` compiler).
- `# For Cygwin and MinGW, ensure paths are in Unix format before anything is touched`: a comment written by the author; the tool ignores it. It explains the lines below.
- `if [ -n "${JAVA_HOME-}" ]; then`: `[ -n X ]` is true when `X` is not empty: the user set `JAVA_HOME`.
- `if [ -x "$JAVA_HOME/jre/sh/java" ]; then`: `[ -x FILE ]` is true when the file exists and may be executed. This is the odd layout of IBM's JDK on AIX.
- `# IBM's JDK on AIX uses strange locations for the executables`: a comment written by the author; the tool ignores it. It explains the lines below.
- `JAVACMD="$JAVA_HOME/jre/sh/java"`: Sets `JAVACMD` to the IBM-layout launcher.
- `JAVACCMD="$JAVA_HOME/jre/sh/javac"`: Sets `JAVACCMD` to the IBM-layout compiler.
- `else`: `else` starts the branch used when the `if` test above was false.
- `JAVACMD="$JAVA_HOME/bin/java"`: Normal layout: the launcher is `bin/java` under `JAVA_HOME`.

```bash
      JAVACCMD="$JAVA_HOME/bin/javac"
```

- `JAVACCMD="$JAVA_HOME/bin/javac"`: The compiler is `bin/javac` under `JAVA_HOME`.

```bash
      if [ ! -x "$JAVACMD" ] || [ ! -x "$JAVACCMD" ]; then
        echo "The JAVA_HOME environment variable is not defined correctly, so mvnw cannot run." >&2
        echo "JAVA_HOME is set to \"$JAVA_HOME\", but \"\$JAVA_HOME/bin/java\" or \"\$JAVA_HOME/bin/javac\" does not exist." >&2
        return 1
      fi
    fi
  else
```

- `if [ ! -x "$JAVACMD" ] || [ ! -x "$JAVACCMD" ]; then`: True when `java` or `javac` cannot be executed (`!` negates a test, `||` means or).
- `echo "The JAVA_HOME environment variable is not defined correctly, so mvnw cannot run."...`: Prints an error message. `>&2` sends it to standard error (file descriptor 2), the stream meant for errors.
- `echo "JAVA_HOME is set to \"$JAVA_HOME\", but \"\$JAVA_HOME/bin/java\" or \"\$JAVA_HOME...`: Prints which value `JAVA_HOME` has and that the needed programs are missing there. The backslashes keep the quote and dollar characters literal.
- `return 1`: Leaves the function and reports failure (exit status 1).
- `fi`: `fi` (`if` backwards) ends an `if` statement.
- `fi`: `fi` (`if` backwards) ends an `if` statement.
- `else`: `else` starts the branch used when the `if` test above was false.

```bash
    JAVACMD="$(
      'set' +e
      'unset' -f command 2>/dev/null
      'command' -v java
    )" || :
    JAVACCMD="$(
      'set' +e
      'unset' -f command 2>/dev/null
      'command' -v javac
    )" || :
```

- `JAVACMD="$(`: Starts command substitution `$( ... )`: the output of the commands inside becomes the value of `JAVACMD`.
- `JAVACCMD="$(`: The same construction for `javac`.

```bash
    if [ ! -x "${JAVACMD-}" ] || [ ! -x "${JAVACCMD-}" ]; then
      echo "The java/javac command does not exist in PATH nor is JAVA_HOME set, so mvnw cannot run." >&2
      return 1
    fi
  fi
}
```

- `if [ ! -x "${JAVACMD-}" ] || [ ! -x "${JAVACCMD-}" ]; then`: True when either program was not found.
- `echo "The java/javac command does not exist in PATH nor is JAVA_HOME set, so mvnw canno...`: Prints the error to standard error.
- `return 1`: Leaves the function and reports failure (exit status 1).
- `fi`: `fi` (`if` backwards) ends an `if` statement.
- `fi`: `fi` (`if` backwards) ends an `if` statement.
- `}`: Closes the function body.

```bash
# hash string like Java String::hashCode
hash_string() {
  str="${1:-}" h=0
  while [ -n "$str" ]; do
    char="${str%"${str#?}"}"
    h=$(((h * 31 + $(LC_CTYPE=C printf %d "'$char")) % 4294967296))
    str="${str#?}"
  done
  printf %x\\n $h
}
```

- `# hash string like Java String::hashCode`: a comment written by the author; the tool ignores it. It explains the lines below.
- `hash_string() {`: Defines `hash_string`, which computes the same number Java's `String.hashCode()` would give, used to name the folder of the downloaded Maven.
- `str="${1:-}" h=0`: Two assignments on one line: `str` is the first argument (empty if none) and `h`, the hash so far, starts at 0.
- `while [ -n "$str" ]; do`: Loop while the text `str` is not empty.
- `char="${str%"${str#?}"}"`: Takes the first character of `str`. `${str#?}` is the text without its first character and `${str%X}` removes the suffix `X`, so removing the rest leaves the first character.
- `h=$(((h * 31 + $(LC_CTYPE=C printf %d "'$char")) % 4294967296))`: Arithmetic `$(( ))`: the new hash is `(h * 31 + code of the character) modulo 4294967296` (2 to the power 32), exactly Java's formula. `printf %d "'c"` prints the character code.
- `str="${str#?}"`: Drops the first character, so the loop moves on.
- `done`: `done` ends a loop.
- `printf %x\\n $h`: Prints the hash as hexadecimal (`%x`).
- `}`: Closes the function body.

```bash
verbose() { :; }
[ "${MVNW_VERBOSE-}" != true ] || verbose() { printf %s\\n "${1-}"; }
```

- `verbose() { :; }`: Defines `verbose` as a function that does nothing (`:`).
- `[ "${MVNW_VERBOSE-}" != true ] || verbose() { printf %s\\n "${1-}"; }`: When `MVNW_VERBOSE` is `true`, redefines `verbose` to print its argument. Messages therefore appear only in verbose mode.

```bash
die() {
  printf %s\\n "$1" >&2
  exit 1
}
```

- `die() {`: Defines `die`: print the message to standard error and stop with exit status 1.
- `printf %s\\n "$1" >&2`: Prints the message to standard error.
- `exit 1`: Stops the script with status 1 (failure).
- `}`: Closes the function body.

```bash
trim() {
  # MWRAPPER-139:
  #   Trims trailing and leading whitespace, carriage returns, tabs, and linefeeds.
  #   Needed for removing poorly interpreted newline sequences when running in more
  #   exotic environments such as mingw bash on Windows.
  printf "%s" "${1}" | tr -d '[:space:]'
}
```

- `trim() {`: Defines `trim`: removes white space, carriage returns and tabs from its argument (needed on Windows shells that leave stray characters).
- `# MWRAPPER-139:`: a comment written by the author; the tool ignores it. It explains the lines below.
- `#   Trims trailing and leading whitespace, carriage returns, tabs, and linefeeds.`: a comment written by the author; the tool ignores it. It explains the lines below.
- `#   Needed for removing poorly interpreted newline sequences when running in more`: a comment written by the author; the tool ignores it. It explains the lines below.
- `#   exotic environments such as mingw bash on Windows.`: a comment written by the author; the tool ignores it. It explains the lines below.
- `printf "%s" "${1}" | tr -d '[:space:]'`: `tr -d '[:space:]'` deletes every white-space character from what `printf` prints (`|` pipes one program's output into the next).
- `}`: Closes the function body.

```bash
scriptDir="$(dirname "$0")"
scriptName="$(basename "$0")"
```

- `scriptDir="$(dirname "$0")"`: `$0` is the path this script was started by; `dirname` gives its folder.
- `scriptName="$(basename "$0")"`: `basename` gives the file name only (`mvnw`).

```bash
# parse distributionUrl and optional distributionSha256Sum, requires .mvn/wrapper/maven-wrapper.properties
while IFS="=" read -r key value; do
  case "${key-}" in
  distributionUrl) distributionUrl=$(trim "${value-}") ;;
  distributionSha256Sum) distributionSha256Sum=$(trim "${value-}") ;;
  esac
done <"$scriptDir/.mvn/wrapper/maven-wrapper.properties"
[ -n "${distributionUrl-}" ] || die "cannot read distributionUrl property in $scriptDir/.mvn/wrapper/maven-wrapper.properties"
```

- `# parse distributionUrl and optional distributionSha256Sum, requires .mvn/wrapper/maven-wrapper.prop`: a comment written by the author; the tool ignores it. It explains the lines below.
- `while IFS="=" read -r key value; do`: Reads a file line by line. `IFS="="` makes `=` the separator, so each line `key=value` fills the variables `key` and `value`; `-r` keeps backslashes as they are.
- `case "${key-}" in`: Looks at the key just read.
- `distributionUrl) distributionUrl=$(trim "${value-}") ;;`: If the key is `distributionUrl`, store its trimmed value in a variable of that name.
- `distributionSha256Sum) distributionSha256Sum=$(trim "${value-}") ;;`: If the key is `distributionSha256Sum`, store its trimmed value (an optional checksum).
- `esac`: `esac` (`case` backwards) ends the `case` statement.
- `done <"$scriptDir/.mvn/wrapper/maven-wrapper.properties"`: `<FILE` feeds the file to the loop as its input: the loop reads `.mvn/wrapper/maven-wrapper.properties` (`maven.md`).
- `[ -n "${distributionUrl-}" ] || die "cannot read distributionUrl property in $scriptDir...`: Stops with an error if the properties file gave no `distributionUrl`.

```bash
case "${distributionUrl##*/}" in
maven-mvnd-*bin.*)
  MVN_CMD=mvnd.sh _MVNW_REPO_PATTERN=/maven/mvnd/
  case "${PROCESSOR_ARCHITECTURE-}${PROCESSOR_ARCHITEW6432-}:$(uname -a)" in
  *AMD64:CYGWIN* | *AMD64:MINGW*) distributionPlatform=windows-amd64 ;;
  :Darwin*x86_64) distributionPlatform=darwin-amd64 ;;
  :Darwin*arm64) distributionPlatform=darwin-aarch64 ;;
  :Linux*x86_64*) distributionPlatform=linux-amd64 ;;
  *)
    echo "Cannot detect native platform for mvnd on $(uname)-$(uname -m), use pure java version" >&2
```

- `case "${distributionUrl##*/}" in`: `${x##*/}` removes everything up to the last `/`, leaving the file name of the URL; `case` then looks at that name.
- `maven-mvnd-*bin.*)`: The file name of the Maven daemon (`mvnd`) distribution; this repository does not use it.
- `MVN_CMD=mvnd.sh _MVNW_REPO_PATTERN=/maven/mvnd/`: For mvnd the program to run is `mvnd.sh`, and the download address contains `/maven/mvnd/`.
- `case "${PROCESSOR_ARCHITECTURE-}${PROCESSOR_ARCHITEW6432-}:$(uname -a)" in`: Detects the platform from environment variables and `uname -a`.
- `*AMD64:CYGWIN* | *AMD64:MINGW*) distributionPlatform=windows-amd64 ;;`: Windows on 64-bit Intel/AMD.
- `:Darwin*x86_64) distributionPlatform=darwin-amd64 ;;`: macOS on Intel.
- `:Darwin*arm64) distributionPlatform=darwin-aarch64 ;;`: macOS on Apple silicon.
- `:Linux*x86_64*) distributionPlatform=linux-amd64 ;;`: Linux on 64-bit Intel/AMD.
- `*)`: `*)` is the catch-all pattern: anything that did not match above.
- `echo "Cannot detect native platform for mvnd on $(uname)-$(uname -m), use pure java ver...`: Warns on standard error and falls back to a pure Java variant.

```bash
    distributionPlatform=linux-amd64
    ;;
  esac
  distributionUrl="${distributionUrl%-bin.*}-$distributionPlatform.zip"
  ;;
maven-mvnd-*) MVN_CMD=mvnd.sh _MVNW_REPO_PATTERN=/maven/mvnd/ ;;
*) MVN_CMD="mvn${scriptName#mvnw}" _MVNW_REPO_PATTERN=/org/apache/maven/ ;;
esac
```

- `distributionPlatform=linux-amd64`: Sets the platform name used to build the download address.
- `;;`: `;;` ends one branch of a `case`.
- `esac`: `esac` (`case` backwards) ends the `case` statement.
- `distributionUrl="${distributionUrl%-bin.*}-$distributionPlatform.zip"`: Rebuilds the URL for the platform-specific mvnd zip (`${x%-bin.*}` removes the shortest suffix that matches).
- `;;`: `;;` ends one branch of a `case`.
- `maven-mvnd-*) MVN_CMD=mvnd.sh _MVNW_REPO_PATTERN=/maven/mvnd/ ;;`: Another mvnd file name pattern.
- `*) MVN_CMD="mvn${scriptName#mvnw}" _MVNW_REPO_PATTERN=/org/apache/maven/ ;;`: **The normal case**: the program to run is `mvn` plus whatever follows `mvnw` in the script's own name (`${x#mvnw}` removes the prefix), so `mvnw` runs `mvn`. The download address contains `/org/apache/maven/`.
- `esac`: `esac` (`case` backwards) ends the `case` statement.

```bash
# apply MVNW_REPOURL and calculate MAVEN_HOME
# maven home pattern: ~/.m2/wrapper/dists/{apache-maven-<version>,maven-mvnd-<version>-<platform>}/<hash>
[ -z "${MVNW_REPOURL-}" ] || distributionUrl="$MVNW_REPOURL$_MVNW_REPO_PATTERN${distributionUrl#*"$_MVNW_REPO_PATTERN"}"
distributionUrlName="${distributionUrl##*/}"
distributionUrlNameMain="${distributionUrlName%.*}"
distributionUrlNameMain="${distributionUrlNameMain%-bin}"
MAVEN_USER_HOME="${MAVEN_USER_HOME:-${HOME}/.m2}"
MAVEN_HOME="${MAVEN_USER_HOME}/wrapper/dists/${distributionUrlNameMain-}/$(hash_string "$distributionUrl")"
```

- `# apply MVNW_REPOURL and calculate MAVEN_HOME`: a comment written by the author; the tool ignores it. It explains the lines below.
- `# maven home pattern: ~/.m2/wrapper/dists/{apache-maven-<version>,maven-mvnd-<version>-<platform>}/<`: a comment written by the author; the tool ignores it. It explains the lines below.
- `[ -z "${MVNW_REPOURL-}" ] || distributionUrl="$MVNW_REPOURL$_MVNW_REPO_PATTERN${distrib...`: If `MVNW_REPOURL` is set, swaps the base of the download address for that mirror.
- `distributionUrlName="${distributionUrl##*/}"`: The file name part of the URL, for example `apache-maven-3.9.9-bin.zip`.
- `distributionUrlNameMain="${distributionUrlName%.*}"`: The name without its file ending (`.zip`).
- `distributionUrlNameMain="${distributionUrlNameMain%-bin}"`: And without `-bin`: `apache-maven-3.9.9`.
- `MAVEN_USER_HOME="${MAVEN_USER_HOME:-${HOME}/.m2}"`: Where Maven keeps its files: `MAVEN_USER_HOME` if set, otherwise `~/.m2`. `${x:-y}` means `x` or, if empty, `y`.
- `MAVEN_HOME="${MAVEN_USER_HOME}/wrapper/dists/${distributionUrlNameMain-}/$(hash_string ...`: The folder where this Maven version lives: `~/.m2/wrapper/dists/<name>/<hash of the URL>`.

```bash
exec_maven() {
  unset MVNW_VERBOSE MVNW_USERNAME MVNW_PASSWORD MVNW_REPOURL || :
  exec "$MAVEN_HOME/bin/$MVN_CMD" "$@" || die "cannot exec $MAVEN_HOME/bin/$MVN_CMD"
}
```

- `exec_maven() {`: Defines `exec_maven`, which starts the real Maven.
- `unset MVNW_VERBOSE MVNW_USERNAME MVNW_PASSWORD MVNW_REPOURL || :`: Removes the wrapper's own settings from the environment so that Maven does not see them (the password is a secret).
- `exec "$MAVEN_HOME/bin/$MVN_CMD" "$@" || die "cannot exec $MAVEN_HOME/bin/$MVN_CMD"`: `exec` **replaces** the script's process by Maven, so nothing of the script remains. `"$@"` passes on every argument exactly as given (so `./mvnw -q test` becomes `mvn -q test`). If `exec` fails, `die` reports it.
- `}`: Closes the function body.

```bash
if [ -d "$MAVEN_HOME" ]; then
  verbose "found existing MAVEN_HOME at $MAVEN_HOME"
  exec_maven "$@"
fi
```

- `if [ -d "$MAVEN_HOME" ]; then`: `[ -d X ]` is true when `X` is a folder: Maven was downloaded before.
- `verbose "found existing MAVEN_HOME at $MAVEN_HOME"`: Prints a message in verbose mode.
- `exec_maven "$@"`: Starts Maven with the same arguments.
- `fi`: `fi` (`if` backwards) ends an `if` statement.

```bash
case "${distributionUrl-}" in
*?-bin.zip | *?maven-mvnd-?*-?*.zip) ;;
*) die "distributionUrl is not valid, must match *-bin.zip or maven-mvnd-*.zip, but found '${distributionUrl-}'" ;;
esac
```

- `case "${distributionUrl-}" in`: Checks that the URL looks like a valid distribution.
- `*?-bin.zip | *?maven-mvnd-?*-?*.zip) ;;`: Valid names end in `-bin.zip` (or are an mvnd zip); `;;` ends the branch and nothing is done.
- `*) die "distributionUrl is not valid, must match *-bin.zip or maven-mvnd-*.zip, but fou...`: Anything else is an error.
- `esac`: `esac` (`case` backwards) ends the `case` statement.

```bash
# prepare tmp dir
if TMP_DOWNLOAD_DIR="$(mktemp -d)" && [ -d "$TMP_DOWNLOAD_DIR" ]; then
  clean() { rm -rf -- "$TMP_DOWNLOAD_DIR"; }
  trap clean HUP INT TERM EXIT
else
  die "cannot create temp dir"
fi
```

- `# prepare tmp dir`: a comment written by the author; the tool ignores it. It explains the lines below.
- `if TMP_DOWNLOAD_DIR="$(mktemp -d)" && [ -d "$TMP_DOWNLOAD_DIR" ]; then`: `mktemp -d` creates a new empty temporary folder and prints its name; the test also checks that it exists.
- `clean() { rm -rf -- "$TMP_DOWNLOAD_DIR"; }`: Defines `clean`, which deletes that temporary folder (`rm -rf` removes recursively without asking; `--` ends the options).
- `trap clean HUP INT TERM EXIT`: `trap` registers `clean` to run when the script ends or receives the hang-up, interrupt or terminate signals, so no temporary files are left.
- `else`: `else` starts the branch used when the `if` test above was false.
- `die "cannot create temp dir"`: Stop if no temporary folder could be made.
- `fi`: `fi` (`if` backwards) ends an `if` statement.

```bash
mkdir -p -- "${MAVEN_HOME%/*}"
```

- `mkdir -p -- "${MAVEN_HOME%/*}"`: Creates the parent folder of `MAVEN_HOME` (`${x%/*}` removes the last path part).

```bash
# Download and Install Apache Maven
verbose "Couldn't find MAVEN_HOME, downloading and installing it ..."
verbose "Downloading from: $distributionUrl"
verbose "Downloading to: $TMP_DOWNLOAD_DIR/$distributionUrlName"
```

- `# Download and Install Apache Maven`: a comment written by the author; the tool ignores it. It explains the lines below.
- `verbose "Couldn't find MAVEN_HOME, downloading and installing it ..."`: Verbose message.
- `verbose "Downloading from: $distributionUrl"`: Verbose message with the source.
- `verbose "Downloading to: $TMP_DOWNLOAD_DIR/$distributionUrlName"`: Verbose message with the target.

```bash
# select .zip or .tar.gz
if ! command -v unzip >/dev/null; then
  distributionUrl="${distributionUrl%.zip}.tar.gz"
  distributionUrlName="${distributionUrl##*/}"
fi
```

- `# select .zip or .tar.gz`: a comment written by the author; the tool ignores it. It explains the lines below.
- `if ! command -v unzip >/dev/null; then`: If there is no `unzip` program, ...
- `distributionUrl="${distributionUrl%.zip}.tar.gz"`: ... ask for the `.tar.gz` form of the download instead.
- `distributionUrlName="${distributionUrl##*/}"`: The file name part of the URL, for example `apache-maven-3.9.9-bin.zip`.
- `fi`: `fi` (`if` backwards) ends an `if` statement.

```bash
# verbose opt
__MVNW_QUIET_WGET=--quiet __MVNW_QUIET_CURL=--silent __MVNW_QUIET_UNZIP=-q __MVNW_QUIET_TAR=''
[ "${MVNW_VERBOSE-}" != true ] || __MVNW_QUIET_WGET='' __MVNW_QUIET_CURL='' __MVNW_QUIET_UNZIP='' __MVNW_QUIET_TAR=v
```

- `# verbose opt`: a comment written by the author; the tool ignores it. It explains the lines below.
- `__MVNW_QUIET_WGET=--quiet __MVNW_QUIET_CURL=--silent __MVNW_QUIET_UNZIP=-q __MVNW_QUIET...`: Sets the quiet options of the download tools in four variables.
- `[ "${MVNW_VERBOSE-}" != true ] || __MVNW_QUIET_WGET='' __MVNW_QUIET_CURL='' __MVNW_QUIE...`: In verbose mode, clears the quiet options.

```bash
# normalize http auth
case "${MVNW_PASSWORD:+has-password}" in
'') MVNW_USERNAME='' MVNW_PASSWORD='' ;;
has-password) [ -n "${MVNW_USERNAME-}" ] || MVNW_USERNAME='' MVNW_PASSWORD='' ;;
esac
```

- `# normalize http auth`: a comment written by the author; the tool ignores it. It explains the lines below.
- `case "${MVNW_PASSWORD:+has-password}" in`: Looks at whether a password was set (`${x:+y}` gives `y` only if `x` is set and not empty).
- `'') MVNW_USERNAME='' MVNW_PASSWORD='' ;;`: No password: clear both user name and password.
- `has-password) [ -n "${MVNW_USERNAME-}" ] || MVNW_USERNAME='' MVNW_PASSWORD='' ;;`: Password set: keep it only if a user name is set too.
- `esac`: `esac` (`case` backwards) ends the `case` statement.

```bash
if [ -z "${MVNW_USERNAME-}" ] && command -v wget >/dev/null; then
  verbose "Found wget ... using wget"
  wget ${__MVNW_QUIET_WGET:+"$__MVNW_QUIET_WGET"} "$distributionUrl" -O "$TMP_DOWNLOAD_DIR/$distributionUrlName" || die "wget: Failed to fetch $distributionUrl"
elif [ -z "${MVNW_USERNAME-}" ] && command -v curl >/dev/null; then
  verbose "Found curl ... using curl"
  curl ${__MVNW_QUIET_CURL:+"$__MVNW_QUIET_CURL"} -f -L -o "$TMP_DOWNLOAD_DIR/$distributionUrlName" "$distributionUrl" || die "curl: Failed to fetch $distributionUrl"
elif set_java_home; then
  verbose "Falling back to use Java to download"
  javaSource="$TMP_DOWNLOAD_DIR/Downloader.java"
  targetZip="$TMP_DOWNLOAD_DIR/$distributionUrlName"
```

- `if [ -z "${MVNW_USERNAME-}" ] && command -v wget >/dev/null; then`: No user name and `wget` is installed: use `wget`.
- `verbose "Found wget ... using wget"`: Verbose message.
- `wget ${__MVNW_QUIET_WGET:+"$__MVNW_QUIET_WGET"} "$distributionUrl" -O "$TMP_DOWNLOAD_DI...`: Downloads the URL (`-O` names the output file). If it fails, `die`.
- `elif [ -z "${MVNW_USERNAME-}" ] && command -v curl >/dev/null; then`: Otherwise, if `curl` is installed (`curl.md`), use it.
- `verbose "Found curl ... using curl"`: Verbose message.
- `curl ${__MVNW_QUIET_CURL:+"$__MVNW_QUIET_CURL"} -f -L -o "$TMP_DOWNLOAD_DIR/$distributi...`: Downloads with `-f` (fail on HTTP errors), `-L` (follow redirects) and `-o` (output file).
- `elif set_java_home; then`: Otherwise, if Java can be found, use Java itself to download.
- `verbose "Falling back to use Java to download"`: Verbose message.
- `javaSource="$TMP_DOWNLOAD_DIR/Downloader.java"`: Path of a small Java source file to write.
- `targetZip="$TMP_DOWNLOAD_DIR/$distributionUrlName"`: Path of the file to download.

```bash
  cat >"$javaSource" <<-END
	public class Downloader extends java.net.Authenticator
	{
	  protected java.net.PasswordAuthentication getPasswordAuthentication()
	  {
	    return new java.net.PasswordAuthentication( System.getenv( "MVNW_USERNAME" ), System.getenv( "MVNW_PASSWORD" ).toCharArray() );
	  }
	  public static void main( String[] args ) throws Exception
	  {
	    setDefault( new Downloader() );
```

- `cat >"$javaSource" <<-END`: A **here-document**: everything up to the line `END` is written to the file `Downloader.java` (`<<-` allows tabs in front of the lines).
- `public class Downloader extends java.net.Authenticator`: A tiny Java program: a class that can answer a web server's request for user name and password.
- `{`: Opens a block.
- `protected java.net.PasswordAuthentication getPasswordAuthentication()`: Supplies the user name and password from the environment variables.
- `{`: Opens a block.
- `return new java.net.PasswordAuthentication( System.getenv( "MVNW_USERNAME" ), System.ge...`: Reads `MVNW_USERNAME` and `MVNW_PASSWORD` and returns them.
- `}`: Closes the function body.
- `public static void main( String[] args ) throws Exception`: The entry point of the Java program.
- `{`: Opens a block.
- `setDefault( new Downloader() );`: Installs the authenticator.

```bash
	    java.nio.file.Files.copy( java.net.URI.create( args[0] ).toURL().openStream(), java.nio.file.Paths.get( args[1] ).toAbsolutePath().normalize() );
	  }
	}
	END
  # For Cygwin/MinGW, switch paths to Windows format before running javac and java
  verbose " - Compiling Downloader.java ..."
  "$(native_path "$JAVACCMD")" "$(native_path "$javaSource")" || die "Failed to compile Downloader.java"
  verbose " - Running Downloader.java ..."
  "$(native_path "$JAVACMD")" -cp "$(native_path "$TMP_DOWNLOAD_DIR")" Downloader "$distributionUrl" "$(native_path "$targetZip")"
fi
```

- `java.nio.file.Files.copy( java.net.URI.create( args[0] ).toURL().openStream(), java.nio...`: Opens the URL (first argument), and copies what it delivers into the target file (second argument).
- `}`: Closes the function body.
- `}`: Closes the function body.
- `END`: The end marker of the here-document.
- `# For Cygwin/MinGW, switch paths to Windows format before running javac and java`: a comment written by the author; the tool ignores it. It explains the lines below.
- `verbose " - Compiling Downloader.java ..."`: Verbose message.
- `"$(native_path "$JAVACCMD")" "$(native_path "$javaSource")" || die "Failed to compile D...`: Compiles `Downloader.java` with `javac`. `native_path` converts paths on Windows-like shells.
- `verbose " - Running Downloader.java ..."`: Verbose message.
- `"$(native_path "$JAVACMD")" -cp "$(native_path "$TMP_DOWNLOAD_DIR")" Downloader "$distr...`: Runs the compiled class with `java -cp` (the class path) giving the URL and the target file.
- `fi`: `fi` (`if` backwards) ends an `if` statement.

```bash
# If specified, validate the SHA-256 sum of the Maven distribution zip file
if [ -n "${distributionSha256Sum-}" ]; then
  distributionSha256Result=false
  if [ "$MVN_CMD" = mvnd.sh ]; then
    echo "Checksum validation is not supported for maven-mvnd." >&2
    echo "Please disable validation by removing 'distributionSha256Sum' from your maven-wrapper.properties." >&2
    exit 1
  elif command -v sha256sum >/dev/null; then
    if echo "$distributionSha256Sum  $TMP_DOWNLOAD_DIR/$distributionUrlName" | sha256sum -c - >/dev/null 2>&1; then
      distributionSha256Result=true
```

- `# If specified, validate the SHA-256 sum of the Maven distribution zip file`: a comment written by the author; the tool ignores it. It explains the lines below.
- `if [ -n "${distributionSha256Sum-}" ]; then`: Only when a checksum is given in the properties file.
- `distributionSha256Result=false`: Assume failure until proved otherwise.
- `if [ "$MVN_CMD" = mvnd.sh ]; then`: mvnd does not support checksums.
- `echo "Checksum validation is not supported for maven-mvnd." >&2`: Message on standard error.
- `echo "Please disable validation by removing 'distributionSha256Sum' from your maven-wra...`: Tells the user how to turn validation off.
- `exit 1`: Stops the script with status 1 (failure).
- `elif command -v sha256sum >/dev/null; then`: If `sha256sum` exists (Linux)...
- `if echo "$distributionSha256Sum  $TMP_DOWNLOAD_DIR/$distributionUrlName" | sha256sum -c...`: Pipes the expected checksum and file name to `sha256sum -c` (check mode). `>/dev/null 2>&1` throws away all output; only the exit status matters.
- `distributionSha256Result=true`: The checksum matched.

```bash
    fi
  elif command -v shasum >/dev/null; then
    if echo "$distributionSha256Sum  $TMP_DOWNLOAD_DIR/$distributionUrlName" | shasum -a 256 -c >/dev/null 2>&1; then
      distributionSha256Result=true
    fi
  else
    echo "Checksum validation was requested but neither 'sha256sum' or 'shasum' are available." >&2
    echo "Please install either command, or disable validation by removing 'distributionSha256Sum' from your maven-wrapper.properties." >&2
    exit 1
  fi
```

- `fi`: `fi` (`if` backwards) ends an `if` statement.
- `elif command -v shasum >/dev/null; then`: Otherwise, if `shasum` exists (macOS), do the same with `shasum -a 256`.
- `if echo "$distributionSha256Sum  $TMP_DOWNLOAD_DIR/$distributionUrlName" | shasum -a 25...`: Pipes the expected checksum and file name to `sha256sum -c` (check mode). `>/dev/null 2>&1` throws away all output; only the exit status matters.
- `distributionSha256Result=true`: The checksum matched.
- `fi`: `fi` (`if` backwards) ends an `if` statement.
- `else`: `else` starts the branch used when the `if` test above was false.
- `echo "Checksum validation was requested but neither 'sha256sum' or 'shasum' are availab...`: Neither tool exists: tell the user.
- `echo "Please install either command, or disable validation by removing 'distributionSha...`: How to fix it.
- `exit 1`: Stops the script with status 1 (failure).
- `fi`: `fi` (`if` backwards) ends an `if` statement.

```bash
  if [ $distributionSha256Result = false ]; then
    echo "Error: Failed to validate Maven distribution SHA-256, your Maven distribution might be compromised." >&2
    echo "If you updated your Maven version, you need to update the specified distributionSha256Sum property." >&2
    exit 1
  fi
fi
```

- `if [ $distributionSha256Result = false ]; then`: If the check failed...
- `echo "Error: Failed to validate Maven distribution SHA-256, your Maven distribution mig...`: ... print a warning that the download may be compromised.
- `echo "If you updated your Maven version, you need to update the specified distributionS...`: and a hint to update the checksum property.
- `exit 1`: Stops the script with status 1 (failure).
- `fi`: `fi` (`if` backwards) ends an `if` statement.
- `fi`: `fi` (`if` backwards) ends an `if` statement.

```bash
# unzip and move
if command -v unzip >/dev/null; then
  unzip ${__MVNW_QUIET_UNZIP:+"$__MVNW_QUIET_UNZIP"} "$TMP_DOWNLOAD_DIR/$distributionUrlName" -d "$TMP_DOWNLOAD_DIR" || die "failed to unzip"
else
  tar xzf${__MVNW_QUIET_TAR:+"$__MVNW_QUIET_TAR"} "$TMP_DOWNLOAD_DIR/$distributionUrlName" -C "$TMP_DOWNLOAD_DIR" || die "failed to untar"
fi
```

- `# unzip and move`: a comment written by the author; the tool ignores it. It explains the lines below.
- `if command -v unzip >/dev/null; then`: If `unzip` exists, use it.
- `unzip ${__MVNW_QUIET_UNZIP:+"$__MVNW_QUIET_UNZIP"} "$TMP_DOWNLOAD_DIR/$distributionUrlN...`: Unpacks the zip into the temporary folder (`-d` names the target folder); on failure, `die`.
- `else`: `else` starts the branch used when the `if` test above was false.
- `tar xzf${__MVNW_QUIET_TAR:+"$__MVNW_QUIET_TAR"} "$TMP_DOWNLOAD_DIR/$distributionUrlName...`: Otherwise unpacks a `.tar.gz` with `tar` (`x` extract, `z` gunzip, `f` file; `-C` target folder).
- `fi`: `fi` (`if` backwards) ends an `if` statement.

```bash
# Find the actual extracted directory name (handles snapshots where filename != directory name)
actualDistributionDir=""
```

- `# Find the actual extracted directory name (handles snapshots where filename != directory name)`: a comment written by the author; the tool ignores it. It explains the lines below.
- `actualDistributionDir=""`: Will hold the name of the unpacked Maven folder.

```bash
# First try the expected directory name (for regular distributions)
if [ -d "$TMP_DOWNLOAD_DIR/$distributionUrlNameMain" ]; then
  if [ -f "$TMP_DOWNLOAD_DIR/$distributionUrlNameMain/bin/$MVN_CMD" ]; then
    actualDistributionDir="$distributionUrlNameMain"
  fi
fi
```

- `# First try the expected directory name (for regular distributions)`: a comment written by the author; the tool ignores it. It explains the lines below.
- `if [ -d "$TMP_DOWNLOAD_DIR/$distributionUrlNameMain" ]; then`: If the expected folder exists...
- `if [ -f "$TMP_DOWNLOAD_DIR/$distributionUrlNameMain/bin/$MVN_CMD" ]; then`: ... and contains the Maven program (`[ -f X ]` tests for a file)...
- `actualDistributionDir="$distributionUrlNameMain"`: ... use it.
- `fi`: `fi` (`if` backwards) ends an `if` statement.
- `fi`: `fi` (`if` backwards) ends an `if` statement.

```bash
# If not found, search for any directory with the Maven executable (for snapshots)
if [ -z "$actualDistributionDir" ]; then
  # enable globbing to iterate over items
  set +f
  for dir in "$TMP_DOWNLOAD_DIR"/*; do
    if [ -d "$dir" ]; then
      if [ -f "$dir/bin/$MVN_CMD" ]; then
        actualDistributionDir="$(basename "$dir")"
        break
      fi
```

- `# If not found, search for any directory with the Maven executable (for snapshots)`: a comment written by the author; the tool ignores it. It explains the lines below.
- `if [ -z "$actualDistributionDir" ]; then`: If it was not found, search every folder.
- `# enable globbing to iterate over items`: a comment written by the author; the tool ignores it. It explains the lines below.
- `set +f`: Switch globbing back on so `*` works in the next line.
- `for dir in "$TMP_DOWNLOAD_DIR"/*; do`: Loop over everything in the temporary folder.
- `if [ -d "$dir" ]; then`: Only folders.
- `if [ -f "$dir/bin/$MVN_CMD" ]; then`: One that contains the Maven program.
- `actualDistributionDir="$(basename "$dir")"`: Remember its name.
- `break`: Leave the loop.
- `fi`: `fi` (`if` backwards) ends an `if` statement.

```bash
    fi
  done
  set -f
fi
```

- `fi`: `fi` (`if` backwards) ends an `if` statement.
- `done`: `done` ends a loop.
- `set -f`: Switch globbing off again.
- `fi`: `fi` (`if` backwards) ends an `if` statement.

```bash
if [ -z "$actualDistributionDir" ]; then
  verbose "Contents of $TMP_DOWNLOAD_DIR:"
  verbose "$(ls -la "$TMP_DOWNLOAD_DIR")"
  die "Could not find Maven distribution directory in extracted archive"
fi
```

- `if [ -z "$actualDistributionDir" ]; then`: If it was not found, search every folder.
- `verbose "Contents of $TMP_DOWNLOAD_DIR:"`: Verbose message.
- `verbose "$(ls -la "$TMP_DOWNLOAD_DIR")"`: Verbose listing of the folder.
- `die "Could not find Maven distribution directory in extracted archive"`: Stop with an error.
- `fi`: `fi` (`if` backwards) ends an `if` statement.

```bash
verbose "Found extracted Maven distribution directory: $actualDistributionDir"
printf %s\\n "$distributionUrl" >"$TMP_DOWNLOAD_DIR/$actualDistributionDir/mvnw.url"
mv -- "$TMP_DOWNLOAD_DIR/$actualDistributionDir" "$MAVEN_HOME" || [ -d "$MAVEN_HOME" ] || die "fail to move MAVEN_HOME"
```

- `verbose "Found extracted Maven distribution directory: $actualDistributionDir"`: Verbose message.
- `printf %s\\n "$distributionUrl" >"$TMP_DOWNLOAD_DIR/$actualDistributionDir/mvnw.url"`: Writes the URL into a file `mvnw.url` inside the unpacked folder, as a record of where it came from.
- `mv -- "$TMP_DOWNLOAD_DIR/$actualDistributionDir" "$MAVEN_HOME" || [ -d "$MAVEN_HOME" ] ...`: Moves the unpacked Maven to its final place. If the move fails but the target exists (another process was faster), carry on; otherwise `die`.

```bash
clean || :
exec_maven "$@"
```

- `clean || :`: Deletes the temporary folder now.
- `exec_maven "$@"`: Starts Maven with the same arguments.

### java/mvnw.cmd (batch + PowerShell)

The first part is a **batch file** (the old Windows command language); it starts PowerShell on this same file and runs what PowerShell prints. The second part, after the line `: end batch / begin powershell #>`, is the **PowerShell** program that does the work.

`java/mvnw.cmd`

```text
<# : batch portion
@REM ----------------------------------------------------------------------------
@REM Licensed to the Apache Software Foundation (ASF) under one
@REM or more contributor license agreements.  See the NOTICE file
@REM distributed with this work for additional information
@REM regarding copyright ownership.  The ASF licenses this file
@REM to you under the Apache License, Version 2.0 (the
@REM "License"); you may not use this file except in compliance
@REM with the License.  You may obtain a copy of the License at
@REM
```

- `<# : batch portion`: The first line is both a batch comment and the start of a PowerShell block comment `<# ... #>`; that is how one file can be read by two interpreters.
- `@REM ----------------------------------------------------------------------------`: A batch comment (`REM` = remark); the `@` stops the line being echoed.
- `@REM Licensed to the Apache Software Foundation (ASF) under one`: A batch comment (`REM` = remark); the `@` stops the line being echoed.
- `@REM or more contributor license agreements.  See the NOTICE file`: A batch comment (`REM` = remark); the `@` stops the line being echoed.
- `@REM distributed with this work for additional information`: A batch comment (`REM` = remark); the `@` stops the line being echoed.
- `@REM regarding copyright ownership.  The ASF licenses this file`: A batch comment (`REM` = remark); the `@` stops the line being echoed.
- `@REM to you under the Apache License, Version 2.0 (the`: A batch comment (`REM` = remark); the `@` stops the line being echoed.
- `@REM with the License.  You may obtain a copy of the License at`: A batch comment (`REM` = remark); the `@` stops the line being echoed.
- `@REM`: A batch comment (`REM` = remark); the `@` stops the line being echoed.

```text
@REM    http://www.apache.org/licenses/LICENSE-2.0
@REM
@REM Unless required by applicable law or agreed to in writing,
@REM software distributed under the License is distributed on an
@REM "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
@REM KIND, either express or implied.  See the License for the
@REM specific language governing permissions and limitations
@REM under the License.
@REM ----------------------------------------------------------------------------
```

- `@REM    http://www.apache.org/licenses/LICENSE-2.0`: A batch comment (`REM` = remark); the `@` stops the line being echoed.
- `@REM`: A batch comment (`REM` = remark); the `@` stops the line being echoed.
- `@REM Unless required by applicable law or agreed to in writing,`: A batch comment (`REM` = remark); the `@` stops the line being echoed.
- `@REM software distributed under the License is distributed on an`: A batch comment (`REM` = remark); the `@` stops the line being echoed.
- `@REM "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY`: A batch comment (`REM` = remark); the `@` stops the line being echoed.
- `@REM KIND, either express or implied.  See the License for the`: A batch comment (`REM` = remark); the `@` stops the line being echoed.
- `@REM specific language governing permissions and limitations`: A batch comment (`REM` = remark); the `@` stops the line being echoed.
- `@REM under the License.`: A batch comment (`REM` = remark); the `@` stops the line being echoed.
- `@REM ----------------------------------------------------------------------------`: A batch comment (`REM` = remark); the `@` stops the line being echoed.

```text
@REM ----------------------------------------------------------------------------
@REM Apache Maven Wrapper startup batch script, version 3.3.4
@REM
@REM Optional ENV vars
@REM   MVNW_REPOURL - repo url base for downloading maven distribution
@REM   MVNW_USERNAME/MVNW_PASSWORD - user and password for downloading maven
@REM   MVNW_VERBOSE - true: enable verbose log; others: silence the output
@REM ----------------------------------------------------------------------------
```

- `@REM ----------------------------------------------------------------------------`: A batch comment (`REM` = remark); the `@` stops the line being echoed.
- `@REM Apache Maven Wrapper startup batch script, version 3.3.4`: A batch comment (`REM` = remark); the `@` stops the line being echoed.
- `@REM`: A batch comment (`REM` = remark); the `@` stops the line being echoed.
- `@REM Optional ENV vars`: A batch comment (`REM` = remark); the `@` stops the line being echoed.
- `@REM   MVNW_REPOURL - repo url base for downloading maven distribution`: A batch comment (`REM` = remark); the `@` stops the line being echoed.
- `@REM   MVNW_USERNAME/MVNW_PASSWORD - user and password for downloading maven`: A batch comment (`REM` = remark); the `@` stops the line being echoed.
- `@REM   MVNW_VERBOSE - true: enable verbose log; others: silence the output`: A batch comment (`REM` = remark); the `@` stops the line being echoed.
- `@REM ----------------------------------------------------------------------------`: A batch comment (`REM` = remark); the `@` stops the line being echoed.

```text
@IF "%__MVNW_ARG0_NAME__%"=="" (SET __MVNW_ARG0_NAME__=%~nx0)
@SET __MVNW_CMD__=
@SET __MVNW_ERROR__=
@SET __MVNW_PSMODULEP_SAVE=%PSModulePath%
@SET PSModulePath=
@FOR /F "usebackq tokens=1* delims==" %%A IN (`powershell -noprofile "& {$scriptDir='%~dp0'; $script='%__MVNW_ARG0_NAME__%'; icm -ScriptBlock ([Scriptblock]::Create((Get-Content -Raw '%~f0'))) -NoNewScope}"`) DO @(
  IF "%%A"=="MVN_CMD" (set __MVNW_CMD__=%%B) ELSE IF "%%B"=="" (echo %%A) ELSE (echo %%A=%%B)
)
@SET PSModulePath=%__MVNW_PSMODULEP_SAVE%
@SET __MVNW_PSMODULEP_SAVE=
```

- `@IF "%__MVNW_ARG0_NAME__%"=="" (SET __MVNW_ARG0_NAME__=%~nx0)`: If the variable is empty, set it to this script's own file name (`%~nx0` = name and extension of argument 0).
- `@SET __MVNW_CMD__=`: Clears the variable that will hold the command to run.
- `@SET __MVNW_ERROR__=`: Clears an error variable.
- `@SET __MVNW_PSMODULEP_SAVE=%PSModulePath%`: Saves the PowerShell module path.
- `@SET PSModulePath=`: Empties it, so that PowerShell starts cleanly.
- `@FOR /F "usebackq tokens=1* delims==" %%A IN (`powershell -noprofile "& {$scriptDir='%~...`: Runs PowerShell on this very file (`%~f0`) and reads its output line by line; each line `NAME=value` is split at `=` into `%%A` and `%%B`.
- `@SET PSModulePath=%__MVNW_PSMODULEP_SAVE%`: Restores the module path.
- `@SET __MVNW_PSMODULEP_SAVE=`: Clears the saved copy.

```text
@SET __MVNW_ARG0_NAME__=
@SET MVNW_USERNAME=
@SET MVNW_PASSWORD=
@IF NOT "%__MVNW_CMD__%"=="" ("%__MVNW_CMD__%" %*)
@echo Cannot start maven from wrapper >&2 && exit /b 1
@GOTO :EOF
: end batch / begin powershell #>
```

- `@SET __MVNW_ARG0_NAME__=`: Clears the script-name variable.
- `@SET MVNW_USERNAME=`: Clears the user name so that Maven does not see it.
- `@SET MVNW_PASSWORD=`: Clears the password for the same reason.
- `@IF NOT "%__MVNW_CMD__%"=="" ("%__MVNW_CMD__%" %*)`: If PowerShell produced a command, run it with all the arguments (`%*`).
- `@echo Cannot start maven from wrapper >&2 && exit /b 1`: Otherwise print an error to standard error and exit with status 1.
- `@GOTO :EOF`: Jump to the end of the file, so the batch interpreter never reads the PowerShell part.
- `: end batch / begin powershell #>`: A label in batch; in PowerShell it closes the block comment started on line 1. From here on the file is PowerShell.

```text
$ErrorActionPreference = "Stop"
if ($env:MVNW_VERBOSE -eq "true") {
  $VerbosePreference = "Continue"
}
```

- `$ErrorActionPreference = "Stop"`: Make every PowerShell error stop the script.
- `if ($env:MVNW_VERBOSE -eq "true") {`: In verbose mode...
- `$VerbosePreference = "Continue"`: ... print the verbose messages.
- `}`: Closes a block.

```text
# calculate distributionUrl, requires .mvn/wrapper/maven-wrapper.properties
$distributionUrl = (Get-Content -Raw "$scriptDir/.mvn/wrapper/maven-wrapper.properties" | ConvertFrom-StringData).distributionUrl
if (!$distributionUrl) {
  Write-Error "cannot read distributionUrl property in $scriptDir/.mvn/wrapper/maven-wrapper.properties"
}
```

- `# calculate distributionUrl, requires .mvn/wrapper/maven-wrapper.properties`: a comment written by the author; the tool ignores it. It explains the lines below.
- `$distributionUrl = (Get-Content -Raw "$scriptDir/.mvn/wrapper/maven-wrapper.properties"...`: Reads `maven-wrapper.properties` as text and `ConvertFrom-StringData` turns its `key=value` lines into a table; takes the entry `distributionUrl`.
- `if (!$distributionUrl) {`: If it is missing...
- `Write-Error "cannot read distributionUrl property in $scriptDir/.mvn/wrapper/maven-wrap...`: ... stop with an error.
- `}`: Closes a block.

```text
switch -wildcard -casesensitive ( $($distributionUrl -replace '^.*/','') ) {
  "maven-mvnd-*" {
    $USE_MVND = $true
    $distributionUrl = $distributionUrl -replace '-bin\.[^.]*$',"-windows-amd64.zip"
    $MVN_CMD = "mvnd.cmd"
    break
  }
  default {
    $USE_MVND = $false
    $MVN_CMD = $script -replace '^mvnw','mvn'
```

- `switch -wildcard -casesensitive ( $($distributionUrl -replace '^.*/','') ) {`: Chooses by the file name of the URL (`-replace '^.*/',''` removes everything up to the last slash), matching wildcards.
- `"maven-mvnd-*" {`: Case: the Maven daemon, not used here.
- `$USE_MVND = $true`: Remember that mvnd is used.
- `$distributionUrl = $distributionUrl -replace '-bin\.[^.]*$',"-windows-amd64.zip"`: Use the Windows 64-bit zip.
- `$MVN_CMD = "mvnd.cmd"`: The program to run.
- `break`: Leave the `switch`.
- `}`: Closes a block.
- `default {`: Case: everything else, the normal Maven.
- `$USE_MVND = $false`: mvnd is not used.
- `$MVN_CMD = $script -replace '^mvnw','mvn'`: The program is `mvn` plus whatever follows `mvnw` in this script's name.

```text
    break
  }
}
```

- `break`: Leave the `switch`.
- `}`: Closes a block.
- `}`: Closes a block.

```text
# apply MVNW_REPOURL and calculate MAVEN_HOME
# maven home pattern: ~/.m2/wrapper/dists/{apache-maven-<version>,maven-mvnd-<version>-<platform>}/<hash>
if ($env:MVNW_REPOURL) {
  $MVNW_REPO_PATTERN = if ($USE_MVND -eq $False) { "/org/apache/maven/" } else { "/maven/mvnd/" }
  $distributionUrl = "$env:MVNW_REPOURL$MVNW_REPO_PATTERN$($distributionUrl -replace "^.*$MVNW_REPO_PATTERN",'')"
}
$distributionUrlName = $distributionUrl -replace '^.*/',''
$distributionUrlNameMain = $distributionUrlName -replace '\.[^.]*$','' -replace '-bin$',''
```

- `# apply MVNW_REPOURL and calculate MAVEN_HOME`: a comment written by the author; the tool ignores it. It explains the lines below.
- `# maven home pattern: ~/.m2/wrapper/dists/{apache-maven-<version>,maven-mvnd-<version>-<platform>}/<`: a comment written by the author; the tool ignores it. It explains the lines below.
- `if ($env:MVNW_REPOURL) {`: A mirror was set.
- `$MVNW_REPO_PATTERN = if ($USE_MVND -eq $False) { "/org/apache/maven/" } else { "/maven/...`: Chooses the part of the address that is replaced.
- `$distributionUrl = "$env:MVNW_REPOURL$MVNW_REPO_PATTERN$($distributionUrl -replace "^.*...`: Swaps the base of the address.
- `}`: Closes a block.
- `$distributionUrlName = $distributionUrl -replace '^.*/',''`: The file name of the URL.
- `$distributionUrlNameMain = $distributionUrlName -replace '\.[^.]*$','' -replace '-bin$',''`: The name without ending and without `-bin`.

```text
$MAVEN_M2_PATH = "$HOME/.m2"
if ($env:MAVEN_USER_HOME) {
  $MAVEN_M2_PATH = "$env:MAVEN_USER_HOME"
}
```

- `$MAVEN_M2_PATH = "$HOME/.m2"`: Default Maven folder.
- `if ($env:MAVEN_USER_HOME) {`: Unless the user chose another.
- `$MAVEN_M2_PATH = "$env:MAVEN_USER_HOME"`: Use the user's choice.
- `}`: Closes a block.

```text
if (-not (Test-Path -Path $MAVEN_M2_PATH)) {
    New-Item -Path $MAVEN_M2_PATH -ItemType Directory | Out-Null
}
```

- `if (-not (Test-Path -Path $MAVEN_M2_PATH)) {`: If the folder does not exist...
- `New-Item -Path $MAVEN_M2_PATH -ItemType Directory | Out-Null`: ... create it. `| Out-Null` discards the output.
- `}`: Closes a block.

```text
$MAVEN_WRAPPER_DISTS = $null
if ((Get-Item $MAVEN_M2_PATH).Target[0] -eq $null) {
  $MAVEN_WRAPPER_DISTS = "$MAVEN_M2_PATH/wrapper/dists"
} else {
  $MAVEN_WRAPPER_DISTS = (Get-Item $MAVEN_M2_PATH).Target[0] + "/wrapper/dists"
}
```

- `$MAVEN_WRAPPER_DISTS = $null`: Will hold the folder for downloaded distributions.
- `if ((Get-Item $MAVEN_M2_PATH).Target[0] -eq $null) {`: If the folder is not a link...
- `$MAVEN_WRAPPER_DISTS = "$MAVEN_M2_PATH/wrapper/dists"`: ... use it directly.
- `} else {`: Otherwise...
- `$MAVEN_WRAPPER_DISTS = (Get-Item $MAVEN_M2_PATH).Target[0] + "/wrapper/dists"`: ... follow the link to its real place.
- `}`: Closes a block.

```text
$MAVEN_HOME_PARENT = "$MAVEN_WRAPPER_DISTS/$distributionUrlNameMain"
$MAVEN_HOME_NAME = ([System.Security.Cryptography.SHA256]::Create().ComputeHash([byte[]][char[]]$distributionUrl) | ForEach-Object {$_.ToString("x2")}) -join ''
$MAVEN_HOME = "$MAVEN_HOME_PARENT/$MAVEN_HOME_NAME"
```

- `$MAVEN_HOME_PARENT = "$MAVEN_WRAPPER_DISTS/$distributionUrlNameMain"`: The folder named after the Maven version.
- `$MAVEN_HOME_NAME = ([System.Security.Cryptography.SHA256]::Create().ComputeHash([byte[]...`: A name made from the SHA-256 hash of the download address, written as hexadecimal (`sha-256.md`).
- `$MAVEN_HOME = "$MAVEN_HOME_PARENT/$MAVEN_HOME_NAME"`: The final folder.

```text
if (Test-Path -Path "$MAVEN_HOME" -PathType Container) {
  Write-Verbose "found existing MAVEN_HOME at $MAVEN_HOME"
  Write-Output "MVN_CMD=$MAVEN_HOME/bin/$MVN_CMD"
  exit $?
}
```

- `if (Test-Path -Path "$MAVEN_HOME" -PathType Container) {`: If it already exists, Maven was installed before.
- `Write-Verbose "found existing MAVEN_HOME at $MAVEN_HOME"`: Verbose message.
- `Write-Output "MVN_CMD=$MAVEN_HOME/bin/$MVN_CMD"`: Prints the line the batch part reads: the path of the program to run.
- `exit $?`: Ends, passing on the status of the last command.
- `}`: Closes a block.

```text
if (! $distributionUrlNameMain -or ($distributionUrlName -eq $distributionUrlNameMain)) {
  Write-Error "distributionUrl is not valid, must end with *-bin.zip, but found $distributionUrl"
}
```

- `if (! $distributionUrlNameMain -or ($distributionUrlName -eq $distributionUrlNameMain)) {`: Validates the address.
- `Write-Error "distributionUrl is not valid, must end with *-bin.zip, but found $distribu...`: Stops with an error if it is not.
- `}`: Closes a block.

```text
# prepare tmp dir
$TMP_DOWNLOAD_DIR_HOLDER = New-TemporaryFile
$TMP_DOWNLOAD_DIR = New-Item -Itemtype Directory -Path "$TMP_DOWNLOAD_DIR_HOLDER.dir"
$TMP_DOWNLOAD_DIR_HOLDER.Delete() | Out-Null
trap {
  if ($TMP_DOWNLOAD_DIR.Exists) {
    try { Remove-Item $TMP_DOWNLOAD_DIR -Recurse -Force | Out-Null }
    catch { Write-Warning "Cannot remove $TMP_DOWNLOAD_DIR" }
  }
}
```

- `# prepare tmp dir`: a comment written by the author; the tool ignores it. It explains the lines below.
- `$TMP_DOWNLOAD_DIR_HOLDER = New-TemporaryFile`: Creates a temporary file to get a unique name.
- `$TMP_DOWNLOAD_DIR = New-Item -Itemtype Directory -Path "$TMP_DOWNLOAD_DIR_HOLDER.dir"`: Creates a temporary folder with that name plus `.dir`.
- `$TMP_DOWNLOAD_DIR_HOLDER.Delete() | Out-Null`: Deletes the temporary file.
- `trap {`: A **trap** runs when an error stops the script: it cleans up.
- `if ($TMP_DOWNLOAD_DIR.Exists) {`: If the folder is there...
- `try { Remove-Item $TMP_DOWNLOAD_DIR -Recurse -Force | Out-Null }`: ... delete it with everything inside.
- `catch { Write-Warning "Cannot remove $TMP_DOWNLOAD_DIR" }`: If deleting fails, warn.
- `}`: Closes a block.
- `}`: Closes a block.

```text
New-Item -Itemtype Directory -Path "$MAVEN_HOME_PARENT" -Force | Out-Null
```

- `New-Item -Itemtype Directory -Path "$MAVEN_HOME_PARENT" -Force | Out-Null`: Creates the parent folder of the target.

```text
# Download and Install Apache Maven
Write-Verbose "Couldn't find MAVEN_HOME, downloading and installing it ..."
Write-Verbose "Downloading from: $distributionUrl"
Write-Verbose "Downloading to: $TMP_DOWNLOAD_DIR/$distributionUrlName"
```

- `# Download and Install Apache Maven`: a comment written by the author; the tool ignores it. It explains the lines below.
- `Write-Verbose "Couldn't find MAVEN_HOME, downloading and installing it ..."`: Verbose message.
- `Write-Verbose "Downloading from: $distributionUrl"`: Verbose message.
- `Write-Verbose "Downloading to: $TMP_DOWNLOAD_DIR/$distributionUrlName"`: Verbose message.

```text
$webclient = New-Object System.Net.WebClient
if ($env:MVNW_USERNAME -and $env:MVNW_PASSWORD) {
  $webclient.Credentials = New-Object System.Net.NetworkCredential($env:MVNW_USERNAME, $env:MVNW_PASSWORD)
}
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$webclient.DownloadFile($distributionUrl, "$TMP_DOWNLOAD_DIR/$distributionUrlName") | Out-Null
```

- `$webclient = New-Object System.Net.WebClient`: A web client object for the download.
- `if ($env:MVNW_USERNAME -and $env:MVNW_PASSWORD) {`: If a user name and password are set...
- `$webclient.Credentials = New-Object System.Net.NetworkCredential($env:MVNW_USERNAME, $e...`: ... give them to the client.
- `}`: Closes a block.
- `[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12`: Insist on TLS 1.2 for the download.
- `$webclient.DownloadFile($distributionUrl, "$TMP_DOWNLOAD_DIR/$distributionUrlName") | O...`: Downloads the file.

```text
# If specified, validate the SHA-256 sum of the Maven distribution zip file
$distributionSha256Sum = (Get-Content -Raw "$scriptDir/.mvn/wrapper/maven-wrapper.properties" | ConvertFrom-StringData).distributionSha256Sum
if ($distributionSha256Sum) {
  if ($USE_MVND) {
    Write-Error "Checksum validation is not supported for maven-mvnd. `nPlease disable validation by removing 'distributionSha256Sum' from your maven-wrapper.properties."
  }
  Import-Module $PSHOME\Modules\Microsoft.PowerShell.Utility -Function Get-FileHash
  if ((Get-FileHash "$TMP_DOWNLOAD_DIR/$distributionUrlName" -Algorithm SHA256).Hash.ToLower() -ne $distributionSha256Sum) {
    Write-Error "Error: Failed to validate Maven distribution SHA-256, your Maven distribution might be compromised. If you updated your Maven version, you need to update the specified distributionSha256Sum property."
  }
```

- `# If specified, validate the SHA-256 sum of the Maven distribution zip file`: a comment written by the author; the tool ignores it. It explains the lines below.
- `$distributionSha256Sum = (Get-Content -Raw "$scriptDir/.mvn/wrapper/maven-wrapper.prope...`: Reads the optional checksum from the properties.
- `if ($distributionSha256Sum) {`: If a checksum is given...
- `if ($USE_MVND) {`: mvnd cannot be checked.
- `Write-Error "Checksum validation is not supported for maven-mvnd. `nPlease disable vali...`: Stop with an explanation.
- `}`: Closes a block.
- `Import-Module $PSHOME\Modules\Microsoft.PowerShell.Utility -Function Get-FileHash`: Loads the module that has `Get-FileHash`.
- `if ((Get-FileHash "$TMP_DOWNLOAD_DIR/$distributionUrlName" -Algorithm SHA256).Hash.ToLo...`: Computes the SHA-256 of the download and compares it with the expected value.
- `Write-Error "Error: Failed to validate Maven distribution SHA-256, your Maven distribut...`: A mismatch stops the script: the download may be compromised.
- `}`: Closes a block.

```text
}
```

- `}`: Closes a block.

```text
# unzip and move
Expand-Archive "$TMP_DOWNLOAD_DIR/$distributionUrlName" -DestinationPath "$TMP_DOWNLOAD_DIR" | Out-Null
```

- `# unzip and move`: a comment written by the author; the tool ignores it. It explains the lines below.
- `Expand-Archive "$TMP_DOWNLOAD_DIR/$distributionUrlName" -DestinationPath "$TMP_DOWNLOAD...`: Unzips the download.

```text
# Find the actual extracted directory name (handles snapshots where filename != directory name)
$actualDistributionDir = ""
```

- `# Find the actual extracted directory name (handles snapshots where filename != directory name)`: a comment written by the author; the tool ignores it. It explains the lines below.
- `$actualDistributionDir = ""`: Will hold the unpacked folder's name.

```text
# First try the expected directory name (for regular distributions)
$expectedPath = Join-Path "$TMP_DOWNLOAD_DIR" "$distributionUrlNameMain"
$expectedMvnPath = Join-Path "$expectedPath" "bin/$MVN_CMD"
if ((Test-Path -Path $expectedPath -PathType Container) -and (Test-Path -Path $expectedMvnPath -PathType Leaf)) {
  $actualDistributionDir = $distributionUrlNameMain
}
```

- `# First try the expected directory name (for regular distributions)`: a comment written by the author; the tool ignores it. It explains the lines below.
- `$expectedPath = Join-Path "$TMP_DOWNLOAD_DIR" "$distributionUrlNameMain"`: The folder expected inside the zip.
- `$expectedMvnPath = Join-Path "$expectedPath" "bin/$MVN_CMD"`: Where the Maven program should be inside it.
- `if ((Test-Path -Path $expectedPath -PathType Container) -and (Test-Path -Path $expected...`: If both exist...
- `$actualDistributionDir = $distributionUrlNameMain`: ... use that name.
- `}`: Closes a block.

```text
# If not found, search for any directory with the Maven executable (for snapshots)
if (!$actualDistributionDir) {
  Get-ChildItem -Path "$TMP_DOWNLOAD_DIR" -Directory | ForEach-Object {
    $testPath = Join-Path $_.FullName "bin/$MVN_CMD"
    if (Test-Path -Path $testPath -PathType Leaf) {
      $actualDistributionDir = $_.Name
    }
  }
}
```

- `# If not found, search for any directory with the Maven executable (for snapshots)`: a comment written by the author; the tool ignores it. It explains the lines below.
- `if (!$actualDistributionDir) {`: Otherwise search every folder.
- `Get-ChildItem -Path "$TMP_DOWNLOAD_DIR" -Directory | ForEach-Object {`: Loops over the folders in the temporary folder.
- `$testPath = Join-Path $_.FullName "bin/$MVN_CMD"`: The Maven program path in this folder.
- `if (Test-Path -Path $testPath -PathType Leaf) {`: If the file exists...
- `$actualDistributionDir = $_.Name`: ... remember the folder name.
- `}`: Closes a block.
- `}`: Closes a block.
- `}`: Closes a block.

```text
if (!$actualDistributionDir) {
  Write-Error "Could not find Maven distribution directory in extracted archive"
}
```

- `if (!$actualDistributionDir) {`: Otherwise search every folder.
- `Write-Error "Could not find Maven distribution directory in extracted archive"`: Stop with an error if none was found.
- `}`: Closes a block.

```text
Write-Verbose "Found extracted Maven distribution directory: $actualDistributionDir"
Rename-Item -Path "$TMP_DOWNLOAD_DIR/$actualDistributionDir" -NewName $MAVEN_HOME_NAME | Out-Null
try {
  Move-Item -Path "$TMP_DOWNLOAD_DIR/$MAVEN_HOME_NAME" -Destination $MAVEN_HOME_PARENT | Out-Null
} catch {
  if (! (Test-Path -Path "$MAVEN_HOME" -PathType Container)) {
    Write-Error "fail to move MAVEN_HOME"
  }
} finally {
  try { Remove-Item $TMP_DOWNLOAD_DIR -Recurse -Force | Out-Null }
```

- `Write-Verbose "Found extracted Maven distribution directory: $actualDistributionDir"`: Verbose message.
- `Rename-Item -Path "$TMP_DOWNLOAD_DIR/$actualDistributionDir" -NewName $MAVEN_HOME_NAME ...`: Renames the unpacked folder to the hash-based name used for `MAVEN_HOME`.
- `try {`: Starts a `try` block: if something inside fails, the `catch` block runs.
- `Move-Item -Path "$TMP_DOWNLOAD_DIR/$MAVEN_HOME_NAME" -Destination $MAVEN_HOME_PARENT | ...`: Moves the unpacked folder to its final place.
- `} catch {`: The error handler: if the move failed...
- `if (! (Test-Path -Path "$MAVEN_HOME" -PathType Container)) {`: ... check whether `MAVEN_HOME` exists anyway (another process may have installed it first).
- `Write-Error "fail to move MAVEN_HOME"`: Stops with an error.
- `}`: Closes a block.
- `} finally {`: The `finally` block runs always, error or not.
- `try { Remove-Item $TMP_DOWNLOAD_DIR -Recurse -Force | Out-Null }`: ... delete it with everything inside.

```text
  catch { Write-Warning "Cannot remove $TMP_DOWNLOAD_DIR" }
}
```

- `catch { Write-Warning "Cannot remove $TMP_DOWNLOAD_DIR" }`: If deleting fails, warn.
- `}`: Closes a block.

```text
Write-Output "MVN_CMD=$MAVEN_HOME/bin/$MVN_CMD"
```

- `Write-Output "MVN_CMD=$MAVEN_HOME/bin/$MVN_CMD"`: Prints the line the batch part reads: the path of the program to run.

## Try it yourself

1. `cd java && ./mvnw -v` prints `Apache Maven 3.9.9` and the Java version found (the first call downloads Maven).
2. `MVNW_VERBOSE=true ./mvnw -v` also prints the `verbose` messages: `found existing MAVEN_HOME at ...` once Maven is installed.
3. `ls ~/.m2/wrapper/dists/` lists the installed Maven distributions, each in a folder named after a hash.
4. `sh -n java/mvnw && echo syntax ok` checks the shell syntax without running the script and prints `syntax ok`.

## Mistakes people make

- Editing the wrapper scripts by hand; regenerate them with the Maven Wrapper plug-in.
- Running `mvnw` from the wrong folder: it uses its own location, but the arguments (`pom.xml`) refer to the current folder.
- Setting `JAVA_HOME` to a JRE without `javac`: the shell script needs both programs.
- Behind a proxy without `MVNW_REPOURL`: the download fails.

## Check yourself

1. **What is the first line `#!/bin/sh` called?**  
   The shebang: it names the program that runs the script.
2. **What does `exec` do?**  
   Replaces the running script by the program it names.
3. **Where is the downloaded Maven kept?**  
   Under `~/.m2/wrapper/dists/`.
4. **Why is the folder name a hash of the address?**  
   So different Maven versions or mirrors never collide.
5. **What does `"$@"` do?**  
   Passes all arguments on unchanged.

## Further reading

Apache Maven Wrapper: https://maven.apache.org/tools/wrapper/ . POSIX shell: https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html . PowerShell: https://learn.microsoft.com/powershell/
