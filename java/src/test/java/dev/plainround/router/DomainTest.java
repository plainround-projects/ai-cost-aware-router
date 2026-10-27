package dev.plainround.router;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.plainround.router.domain.Checks;
import dev.plainround.router.domain.Llm.ChatRequest;
import dev.plainround.router.domain.Llm.Message;
import dev.plainround.router.domain.Routing;
import dev.plainround.router.domain.Routing.CheckRates;
import dev.plainround.router.domain.Routing.DayBudget;
import dev.plainround.router.domain.Stats;
import dev.plainround.router.domain.Tasks;
import dev.plainround.router.domain.Tasks.Kind;
import dev.plainround.router.domain.Tasks.RefundOrder;
import dev.plainround.router.domain.Tasks.Task;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

/** The domain behaves exactly like the Python port; reference values were printed by Python. */
class DomainTest {

    private static Task refundTask(String text, RefundOrder... orders) {
        return new Task("t", Kind.REFUND, "easy", "test", text, 0, List.of(orders));
    }

    @Test
    void fixtureKeysEqualThePythonKeys() {
        ChatRequest full = new ChatRequest("m", List.of(new Message("system", "sys é"), new Message("user", "hi")), 0.7, 50, 3);
        assertEquals("a9ac1dcf4c0607c0fe3ef520314f34301f1b7abe8c1c3847e43d884143adb4f5", full.fixtureKey());
    }

    @Test
    void shuffleMatchesPython() {
        assertEquals(List.of(1, 9, 8, 6, 7, 2, 0, 5, 4, 3), java.util.stream.IntStream.of(Stats.shuffledIndices(10, 11)).boxed().toList());
    }

    @Test
    void refundRulesFollowThePolicy() {
        assertEquals(5000, Tasks.refundCents(new RefundOrder("o", 5000, 10, 5000, false)));
        assertEquals(4000, Tasks.refundCents(new RefundOrder("o", 5000, 20, 5000, false)));
        assertEquals(0, Tasks.refundCents(new RefundOrder("o", 5000, 31, 5000, false)));
        assertEquals(2500, Tasks.refundCents(new RefundOrder("o", 5000, 20, 2500, true)));
        assertEquals(1000, Tasks.refundCents(new RefundOrder("o", 5000, 16, 1250, false)));
    }

    @Test
    void answersAreParsedLikePython() {
        assertEquals("billing", Checks.parseLabel(" Billing. "));
        assertEquals("shipping", Checks.parseLabel("\"shipping\""));
        assertNull(Checks.parseLabel("customer support"));
        assertEquals(4000, Checks.parseAmountCents("$40.00"));
        assertEquals(1200, Checks.parseAmountCents("12"));
        assertEquals(123450, Checks.parseAmountCents("1,234.5"));
        assertEquals(4000, Checks.parseAmountCents("Worked out: 50 - 10 = 40\nRefund: 40.00"));
        assertEquals(725, Checks.parseAmountCents("Refund: $5.00 ... then\nRefund: $7.25"));
        assertNull(Checks.parseAmountCents("The refund is 40.00 dollars"));
        String reply = "Answer: yes\nQuote: \"" + Tasks.POLICY_LINES.get(2) + "\"\n\nQuestion: and then it kept going";
        assertEquals(2, Checks.quotedLineIndex(reply));
        assertNull(Checks.quotedLineIndex("no quote at all"));
        assertTrue(Checks.checkPolicy(reply));
        assertTrue(Checks.checkLabelAgreement("billing", "Billing."));
        assertFalse(Checks.checkLabelAgreement("billing", "returns"));
    }

    @Test
    void gradingAndTheRefundCheckUseTheRecomputedAmount() {
        Task task = refundTask("Order PR-100001 arrived 20 days ago.", new RefundOrder("PR-100001", 5000, 20, 5000, false));
        assertTrue(Checks.isCorrect(task, "40.00"));
        assertFalse(Checks.checkRefund(task, "50.00"));
    }

    @Test
    void theHardSignalSeesTwoOrdersOrAnExceptionWord() {
        assertTrue(Routing.hardSignal(refundTask("Order PR-100001 and PR-200002 are returned.")));
        assertTrue(Routing.hardSignal(refundTask("The item was damaged.")));
        assertFalse(Routing.hardSignal(refundTask("I was charged twice for PR-100001.")));
    }

    @Test
    void checkRatesAndTheDayBudget() {
        CheckRates r = Routing.checkRates(List.of(true, true, false, true), List.of(true, false, true, false));
        assertEquals(1.0, r.falseAcceptRate());
        assertEquals(0.5, r.falseRejectRate());
        assertEquals(2.0 / 3.0, r.wrongAmongAccepted(), 1e-12);
        DayBudget day = new DayBudget(2.0);
        day.add(1.5);
        assertEquals(0.75, day.usedShare());
        assertThrows(IllegalArgumentException.class, () -> new DayBudget(0));
        assertThrows(IllegalArgumentException.class, () -> new Routing.PriceTable("x", Map.of("small", 1.0)));
        assertEquals(1.2, new Routing.PriceTable("x", Map.of("small", 1.0, "medium", 1.0, "large", 1.2)).cost("large", 1000), 1e-12);
    }
}
