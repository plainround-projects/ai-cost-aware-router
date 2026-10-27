package dev.plainround.router.interfaces;

import dev.plainround.router.application.AnswerChecks;
import dev.plainround.router.application.CostRouter;
import dev.plainround.router.application.Experiments;
import dev.plainround.router.application.Experiments.DayResult;
import dev.plainround.router.application.Experiments.Outcome;
import dev.plainround.router.application.Experiments.Summary;
import dev.plainround.router.application.ModelTiers;
import dev.plainround.router.application.ModelTiers.Answered;
import dev.plainround.router.domain.Llm.ChatModel;
import dev.plainround.router.domain.Routing;
import dev.plainround.router.domain.Routing.Bar;
import dev.plainround.router.domain.Routing.PriceTable;
import dev.plainround.router.domain.Routing.Rate;
import dev.plainround.router.domain.Routing.RouterConfig;
import dev.plainround.router.domain.Tasks.Task;
import dev.plainround.router.infrastructure.DataFiles;
import dev.plainround.router.infrastructure.FilePrompts;
import dev.plainround.router.infrastructure.RecordedChatModel;
import dev.plainround.router.infrastructure.SpringAiChatModel;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import tools.jackson.databind.SerializationFeature;
import tools.jackson.databind.json.JsonMapper;

/** Runs steps 1 to 6 on the same data, prompts and fixtures as Python and writes router.json, day.json and audit.json. */
public final class Main {

    private Main() {}

    public static void main(String[] args) throws Exception {
        Map<String, String> flags = new LinkedHashMap<>();
        for (int i = 0; i + 1 < args.length; i += 2) {
            flags.put(args[i].replaceFirst("^--", ""), args[i + 1]);
        }
        Path data = Path.of(flags.getOrDefault("data", "data"));
        Path configDir = Path.of(flags.getOrDefault("config", "config"));
        Path out = Path.of(flags.getOrDefault("out", "reports/java"));
        ChatModel model = "recorded".equals(env("LLM_PROVIDER", "recorded"))
                ? new RecordedChatModel(Path.of(flags.getOrDefault("fixtures", "tests/fixtures")))
                : new SpringAiChatModel(env("LLM_BASE_URL", "http://localhost:11434/v1"), env("OPENAI_API_KEY", ""));
        Map<String, String> models = Map.of("small", env("TIER_SMALL", "qwen2.5:0.5b"), "medium", env("TIER_MEDIUM", "llama3.2:1b"), "large", env("TIER_LARGE", "qwen2.5:1.5b"));
        PriceTable prices = DataFiles.loadPrices(configDir);
        Bar bar = DataFiles.loadBar(configDir);
        ModelTiers tiers = new ModelTiers(model, new FilePrompts(Path.of(flags.getOrDefault("prompts", "prompts"))), models, prices);
        List<Task> tasks = DataFiles.loadTasks(data);
        List<Task> build = tasks.stream().filter(t -> t.split().equals("build")).toList();
        List<Task> test = tasks.stream().filter(t -> t.split().equals("test")).toList();

        Map<String, Map<String, Answered>> answers = Experiments.collectAnswers(tasks, tiers);
        var rates = Experiments.checkResults(build, answers, tiers);
        RouterConfig config = Experiments.tune(build, answers, rates, bar);
        RouterConfig noBar = Experiments.tune(build, answers, rates, new Bar(1.0, bar.hardAccuracyBar(), bar.accuracyMargin(), bar.requestCap(), bar.tightenAt(), bar.dayBudgetFractions()));

        List<Outcome> outcomes = Experiments.routeAll(test, router(tiers, config), null);
        Map<String, Summary> methods = new LinkedHashMap<>();
        methods.put("router", Experiments.summarize(outcomes));
        methods.put("router_no_bar", Experiments.summarize(Experiments.routeAll(test, router(tiers, noBar), null)));
        for (String tier : Routing.TIERS) {
            methods.put(tier, Experiments.singleModelSummary(test, answers, tier));
        }
        Map<String, Object> byKind = new LinkedHashMap<>();
        for (String kind : Experiments.KINDS) {
            List<Outcome> subset = outcomes.stream().filter(o -> o.kind().equals(kind)).toList();
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("n", subset.size());
            m.put("accuracy", (double) subset.stream().filter(Outcome::correct).count() / subset.size());
            m.put("cost", subset.stream().mapToDouble(o -> o.decision().spent()).sum());
            byKind.put(kind, m);
        }
        Map<String, Object> router = new LinkedHashMap<>();
        router.put("config", configJson(config));
        router.put("config_no_bar", configJson(noBar));
        Map<String, Object> methodJson = new LinkedHashMap<>();
        methods.forEach((k, v) -> methodJson.put(k, summaryJson(v)));
        router.put("methods", methodJson);
        router.put("by_kind", byKind);
        router.put("verdict", Experiments.compareToLarge(test, answers, outcomes, bar));

        List<Object> days = new ArrayList<>();
        for (double fraction : bar.dayBudgetFractions()) {
            days.add(dayJson(Experiments.runDay(test, answers, () -> router(tiers, config), fraction, 11)));
        }
        Map<String, Object> day = new LinkedHashMap<>();
        day.put("days", days);

        Map<String, Object> before = Experiments.falseAccepts(outcomes, config);
        String kind = Experiments.weakestKind(outcomes);
        Map<String, Object> change = null;
        if (kind != null) {
            Experiments.Hardened hardened = Experiments.harden(config, kind);
            RouterConfig changed = hardened.config();
            List<Outcome> after = Experiments.routeAll(test, router(tiers, changed), null);
            Summary a = Experiments.summarize(outcomes);
            Summary b = Experiments.summarize(after);
            change = new LinkedHashMap<>();
            change.put("kind", kind);
            change.put("description", hardened.description());
            change.put("config_after", configJson(changed));
            change.put("accuracy_before", a.accuracy().value());
            change.put("accuracy_after", b.accuracy().value());
            change.put("cost_per_correct_before", a.costPerCorrect());
            change.put("cost_per_correct_after", b.costPerCorrect());
            change.put("false_accepts_before", before.get("false_accepts"));
            change.put("false_accepts_after", Experiments.falseAccepts(after, changed).get("false_accepts"));
        }
        Map<String, Object> audit = new LinkedHashMap<>();
        audit.put("before", before);
        audit.put("change", change);

        Files.createDirectories(out);
        JsonMapper json = JsonMapper.builder().enable(SerializationFeature.INDENT_OUTPUT).enable(SerializationFeature.ORDER_MAP_ENTRIES_BY_KEYS).build();
        Files.writeString(out.resolve("router.json"), json.writeValueAsString(router) + "\n", StandardCharsets.UTF_8);
        Files.writeString(out.resolve("day.json"), json.writeValueAsString(day) + "\n", StandardCharsets.UTF_8);
        Files.writeString(out.resolve("audit.json"), json.writeValueAsString(audit) + "\n", StandardCharsets.UTF_8);
        System.out.println("java: router accuracy " + methods.get("router").accuracy().value() + "; wrote " + out);
    }

    private static CostRouter router(ModelTiers tiers, RouterConfig config) {
        return new CostRouter(tiers, new AnswerChecks(tiers, config.labelCheck(), config.policyCheck()), config);
    }

    private static String env(String name, String fallback) {
        String value = System.getenv(name);
        return value == null || value.isBlank() ? fallback : value;
    }

    private static Map<String, Object> configJson(RouterConfig c) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("start", c.start());
        m.put("hard_start", c.hardStart());
        m.put("label_check", c.labelCheck());
        m.put("policy_check", c.policyCheck());
        m.put("request_cap", c.requestCap());
        m.put("tighten_at", c.tightenAt());
        return m;
    }

    private static Object finite(double v) {
        return Double.isInfinite(v) ? null : v;
    }

    private static Map<String, Object> rateJson(Rate r) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("successes", r.successes());
        m.put("trials", r.trials());
        m.put("value", r.value());
        m.put("low", r.low());
        m.put("high", r.high());
        return m;
    }

    private static Map<String, Object> summaryJson(Summary s) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("n", s.n());
        m.put("accuracy", rateJson(s.accuracy()));
        m.put("total_cost", s.totalCost());
        m.put("cost_per_correct", s.costPerCorrect());
        List<Object> interval = new ArrayList<>();
        interval.add(finite(s.costPerCorrectInterval()[0]));
        interval.add(finite(s.costPerCorrectInterval()[1]));
        m.put("cost_per_correct_interval", interval);
        m.put("served_by", s.servedBy());
        m.put("escalated", s.escalated());
        m.put("max_request_spend", s.maxRequestSpend());
        return m;
    }

    private static Map<String, Object> dayJson(DayResult d) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("fraction", d.fraction());
        m.put("budget", d.budget());
        m.put("spent", d.spent());
        m.put("under_budget", d.underBudget());
        m.put("requests_over_cap", d.requestsOverCap());
        m.put("crossed_at", d.crossedAt());
        m.put("accuracy_before", rateJson(d.accuracyBefore()));
        m.put("accuracy_after", rateJson(d.accuracyAfter()));
        m.put("large_served_after", d.largeServedAfter());
        m.put("outcomes", List.of());
        return m;
    }
}
