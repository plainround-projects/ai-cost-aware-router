package dev.plainround.router.domain;

import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;

/** The tasks the router serves, the policy text, and the refund arithmetic (a port of tasks.py). */
public final class Tasks {

    private Tasks() {}

    public static final List<String> LABELS = List.of("billing", "shipping", "returns", "account");

    public static final String REFUND_POLICY =
            "Refunds are 100% of the returned items' price for returns within 15 days of delivery, 80% from day 16 to "
                    + "day 30, and nothing after day 30. Damaged items are refunded 100% of their price within 30 days.";

    public static final List<String> POLICY_LINES = List.of(
            "Returns are accepted within 30 days of delivery.",
            "The customer pays return shipping unless the item arrived damaged or wrong.",
            "Refunds reach the original payment method within 5 business days after the returned item arrives.",
            "An exchange for another size or color is free within 30 days if the item is unopened.",
            "A damaged item is refunded in full, with a prepaid return label, within 30 days of delivery.",
            "Gift cards pay for items only; they cannot pay for shipping.",
            "Electronics have a warranty of 12 months from delivery.",
            "We match a lower price from another shop within 7 days of purchase.",
            "An order can be cancelled for free until it ships, normally within 2 hours of ordering.",
            "We never sell or share a customer's personal data with other companies.");

    public static final Pattern ORDER_ID = Pattern.compile("\\bPR-\\d{6}\\b");
    public static final List<String> EXCEPTION_WORDS = List.of("damaged", "broken", "exception", "only part", "partial");

    public enum Kind {
        LABEL("label"),
        REFUND("refund"),
        POLICY("policy");

        private final String value;

        Kind(String value) {
            this.value = value;
        }

        public String value() {
            return value;
        }

        public static Kind of(String value) {
            for (Kind k : values()) {
                if (k.value.equals(value)) {
                    return k;
                }
            }
            throw new IllegalArgumentException("unknown kind " + value);
        }
    }

    public record RefundOrder(String orderId, int totalCents, int days, int returnedCents, boolean damaged) {}

    /** gold is a String (label), an Integer (refund cents or policy line index). */
    public record Task(String taskId, Kind kind, String difficulty, String split, String text, Object gold, List<RefundOrder> orders) {}

    public static int refundCents(RefundOrder order) {
        if (order.days() > 30) {
            return 0;
        }
        if (order.damaged() || order.days() <= 15) {
            return order.returnedCents();
        }
        return (order.returnedCents() * 80 + 50) / 100;
    }

    public static int expectedRefundCents(Task task) {
        int sum = 0;
        for (RefundOrder o : task.orders()) {
            sum += refundCents(o);
        }
        return sum;
    }

    public static Map<String, Integer> noCounts() {
        return Map.of();
    }
}
