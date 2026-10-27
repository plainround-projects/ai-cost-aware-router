package dev.plainround.router.application;

import dev.plainround.router.application.ModelTiers.Answered;
import dev.plainround.router.domain.Checks;
import dev.plainround.router.domain.Tasks.Kind;
import dev.plainround.router.domain.Tasks.Task;

/** The checks the router runs on an answer; no gold answer is visible to them (a port of answer_checks.py). */
public final class AnswerChecks {

    public record CheckResult(boolean passed, double extraCost, int extraTokens) {}

    private final ModelTiers tiers;
    private final String labelCheck;
    private final String policyCheck;

    public AnswerChecks(ModelTiers tiers, String labelCheck, String policyCheck) {
        this.tiers = tiers;
        this.labelCheck = labelCheck;
        this.policyCheck = policyCheck;
    }

    public CheckResult check(Task task, String tier, String text) {
        if (task.kind() == Kind.REFUND) {
            return new CheckResult(Checks.checkRefund(task, text), 0.0, 0);
        }
        if (task.kind() == Kind.POLICY) {
            boolean passed = policyCheck.equals("overlap") ? Checks.checkPolicyOverlap(task.text(), text) : Checks.checkPolicy(text);
            return new CheckResult(passed, 0.0, 0);
        }
        if (labelCheck.equals("shape")) {
            return new CheckResult(Checks.checkLabelShape(text), 0.0, 0);
        }
        Answered second = tiers.call(tier, task, true);
        return new CheckResult(Checks.checkLabelAgreement(text, second.text()), second.cost(), second.tokens());
    }

    public double estimateExtra(Task task, String tier) {
        return task.kind() == Kind.LABEL && labelCheck.equals("agreement") ? tiers.estimate(tier, task, 1) : 0.0;
    }
}
