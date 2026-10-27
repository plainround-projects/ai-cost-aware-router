# Java 21

## What it is

Java is a programming language that is **compiled** to bytecode (`.class` files) and run by the Java Virtual Machine (JVM). Every piece of code lives in a **class**; files are grouped in **packages**; all variables and parameters have a declared **type** that the compiler checks before the program runs. A **JDK** (Java Development Kit) contains the compiler `javac`, the `java` launcher and the standard library.

## Why this repository uses it

Each lesson asks for a second implementation in Java with Spring AI: the same experiment, written against the same layers and checked against the Python result (a *parity* check, or a measurement of the client difference in the serve project). It shows that the design (a domain with no vendor code, ports and adapters) does not depend on one language.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `java/src/main/java/**/*.java (16 files)` | The Java program. |
| `java/src/test/java/**/*.java (3 files)` | Its tests. |
| `java/pom.xml` | The Maven build file (`maven.md`). |
| `java/mvnw` | The Maven wrapper script. |


## How it works underneath

**Compile, then run.** `javac` checks the source and writes bytecode; the JVM loads the classes it needs, interprets the bytecode and, for hot code, compiles it to machine code while running (the *JIT compiler*). That is why a Java program is slow for its first seconds and then fast, and why the load tests discard a warm-up period.

**Types.** Primitives (`int`, `double`, `boolean`, `long`) hold plain values. Everything else is an object reference and may be `null`. Generics (`List<String>`) let a collection remember its element type. The compiler rejects a wrong type.

**Records, interfaces, classes.** A `record` is an immutable data carrier. An `interface` lists methods; a class `implements` it. `final` forbids extension, `static` belongs to the class, not to an object, `private` hides a member from other classes.

**Exceptions.** `throw new X(...)` raises; `try { } catch (X e) { }` handles; `try (resource) { }` closes the resource at the end. *Checked* exceptions (such as `IOException`) must be declared or caught; `RuntimeException` and its children need not.

**Modern syntax used here.** `switch` as an expression with `->` arms returns a value; `var` lets the compiler infer a local type; lambdas `x -> x + 1` are small anonymous functions; streams (`files.filter(...).sorted().toList()`) process collections in a pipeline.

**Packages and layers.** A class's package is its address. The tests of the architecture (`archunit.md`) read these addresses to enforce the same dependency rule as `lint-imports` does for Python.

## Walkthrough of this repository's use

### All main classes

| File | What it does (first sentence of its Javadoc) |
| --- | --- |
| `java/src/main/java/dev/plainround/router/application/AnswerChecks.java` | The checks the router runs on an answer; no gold answer is visible to them (a port of answer_checks.py). |
| `java/src/main/java/dev/plainround/router/application/CostRouter.java` | Cheapest tier first, a check after every answer, escalation on a failed check (a port of router.py). |
| `java/src/main/java/dev/plainround/router/application/Experiments.java` | The lesson's steps as functions over the tier, check and router objects (a port of experiments.py). |
| `java/src/main/java/dev/plainround/router/application/ModelTiers.java` | The three model tiers: prompts, calls and cost (a port of tiers.py). |
| `java/src/main/java/dev/plainround/router/application/PromptStore.java` | Versioned prompt templates looked up by name such as label.v2. |
| `java/src/main/java/dev/plainround/router/application/Templates.java` | Prompt templates use {{name}} placeholders; rendering fails loudly on a missing value. |
| `java/src/main/java/dev/plainround/router/domain/Checks.java` | Parsing answers, grading them against the truth, and the checks the router can run (a port of checks.py). |
| `java/src/main/java/dev/plainround/router/domain/Llm.java` | Value types for talking to a chat model. |
| `java/src/main/java/dev/plainround/router/domain/Routing.java` | Pricing, router configuration, the daily budget, signals and metrics (ports of pricing.py, routing.py, signals.py, metrics.py). |
| `java/src/main/java/dev/plainround/router/domain/Stats.java` | Small statistics, written to give the same numbers as the Python port. |
| `java/src/main/java/dev/plainround/router/domain/Tasks.java` | The tasks the router serves, the policy text, and the refund arithmetic (a port of tasks.py). |
| `java/src/main/java/dev/plainround/router/infrastructure/DataFiles.java` | Reads the same data and configuration files as the Python port. |
| `java/src/main/java/dev/plainround/router/infrastructure/FilePrompts.java` | Prompt templates from versioned files; the trailing newlines are removed, as in the Python port. |
| `java/src/main/java/dev/plainround/router/infrastructure/RecordedChatModel.java` | Replays the same JSONL fixtures as the Python recorded adapter; an unknown request is an error. |
| `java/src/main/java/dev/plainround/router/infrastructure/SpringAiChatModel.java` | * The live adapter: Spring AI's ChatClient pointed at an OpenAI-compatible endpoint (a local ollama or llama.cpp server, or a hosted provider). |
| `java/src/main/java/dev/plainround/router/interfaces/Main.java` | Runs steps 1 to 6 on the same data, prompts and fixtures as Python and writes router.json, day.json and audit.json. |

### The value types

`java/src/main/java/dev/plainround/router/domain/Llm.java`

```java
package dev.plainround.router.domain;
```

Every Java file starts with its **package**: the folder-like name of the group the class belongs to. It matches the folder path under `src/main/java`. The names `domain`, `application`, `infrastructure`, `interfaces` are the same four layers as in the Python half.

```java
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;
import java.util.List;
import java.util.Locale;
import java.util.Set;
```

**Imports** make classes from other packages usable by their short names. `java.security.MessageDigest` computes hashes, `HexFormat` writes bytes as hexadecimal, `Locale` fixes number formatting, `List` and `Set` are collections.

```java
/** Value types for talking to a chat model. Nothing here knows a vendor, an SDK or HTTP. */
public final class Llm {
```

A `/** ... */` comment is **Javadoc**, documentation that tools read. `public final class Llm` is a class that cannot be subclassed (`final`) and is visible everywhere (`public`). The class is only a namespace for the types inside it.

```java
    private Llm() {}
```

A private empty constructor: nobody can create an `Llm` object, because the class only groups static members.

```java
    /** A failure of a model call. */
    public static class ModelException extends RuntimeException {
        public ModelException(String message) {
            super(message);
        }
    }
```

A nested class that extends `RuntimeException` (an **unchecked** exception: the compiler does not force callers to catch it). `super(message)` passes the text to the parent constructor.

```java
    /** The recorded adapter has no response for this exact request. */
    public static final class FixtureMissException extends ModelException {
        public FixtureMissException(String message) {
            super(message);
        }
    }
```

`FixtureMissException` extends `ModelException`; as in the Python half, a missing recording is its own kind of failure.

```java
    private static final Set<String> ROLES = Set.of("system", "user", "assistant");
```

`static final` is a constant. `Set.of(...)` creates an immutable set. `Set<String>` is a **generic** type: a set whose elements are strings.

```java
    /** One chat message. */
    public record Message(String role, String content) {
        public Message {
            if (!ROLES.contains(role)) {
                throw new IllegalArgumentException("unknown role " + role);
            }
        }
    }
```

A **record** is a short way to declare an immutable data class: the header `(String role, String content)` declares two private final fields, a constructor, getters named `role()` and `content()`, and `equals`/`hashCode`/`toString`. The block in braces without parameters is a **compact constructor**: it runs before the fields are assigned, so it can reject a bad role by throwing `IllegalArgumentException`.

```java
    /** Everything that decides a model's answer. */
    public record ChatRequest(String model, List<Message> messages, double temperature, int maxTokens, Integer seed) {
        public ChatRequest {
            if (model == null || model.isEmpty()) {
                throw new IllegalArgumentException("model must not be empty");
            }
            if (messages.isEmpty()) {
                throw new IllegalArgumentException("a request needs at least one message");
            }
            if (temperature < 0.0 || temperature > 2.0) {
                throw new IllegalArgumentException("temperature must be between 0 and 2");
            }
            if (maxTokens <= 0) {
                throw new IllegalArgumentException("max_tokens must be positive");
            }
            messages = List.copyOf(messages);
        }
```

The request record. `Integer seed` (capital I) is the boxed type that can be `null`; `int` cannot. The compact constructor validates every field like the Python `__post_init__` and then copies the list with `List.copyOf` so nobody can change it later.

```java
        /** The same hash as the Python port, so both read one fixture file. */
        public String fixtureKey() {
            StringBuilder joined = new StringBuilder();
            joined.append(model).append('\u001e');
            joined.append(String.format(Locale.ROOT, "%.3f", temperature)).append('\u001e');
            joined.append(maxTokens).append('\u001e');
            joined.append(seed == null ? "-" : seed.toString());
            for (Message m : messages) {
                joined.append('\u001e').append(m.role()).append('\u001f').append(m.content());
            }
            try {
                byte[] digest = MessageDigest.getInstance("SHA-256").digest(joined.toString().getBytes(StandardCharsets.UTF_8));
                return HexFormat.of().formatHex(digest);
            } catch (NoSuchAlgorithmException e) {
                throw new IllegalStateException(e);
            }
        }
    }
```

`fixtureKey` builds the same text as the Python method (`sha-256.md`): the model, then the temperature formatted with exactly three decimals (`Locale.ROOT` avoids a decimal comma on some systems), the maximum tokens, the seed or `-`, and each message with the separator characters `\u001e` (record separator) and `\u001f` (unit separator). Then `MessageDigest.getInstance("SHA-256")` hashes the UTF-8 bytes and `HexFormat.of().formatHex(...)` writes them as hex. The checked exception `NoSuchAlgorithmException` cannot really happen for SHA-256, so it is wrapped in an unchecked one.

```java
    /** Billed token counts. */
    public record Usage(int inputTokens, int outputTokens) {
        public int total() {
            return inputTokens + outputTokens;
        }
    }
```

A record with a computed method `total()`.

```java
    /** A completed call. */
    public record ChatResponse(String text, Usage usage, String model, String finishReason, double latencySeconds) {}
```

The response record: a one-line record with an empty body `{}`.

```java
    /** The one port the application needs from a model. */
    public interface ChatModel {
        ChatResponse complete(ChatRequest request);
    }
}
```

An **interface** lists methods without bodies. `ChatModel` is the one thing the application needs from a model; the recorded adapter and the Spring AI adapter both `implements` it.

## Try it yourself

1. `java -version` prints `openjdk version "21...` (Java 21 is what the build needs).
2. `cd java && ./mvnw -q -B -DskipTests package` compiles and builds the jar under `java/target/` (the first run downloads Maven and the libraries).
3. `ls java/target/*.jar` lists the built jar.
4. `cd java && ./mvnw -q -B test` runs the tests and prints a `Tests run: N, Failures: 0` summary (or nothing in `-q` mode when all pass).
5. `javap -cp java/target/classes -p dev.plainround.router.domain.Llm` (adapt the class name to a class listed above) prints the members of a compiled class.

## Mistakes people make

- **Comparing strings with `==`.** Use `.equals(...)`; `==` compares object identity.
- **Integer division**: `1 / 2` is `0`. Write `1 / 2.0`.
- **`NullPointerException`** from a boxed type (`Integer`) that is `null`.
- **Formatting numbers with the default locale**, which can print `0,500` instead of `0.500`; `Locale.ROOT` avoids it.
- **Mutating a list that another class holds**; records plus `List.copyOf` prevent it.

## Check yourself

1. **What does `javac` produce?**  
   Bytecode in `.class` files, which the JVM runs.
2. **What is a record?**  
   A compact immutable data class with generated constructor, getters, `equals`, `hashCode` and `toString`.
3. **What is the difference between `int` and `Integer`?**  
   `int` is a primitive and cannot be null; `Integer` is an object and can be null.
4. **Why do Java files start with `package`?**  
   It gives the class its address, which must match its folder.
5. **Why is `RuntimeException` convenient?**  
   It is unchecked, so methods need not declare or catch it.

## Further reading

The Java Language Specification: https://docs.oracle.com/javase/specs/jls/se21/html/index.html . Java SE 21 API: https://docs.oracle.com/en/java/javase/21/docs/api/ . Tutorials: https://dev.java/learn/
