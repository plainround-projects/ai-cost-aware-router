# Spring AI 2.0.1 (on Spring Boot 4.0.5)

## What it is

**Spring** is the most widely used application framework for Java. **Spring AI** is its module for calling AI models: a `ChatClient` offers a fluent way to write a prompt, set options, call a model and read the reply, independent of the vendor. Different **model** classes (OpenAI-compatible, Anthropic, Ollama and others) plug in underneath.

## Why this repository uses it

The lessons ask for the Java half to use Spring AI, to show that the same experiment can be done with the framework a Java team would use. Here it is used in the smallest way: only as the adapter that sends a request to an OpenAI-compatible server, so ollama and llama.cpp work without changes. No Spring Boot application is started.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `java/src/main/java/dev/plainround/router/infrastructure/SpringAiChatModel.java` | The adapter. |
| `java/pom.xml` | Imports the Spring AI BOM and two modules: `spring-ai-openai` and `spring-ai-client-chat`. |


## How it works underneath

`ChatClient.builder(model).build()` wraps a `ChatModel` (an implementation that knows one provider's HTTP protocol). A call such as `client.prompt().messages(...).options(...).call()` assembles a `Prompt`, passes it to the model, which makes the HTTP request (`/chat/completions`) and parses the reply into a `ChatResponse` with a list of results and metadata, including token usage. `.stream()` instead returns a reactive stream (Project Reactor's `Flux`) of partial responses. Options such as `temperature`, `maxTokens` and `seed` are provider-specific and live on `OpenAiChatOptions`. Because the OpenAI protocol is copied by many servers, pointing `baseUrl` at `http://localhost:11434` (ollama) or `llama-server` is enough.

The library is used here through its **BOM** (`maven.md`): one version number, 2.0.1, selects matching versions of all its modules.

## Walkthrough of this repository's use

`java/src/main/java/dev/plainround/router/infrastructure/SpringAiChatModel.java`

```java
package dev.plainround.router.infrastructure;
```

Package and imports. Note what is imported from the domain (the project's own `ChatModel` interface and request/response records) and what from Spring AI: `ChatClient`, `OpenAiChatModel`, `OpenAiChatOptions`.

```java
import dev.plainround.router.domain.Llm.ChatModel;
import dev.plainround.router.domain.Llm.ChatRequest;
import dev.plainround.router.domain.Llm.ChatResponse;
import dev.plainround.router.domain.Llm.Message;
import dev.plainround.router.domain.Llm.ModelException;
import dev.plainround.router.domain.Llm.Usage;
```

The domain types this adapter translates to and from.

```java
import java.util.ArrayList;
import java.util.List;
```

Collections.

```java
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.openai.OpenAiChatModel;
import org.springframework.ai.openai.OpenAiChatOptions;
```

Spring AI: `ChatClient` is its high-level, fluent chat interface; `OpenAiChatModel` is the model implementation for any OpenAI-compatible HTTP server; `OpenAiChatOptions` holds settings.

```java
/**
 * The live adapter: Spring AI's ChatClient pointed at an OpenAI-compatible endpoint (a local ollama or llama.cpp
 * server, or a hosted provider). The domain never sees Spring AI; only this class does.
 */
```

Javadoc: the live adapter. **Only this class sees Spring AI**; ArchUnit enforces that (`archunit.md`).

```java
public final class SpringAiChatModel implements ChatModel {

    private final ChatClient client;
```

The class implements the domain interface `ChatModel`, so the application can use it like the recorded adapter.

```java
    public SpringAiChatModel(String baseUrl, String apiKey) {
        String root = baseUrl.endsWith("/v1") ? baseUrl.substring(0, baseUrl.length() - 3) : baseUrl;
        OpenAiChatModel model = OpenAiChatModel.builder()
                .options(OpenAiChatOptions.builder().baseUrl(root).apiKey(apiKey == null || apiKey.isBlank() ? "none" : apiKey).build())
                .build();
        this.client = ChatClient.builder(model).build();
    }
```

The constructor builds the client once. The code cuts a trailing `/v1` from the base address, on the assumption that the library adds `/v1/chat/completions` itself. **Caution:** the Spring AI 2.0 reference describes the OpenAI base URL as including `/v1` (the library adds only `/chat/completions`), and the serve and gateway adapters of this track keep the `/v1`. The Java half of this repository runs on recorded data in its checks, so this live path has not been exercised here; treat it as unverified. The API key is replaced by the placeholder `none` when empty, because the library insists on a value; ollama ignores it. `OpenAiChatModel.builder().options(...).build()` is the **builder pattern**: set options step by step, then build.

```java
    @Override
    public ChatResponse complete(ChatRequest request) {
```

`@Override` marks that this method implements the interface's method; the compiler checks the signature.

```java
        long started = System.nanoTime();
        List<org.springframework.ai.chat.messages.Message> messages = new ArrayList<>();
        for (Message m : request.messages()) {
            messages.add(switch (m.role()) {
                case "system" -> new org.springframework.ai.chat.messages.SystemMessage(m.content());
                case "assistant" -> new org.springframework.ai.chat.messages.AssistantMessage(m.content());
                default -> new org.springframework.ai.chat.messages.UserMessage(m.content());
            });
        }
```

Starts a stopwatch with `System.nanoTime()` and converts each domain message to the matching Spring AI message type with a `switch` **expression**: `system`, `assistant`, anything else `user`.

```java
        OpenAiChatOptions.Builder options = OpenAiChatOptions.builder()
                .model(request.model())
                .temperature(request.temperature())
                .maxTokens(request.maxTokens());
        if (request.seed() != null) {
            options.seed(request.seed());
        }
```

Per-call options: model, temperature, maximum tokens, and the seed if there is one.

```java
        try {
            org.springframework.ai.chat.client.ChatClientResponse response =
                    client.prompt().messages(messages).options(options).call().chatClientResponse();
            org.springframework.ai.chat.model.ChatResponse chat = response.chatResponse();
            String text = chat.getResult().getOutput().getText();
            var usage = chat.getMetadata().getUsage();
            return new ChatResponse(
                    text == null ? "" : text,
                    new Usage(usage.getPromptTokens() == null ? 0 : usage.getPromptTokens(), usage.getCompletionTokens() == null ? 0 : usage.getCompletionTokens()),
                    request.model(),
                    "stop",
                    (System.nanoTime() - started) / 1e9);
```

The call: `client.prompt().messages(messages).options(options).call().chatClientResponse()` sends the request and waits (a blocking call). The text is the first result's output; the usage holds the token counts, which may be `null`, hence the checks. The result is converted back to the domain's `ChatResponse` with the measured latency in seconds (`/ 1e9` converts nanoseconds).

```java
        } catch (RuntimeException e) {
            throw new ModelException("model call failed: " + e.getClass().getSimpleName());
        }
    }
}
```

Any runtime failure becomes the domain's `ModelException`, with only the exception class name, so no vendor type leaks upward.

## Try it yourself

1. `cd java && ./mvnw -q -B dependency:tree | grep spring-ai` lists the two Spring AI modules and the ones they pull in.
2. `grep -rn "org.springframework" java/src/main --include=*.java | cut -d: -f1 | sort -u` shows that only the adapter file imports Spring.
3. With ollama running, `make parity` (or the repository's Java command from the README) runs the Java side on the recorded data; it needs no model server.
4. `cd java && ./mvnw -q -B test -Dtest=ArchitectureTest` proves that the rest of the code stays free of Spring.

## Mistakes people make

- **Letting Spring AI types leak into the domain**: you then cannot test or replace it. The ArchUnit rules prevent it.
- **Forgetting that Spring AI appends the path** and doubling `/v1` or `/chat/completions`.
- **Counting every streamed chunk as a token**: header chunks and the usage chunk carry no text.
- **Letting hidden retries multiply**: the gateway switches the library's retries off and retries once, in its own router.
- **Treating token usage as always present**: it can be `null` for some servers.

## Check yourself

1. **What does `ChatClient` do?**  
   It gives a fluent API to build a prompt, set options, call a model and read the reply.
2. **Why is Spring AI confined to one class?**  
   So that the domain and application stay vendor-free and testable; ArchUnit enforces it.
3. **What does `.stream()` return?**  
   A reactive stream of partial responses, one per chunk.
4. **Does the base address given to Spring AI include `/v1`?**  
   In the Spring AI 2.0 reference it does, and the library appends `/chat/completions`; check the adapter of your repository against its server before relying on the live path.
5. **What is a BOM?**  
   A list of matching library versions imported once, so modules need no version.

## Further reading

Spring AI reference: https://docs.spring.io/spring-ai/reference/ (ChatClient API, OpenAI chat). Pinned: Spring AI 2.0.1, Spring Boot 4.0.5 BOM.
