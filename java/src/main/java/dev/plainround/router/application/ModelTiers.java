package dev.plainround.router.application;

import dev.plainround.router.domain.Llm.ChatModel;
import dev.plainround.router.domain.Llm.ChatRequest;
import dev.plainround.router.domain.Llm.ChatResponse;
import dev.plainround.router.domain.Llm.Message;
import dev.plainround.router.domain.Routing.PriceTable;
import dev.plainround.router.domain.Tasks;
import dev.plainround.router.domain.Tasks.Kind;
import dev.plainround.router.domain.Tasks.Task;
import java.util.List;
import java.util.Map;

/** The three model tiers: prompts, calls and cost (a port of tiers.py). */
public final class ModelTiers {

    public record Answered(String text, double cost, int tokens, double latency) {}

    private static int maxTokens(Kind kind) {
        return kind == Kind.LABEL ? 8 : 80;
    }

    private final ChatModel model;
    private final PromptStore prompts;
    private final Map<String, String> models;
    private final PriceTable prices;

    public ModelTiers(ChatModel model, PromptStore prompts, Map<String, String> models, PriceTable prices) {
        this.model = model;
        this.prompts = prompts;
        this.models = models;
        this.prices = prices;
    }

    public String prompt(Task task) {
        switch (task.kind()) {
            case LABEL:
                return Templates.render(prompts.get("label.v2"), Map.of("text", task.text()));
            case REFUND:
                return Templates.render(prompts.get("refund.v2"), Map.of("policy", Tasks.REFUND_POLICY, "text", task.text()));
            default:
                StringBuilder lines = new StringBuilder();
                for (int i = 0; i < Tasks.POLICY_LINES.size(); i++) {
                    if (i > 0) {
                        lines.append('\n');
                    }
                    lines.append(i + 1).append(". ").append(Tasks.POLICY_LINES.get(i));
                }
                return Templates.render(prompts.get("policy.v2"), Map.of("policy_lines", lines.toString(), "text", task.text()));
        }
    }

    public ChatRequest request(String tier, Task task, boolean secondSample) {
        double temperature = secondSample ? 0.8 : 0.0;
        Integer seed = secondSample ? 7 : null;
        return new ChatRequest(models.get(tier), List.of(new Message("user", prompt(task))), temperature, maxTokens(task.kind()), seed);
    }

    public Answered call(String tier, Task task, boolean secondSample) {
        ChatResponse response = model.complete(request(tier, task, secondSample));
        return new Answered(response.text().strip(), prices.cost(tier, response.usage().total()), response.usage().total(), response.latencySeconds());
    }

    public double estimate(String tier, Task task, int calls) {
        int tokens = (prompt(task).length() + 2) / 3 + maxTokens(task.kind());
        return prices.estimate(tier, tokens) * calls;
    }
}
