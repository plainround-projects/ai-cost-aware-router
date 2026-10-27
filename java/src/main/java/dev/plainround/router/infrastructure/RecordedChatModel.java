package dev.plainround.router.infrastructure;

import dev.plainround.router.domain.Llm.ChatModel;
import dev.plainround.router.domain.Llm.ChatRequest;
import dev.plainround.router.domain.Llm.ChatResponse;
import dev.plainround.router.domain.Llm.FixtureMissException;
import dev.plainround.router.domain.Llm.Usage;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Stream;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

/** Replays the same JSONL fixtures as the Python recorded adapter; an unknown request is an error. */
public final class RecordedChatModel implements ChatModel {

    private final Map<String, ChatResponse> responses = new HashMap<>();

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

    public int size() {
        return responses.size();
    }

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
