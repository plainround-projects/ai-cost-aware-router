# Maven 3.9.9 and the Maven wrapper

## What it is

**Maven** is a build tool for Java. You describe the project in a file called `pom.xml` (the *Project Object Model*): its name, the Java version, the libraries it needs and the plug-ins that compile, test and package it. Maven downloads the libraries from a central repository, runs the build in fixed **phases** (`compile`, `test`, `package`, ...) and produces a `.jar` (a zip of compiled classes). The **wrapper** (`mvnw`) is a small script that downloads the right Maven version first, so you do not have to install it.

## Why this repository uses it

Without a build tool, a Java program is a pile of files and a list of downloads. `pom.xml` fixes exact library versions (Spring AI, JUnit, ArchUnit) and the wrapper fixes the Maven version, so the Java half builds the same way on your machine, in CI and in Docker.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `java/pom.xml` | The build description. |
| `java/mvnw` | Wrapper script for macOS and Linux. |
| `java/mvnw.cmd` | Wrapper script for Windows. |
| `java/.mvn/wrapper/maven-wrapper.properties` | Which Maven version the wrapper downloads. |
| `Makefile` | `make java-test` and friends call `./mvnw`. |


## How it works underneath

**Coordinates.** Every library is identified by `groupId` (the publisher), `artifactId` (the library) and `version`. Maven resolves a dependency by downloading `<group path>/<artifact>/<version>/<artifact>-<version>.jar` and its own `pom.xml`, which lists the libraries *it* needs (transitive dependencies). Downloads are cached in `~/.m2/repository`.

**Lifecycle.** A phase runs all earlier phases. `mvn test` = validate, compile, test. `mvn package` = ... test, then package into a jar. `-DskipTests` skips running tests; `-q` is quiet; `-B` is batch mode (no colors, no progress bars) for logs.

**Plug-ins.** Phases do nothing by themselves; plug-ins bound to them do the work: the *compiler* plug-in runs `javac`, *surefire* runs the tests, *shade* builds one jar that contains the program and all libraries (a "fat jar") so that `java -jar` works.

**BOM.** A *bill of materials* imported in `dependencyManagement` is a list of matching versions of many libraries; with it you name a library without a version and Maven picks the compatible one.

**Wrapper.** `mvnw` reads `.mvn/wrapper/maven-wrapper.properties`, downloads the named Maven distribution into `~/.m2/wrapper`, and runs it.

## Walkthrough of this repository's use

### The build file

`java/pom.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
```

- `<?xml version="1.0" encoding="UTF-8"?>`: The XML declaration: this file is XML, encoded as UTF-8.
- `<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XM...`: The root element of every Maven build file. `xmlns` names the XML vocabulary (a namespace) the tags belong to; `xsi:schemaLocation` points to the schema that defines which tags are allowed, so editors can validate the file.
- `xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/mave...`: The rest of the root element's attributes.
- `<modelVersion>4.0.0</modelVersion>`: The version of the Maven file format (always 4.0.0 for Maven 3 and 4).

```xml
  <groupId>dev.plainround</groupId>
  <artifactId>cost-router-java</artifactId>
  <version>0.1.0</version>
  <name>cost-router-java</name>
  <description>Java (Spring AI) port of the cost-aware router: same data, prompts, fixtures and reports.</description>
```

- `<groupId>dev.plainround</groupId>`: Part 1 of this project's coordinates: the group (like a reversed domain name) that owns it.
- `<artifactId>cost-router-java</artifactId>`: Part 2: the project's name; it also names the jar.
- `<version>0.1.0</version>`: Part 3: the version of this release.
- `<name>cost-router-java</name>`: A display name.
- `<description>Java (Spring AI) port of the cost-aware router: same data, prompts, fixtur...`: One sentence on what the project is.

```xml
  <properties>
    <java.version>21</java.version>
    <maven.compiler.release>21</maven.compiler.release>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <spring-ai.version>2.0.1</spring-ai.version>
    <spring-boot.version>4.0.5</spring-boot.version>
    <junit.version>5.12.2</junit.version>
    <archunit.version>1.4.1</archunit.version>
  </properties>
```

- `<properties>`: Named values used elsewhere in the file as `${name}`.
- `<java.version>21</java.version>`: The Java version (21).
- `<maven.compiler.release>21</maven.compiler.release>`: Tells the compiler to produce code for Java 21 and to allow only the Java 21 library API.
- `<project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>`: Source files are UTF-8.
- `<spring-ai.version>2.0.1</spring-ai.version>`: The Spring AI version, written once here and used by the next sections.
- `<spring-boot.version>4.0.5</spring-boot.version>`: The Spring Boot version used only to align library versions (below).
- `<junit.version>5.12.2</junit.version>`: The JUnit test library version.
- `<archunit.version>1.4.1</archunit.version>`: The ArchUnit version.
- `</properties>`: Ends the properties.

```xml
  <dependencyManagement>
    <dependencies>
      <dependency>
        <groupId>org.springframework.ai</groupId>
        <artifactId>spring-ai-bom</artifactId>
        <version>${spring-ai.version}</version>
        <type>pom</type>
        <scope>import</scope>
      </dependency>
      <!-- Aligns Jackson 2 annotations, Jackson 3, Reactor and Netty with what Spring AI 2.0 is built against. -->
      <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-dependencies</artifactId>
        <version>${spring-boot.version}</version>
        <type>pom</type>
        <scope>import</scope>
```

- `<dependencyManagement>`: Rules for versions only: nothing here is added to the program. It says which version to use whenever a dependency below does not name one.
- `<dependencies>`: The list inside dependencyManagement.
- `<dependency>`: One entry.
- `<groupId>org.springframework.ai</groupId>`: The group of the Spring AI bill of materials.
- `<artifactId>spring-ai-bom</artifactId>`: A "BOM" (bill of materials) is a pom that lists a consistent set of library versions.
- `<version>${spring-ai.version}</version>`: The version, taken from the property above.
- `<type>pom</type>`: The imported artifact is a pom, not a jar.
- `<scope>import</scope>`: `import` merges that pom's version list into this one.
- `</dependency>`: Ends the entry.
- `<!-- Aligns Jackson 2 annotations, Jackson 3, Reactor and Netty with what Spring AI 2.0...`: An XML comment (ignored by Maven) explaining why the Spring Boot list is imported.
- `<dependency>`: One entry.
- `<groupId>org.springframework.boot</groupId>`: The group of the Spring Boot dependency list.
- `<artifactId>spring-boot-dependencies</artifactId>`: Spring Boot's own list of versions. Importing it makes Jackson, Reactor and Netty line up with what Spring AI 2.0 was built against.
- `<version>${spring-boot.version}</version>`: The version, taken from the property above.
- `<type>pom</type>`: The imported artifact is a pom, not a jar.
- `<scope>import</scope>`: `import` merges that pom's version list into this one.

```xml
      </dependency>
    </dependencies>
  </dependencyManagement>
```

- `</dependency>`: Ends the entry.
- `</dependencies>`: Ends the list.
- `</dependencyManagement>`: Ends dependencyManagement.

```xml
  <dependencies>
    <dependency>
      <groupId>org.springframework.ai</groupId>
      <artifactId>spring-ai-openai</artifactId>
    </dependency>
    <dependency>
      <groupId>org.springframework.ai</groupId>
      <artifactId>spring-ai-client-chat</artifactId>
    </dependency>
    <dependency>
      <groupId>org.junit.jupiter</groupId>
      <artifactId>junit-jupiter</artifactId>
      <version>${junit.version}</version>
      <scope>test</scope>
    </dependency>
    <dependency>
```

- `<dependencies>`: The libraries the program is built with.
- `<dependency>`: One library.
- `<groupId>org.springframework.ai</groupId>`: Group of the Spring AI libraries.
- `<artifactId>spring-ai-openai</artifactId>`: Spring AI's client for OpenAI-compatible chat servers (`spring-ai.md`). No version: the BOM above supplies it.
- `</dependency>`: Ends the library entry.
- `<dependency>`: One library.
- `<groupId>org.springframework.ai</groupId>`: Group of the Spring AI libraries.
- `<artifactId>spring-ai-client-chat</artifactId>`: Spring AI's `ChatClient`, the high-level API that builds a prompt and calls the model. Version from the BOM.
- `</dependency>`: Ends the library entry.
- `<dependency>`: One library.
- `<groupId>org.junit.jupiter</groupId>`: Group of JUnit 5.
- `<artifactId>junit-jupiter</artifactId>`: JUnit 5 with its parameterized-test support (`junit.md`).
- `<version>${junit.version}</version>`: The version from the property.
- `<scope>test</scope>`: `test` means: used when compiling and running the tests only, never packaged into the program.
- `</dependency>`: Ends the library entry.
- `<dependency>`: One library.

```xml
      <groupId>com.tngtech.archunit</groupId>
      <artifactId>archunit-junit5</artifactId>
      <version>${archunit.version}</version>
      <scope>test</scope>
    </dependency>
  </dependencies>
```

- `<groupId>com.tngtech.archunit</groupId>`: Group of ArchUnit.
- `<artifactId>archunit-junit5</artifactId>`: ArchUnit with its JUnit 5 integration (`archunit.md`).
- `<version>${archunit.version}</version>`: The version from the property.
- `<scope>test</scope>`: `test` means: used when compiling and running the tests only, never packaged into the program.
- `</dependency>`: Ends the library entry.
- `</dependencies>`: Ends the dependency list.

```xml
  <build>
    <finalName>cost-router-java</finalName>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.13.0</version>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-surefire-plugin</artifactId>
        <version>3.5.2</version>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-shade-plugin</artifactId>
```

- `<build>`: How to build.
- `<finalName>cost-router-java</finalName>`: The jar is named `NAME.jar` (so `java -jar target/NAME.jar` works).
- `<plugins>`: Tools that take part in the build.
- `<plugin>`: One plugin.
- `<groupId>org.apache.maven.plugins</groupId>`: The group of the standard Maven plugins.
- `<artifactId>maven-compiler-plugin</artifactId>`: Compiles the Java source.
- `<version>3.13.0</version>`: The plugin's version, fixed so builds are repeatable.
- `</plugin>`: Ends the plugin.
- `<plugin>`: One plugin.
- `<groupId>org.apache.maven.plugins</groupId>`: The group of the standard Maven plugins.
- `<artifactId>maven-surefire-plugin</artifactId>`: Runs the unit tests.
- `<version>3.5.2</version>`: The plugin's version, fixed so builds are repeatable.
- `</plugin>`: Ends the plugin.
- `<plugin>`: One plugin.
- `<groupId>org.apache.maven.plugins</groupId>`: The group of the standard Maven plugins.
- `<artifactId>maven-shade-plugin</artifactId>`: Builds one "fat" jar that contains the program and all its libraries, so one file runs anywhere.

```xml
        <version>3.6.0</version>
        <executions>
          <execution>
            <phase>package</phase>
            <goals>
              <goal>shade</goal>
            </goals>
            <configuration>
              <createDependencyReducedPom>false</createDependencyReducedPom>
              <transformers>
                <transformer implementation="org.apache.maven.plugins.shade.resource.ManifestResourceTransformer">
                  <mainClass>dev.plainround.router.interfaces.Main</mainClass>
                </transformer>
                <transformer implementation="org.apache.maven.plugins.shade.resource.ServicesResourceTransformer"/>
              </transformers>
              <filters>
```

- `<version>3.6.0</version>`: The plugin's version, fixed so builds are repeatable.
- `<executions>`: When the plugin runs.
- `<execution>`: One run.
- `<phase>package</phase>`: During the `package` phase of Maven's life cycle.
- `<goals>`: The tasks to run.
- `<goal>shade</goal>`: The task `shade`: merge everything into one jar.
- `</goals>`: Ends the tasks.
- `<configuration>`: Settings of the task.
- `<createDependencyReducedPom>false</createDependencyReducedPom>`: Do not write an extra pom without the merged libraries.
- `<transformers>`: Steps that adjust files while merging.
- `<transformer implementation="org.apache.maven.plugins.shade.resource.ManifestResourceTr...`: Writes the jar's manifest (its metadata file).
- `<mainClass>dev.plainround.router.interfaces.Main</mainClass>`: The class whose `main` method starts the program; it goes into the manifest, which is what makes `java -jar` work.
- `</transformer>`: Ends the transformer.
- `<transformer implementation="org.apache.maven.plugins.shade.resource.ServicesResourceTr...`: Merges the `META-INF/services` files of the libraries (Java's way of registering plug-ins) instead of letting one overwrite another.
- `</transformers>`: Ends the transformers.
- `<filters>`: Which files to leave out.

```xml
                <filter>
                  <artifact>*:*</artifact>
                  <excludes>
                    <exclude>META-INF/*.SF</exclude>
                    <exclude>META-INF/*.DSA</exclude>
                    <exclude>META-INF/*.RSA</exclude>
                    <exclude>META-INF/MANIFEST.MF</exclude>
                    <exclude>META-INF/versions/**/module-info.class</exclude>
                    <exclude>module-info.class</exclude>
                  </excludes>
                </filter>
              </filters>
            </configuration>
          </execution>
        </executions>
      </plugin>
```

- `<filter>`: One filter.
- `<artifact>*:*</artifact>`: Applies to every library.
- `<excludes>`: The files to leave out.
- `<exclude>META-INF/*.SF</exclude>`: Signature files of the original jars. Merged jars would no longer match the signatures, and Java would refuse to load them.
- `<exclude>META-INF/*.DSA</exclude>`: Signature files of the original jars. Merged jars would no longer match the signatures, and Java would refuse to load them.
- `<exclude>META-INF/*.RSA</exclude>`: Signature files of the original jars. Merged jars would no longer match the signatures, and Java would refuse to load them.
- `<exclude>META-INF/MANIFEST.MF</exclude>`: Each library's own manifest; the program's manifest is written instead.
- `<exclude>META-INF/versions/**/module-info.class</exclude>`: Module descriptors of multi-release jars, which are not wanted in a merged jar.
- `<exclude>module-info.class</exclude>`: Module descriptors, for the same reason.
- `</excludes>`: Ends the list.
- `</filter>`: Ends the filter.
- `</filters>`: Ends the filters.
- `</configuration>`: Ends the settings.
- `</execution>`: Ends the run.
- `</executions>`: Ends the runs.
- `</plugin>`: Ends the plugin.

```xml
    </plugins>
  </build>
</project>
```

- `</plugins>`: Ends the plugins.
- `</build>`: Ends the build section.
- `</project>`: Ends the file.

### The wrapper settings

`java/.mvn/wrapper/maven-wrapper.properties`

```properties
wrapperVersion=3.3.4
distributionType=only-script
distributionUrl=https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/3.9.9/apache-maven-3.9.9-bin.zip
```

- `wrapperVersion=3.3.4`: The version of the wrapper scripts themselves.
- `distributionType=only-script`: The wrapper downloads no helper jar; the `mvnw` script does the download with shell tools.
- `distributionUrl=https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/3.9....`: Where `mvnw` downloads Maven 3.9.9 from the first time you run it. After that it is cached in `~/.m2/wrapper`.

### How the Makefile uses it

`Makefile`

```make
java-test: ## step 7: build and test the Java (Spring AI) port
	cd java && ./mvnw -q -B verify
```

`cd java && ./mvnw -q -B test` changes into the `java` folder and runs the test phase quietly in batch mode (in a Makefile the two commands share a line, because every recipe line gets its own shell; see `make.md`).

## Try it yourself

1. `cd java && ./mvnw -v` prints `Apache Maven 3.9.9` and the Java version it found (the first call downloads Maven).
2. `cd java && ./mvnw -q -B dependency:tree | head -20` shows the library tree.
3. `cd java && ./mvnw -q -B -DskipTests package && ls target/*.jar` builds the jar.
4. `unzip -l java/target/*.jar | head` lists what the fat jar contains.
5. `ls ~/.m2/repository | head` shows the local library cache.

## Mistakes people make

- **Different Maven versions on different machines**: use `./mvnw`, not `mvn`.
- **Putting two versions of one library in the tree.** Importing the BOM keeps them aligned.
- **Running tests in the Docker build**: `-DskipTests` there; `make java-test` runs them.
- **Editing `target/`**: it is generated and ignored by git.
- **Offline builds without a warm cache** fail with a download error.

## Check yourself

1. **What identifies a library in Maven?**  
   `groupId`, `artifactId` and `version`.
2. **What does `mvn package` run besides packaging?**  
   All earlier phases, including compile and test (unless skipped).
3. **What is the wrapper for?**  
   It downloads and runs the exact Maven version, so nobody has to install Maven.
4. **What does the shade plug-in do?**  
   Builds one jar that contains the program and all its libraries.
5. **What is a BOM?**  
   A list of matching library versions that you import so that you need not pick versions yourself.

## Further reading

Maven documentation: https://maven.apache.org/guides/ (POM reference, lifecycle). Maven Wrapper: https://maven.apache.org/tools/wrapper/ . Pinned: Maven 3.9.9 (wrapper properties), compiler plug-in 3.13.0, surefire 3.5.2, shade 3.6.0, Java 21.
