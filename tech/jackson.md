# Jackson 3 (tools.jackson)

## What it is

**Jackson** is the standard Java library for reading and writing JSON. **Jackson 3** is the current major version; its classes are in the package `tools.jackson` (version 2 used `com.fasterxml.jackson`). The central idea: parse text into a *tree* of nodes (`JsonNode`) that you can walk, or map JSON straight to Java objects. This repository uses the tree.

## Why this repository uses it

The Java half must read exactly the files the Python half wrote: the JSONL recordings, the data sets, the agreed numbers and the gateway's configuration. Jackson parses them, and the parity tests then write JSON back and compare it with the Python reports.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `java/src/main/java/dev/plainround/router/infrastructure/RecordedChatModel.java` | Reads the recorded fixtures. |
| `java/src/main/java/dev/plainround/router/infrastructure/DataFiles.java` | Reads data sets. |
| `java/src/main/java/dev/plainround/router/interfaces/Main.java` | Reads agreed numbers and writes reports. |
| `java/src/test/java/dev/plainround/router/ParityTest.java` | Compares JSON trees. |
| `java/pom.xml` | Jackson arrives with the Spring Boot BOM. |


## How it works underneath

A JSON parser reads the characters and creates one node per value: an *object node* (named children), an *array node* (indexed children), or a leaf (text, number, boolean, null). `readTree(text)` returns the root node. `node.get("name")` returns the child (or `null` if missing, which is why code calls `has(...)` when a field is optional); `asString()`, `asInt()`, `asDouble()` convert a leaf; nodes can be looped over like lists. `JsonMapper` is the configured, thread-safe reader/writer; it is created once and reused. Jackson 3 made the mapper immutable, so settings go through `JsonMapper.builder()...build()`.

## Walkthrough of this repository's use

`java/src/main/java/dev/plainround/router/infrastructure/RecordedChatModel.java`

```java
package dev.plainround.router.infrastructure;

import dev.plainround.router.domain.Llm.ChatModel;
import dev.plainround.router.domain.Llm.ChatRequest;
import dev.plainround.router.domain.Llm.ChatResponse;
import dev.plainround.router.domain.Llm.FixtureMissException;
import dev.plainround.router.domain.Llm.Usage;
```

Package, then imports. The Jackson ones live in the package **`tools.jackson`**: Jackson 3 moved from `com.fasterxml.jackson` to `tools.jackson` (only the annotations kept the old name).

```java
import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Stream;
```

Standard-library imports: files, charsets, collections and streams.

```java
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;
```

`JsonNode` is a node of a parsed JSON tree; `JsonMapper` reads and writes JSON.

```java
/** Replays the same JSONL fixtures as the Python recorded adapter; an unknown request is an error. */
```

Javadoc: replays the same JSONL fixtures as the Python adapter.

```java
public final class RecordedChatModel implements ChatModel {

    private final Map<String, ChatResponse> responses = new HashMap<>();
```

The replaying adapter, implementing the domain's `ChatModel` interface. It keeps a map from the SHA-256 key to the recorded response.

```java
    public RecordedChatModel(Path fixtures) {
        JsonMapper json = JsonMapper.builder().build();
        try (Stream<Path> files = Files.isDirectory(fixtures) ? Files.list(fixtures) : Stream.of(fixtures)) {
            for (Path file : files.filter(p -> p.toString().endsWith(".jsonl")).sorted().toList()) {
                List<String> lines = Files.readAllLines(file, StandardCharsets.UTF_8);
                for (String line : lines) {
                    if (line.isBlank()) {
                        continue;
                    }
                    JsonNode row = json.readTree(line);
                    JsonNode r = row.get("response");
                    responses.put(
                            row.get("key").asString(),
                            new ChatResponse(
                                    r.get("text").asString(),
                                    new Usage(r.get("input_tokens").asInt(), r.get("output_tokens").asInt()),
                                    r.get("model").asString(),
                                    r.has("finish_reason") ? r.get("finish_reason").asString() : "stop",
                                    r.has("latency_s") ? r.get("latency_s").asDouble() : 0.0));
                }
            }
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }
```

`JsonMapper.builder().build()` makes a reader with default settings. `try (Stream<Path> files = ...)` is **try-with-resources**: the stream is closed at the end. Either every file in the folder or the one file is read; only `*.jsonl` files, sorted by name so the order is fixed. Each non-blank line is parsed with `readTree(line)` into a tree; `row.get("key")` picks a field and `.asString()` reads it as text (Jackson 3 calls this method `asString()`; Jackson 2 called it `asText()`), `.asInt()` and `.asDouble()` read numbers. `r.has("finish_reason")` checks whether a field exists. An `IOException` is wrapped in the unchecked `UncheckedIOException`.

```java
    public int size() {
        return responses.size();
    }
```

The number of recorded responses.

```java
    @Override
    public ChatResponse complete(ChatRequest request) {
        ChatResponse found = responses.get(request.fixtureKey());
        if (found == null) {
            throw new FixtureMissException("no recorded response for model=" + request.model() + " key="
                    + request.fixtureKey().substring(0, 12) + " (" + request.messages().size() + " messages)");
        }
        return found;
    }
}
```

`complete` looks up `request.fixtureKey()` (`sha-256.md`) and returns the stored response. If there is none it throws `FixtureMissException` with the first 12 characters of the key, exactly like the Python adapter.

## Try it yourself

1. `cd java && ./mvnw -q -B dependency:tree | grep jackson` lists the Jackson modules in the tree (`tools.jackson.core`, `tools.jackson.databind`).
2. `grep -rn "tools.jackson" java/src --include=*.java | cut -d: -f1 | sort -u` lists the files that use it.
3. `grep -rn "asText()" java/src --include=*.java | wc -l` prints `0`: this code uses `asString()`.
4. Break a key name in a test fixture copy and run the Java tests: a `NullPointerException` at the `get(...)` call shows what a missing field does.

## Mistakes people make

- **Calling `get("x")` on a missing field** and using the result: it is `null`. Check with `has` first.
- **Using Jackson 2 names** (`com.fasterxml.jackson.databind`, `asText`) from old examples.
- **Creating a mapper per call.** Create one and reuse it.
- **Reading big numbers as `int`.** Use `asLong` or `asDouble` when needed.

## Check yourself

1. **What package holds Jackson 3's databind classes?**  
   `tools.jackson.databind`.
2. **What does `readTree` return?**  
   The root `JsonNode` of the parsed JSON.
3. **What does `get("x")` return when the field is missing?**  
   `null`.
4. **Which method reads a leaf as text in Jackson 3?**  
   `asString()`.
5. **How is the mapper configured in Jackson 3?**  
   Through `JsonMapper.builder()...build()`; the result is immutable.

## Further reading

Jackson 3 repository and release notes: https://github.com/FasterXML/jackson (Jackson 3 migration guide) . Pinned by the Spring Boot BOM 4.0.5 (`java/pom.xml`).
