package dev.plainround.router.domain;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;
import java.util.List;
import java.util.Locale;
import java.util.Set;

/** Value types for talking to a chat model. Nothing here knows a vendor, an SDK or HTTP. */
public final class Llm {

    private Llm() {}

    /** A failure of a model call. */
    public static class ModelException extends RuntimeException {
        public ModelException(String message) {
            super(message);
        }
    }

    /** The recorded adapter has no response for this exact request. */
    public static final class FixtureMissException extends ModelException {
        public FixtureMissException(String message) {
            super(message);
        }
    }

    private static final Set<String> ROLES = Set.of("system", "user", "assistant");

    /** One chat message. */
    public record Message(String role, String content) {
        public Message {
            if (!ROLES.contains(role)) {
                throw new IllegalArgumentException("unknown role " + role);
            }
        }
    }

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

    /** Billed token counts. */
    public record Usage(int inputTokens, int outputTokens) {
        public int total() {
            return inputTokens + outputTokens;
        }
    }

    /** A completed call. */
    public record ChatResponse(String text, Usage usage, String model, String finishReason, double latencySeconds) {}

    /** The one port the application needs from a model. */
    public interface ChatModel {
        ChatResponse complete(ChatRequest request);
    }
}
