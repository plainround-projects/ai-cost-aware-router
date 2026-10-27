package dev.plainround.router.domain;

import java.util.List;
import java.util.Map;

/** Pricing, router configuration, the daily budget, signals and metrics (ports of pricing.py, routing.py, signals.py, metrics.py). */
public final class Routing {

    private Routing() {}

    public static final List<String> TIERS = List.of("small", "medium", "large");

    public record Bar(double falseAcceptBar, double hardAccuracyBar, double accuracyMargin, double requestCap, double tightenAt, List<Double> dayBudgetFractions) {}

    public record PriceTable(String asOf, Map<String, Double> per1kTokens) {
        public PriceTable {
            for (String tier : TIERS) {
                if (!per1kTokens.containsKey(tier)) {
                    throw new IllegalArgumentException("price table lacks tier " + tier);
                }
            }
        }

        public double cost(String tier, int totalTokens) {
            return totalTokens / 1000.0 * per1kTokens.get(tier);
        }

        public double estimate(String tier, int tokens) {
            return tokens / 1000.0 * per1kTokens.get(tier);
        }
    }

    public record RouterConfig(Map<String, String> start, Map<String, String> hardStart, String labelCheck, double requestCap, double tightenAt, String policyCheck) {
        public int startIndex(String kind, boolean hard) {
            String tier = hard && hardStart.get(kind) != null && !hardStart.get(kind).isEmpty() ? hardStart.get(kind) : start.get(kind);
            return TIERS.indexOf(tier);
        }
    }

    public static final class DayBudget {
        private final double budget;
        private double used;

        public DayBudget(double budget) {
            if (budget <= 0) {
                throw new IllegalArgumentException("a budget must be positive");
            }
            this.budget = budget;
        }

        public double budget() {
            return budget;
        }

        public double used() {
            return used;
        }

        public double usedShare() {
            return used / budget;
        }

        public void add(double amount) {
            used += amount;
        }
    }

    public record Attempt(String tier, boolean passed, double cost, int tokens) {}

    public record Decision(String taskId, String answer, String servedBy, List<Attempt> attempts, double spent, int tokens, double shareBefore, List<String> tags) {}

    public static boolean hardSignal(Tasks.Task task) {
        String lowered = task.text().toLowerCase();
        java.util.Set<String> ids = new java.util.HashSet<>();
        java.util.regex.Matcher m = Tasks.ORDER_ID.matcher(task.text());
        while (m.find()) {
            ids.add(m.group());
        }
        return ids.size() >= 2 || Tasks.EXCEPTION_WORDS.stream().anyMatch(lowered::contains);
    }

    public record Rate(int successes, int trials, double value, double low, double high) {}

    public static Rate rate(int successes, int trials) {
        Stats.Interval w = Stats.wilson(successes, trials);
        return new Rate(successes, trials, trials == 0 ? 0.0 : (double) successes / trials, w.low(), w.high());
    }

    public static Double costPerCorrect(double totalCost, int correct) {
        return correct == 0 ? null : totalCost / correct;
    }

    public static double[] bootstrapCostPerCorrect(List<Double> costs, List<Boolean> corrects) {
        int n = costs.size();
        if (n == 0) {
            return new double[] {0.0, 0.0};
        }
        int resamples = 2000;
        Stats.SplitMix64 rng = new Stats.SplitMix64(7);
        double[] values = new double[resamples];
        for (int r = 0; r < resamples; r++) {
            double total = 0.0;
            int right = 0;
            for (int k = 0; k < n; k++) {
                int i = rng.below(n);
                total += costs.get(i);
                right += corrects.get(i) ? 1 : 0;
            }
            values[r] = right == 0 ? Double.POSITIVE_INFINITY : total / right;
        }
        java.util.Arrays.sort(values);
        return new double[] {values[(int) (0.025 * resamples)], values[Math.min(resamples - 1, (int) (0.975 * resamples))]};
    }

    public static double[] bootstrapAccuracyDifference(List<Boolean> a, List<Boolean> b) {
        int n = a.size();
        if (n == 0) {
            return new double[] {0.0, 0.0, 0.0};
        }
        double[] diffs = new double[n];
        double sum = 0.0;
        for (int i = 0; i < n; i++) {
            diffs[i] = (a.get(i) ? 1.0 : 0.0) - (b.get(i) ? 1.0 : 0.0);
            sum += diffs[i];
        }
        int resamples = 2000;
        Stats.SplitMix64 rng = new Stats.SplitMix64(7);
        double[] means = new double[resamples];
        for (int r = 0; r < resamples; r++) {
            double total = 0.0;
            for (int k = 0; k < n; k++) {
                total += diffs[rng.below(n)];
            }
            means[r] = total / n;
        }
        java.util.Arrays.sort(means);
        return new double[] {sum / n, means[(int) (0.025 * resamples)], means[Math.min(resamples - 1, (int) (0.975 * resamples))]};
    }

    public record CheckRates(int accepted, int wrong, int right, int falseAccepts, int falseRejects, double falseAcceptRate, double falseRejectRate, double wrongAmongAccepted) {}

    public static CheckRates checkRates(List<Boolean> passed, List<Boolean> correct) {
        int accepted = 0;
        int wrong = 0;
        int falseAccepts = 0;
        int falseRejects = 0;
        for (int i = 0; i < passed.size(); i++) {
            boolean p = passed.get(i);
            boolean c = correct.get(i);
            accepted += p ? 1 : 0;
            wrong += c ? 0 : 1;
            falseAccepts += p && !c ? 1 : 0;
            falseRejects += !p && c ? 1 : 0;
        }
        int right = correct.size() - wrong;
        return new CheckRates(
                accepted,
                wrong,
                right,
                falseAccepts,
                falseRejects,
                wrong == 0 ? 0.0 : (double) falseAccepts / wrong,
                right == 0 ? 0.0 : (double) falseRejects / right,
                accepted == 0 ? 0.0 : (double) falseAccepts / accepted);
    }
}
