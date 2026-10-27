# ArchUnit 1.4.1

## What it is

**ArchUnit** is a Java library that checks the structure of a program as a unit test. It reads the compiled classes, builds a graph of which class uses which, and lets you write rules such as "no class in package A may use a class in package B". If a rule is broken, the test fails and lists the offending classes.

## Why this repository uses it

The promise of this design is that the domain knows nothing about frameworks and the application knows nothing about adapters. In Python that is `import-linter` (`import-linter.md`); in Java the same promise is an ArchUnit test, so the second implementation cannot quietly drift.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `java/src/test/java/dev/plainround/router/ArchitectureTest.java` | The rules. |
| `java/pom.xml` | Declares `archunit-junit5`. |


## How it works underneath

ArchUnit uses a library (ASM) to read the bytecode of the `.class` files. For every class it records the types of its fields, the parameter and return types of its methods, the classes it calls, and the exceptions it throws. Rules are written in a fluent style, `noClasses().that().resideInAPackage(...).should().dependOnClassesThat().resideInAnyPackage(...)`, and are evaluated over that graph. The JUnit 5 integration finds fields annotated `@ArchTest` and reports each as a test. Package patterns use `..` for "any number of segments" and `*` for one.

## Walkthrough of this repository's use

`java/src/test/java/dev/plainround/router/ArchitectureTest.java`

```java
package dev.plainround.router;
```

The test lives in the project's root package.

```java
import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;
```

A static import so that `noClasses()` can be called without a prefix.

```java
import com.tngtech.archunit.core.importer.ImportOption;
import com.tngtech.archunit.junit.AnalyzeClasses;
import com.tngtech.archunit.junit.ArchTest;
import com.tngtech.archunit.lang.ArchRule;
```

ArchUnit's classes: the import options, JUnit 5 annotations and the rule type.

```java
/** The dependency rule: domain depends on nothing, application on domain, nothing on interfaces. */
```

Javadoc: the rule in one sentence.

```java
@AnalyzeClasses(packages = "dev.plainround.router", importOptions = ImportOption.DoNotIncludeTests.class)
```

Tells ArchUnit which compiled classes to read: everything under the package, with `DoNotIncludeTests` leaving out the test classes.

```java
class ArchitectureTest {
```

A normal test class.

```java
    @ArchTest
    static final ArchRule domainKnowsNoOuterLayerAndNoSdk = noClasses()
            .that().resideInAPackage("..domain..")
            .should().dependOnClassesThat().resideInAnyPackage(
                    "..application..", "..infrastructure..", "..interfaces..", "org.springframework..", "com.openai..", "tools.jackson..");
```

Each `static final ArchRule` field marked `@ArchTest` is run as one test. This rule: **no class in a package called `domain` may depend on** classes in the application, infrastructure or interfaces packages, Spring, the OpenAI client library, or Jackson. `"..domain.."` is a package pattern: `..` stands for any number of package segments. So the domain is plain Java.

```java
    @ArchTest
    static final ArchRule applicationKnowsNeitherInfrastructureNorSpring = noClasses()
            .that().resideInAPackage("..application..")
            .should().dependOnClassesThat().resideInAnyPackage("..infrastructure..", "..interfaces..", "org.springframework..", "com.openai..");
```

The application layer may use the domain, but not infrastructure, interfaces, Spring or the OpenAI client.

```java
    @ArchTest
    static final ArchRule nothingDependsOnInterfaces = noClasses()
            .that().resideOutsideOfPackage("..interfaces..")
            .should().dependOnClassesThat().resideInAPackage("..interfaces..");
}
```

No class outside `interfaces` may depend on a class in `interfaces`: the outermost layer is only the entry point.

## Try it yourself

1. `cd java && ./mvnw -q -B test -Dtest=ArchitectureTest` runs only the architecture rules; no output and exit status 0 mean all rules hold.
2. In a domain class add `import org.springframework.stereotype.Component;` and a field of that type, then rerun: the failing rule prints `Rule '...' was violated (1 times)` and names the class. Undo with `git checkout .`.
3. `unzip -l java/target/*.jar | grep domain | head` shows the compiled domain classes the rules read.

## Mistakes people make

- **Rules that match nothing.** A typo in a package name makes a rule pass for the wrong reason; ArchUnit's `failOnEmptyShould` default catches some of this.
- **Testing only direct dependencies** and forgetting that a rule can be broken through a type in a method signature.
- **Including test classes** in the analysis; the import option excludes them.
- **Treating the rules as documentation only.** They run on every `make java-test`.

## Check yourself

1. **What does ArchUnit read?**  
   The compiled classes (bytecode), not the source.
2. **What does `..domain..` match?**  
   Any package that has a segment named `domain`, at any depth.
3. **What marks a rule field as a test?**  
   The `@ArchTest` annotation.
4. **Which Python tool plays the same role?**  
   `import-linter`.
5. **Why exclude test classes from the analysis?**  
   Tests may use anything; only production code must obey the layers.

## Further reading

ArchUnit user guide: https://www.archunit.org/userguide/html/000_Index.html . Pinned version: 1.4.1 (java/pom.xml).
