package dev.plainround.router.infrastructure;

import dev.plainround.router.domain.Llm.ChatModel;
import dev.plainround.router.domain.Llm.ChatRequest;
import dev.plainround.router.domain.Llm.ChatResponse;
import dev.plainround.router.domain.Llm.Message;
import dev.plainround.router.domain.Llm.ModelException;
import dev.plainround.router.domain.Llm.Usage;
import java.util.ArrayList;
import java.util.List;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.openai.OpenAiChatModel;
import org.springframework.ai.openai.OpenAiChatOptions;

/**
 * The live adapter: Spring AI's ChatClient pointed at an OpenAI-compatible endpoint (a local ollama or llama.cpp
 * server, or a hosted provider). The domain never sees Spring AI; only this class does.
 */
public final class SpringAiChatModel implements ChatModel {

    private final ChatClient client;

    public SpringAiChatModel(String baseUrl, String apiKey) {
        String root = baseUrl.endsWith("/v1") ? baseUrl.substring(0, baseUrl.length() - 3) : baseUrl;
        OpenAiChatModel model = OpenAiChatModel.builder()
                .options(OpenAiChatOptions.builder().baseUrl(root).apiKey(apiKey == null || apiKey.isBlank() ? "none" : apiKey).build())
                .build();
        this.client = ChatClient.builder(model).build();
    }

    @Override
    public ChatResponse complete(ChatRequest request) {
        long started = System.nanoTime();
        List<org.springframework.ai.chat.messages.Message> messages = new ArrayList<>();
        for (Message m : request.messages()) {
            messages.add(switch (m.role()) {
                case "system" -> new org.springframework.ai.chat.messages.SystemMessage(m.content());
                case "assistant" -> new org.springframework.ai.chat.messages.AssistantMessage(m.content());
                default -> new org.springframework.ai.chat.messages.UserMessage(m.content());
            });
        }
        OpenAiChatOptions.Builder options = OpenAiChatOptions.builder()
                .model(request.model())
                .temperature(request.temperature())
                .maxTokens(request.maxTokens());
        if (request.seed() != null) {
            options.seed(request.seed());
        }
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
        } catch (RuntimeException e) {
            throw new ModelException("model call failed: " + e.getClass().getSimpleName());
        }
    }
}
