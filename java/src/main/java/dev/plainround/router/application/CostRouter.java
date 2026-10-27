package dev.plainround.router.application;

import dev.plainround.router.application.AnswerChecks.CheckResult;
import dev.plainround.router.application.ModelTiers.Answered;
import dev.plainround.router.domain.Routing;
import dev.plainround.router.domain.Routing.Attempt;
import dev.plainround.router.domain.Routing.DayBudget;
import dev.plainround.router.domain.Routing.Decision;
import dev.plainround.router.domain.Routing.RouterConfig;
import dev.plainround.router.domain.Tasks.Task;
import java.util.ArrayList;
import java.util.List;

/** Cheapest tier first, a check after every answer, escalation on a failed check (a port of router.py). */
public final class CostRouter {

    public static final String ESCALATE = "escalate_to_person";

    private final ModelTiers tiers;
    private final AnswerChecks checks;
    private final RouterConfig config;

    public CostRouter(ModelTiers tiers, AnswerChecks checks, RouterConfig config) {
        this.tiers = tiers;
        this.checks = checks;
        this.config = config;
    }

    public RouterConfig config() {
        return config;
    }

    public Decision route(Task task, DayBudget day) {
        double share = day != null ? day.usedShare() : 0.0;
        List<String> all = Routing.TIERS;
        List<String> allowed = day != null && share >= config.tightenAt() ? all.subList(0, all.size() - 1) : all;
        int start = config.startIndex(task.kind().value(), Routing.hardSignal(task));
        double limit = day == null ? config.requestCap() : Math.min(config.requestCap(), day.budget() - day.used());
        double spent = 0.0;
        int tokens = 0;
        List<Attempt> attempts = new ArrayList<>();
        List<String> tags = new ArrayList<>();
        for (String tier : allowed.subList(Math.min(start, allowed.size()), allowed.size())) {
            double projected = spent + tiers.estimate(tier, task, 1) + checks.estimateExtra(task, tier);
            if (projected > limit) {
                tags.add(limit == config.requestCap() ? "cap" : "budget");
                break;
            }
            Answered answered = tiers.call(tier, task, false);
            CheckResult result = checks.check(task, tier, answered.text());
            double callCost = answered.cost() + result.extraCost();
            spent += callCost;
            tokens += answered.tokens() + result.extraTokens();
            attempts.add(new Attempt(tier, result.passed(), callCost, answered.tokens() + result.extraTokens()));
            if (result.passed()) {
                if (day != null) {
                    day.add(spent);
                }
                return new Decision(task.taskId(), answered.text(), tier, attempts, spent, tokens, share, tags);
            }
        }
        if (day != null) {
            day.add(spent);
        }
        return new Decision(task.taskId(), null, ESCALATE, attempts, spent, tokens, share, tags);
    }
}
