package dev.plainround.router.domain;

import dev.plainround.router.domain.Tasks.Kind;
import dev.plainround.router.domain.Tasks.Task;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** Parsing answers, grading them against the truth, and the checks the router can run (a port of checks.py). */
public final class Checks {

    private Checks() {}

    private static final String NUMBER = "\\$?\\s*(\\d{1,3}(?:,\\d{3})+|\\d+)(?:\\.(\\d{1,2}))?";
    private static final Pattern REFUND_LINE = Pattern.compile("refund\\s*:\\s*" + NUMBER, Pattern.CASE_INSENSITIVE);
    private static final Pattern BARE_AMOUNT = Pattern.compile(NUMBER);
    private static final Pattern QUOTE = Pattern.compile("quote\\s*:\\s*[\"“']?(.+?)[\"”']?\\s*$", Pattern.CASE_INSENSITIVE | Pattern.MULTILINE);

    public static String normalize(String text) {
        String joined = String.join(" ", text.toLowerCase().strip().split("\\s+"));
        int end = joined.length();
        while (end > 0 && joined.charAt(end - 1) == '.') {
            end--;
        }
        return joined.substring(0, end).strip();
    }

    private static String stripChars(String text, String chars) {
        int start = 0;
        int end = text.length();
        while (start < end && chars.indexOf(text.charAt(start)) >= 0) {
            start++;
        }
        while (end > start && chars.indexOf(text.charAt(end - 1)) >= 0) {
            end--;
        }
        return text.substring(start, end);
    }

    public static String parseLabel(String text) {
        String word = stripChars(normalize(text), "\"'`*");
        return Tasks.LABELS.contains(word) ? word : null;
    }

    private static int cents(Matcher m) {
        int dollars = Integer.parseInt(m.group(1).replace(",", ""));
        String fraction = ((m.group(2) == null ? "" : m.group(2)) + "00").substring(0, 2);
        return dollars * 100 + Integer.parseInt(fraction);
    }

    public static Integer parseAmountCents(String text) {
        Matcher m = REFUND_LINE.matcher(text);
        Integer last = null;
        while (m.find()) {
            last = cents(m);
        }
        if (last != null) {
            return last;
        }
        Matcher bare = BARE_AMOUNT.matcher(text.strip());
        return bare.matches() ? cents(bare) : null;
    }

    public static String parseQuote(String text) {
        Matcher m = QUOTE.matcher(text);
        return m.find() ? normalize(m.group(1)) : null;
    }

    public static Integer quotedLineIndex(String text) {
        String quote = parseQuote(text);
        if (quote == null) {
            return null;
        }
        for (int i = 0; i < Tasks.POLICY_LINES.size(); i++) {
            if (normalize(Tasks.POLICY_LINES.get(i)).equals(quote)) {
                return i;
            }
        }
        return null;
    }

    public static boolean isCorrect(Task task, String text) {
        if (task.kind() == Kind.LABEL) {
            String label = parseLabel(text);
            return label != null && label.equals(task.gold());
        }
        if (task.kind() == Kind.REFUND) {
            Integer amount = parseAmountCents(text);
            return amount != null && amount == Tasks.expectedRefundCents(task);
        }
        Integer index = quotedLineIndex(text);
        return index != null && index.equals(task.gold());
    }

    public static boolean checkLabelShape(String text) {
        return parseLabel(text) != null;
    }

    public static boolean checkLabelAgreement(String text, String second) {
        String first = parseLabel(text);
        return first != null && first.equals(parseLabel(second));
    }

    public static boolean checkRefund(Task task, String text) {
        Integer amount = parseAmountCents(text);
        return amount != null && amount == Tasks.expectedRefundCents(task);
    }

    private static final java.util.Set<String> STOPWORDS = java.util.Set.of(
            "a", "an", "the", "of", "to", "in", "on", "for", "is", "are", "be", "do", "does", "can", "i", "my", "me",
            "you", "your", "we", "our", "it", "its", "if", "or", "and", "at", "by", "from", "with", "as", "how", "what",
            "when", "who", "which", "that", "this", "there", "than", "then");
    private static final Pattern WORD = Pattern.compile("[a-z0-9]+");

    public static java.util.Set<String> contentWords(String text) {
        java.util.Set<String> words = new java.util.HashSet<>();
        Matcher m = WORD.matcher(text.toLowerCase());
        while (m.find()) {
            String w = m.group();
            if (STOPWORDS.contains(w)) {
                continue;
            }
            words.add(w.length() > 3 && w.endsWith("s") ? w.substring(0, w.length() - 1) : w);
        }
        return words;
    }

    /** The policy line sharing the most content words with the question, or null when two lines tie for most. */
    public static Integer bestMatchingLine(String question) {
        java.util.Set<String> words = contentWords(question);
        int top = 0;
        int count = 0;
        int index = -1;
        for (int i = 0; i < Tasks.POLICY_LINES.size(); i++) {
            java.util.Set<String> overlap = new java.util.HashSet<>(contentWords(Tasks.POLICY_LINES.get(i)));
            overlap.retainAll(words);
            int score = overlap.size();
            if (score > top) {
                top = score;
                count = 1;
                index = i;
            } else if (score == top) {
                count++;
            }
        }
        return top > 0 && count == 1 ? index : null;
    }

    public static boolean checkPolicyOverlap(String question, String text) {
        Integer quoted = quotedLineIndex(text);
        return quoted != null && quoted.equals(bestMatchingLine(question));
    }

    public static boolean checkPolicy(String text) {
        return quotedLineIndex(text) != null;
    }

    public static List<String> noItems() {
        return new ArrayList<>();
    }
}
