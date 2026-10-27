package dev.plainround.router.domain;

import java.util.Arrays;
import java.util.List;

/** Small statistics, written to give the same numbers as the Python port. */
public final class Stats {

    private Stats() {}

    /** SplitMix64: the same arithmetic as the Python generator, so bootstrap intervals match. */
    public static final class SplitMix64 {
        private long state;

        public SplitMix64(long seed) {
            this.state = seed;
        }

        public long nextU64() {
            state += 0x9E3779B97F4A7C15L;
            long z = state;
            z = (z ^ (z >>> 30)) * 0xBF58476D1CE4E5B9L;
            z = (z ^ (z >>> 27)) * 0x94D049BB133111EBL;
            return z ^ (z >>> 31);
        }

        public int below(int bound) {
            if (bound <= 0) {
                throw new IllegalArgumentException("bound must be positive");
            }
            return (int) Long.remainderUnsigned(nextU64(), bound);
        }
    }

    public record Interval(double low, double high) {}

    public record PairedDifference(double mean, Interval interval) {}

    public static double mean(List<Double> values) {
        if (values.isEmpty()) {
            return 0.0;
        }
        double sum = 0.0;
        for (double v : values) {
            sum += v;
        }
        return sum / values.size();
    }

    public static Interval wilson(int successes, int trials) {
        if (trials <= 0) {
            return new Interval(0.0, 1.0);
        }
        double z = 1.96;
        double p = (double) successes / trials;
        double denominator = 1 + z * z / trials;
        double centre = (p + z * z / (2 * trials)) / denominator;
        double margin = z * Math.sqrt(p * (1 - p) / trials + z * z / (4.0 * trials * trials)) / denominator;
        return new Interval(Math.max(0.0, centre - margin), Math.min(1.0, centre + margin));
    }

    public static Interval bootstrapMeanInterval(List<Double> values, int resamples, long seed) {
        if (values.isEmpty()) {
            return new Interval(0.0, 0.0);
        }
        SplitMix64 rng = new SplitMix64(seed);
        int n = values.size();
        double[] means = new double[resamples];
        for (int r = 0; r < resamples; r++) {
            double sum = 0.0;
            for (int i = 0; i < n; i++) {
                sum += values.get(rng.below(n));
            }
            means[r] = sum / n;
        }
        Arrays.sort(means);
        double tail = (1 - 0.95) / 2;
        return new Interval(means[(int) (tail * resamples)], means[Math.min(resamples - 1, (int) ((1 - tail) * resamples))]);
    }

    public static PairedDifference pairedBootstrapDifference(List<Double> treatment, List<Double> control, int resamples, long seed) {
        if (treatment.size() != control.size()) {
            throw new IllegalArgumentException("a paired comparison needs the same number of items on both sides");
        }
        java.util.ArrayList<Double> differences = new java.util.ArrayList<>();
        for (int i = 0; i < treatment.size(); i++) {
            differences.add(treatment.get(i) - control.get(i));
        }
        return new PairedDifference(mean(differences), bootstrapMeanInterval(differences, resamples, seed));
    }

    /** A seeded Fisher-Yates permutation of 0..n-1, the same as the Python port. */
    public static int[] shuffledIndices(int n, long seed) {
        SplitMix64 rng = new SplitMix64(seed);
        int[] order = new int[n];
        for (int i = 0; i < n; i++) {
            order[i] = i;
        }
        for (int i = n - 1; i > 0; i--) {
            int j = rng.below(i + 1);
            int t = order[i];
            order[i] = order[j];
            order[j] = t;
        }
        return order;
    }
}
