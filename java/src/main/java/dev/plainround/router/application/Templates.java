package dev.plainround.router.application;

import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** Prompt templates use {{name}} placeholders; rendering fails loudly on a missing value. */
public final class Templates {

    private Templates() {}

    private static final Pattern PLACEHOLDER = Pattern.compile("\\{\\{([a-z_]+)\\}\\}");

    public static String render(String template, Map<String, String> values) {
        Matcher unknownCheck = PLACEHOLDER.matcher(template);
        java.util.Set<String> present = new java.util.HashSet<>();
        while (unknownCheck.find()) {
            present.add(unknownCheck.group(1));
        }
        for (String name : values.keySet()) {
            if (!present.contains(name)) {
                throw new IllegalArgumentException("template has no placeholder for " + name);
            }
        }
        Matcher m = PLACEHOLDER.matcher(template);
        StringBuilder out = new StringBuilder();
        while (m.find()) {
            String value = values.get(m.group(1));
            if (value == null) {
                throw new IllegalArgumentException("no value for placeholder {{" + m.group(1) + "}}");
            }
            m.appendReplacement(out, Matcher.quoteReplacement(value));
        }
        m.appendTail(out);
        return out.toString();
    }

    /** Render with only the values the template actually uses. */
    public static String renderAvailable(String template, Map<String, String> values) {
        Map<String, String> used = new java.util.LinkedHashMap<>();
        for (Map.Entry<String, String> e : values.entrySet()) {
            if (template.contains("{{" + e.getKey() + "}}")) {
                used.put(e.getKey(), e.getValue());
            }
        }
        return render(template, used);
    }
}
