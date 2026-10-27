package dev.plainround.router.application;

import dev.plainround.router.application.ModelTiers.Answered;
import dev.plainround.router.domain.Checks;
import dev.plainround.router.domain.Routing;
import dev.plainround.router.domain.Routing.Bar;
import dev.plainround.router.domain.Routing.CheckRates;
import dev.plainround.router.domain.Routing.DayBudget;
import dev.plainround.router.domain.Routing.Decision;
import dev.plainround.router.domain.Routing.Rate;
import dev.plainround.router.domain.Routing.RouterConfig;
import dev.plainround.router.domain.Stats;
import dev.plainround.router.domain.Tasks.Kind;
import dev.plainround.router.domain.Tasks.Task;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.function.Supplier;

/** The lesson's steps as functions over the tier, check and router objects (a port of experiments.py). */
public final class Experiments {

    private Experiments() {}

    public static final List<String> KINDS = List.of("label", "refund", "policy");

    public static final Map<String, List<String>> CHECK_NAMES =
            Map.of("label", List.of("label_shape", "label_agreement"), "refund", List.of("refund_recompute"), "policy", List.of("policy_quote"));

    public record Outcome(Decision decision, String kind, String difficulty, boolean correct) {
        public boolean escalated() {
            return decision.servedBy().equals(CostRouter.ESCALATE);
        }
    }

    public record Summary(
            int n,
            Rate accuracy,
            double totalCost,
            Double costPerCorrect,
            double[] costPerCorrectInterval,
            Map<String, Integer> servedBy,
            int escalated,
            double maxRequestSpend) {}

    public record DayResult(
            double fraction,
            double budget,
            double spent,
            boolean underBudget,
            int requestsOverCap,
            Integer crossedAt,
            Rate accuracyBefore,
            Rate accuracyAfter,
            int largeServedAfter) {}

    public static Map<String, Map<String, Answered>> collectAnswers(List<Task> tasks, ModelTiers tiers) {
        Map<String, Map<String, Answered>> answers = new LinkedHashMap<>();
        for (String tier : Routing.TIERS) {
            Map<String, Answered> byTask = new LinkedHashMap<>();
            for (Task task : tasks) {
                byTask.put(task.taskId(), tiers.call(tier, task, false));
            }
            answers.put(tier, byTask);
        }
        return answers;
    }

    public static Map<String, Map<String, Map<String, CheckRates>>> checkResults(
            List<Task> tasks, Map<String, Map<String, Answered>> answers, ModelTiers tiers) {
        Map<String, Map<String, Map<String, CheckRates>>> out = new LinkedHashMap<>();
        for (String tier : Routing.TIERS) {
            Map<String, Map<String, CheckRates>> byKind = new LinkedHashMap<>();
            for (String kind : KINDS) {
                List<Task> subset = tasks.stream().filter(t -> t.kind().value().equals(kind)).toList();
                List<Boolean> correct = new ArrayList<>();
                List<String> texts = new ArrayList<>();
                for (Task t : subset) {
                    String text = answers.get(tier).get(t.taskId()).text();
                    texts.add(text);
                    correct.add(Checks.isCorrect(t, text));
                }
                Map<String, CheckRates> checks = new LinkedHashMap<>();
                if (kind.equals("label")) {
                    List<Boolean> shape = new ArrayList<>();
                    List<Boolean> agree = new ArrayList<>();
                    for (int i = 0; i < subset.size(); i++) {
                        shape.add(Checks.checkLabelShape(texts.get(i)));
                        String second = tiers.call(tier, subset.get(i), true).text();
                        agree.add(Checks.checkLabelAgreement(texts.get(i), second));
                    }
                    checks.put("label_shape", Routing.checkRates(shape, correct));
                    checks.put("label_agreement", Routing.checkRates(agree, correct));
                } else if (kind.equals("refund")) {
                    List<Boolean> passed = new ArrayList<>();
                    for (int i = 0; i < subset.size(); i++) {
                        passed.add(Checks.checkRefund(subset.get(i), texts.get(i)));
                    }
                    checks.put("refund_recompute", Routing.checkRates(passed, correct));
                } else {
                    List<Boolean> passed = texts.stream().map(Checks::checkPolicy).toList();
                    checks.put("policy_quote", Routing.checkRates(passed, correct));
                }
                byKind.put(kind, checks);
            }
            out.put(tier, byKind);
        }
        return out;
    }

    public static RouterConfig tune(
            List<Task> buildTasks,
            Map<String, Map<String, Answered>> answers,
            Map<String, Map<String, Map<String, CheckRates>>> rates,
            Bar bar) {
        Map<String, String> start = new LinkedHashMap<>();
        Map<String, String> hardStart = new LinkedHashMap<>();
        for (String kind : KINDS) {
            List<String> names = CHECK_NAMES.get(kind);
            String checkName = names.get(names.size() - 1);
            String chosen = Routing.TIERS.get(Routing.TIERS.size() - 1);
            for (String tier : Routing.TIERS) {
                if (rates.get(tier).get(kind).get(checkName).falseAcceptRate() <= bar.falseAcceptBar()) {
                    chosen = tier;
                    break;
                }
            }
            start.put(kind, chosen);
            int index = Routing.TIERS.indexOf(chosen);
            List<Task> signalled = buildTasks.stream().filter(t -> t.kind().value().equals(kind) && Routing.hardSignal(t)).toList();
            if (index < Routing.TIERS.size() - 1 && signalled.size() >= 5) {
                long right = signalled.stream().filter(t -> Checks.isCorrect(t, answers.get(start.get(kind)).get(t.taskId()).text())).count();
                if ((double) right / signalled.size() < bar.hardAccuracyBar()) {
                    hardStart.put(kind, Routing.TIERS.get(index + 1));
                }
            }
        }
        return new RouterConfig(start, hardStart, "agreement", bar.requestCap(), bar.tightenAt(), "quote");
    }

    public static List<Outcome> routeAll(List<Task> tasks, CostRouter router, DayBudget day) {
        List<Outcome> outcomes = new ArrayList<>();
        for (Task task : tasks) {
            Decision decision = router.route(task, day);
            boolean correct = decision.answer() != null && Checks.isCorrect(task, decision.answer());
            outcomes.add(new Outcome(decision, task.kind().value(), task.difficulty(), correct));
        }
        return outcomes;
    }

    public static Summary summarize(List<Outcome> outcomes) {
        List<Boolean> correct = outcomes.stream().map(Outcome::correct).toList();
        List<Double> costs = outcomes.stream().map(o -> o.decision().spent()).toList();
        Map<String, Integer> shares = new TreeMap<>();
        for (Outcome o : outcomes) {
            shares.merge(o.decision().servedBy(), 1, Integer::sum);
        }
        double total = 0.0;
        double max = 0.0;
        for (double c : costs) {
            total += c;
            max = Math.max(max, c);
        }
        int right = (int) correct.stream().filter(c -> c).count();
        return new Summary(
                outcomes.size(),
                Routing.rate(right, correct.size()),
                total,
                Routing.costPerCorrect(total, right),
                Routing.bootstrapCostPerCorrect(costs, correct),
                shares,
                (int) outcomes.stream().filter(Outcome::escalated).count(),
                max);
    }

    public static Summary singleModelSummary(List<Task> tasks, Map<String, Map<String, Answered>> answers, String tier) {
        List<Boolean> correct = new ArrayList<>();
        List<Double> costs = new ArrayList<>();
        double total = 0.0;
        double max = 0.0;
        for (Task t : tasks) {
            Answered a = answers.get(tier).get(t.taskId());
            correct.add(Checks.isCorrect(t, a.text()));
            costs.add(a.cost());
            total += a.cost();
            max = Math.max(max, a.cost());
        }
        int right = (int) correct.stream().filter(c -> c).count();
        Map<String, Integer> served = new TreeMap<>();
        served.put(tier, tasks.size());
        return new Summary(tasks.size(), Routing.rate(right, correct.size()), total, Routing.costPerCorrect(total, right), Routing.bootstrapCostPerCorrect(costs, correct), served, 0, max);
    }

    public static Map<String, Object> compareToLarge(List<Task> tasks, Map<String, Map<String, Answered>> answers, List<Outcome> outcomes, Bar bar) {
        Summary router = summarize(outcomes);
        Summary large = singleModelSummary(tasks, answers, "large");
        List<Boolean> routerCorrect = outcomes.stream().map(Outcome::correct).toList();
        List<Boolean> largeCorrect = tasks.stream().map(t -> Checks.isCorrect(t, answers.get("large").get(t.taskId()).text())).toList();
        double[] diff = Routing.bootstrapAccuracyDifference(routerCorrect, largeCorrect);
        boolean matched = router.accuracy().value() >= large.accuracy().value() - bar.accuracyMargin();
        boolean cheaper = router.costPerCorrect() != null && large.costPerCorrect() != null && router.costPerCorrect() < large.costPerCorrect();
        Map<String, Object> verdict = new LinkedHashMap<>();
        verdict.put("accuracy_difference_vs_large", diff[0]);
        verdict.put("accuracy_difference_interval", List.of(diff[1], diff[2]));
        verdict.put("margin", bar.accuracyMargin());
        verdict.put("matched_within_margin", matched);
        verdict.put("cheaper_per_correct", cheaper);
        verdict.put("verdict", matched && cheaper ? "matched" : (cheaper ? "cheaper but less accurate" : "not cheaper"));
        return verdict;
    }

    public static DayResult runDay(List<Task> tasks, Map<String, Map<String, Answered>> answers, Supplier<CostRouter> routerFactory, double fraction, long seed) {
        int[] order = Stats.shuffledIndices(tasks.size(), seed);
        List<Task> ordered = new ArrayList<>();
        for (int i : order) {
            ordered.add(tasks.get(i));
        }
        double largeCost = 0.0;
        for (Task t : tasks) {
            largeCost += answers.get("large").get(t.taskId()).cost();
        }
        DayBudget day = new DayBudget(largeCost * fraction);
        CostRouter router = routerFactory.get();
        List<Outcome> outcomes = routeAll(ordered, router, day);
        Integer crossed = null;
        for (int i = 0; i < outcomes.size(); i++) {
            if (outcomes.get(i).decision().shareBefore() >= router.config().tightenAt()) {
                crossed = i;
                break;
            }
        }
        List<Outcome> before = crossed != null ? outcomes.subList(0, crossed) : outcomes;
        List<Outcome> after = crossed != null ? outcomes.subList(crossed, outcomes.size()) : List.of();
        double cap = router.config().requestCap();
        int over = (int) outcomes.stream().filter(o -> o.decision().spent() > cap).count();
        int largeAfter = (int) after.stream().filter(o -> o.decision().servedBy().equals("large")).count();
        return new DayResult(
                fraction,
                day.budget(),
                day.used(),
                day.used() <= day.budget(),
                over,
                crossed,
                Routing.rate((int) before.stream().filter(Outcome::correct).count(), before.size()),
                Routing.rate((int) after.stream().filter(Outcome::correct).count(), after.size()),
                largeAfter);
    }

    public static String checkName(String kind, RouterConfig config) {
        if (kind.equals("label")) {
            return "label_" + config.labelCheck();
        }
        return kind.equals("refund") ? "refund_recompute" : "policy_" + config.policyCheck();
    }

    public static Map<String, Object> falseAccepts(List<Outcome> outcomes, RouterConfig config) {
        Map<String, List<String>> grouped = new TreeMap<>();
        int wrong = 0;
        for (Outcome o : outcomes) {
            if (o.decision().answer() == null || o.correct()) {
                continue;
            }
            wrong++;
            grouped.computeIfAbsent(o.decision().servedBy() + "/" + checkName(o.kind(), config), k -> new ArrayList<>()).add(o.decision().taskId());
        }
        Map<String, Integer> byTier = new TreeMap<>();
        Map<String, Object> detail = new LinkedHashMap<>();
        for (Map.Entry<String, List<String>> e : grouped.entrySet()) {
            String tier = e.getKey().split("/")[0];
            byTier.merge(tier, e.getValue().size(), Integer::sum);
            Map<String, Object> d = new LinkedHashMap<>();
            d.put("count", e.getValue().size());
            d.put("tasks", e.getValue());
            detail.put(e.getKey(), d);
        }
        Map<String, Object> out = new LinkedHashMap<>();
        out.put("false_accepts", wrong);
        out.put("by_tier_and_check", detail);
        out.put("by_tier", byTier);
        return out;
    }

    public record Hardened(RouterConfig config, String description) {}

    /** The one change step 6 makes: start one tier higher, or run a stronger check when already at the top tier. */
    public static Hardened harden(RouterConfig config, String kind) {
        int index = Routing.TIERS.indexOf(config.start().get(kind));
        if (index < Routing.TIERS.size() - 1) {
            Map<String, String> start = new LinkedHashMap<>(config.start());
            start.put(kind, Routing.TIERS.get(index + 1));
            Map<String, String> hard = new LinkedHashMap<>();
            for (Map.Entry<String, String> e : config.hardStart().entrySet()) {
                if (!e.getKey().equals(kind) || Routing.TIERS.indexOf(e.getValue()) > index + 1) {
                    hard.put(e.getKey(), e.getValue());
                }
            }
            return new Hardened(
                    new RouterConfig(start, hard, config.labelCheck(), config.requestCap(), config.tightenAt(), config.policyCheck()),
                    kind + " tasks start at " + Routing.TIERS.get(index + 1) + " instead of " + Routing.TIERS.get(index));
        }
        if (kind.equals("policy")) {
            return new Hardened(
                    new RouterConfig(config.start(), config.hardStart(), config.labelCheck(), config.requestCap(), config.tightenAt(), "overlap"),
                    "policy answers must quote the line that best matches the question, not just any line");
        }
        return new Hardened(config, kind + " already starts at the top tier and has no stronger check; nothing changed");
    }

    public static String weakestKind(List<Outcome> outcomes) {
        Map<String, Integer> counts = new TreeMap<>();
        for (Outcome o : outcomes) {
            if (o.decision().answer() != null && !o.correct()) {
                counts.merge(o.kind(), 1, Integer::sum);
            }
        }
        String best = null;
        for (Map.Entry<String, Integer> e : counts.entrySet()) {
            if (best == null || e.getValue() > counts.get(best)) {
                best = e.getKey();
            }
        }
        return best;
    }

    public static boolean isLabelKind(Kind kind) {
        return kind == Kind.LABEL;
    }
}
