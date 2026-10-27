# JUnit 5 (Jupiter) 5.12.2

## What it is

**JUnit** is the standard testing framework for Java. A test is an ordinary method marked with the annotation `@Test`. A test runner finds those methods, runs them one by one, and reports the ones whose assertions failed or that threw an exception. **Jupiter** is the programming model of JUnit 5 (annotations and assertions); the **platform** underneath launches the tests.

## Why this repository uses it

The Java half has to be as trustworthy as the Python half. Unit tests check the domain rules; a stub server checks the streaming client without a model; in four repositories a parity test checks that the Java program reproduces the Python reports.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `java/src/test/java/**/*Test.java (3 files)` | The test classes. |
| `java/pom.xml` | Declares `junit-jupiter` and the surefire plug-in. |
| `Makefile` | `make java-test`. |


## How it works underneath

Maven's *surefire* plug-in scans `target/test-classes` for classes with `@Test` methods and starts the JUnit platform. For each test method JUnit creates a **fresh instance** of the test class (so tests cannot leak state into each other), calls the method, and records the result: *passed*, *failed* (an assertion error) or *errored* (another exception). `assertEquals(expected, actual)` throws `AssertionFailedError` when the values differ, and that is how a test fails. A decimal comparison takes a third argument, the allowed difference (`assertEquals(0.3, x, 1e-9)`), because `double` arithmetic is not exact. `assertThrows(Type.class, () -> code)` passes only if the code throws that type. Tests are listed in the Maven output as `Tests run: N, Failures: F, Errors: E, Skipped: S`.

## Walkthrough of this repository's use

### The tests

| Test class | Test method (its name says what is checked) |
| --- | --- |
| `DomainTest.java` | `fixtureKeysEqualThePythonKeys` |
| `DomainTest.java` | `shuffleMatchesPython` |
| `DomainTest.java` | `refundRulesFollowThePolicy` |
| `DomainTest.java` | `answersAreParsedLikePython` |
| `DomainTest.java` | `gradingAndTheRefundCheckUseTheRecomputedAmount` |
| `DomainTest.java` | `theHardSignalSeesTwoOrdersOrAnExceptionWord` |
| `DomainTest.java` | `checkRatesAndTheDayBudget` |
| `ParityTest.java` | `javaReportsEqualPythonReports` |

### Reading one test class

`java/src/test/java/dev/plainround/router/ParityTest.java`

```java
package dev.plainround.router;
```

The test class lives in the root package of the project.

```java
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
```

**Static imports** let a test call `assertEquals(...)` without writing `Assertions.` first. `assertEquals(expected, actual, message)` fails the test if the values differ; `assertTrue` fails if the condition is false.

```java
import dev.plainround.router.interfaces.Main;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;
```

The program's own entry point `Main`, file and path helpers, the `@Test` annotation, and Jackson's reader (`jackson.md`).

```java
/** Step 7: from the same fixtures the Java port writes the same three reports as the committed Python reports. */
```

Javadoc: the purpose of the test. A **parity** test checks that the Java port writes the same reports as the Python program, from the same recorded answers.

```java
class ParityTest {
```

A test class needs no `public`; JUnit finds it by its `@Test` methods.

```java
    private static final JsonMapper JSON = JsonMapper.builder().build();
```

One shared JSON reader.

```java
    private static void assertSame(JsonNode expected, JsonNode actual, String path) {
        if (expected.isObject()) {
            assertEquals(expected.size(), actual.size(), path + " has different keys");
            for (String name : expected.propertyNames()) {
                assertTrue(actual.has(name), path + "." + name + " is missing");
                assertSame(expected.get(name), actual.get(name), path + "." + name);
            }
        } else if (expected.isArray()) {
            assertEquals(expected.size(), actual.size(), path + " has a different length");
            for (int i = 0; i < expected.size(); i++) {
                assertSame(expected.get(i), actual.get(i), path + "[" + i + "]");
            }
        } else if (expected.isNumber()) {
            assertEquals(expected.asDouble(), actual.asDouble(), 1e-6, path);
        } else {
            assertEquals(expected, actual, path);
        }
    }
```

A recursive comparison of two JSON trees. Objects must have the same size and every key; arrays the same length and equal elements, compared position by position; numbers are compared as decimals with a tolerance of `1e-6` (0.000001), because the two languages may differ in the last digit of a float; everything else is compared with `assertEquals`. The `path` string builds a message such as `.metrics.accuracy` so a failure says where.

```java
    @Test
    void javaReportsEqualPythonReports() throws Exception {
        Path root = Path.of("..");
        Path out = Path.of("target", "parity");
        Main.main(new String[] {
            "--data", root.resolve("data").toString(),
            "--prompts", root.resolve("prompts").toString(),
            "--fixtures", root.resolve("tests/fixtures").toString(),
            "--config", root.resolve("config").toString(),
            "--out", out.toString()
        });
        for (String name : new String[] {"router.json", "day.json", "audit.json"}) {
            assertSame(JSON.readTree(Files.readString(root.resolve("reports").resolve(name))), JSON.readTree(Files.readString(out.resolve(name))), name);
        }
    }
}
```

`@Test` marks a method JUnit must run. It throws `Exception` so checked exceptions need no handling. It calls `Main.main` with the same options as the command line, so the real program runs, writing into `target/parity`.

## Try it yourself

1. `make java-test` ends with `BUILD SUCCESS` in normal mode, or prints nothing at all in quiet mode when every test passes; the exit status is 0.
2. `cd java && ./mvnw -B test | grep "Tests run"` prints one `Tests run: N, Failures: 0, Errors: 0, Skipped: 0` line per class and a total.
3. `cd java && ./mvnw -q -B test -Dtest=ArchitectureTest` runs one class.
4. Change one expected number in a test and run it again to see the failure message: `expected: <...> but was: <...>`. Undo with `git checkout .`.

## Mistakes people make

- **Swapping expected and actual** in `assertEquals`; the failure message then reads backwards.
- **Comparing doubles exactly.** Use the tolerance form.
- **Tests that depend on the order of other tests.** JUnit does not guarantee an order.
- **A test class without any `@Test` method** is silently not run.
- **Using JUnit 4 annotations** (`org.junit.Test`) in a Jupiter project; they are ignored.

## Check yourself

1. **How does JUnit know which methods to run?**  
   Those marked with `@Test` (or `@ParameterizedTest`).
2. **Why does JUnit create a new test-class instance per test?**  
   So that state cannot leak between tests.
3. **What does `assertThrows` check?**  
   That the given code throws an exception of the given type.
4. **Why does a decimal assertion take a tolerance?**  
   Floating-point results can differ in the last digits.
5. **What is a parity test here?**  
   A test that runs the Java program on the recorded data and compares its JSON reports with the committed Python reports.

## Further reading

JUnit 5 user guide: https://junit.org/junit5/docs/current/user-guide/ . Pinned version: 5.12.2 (java/pom.xml).
