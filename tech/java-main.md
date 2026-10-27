# Java code: the main classes, file by file

## What it is

These are all the Java classes of the program, not counting tests. They are the same four layers as the Python half: `domain`, `application`, `infrastructure` and `interfaces`. `java.md` introduces the language; this note reads each class.

## Why this repository uses it

Reading the second implementation next to the first shows what stays the same when the language changes (the layers, the rules, the numbers) and what the language adds (types, records, interfaces).

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `java/src/main/java/dev/plainround/router/application/AnswerChecks.java` | Quoted and explained in the walkthrough below. |
| `java/src/main/java/dev/plainround/router/application/CostRouter.java` | Quoted and explained in the walkthrough below. |
| `java/src/main/java/dev/plainround/router/application/Experiments.java` | Quoted and explained in the walkthrough below. |
| `java/src/main/java/dev/plainround/router/application/ModelTiers.java` | Quoted and explained in the walkthrough below. |
| `java/src/main/java/dev/plainround/router/application/PromptStore.java` | Quoted and explained in the walkthrough below. |
| `java/src/main/java/dev/plainround/router/application/Templates.java` | Quoted and explained in the walkthrough below. |
| `java/src/main/java/dev/plainround/router/domain/Checks.java` | Quoted and explained in the walkthrough below. |
| `java/src/main/java/dev/plainround/router/domain/Llm.java` | Quoted and explained in the walkthrough below. |
| `java/src/main/java/dev/plainround/router/domain/Routing.java` | Quoted and explained in the walkthrough below. |
| `java/src/main/java/dev/plainround/router/domain/Stats.java` | Quoted and explained in the walkthrough below. |
| `java/src/main/java/dev/plainround/router/domain/Tasks.java` | Quoted and explained in the walkthrough below. |
| `java/src/main/java/dev/plainround/router/infrastructure/DataFiles.java` | Quoted and explained in the walkthrough below. |
| `... 4 more files` | All files are listed in the first table of the walkthrough. |


## How it works underneath

A Java program is a set of classes in packages. `Main.main(String[] args)` is where the JVM starts. Classes call each other through interfaces defined in the inner layers; the adapters implement them. Everything is compiled by `javac` before it runs, so a wrong type is an error at build time (`maven.md`).

## Walkthrough of this repository's use

### Files in this note

| File | Lines | What it is |
| --- | --- | --- |
| `java/src/main/java/dev/plainround/router/application/AnswerChecks.java` | 41 | The checks the router runs on an answer; no gold answer is visible to them (a port of answer_checks.py). |
| `java/src/main/java/dev/plainround/router/application/CostRouter.java` | 67 | Cheapest tier first, a check after every answer, escalation on a failed check (a port of router.py). |
| `java/src/main/java/dev/plainround/router/application/Experiments.java` | 330 | The lesson's steps as functions over the tier, check and router objects (a port of experiments.py). |
| `java/src/main/java/dev/plainround/router/application/ModelTiers.java` | 68 | The three model tiers: prompts, calls and cost (a port of tiers.py). |
| `java/src/main/java/dev/plainround/router/application/PromptStore.java` | 6 | Versioned prompt templates looked up by name such as label.v2. |
| `java/src/main/java/dev/plainround/router/application/Templates.java` | 48 | Prompt templates use {{name}} placeholders; rendering fails loudly on a missing value. |
| `java/src/main/java/dev/plainround/router/domain/Checks.java` | 162 | Parsing answers, grading them against the truth, and the checks the router can run (a port of checks.py). |
| `java/src/main/java/dev/plainround/router/domain/Llm.java` | 92 | Value types for talking to a chat model. |
| `java/src/main/java/dev/plainround/router/domain/Routing.java` | 166 | Pricing, router configuration, the daily budget, signals and metrics (ports of pricing.py, routing.py, signals.py, metrics.py). |
| `java/src/main/java/dev/plainround/router/domain/Stats.java` | 107 | Small statistics, written to give the same numbers as the Python port. |
| `java/src/main/java/dev/plainround/router/domain/Tasks.java` | 84 | The tasks the router serves, the policy text, and the refund arithmetic (a port of tasks.py). |
| `java/src/main/java/dev/plainround/router/infrastructure/DataFiles.java` | 89 | Reads the same data and configuration files as the Python port. |
| `java/src/main/java/dev/plainround/router/infrastructure/FilePrompts.java` | 36 | Prompt templates from versioned files; the trailing newlines are removed, as in the Python port. |
| `java/src/main/java/dev/plainround/router/infrastructure/RecordedChatModel.java` | 64 | Replays the same JSONL fixtures as the Python recorded adapter; an unknown request is an error. |
| `java/src/main/java/dev/plainround/router/infrastructure/SpringAiChatModel.java` | 65 | * The live adapter: Spring AI's ChatClient pointed at an OpenAI-compatible endpoint (a local ollama or llama.cpp server, or a hosted provider). |
| `java/src/main/java/dev/plainround/router/interfaces/Main.java` | 189 | Runs steps 1 to 6 on the same data, prompts and fixtures as Python and writes router.json, day.json and audit.json. |

Each file below is quoted exactly, in order, in pieces of about a dozen lines. Under each piece, a bullet list explains every statement in the order it appears. The first time an idea shows up in this note it is explained in a bullet that begins **New idea**.

#### `java/src/main/java/dev/plainround/router/application/AnswerChecks.java`

```java
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
```

- **New idea.** A **package** is the address of a class: a dotted name that matches the folder path under `src/main/java` (or `src/test/java`). Packages group classes and control who may see them.
- `package dev.plainround.router.application;`: declares that this file belongs to the package `dev.plainround.router.application`.
- **New idea.** An **import** lets the file use a class from another package by its short name. `import static` brings in a static method, so it can be called without the class name.
- `import dev.plainround.router.application.ModelTiers.Answered;`: imports the class `dev.plainround.router.application.ModelTiers.Answered` so it can be used by its short name.
- `import dev.plainround.router.domain.Checks;`: imports the class `dev.plainround.router.domain.Checks` so it can be used by its short name.
- `import dev.plainround.router.domain.Tasks.Kind;`: imports the class `dev.plainround.router.domain.Tasks.Kind` so it can be used by its short name.
- `import dev.plainround.router.domain.Tasks.Task;`: imports the class `dev.plainround.router.domain.Tasks.Task` so it can be used by its short name.
- **New idea.** A comment starting with `/**` is **Javadoc**: documentation that tools turn into pages. Ordinary `//` and `/* */` comments are ignored by the compiler.
- `/** ... */`: a Javadoc comment. It says: "The checks the router runs on an answer; no gold answer is visible to them (a port of answer_checks.py)."
- **New idea.** A **class** describes a kind of object: its data (fields) and behaviour (methods). `final` forbids subclasses; `public` makes it visible to every package.
- `public final class AnswerChecks {`: declares the class `AnswerChecks` (public, final).
- **New idea.** A **record** is a short way to write an immutable data class. The header lists the components; Java writes the constructor, the getters (named like the component, `role()`), `equals`, `hashCode` and `toString`. A block `{ ... }` right after the header, without parameters, is a *compact constructor* that checks the values.
- `public record CheckResult(boolean passed, double extraCost, int extraTokens) {`: declares the record `CheckResult` with the components `boolean passed, double extraCost, int extraTokens`.
- **New idea.** A **field** is a variable that belongs to an object (or, if `static`, to the class). `final` means it can be assigned once. `private` hides it from other classes.
- `private final ModelTiers tiers;`: declares the field `tiers` of type `ModelTiers`.
- `private final String labelCheck;`: declares the field `labelCheck` of type `String`.

```java
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
```

- `private final String policyCheck;`: declares the field `policyCheck` of type `String`.
- **New idea.** A **constructor** has the class's name and no return type. It runs when `new ClassName(...)` creates an object and sets up its fields.
- `public AnswerChecks(ModelTiers tiers, String labelCheck, String policyCheck) {`: constructor of `AnswerChecks`, taking `ModelTiers tiers, String labelCheck, String policyCheck`.
- **New idea.** `=` stores a value in a variable; `+=` adds to it; `++` adds one.
- `this.tiers = tiers;`: stores `tiers` into `this.tiers`.
- `this.labelCheck = labelCheck;`: stores `labelCheck` into `this.labelCheck`.
- `this.policyCheck = policyCheck;`: stores `policyCheck` into `this.policyCheck`.
- **New idea.** A **method** is a function that belongs to a class. Its header gives, in order, who may call it (`public`, `private`), whether it belongs to the class (`static`), the type it returns (`void` means nothing), its name, and its parameters with their types.
- `public CheckResult check(Task task, String tier, String text) {`: declares the method `check`, which takes `Task task, String tier, String text` and returns `CheckResult`.
- **New idea.** **if / else** runs a block only when the condition in brackets is true. Conditions use `==`, `!=`, `<`, `>`, `&&` (and), `||` (or) and `!` (not). Compare text with `.equals(...)`, never with `==`.
- `if (task.kind() == Kind.REFUND) {`: runs the block below only if `task.kind() == Kind.REFUND` is true.
- **New idea.** `return value;` ends the method and hands the value to the caller.
- `return new CheckResult(Checks.checkRefund(task, text), 0.0, 0);`: ends the method and hands back `new CheckResult(Checks.checkRefund(task, text), 0.0, 0)`.
- `if (task.kind() == Kind.POLICY) {`: runs the block below only if `task.kind() == Kind.POLICY` is true.
- **New idea.** A **local variable** exists only inside the method (or block) where it is declared. Its type comes first (`var` lets the compiler infer it).
- **New idea.** `condition ? a : b` gives `a` when the condition is true and `b` otherwise.
- `boolean passed = policyCheck.equals("overlap") ? Checks.checkPolicyOverlap(task.text(),...`: declares `passed` of type `boolean` and sets it to `policyCheck.equals("overlap") ? Checks.checkPolicyOverlap(task.text(), text) ...`. `.equals(x)` compares two objects by value.

```java
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
```

- `return new CheckResult(passed, 0.0, 0);`: ends the method and hands back `new CheckResult(passed, 0.0, 0)`.
- `if (labelCheck.equals("shape")) {`: runs the block below only if `labelCheck.equals("shape")` is true. `.equals(x)` compares two objects by value.
- `return new CheckResult(Checks.checkLabelShape(text), 0.0, 0);`: ends the method and hands back `new CheckResult(Checks.checkLabelShape(text), 0.0, 0)`.
- `Answered second = tiers.call(tier, task, true);`: declares `second` of type `Answered` and sets it to `tiers.call(tier, task, true)`.
- `return new CheckResult(Checks.checkLabelAgreement(text, second.text()), second.cost(), ...`: ends the method and hands back `new CheckResult(Checks.checkLabelAgreement(text, second.text()), second.cost(...`.
- `public double estimateExtra(Task task, String tier) {`: declares the method `estimateExtra`, which takes `Task task, String tier` and returns `double`.
- `return task.kind() == Kind.LABEL && labelCheck.equals("agreement") ? tiers.estimate(tie...`: ends the method and hands back `task.kind() == Kind.LABEL && labelCheck.equals("agreement") ? tiers.estimate(...`. `.equals(x)` compares two objects by value.

#### `java/src/main/java/dev/plainround/router/application/CostRouter.java`

```java
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
```

- `package dev.plainround.router.application;`: declares that this file belongs to the package `dev.plainround.router.application`.
- `import dev.plainround.router.application.AnswerChecks.CheckResult;`: imports the class `dev.plainround.router.application.AnswerChecks.CheckResult` so it can be used by its short name.
- `import dev.plainround.router.application.ModelTiers.Answered;`: imports the class `dev.plainround.router.application.ModelTiers.Answered` so it can be used by its short name.
- `import dev.plainround.router.domain.Routing;`: imports the class `dev.plainround.router.domain.Routing` so it can be used by its short name.
- `import dev.plainround.router.domain.Routing.Attempt;`: imports the class `dev.plainround.router.domain.Routing.Attempt` so it can be used by its short name.
- `import dev.plainround.router.domain.Routing.DayBudget;`: imports the class `dev.plainround.router.domain.Routing.DayBudget` so it can be used by its short name.
- `import dev.plainround.router.domain.Routing.Decision;`: imports the class `dev.plainround.router.domain.Routing.Decision` so it can be used by its short name.
- `import dev.plainround.router.domain.Routing.RouterConfig;`: imports the class `dev.plainround.router.domain.Routing.RouterConfig` so it can be used by its short name.
- `import dev.plainround.router.domain.Tasks.Task;`: imports the class `dev.plainround.router.domain.Tasks.Task` so it can be used by its short name.
- `import java.util.ArrayList;`: imports the class `java.util.ArrayList` so it can be used by its short name.
- `import java.util.List;`: imports the class `java.util.List` so it can be used by its short name.
- `/** ... */`: a Javadoc comment. It says: "Cheapest tier first, a check after every answer, escalation on a failed check (a port of router.py)."

```java
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
```

- `public final class CostRouter {`: declares the class `CostRouter` (public, final).
- `public static final String ESCALATE = "escalate_to_person";`: declares the field `ESCALATE` of type `String` and sets it to `"escalate_to_person"`.
- `private final ModelTiers tiers;`: declares the field `tiers` of type `ModelTiers`.
- `private final AnswerChecks checks;`: declares the field `checks` of type `AnswerChecks`.
- `private final RouterConfig config;`: declares the field `config` of type `RouterConfig`.
- `public CostRouter(ModelTiers tiers, AnswerChecks checks, RouterConfig config) {`: constructor of `CostRouter`, taking `ModelTiers tiers, AnswerChecks checks, RouterConfig config`.
- `this.tiers = tiers;`: stores `tiers` into `this.tiers`.
- `this.checks = checks;`: stores `checks` into `this.checks`.
- `this.config = config;`: stores `config` into `this.config`.

```java
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
```

- `public RouterConfig config() {`: declares the method `config`, which takes no arguments and returns `RouterConfig`.
- `return config;`: ends the method and hands back `config`.
- `public Decision route(Task task, DayBudget day) {`: declares the method `route`, which takes `Task task, DayBudget day` and returns `Decision`.
- `double share = day != null ? day.usedShare() : 0.0;`: declares `share` of type `double` and sets it to `day != null ? day.usedShare() : 0.0`.
- **New idea.** **Generics** such as `List<String>` say what a collection holds, so the compiler can reject a wrong type. `Map<String, Integer>` maps text to whole numbers.
- `List<String> all = Routing.TIERS;`: declares `all` of type `List<String>` and sets it to `Routing.TIERS`.
- `List<String> allowed = day != null && share >= config.tightenAt() ? all.subList(0, all....`: declares `allowed` of type `List<String>` and sets it to `day != null && share >= config.tightenAt() ? all.subList(0, all.size() - 1) :...`. `.size()` is the number of items.
- `int start = config.startIndex(task.kind().value(), Routing.hardSignal(task));`: declares `start` of type `int` and sets it to `config.startIndex(task.kind().value(), Routing.hardSignal(task))`.
- `double limit = day == null ? config.requestCap() : Math.min(config.requestCap(), day.bu...`: declares `limit` of type `double` and sets it to `day == null ? config.requestCap() : Math.min(config.requestCap(), day.budget(...`. `Math.xxx` is a standard maths function.
- `double spent = 0.0;`: declares `spent` of type `double` and sets it to `0.0`.
- `int tokens = 0;`: declares `tokens` of type `int` and sets it to `0`.
- **New idea.** `new ClassName(args)` creates an object by calling the constructor.
- `List<Attempt> attempts = new ArrayList<>();`: declares `attempts` of type `List<Attempt>` and sets it to `new ArrayList<>()`. `new ArrayList<>()` makes an empty changeable list.
- `List<String> tags = new ArrayList<>();`: declares `tags` of type `List<String>` and sets it to `new ArrayList<>()`. `new ArrayList<>()` makes an empty changeable list.

```java
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
```

- **New idea.** A **for loop** repeats a block. `for (int i = 0; i < n; i++)` counts; `for (Item x : items)` visits every item of a collection.
- `for (String tier : allowed.subList(Math.min(start, allowed.size()), allowed.size())) {`: repeats the block below once for each item `String tier` taken from `allowed.subList(Math.min(start, allowed.size())...`.
- `double projected = spent + tiers.estimate(tier, task, 1) + checks.estimateExtra(task, t...`: declares `projected` of type `double` and sets it to `spent + tiers.estimate(tier, task, 1) + checks.estimateExtra(task, tier)`.
- `if (projected > limit) {`: runs the block below only if `projected > limit` is true.
- `tags.add(limit == config.requestCap() ? "cap" : "budget");`: stores `= config.requestCap() ? "cap" : "budget")` into `tags.add(limit`.
- `break;`: leaves the loop or switch.
- `Answered answered = tiers.call(tier, task, false);`: declares `answered` of type `Answered` and sets it to `tiers.call(tier, task, false)`.
- `CheckResult result = checks.check(task, tier, answered.text());`: declares `result` of type `CheckResult` and sets it to `checks.check(task, tier, answered.text())`.
- `double callCost = answered.cost() + result.extraCost();`: declares `callCost` of type `double` and sets it to `answered.cost() + result.extraCost()`.
- `spent += callCost;`: adds `callCost` with `spent`.
- `tokens += answered.tokens() + result.extraTokens();`: adds `answered.tokens() + result.extraTokens()` with `tokens`.
- `attempts.add(new Attempt(tier, result.passed(), callCost, answered.tokens() + result.ex...`: runs `attempts.add(new Attempt(tier, result.passed(), callCost, answered.tokens() + result.ex...`. `.add(x)` appends `x`.
- `if (result.passed()) {`: runs the block below only if `result.passed()` is true.
- `if (day != null) {`: runs the block below only if `day != null` is true.
- `day.add(spent);`: runs `day.add(spent)`. `.add(x)` appends `x`.
- `return new Decision(task.taskId(), answered.text(), tier, attempts, spent, tokens, shar...`: ends the method and hands back `new Decision(task.taskId(), answered.text(), tier, attempts, spent, tokens, s...`.

```java
        if (day != null) {
            day.add(spent);
        }
        return new Decision(task.taskId(), null, ESCALATE, attempts, spent, tokens, share, tags);
    }
}
```

- `if (day != null) {`: runs the block below only if `day != null` is true.
- `day.add(spent);`: runs `day.add(spent)`. `.add(x)` appends `x`.
- `return new Decision(task.taskId(), null, ESCALATE, attempts, spent, tokens, share, tags);`: ends the method and hands back `new Decision(task.taskId(), null, ESCALATE, attempts, spent, tokens, share, t...`.

#### `java/src/main/java/dev/plainround/router/application/Experiments.java`

```java
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
```

- `package dev.plainround.router.application;`: declares that this file belongs to the package `dev.plainround.router.application`.
- `import dev.plainround.router.application.ModelTiers.Answered;`: imports the class `dev.plainround.router.application.ModelTiers.Answered` so it can be used by its short name.
- `import dev.plainround.router.domain.Checks;`: imports the class `dev.plainround.router.domain.Checks` so it can be used by its short name.
- `import dev.plainround.router.domain.Routing;`: imports the class `dev.plainround.router.domain.Routing` so it can be used by its short name.
- `import dev.plainround.router.domain.Routing.Bar;`: imports the class `dev.plainround.router.domain.Routing.Bar` so it can be used by its short name.
- `import dev.plainround.router.domain.Routing.CheckRates;`: imports the class `dev.plainround.router.domain.Routing.CheckRates` so it can be used by its short name.
- `import dev.plainround.router.domain.Routing.DayBudget;`: imports the class `dev.plainround.router.domain.Routing.DayBudget` so it can be used by its short name.
- `import dev.plainround.router.domain.Routing.Decision;`: imports the class `dev.plainround.router.domain.Routing.Decision` so it can be used by its short name.
- `import dev.plainround.router.domain.Routing.Rate;`: imports the class `dev.plainround.router.domain.Routing.Rate` so it can be used by its short name.
- `import dev.plainround.router.domain.Routing.RouterConfig;`: imports the class `dev.plainround.router.domain.Routing.RouterConfig` so it can be used by its short name.
- `import dev.plainround.router.domain.Stats;`: imports the class `dev.plainround.router.domain.Stats` so it can be used by its short name.
- `import dev.plainround.router.domain.Tasks.Kind;`: imports the class `dev.plainround.router.domain.Tasks.Kind` so it can be used by its short name.
- `import dev.plainround.router.domain.Tasks.Task;`: imports the class `dev.plainround.router.domain.Tasks.Task` so it can be used by its short name.

```java
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
```

- `import java.util.ArrayList;`: imports the class `java.util.ArrayList` so it can be used by its short name.
- `import java.util.LinkedHashMap;`: imports the class `java.util.LinkedHashMap` so it can be used by its short name.
- `import java.util.List;`: imports the class `java.util.List` so it can be used by its short name.
- `import java.util.Map;`: imports the class `java.util.Map` so it can be used by its short name.
- `import java.util.TreeMap;`: imports the class `java.util.TreeMap` so it can be used by its short name.
- `import java.util.function.Supplier;`: imports the class `java.util.function.Supplier` so it can be used by its short name.
- `/** ... */`: a Javadoc comment. It says: "The lesson's steps as functions over the tier, check and router objects (a port of experiments.py)."
- `public final class Experiments {`: declares the class `Experiments` (public, final).
- `private Experiments() {`: constructor of `Experiments`, taking no arguments.
- `public static final List<String> KINDS = List.of("label", "refund", "policy");`: declares the field `KINDS` of type `List<String>` and sets it to `List.of("label", "refund", "policy")`. `List.of(...)` makes an unchangeable list.

```java
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
```

- `public static final Map<String, List<String>> CHECK_NAMES = Map.of("label", List.of("la...`: declares the field `CHECK_NAMES` of type `List<String>>` and sets it to `Map.of("label", List.of("label_shape", "label_agreement"), "refund", List.of(...`. `List.of(...)` makes an unchangeable list; `Map.of(...)` makes an unchangeable map.
- `public record Outcome(Decision decision, String kind, String difficulty, boolean correc...`: declares the record `Outcome` with the components `Decision decision, String kind, String difficulty, boolean correct`.
- `public boolean escalated() {`: declares the method `escalated`, which takes no arguments and returns `boolean`.
- `return decision.servedBy().equals(CostRouter.ESCALATE);`: ends the method and hands back `decision.servedBy().equals(CostRouter.ESCALATE)`. `.equals(x)` compares two objects by value.
- `public record Summary( int n, Rate accuracy, double totalCost, Double costPerCorrect, d...`: declares the record `Summary` with the components `int n, Rate accuracy, double totalCost, Double costPerCorrect, double[] costPerCorrectInterval, Map<String, Integer> servedBy, int escala...`.

```java
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
```

- `public record DayResult( double fraction, double budget, double spent, boolean underBud...`: declares the record `DayResult` with the components `double fraction, double budget, double spent, boolean underBudget, int requestsOverCap, Integer crossedAt, Rate accuracyBefore, Rate accu...`.
- **New idea.** `static` means the member belongs to the class itself, not to one object; it is called as `ClassName.method()`.
- `public static Map<String, Map<String, Answered>> collectAnswers(List<Task> tasks, Model...`: declares the method `collectAnswers`, which takes `List<Task> tasks, ModelTiers tiers` and returns `Answered>>`. It belongs to the class (`static`).
- `Map<String, Map<String, Answered>> answers = new LinkedHashMap<>();`: declares `answers` of type `Answered>>` and sets it to `new LinkedHashMap<>()`. `new HashMap<>()` makes an empty map.
- `for (String tier : Routing.TIERS) {`: repeats the block below once for each item `String tier` taken from `Routing.TIERS`.

```java
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
```

- `Map<String, Answered> byTask = new LinkedHashMap<>();`: declares `byTask` of type `Answered>` and sets it to `new LinkedHashMap<>()`. `new HashMap<>()` makes an empty map.
- `for (Task task : tasks) {`: repeats the block below once for each item `Task task` taken from `tasks`.
- `byTask.put(task.taskId(), tiers.call(tier, task, false));`: runs `byTask.put(task.taskId(), tiers.call(tier, task, false))`. `.put(k, v)` stores value `v` under key `k`.
- `answers.put(tier, byTask);`: runs `answers.put(tier, byTask)`. `.put(k, v)` stores value `v` under key `k`.
- `return answers;`: ends the method and hands back `answers`.
- `public static Map<String, Map<String, Map<String, CheckRates>>> checkResults( List<Task...`: declares the method `checkResults`, which takes `List<Task> tasks, Map<String, Map<String, Answered>> answers, ModelTiers tiers` and returns `CheckRates>>>`. It belongs to the class (`static`).
- `Map<String, Map<String, Map<String, CheckRates>>> out = new LinkedHashMap<>();`: declares `out` of type `CheckRates>>>` and sets it to `new LinkedHashMap<>()`. `new HashMap<>()` makes an empty map.
- `for (String tier : Routing.TIERS) {`: repeats the block below once for each item `String tier` taken from `Routing.TIERS`.
- `Map<String, Map<String, CheckRates>> byKind = new LinkedHashMap<>();`: declares `byKind` of type `CheckRates>>` and sets it to `new LinkedHashMap<>()`. `new HashMap<>()` makes an empty map.

```java
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
```

- `for (String kind : KINDS) {`: repeats the block below once for each item `String kind` taken from `KINDS`.
- **New idea.** A **lambda** `x -> x + 1` is a small unnamed function; `(a, b) -> a + b` takes two parameters. A method reference `Class::method` is a shorthand for one.
- **New idea.** A **stream** processes a collection as a pipeline: `.filter(...)` keeps items, `.map(...)` changes them, `.sorted()` orders them, `.toList()` or `.collect(...)` gathers the result.
- `List<Task> subset = tasks.stream().filter(t -> t.kind().value().equals(kind)).toList();`: declares `subset` of type `List<Task>` and sets it to `tasks.stream().filter(t -> t.kind().value().equals(kind)).toList()`. `.equals(x)` compares two objects by value; `.stream()` starts a pipeline over the items; `.filter(p)` keeps the items for which `p` is true.
- `List<Boolean> correct = new ArrayList<>();`: declares `correct` of type `List<Boolean>` and sets it to `new ArrayList<>()`. `new ArrayList<>()` makes an empty changeable list.
- `List<String> texts = new ArrayList<>();`: declares `texts` of type `List<String>` and sets it to `new ArrayList<>()`. `new ArrayList<>()` makes an empty changeable list.
- `for (Task t : subset) {`: repeats the block below once for each item `Task t` taken from `subset`.
- `String text = answers.get(tier).get(t.taskId()).text();`: declares `text` of type `String` and sets it to `answers.get(tier).get(t.taskId()).text()`. `.get(x)` reads the item or entry for `x`.
- `texts.add(text);`: runs `texts.add(text)`. `.add(x)` appends `x`.
- `correct.add(Checks.isCorrect(t, text));`: runs `correct.add(Checks.isCorrect(t, text))`. `.add(x)` appends `x`.
- `Map<String, CheckRates> checks = new LinkedHashMap<>();`: declares `checks` of type `CheckRates>` and sets it to `new LinkedHashMap<>()`. `new HashMap<>()` makes an empty map.
- `if (kind.equals("label")) {`: runs the block below only if `kind.equals("label")` is true. `.equals(x)` compares two objects by value.
- `List<Boolean> shape = new ArrayList<>();`: declares `shape` of type `List<Boolean>` and sets it to `new ArrayList<>()`. `new ArrayList<>()` makes an empty changeable list.
- `List<Boolean> agree = new ArrayList<>();`: declares `agree` of type `List<Boolean>` and sets it to `new ArrayList<>()`. `new ArrayList<>()` makes an empty changeable list.
- `for (int i = 0; i < subset.size(); i++) {`: repeats the block below as the counting loop `int i = 0; i < subset.size(); i++` says.
- `shape.add(Checks.checkLabelShape(texts.get(i)));`: runs `shape.add(Checks.checkLabelShape(texts.get(i)))`. `.get(x)` reads the item or entry for `x`; `.add(x)` appends `x`.
- `String second = tiers.call(tier, subset.get(i), true).text();`: declares `second` of type `String` and sets it to `tiers.call(tier, subset.get(i), true).text()`. `.get(x)` reads the item or entry for `x`.
- `agree.add(Checks.checkLabelAgreement(texts.get(i), second));`: runs `agree.add(Checks.checkLabelAgreement(texts.get(i), second))`. `.get(x)` reads the item or entry for `x`; `.add(x)` appends `x`.
- `checks.put("label_shape", Routing.checkRates(shape, correct));`: runs `checks.put("label_shape", Routing.checkRates(shape, correct))`. `.put(k, v)` stores value `v` under key `k`.
- `checks.put("label_agreement", Routing.checkRates(agree, correct));`: runs `checks.put("label_agreement", Routing.checkRates(agree, correct))`. `.put(k, v)` stores value `v` under key `k`.
- `else if (kind.equals("refund")) {`: otherwise, runs the block below only if `kind.equals("refund")` is true. `.equals(x)` compares two objects by value.
- `List<Boolean> passed = new ArrayList<>();`: declares `passed` of type `List<Boolean>` and sets it to `new ArrayList<>()`. `new ArrayList<>()` makes an empty changeable list.
- `for (int i = 0; i < subset.size(); i++) {`: repeats the block below as the counting loop `int i = 0; i < subset.size(); i++` says.
- `passed.add(Checks.checkRefund(subset.get(i), texts.get(i)));`: runs `passed.add(Checks.checkRefund(subset.get(i), texts.get(i)))`. `.get(x)` reads the item or entry for `x`; `.add(x)` appends `x`.
- `checks.put("refund_recompute", Routing.checkRates(passed, correct));`: runs `checks.put("refund_recompute", Routing.checkRates(passed, correct))`. `.put(k, v)` stores value `v` under key `k`.
- `else {`: runs the block below when none of the conditions above held.
- `List<Boolean> passed = texts.stream().map(Checks::checkPolicy).toList();`: declares `passed` of type `List<Boolean>` and sets it to `texts.stream().map(Checks::checkPolicy).toList()`. `.stream()` starts a pipeline over the items; `.map(f)` applies `f` to each item; `.toList()` ends the pipeline with an unchangeable list.
- `checks.put("policy_quote", Routing.checkRates(passed, correct));`: runs `checks.put("policy_quote", Routing.checkRates(passed, correct))`. `.put(k, v)` stores value `v` under key `k`.
- `byKind.put(kind, checks);`: runs `byKind.put(kind, checks)`. `.put(k, v)` stores value `v` under key `k`.

```java
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
```

- `out.put(tier, byKind);`: runs `out.put(tier, byKind)`. `.put(k, v)` stores value `v` under key `k`.
- `return out;`: ends the method and hands back `out`.
- `public static RouterConfig tune( List<Task> buildTasks, Map<String, Map<String, Answere...`: declares the method `tune`, which takes `List<Task> buildTasks, Map<String, Map<String, Answered>> answers, Map<String, Map<String, Map<St...` and returns `RouterConfig`. It belongs to the class (`static`).
- `Map<String, String> start = new LinkedHashMap<>();`: declares `start` of type `String>` and sets it to `new LinkedHashMap<>()`. `new HashMap<>()` makes an empty map.
- `Map<String, String> hardStart = new LinkedHashMap<>();`: declares `hardStart` of type `String>` and sets it to `new LinkedHashMap<>()`. `new HashMap<>()` makes an empty map.
- `for (String kind : KINDS) {`: repeats the block below once for each item `String kind` taken from `KINDS`.
- `List<String> names = CHECK_NAMES.get(kind);`: declares `names` of type `List<String>` and sets it to `CHECK_NAMES.get(kind)`. `.get(x)` reads the item or entry for `x`.

```java
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
```

- `String checkName = names.get(names.size() - 1);`: declares `checkName` of type `String` and sets it to `names.get(names.size() - 1)`. `.size()` is the number of items; `.get(x)` reads the item or entry for `x`.
- `String chosen = Routing.TIERS.get(Routing.TIERS.size() - 1);`: declares `chosen` of type `String` and sets it to `Routing.TIERS.get(Routing.TIERS.size() - 1)`. `.size()` is the number of items; `.get(x)` reads the item or entry for `x`.
- `for (String tier : Routing.TIERS) {`: repeats the block below once for each item `String tier` taken from `Routing.TIERS`.
- `if (rates.get(tier).get(kind).get(checkName).falseAcceptRate() <= bar.falseAcceptBar()) {`: runs the block below only if `rates.get(tier).get(kind).get(checkName).falseAcceptRate() <= bar.falseAccept...` is true. `.get(x)` reads the item or entry for `x`.
- `chosen = tier;`: stores `tier` into `chosen`.
- `break;`: leaves the loop or switch.
- `start.put(kind, chosen);`: runs `start.put(kind, chosen)`. `.put(k, v)` stores value `v` under key `k`.
- `int index = Routing.TIERS.indexOf(chosen);`: declares `index` of type `int` and sets it to `Routing.TIERS.indexOf(chosen)`.
- `List<Task> signalled = buildTasks.stream().filter(t -> t.kind().value().equals(kind) &&...`: declares `signalled` of type `List<Task>` and sets it to `buildTasks.stream().filter(t -> t.kind().value().equals(kind) && Routing.hard...`. `.equals(x)` compares two objects by value; `.stream()` starts a pipeline over the items; `.filter(p)` keeps the items for which `p` is true.
- `if (index < Routing.TIERS.size() - 1 && signalled.size() >= 5) {`: runs the block below only if `index < Routing.TIERS.size() - 1 && signalled.size() >= 5` is true. `.size()` is the number of items.
- `long right = signalled.stream().filter(t -> Checks.isCorrect(t, answers.get(start.get(k...`: declares `right` of type `long` and sets it to `signalled.stream().filter(t -> Checks.isCorrect(t, answers.get(start.get(kind...`. `.get(x)` reads the item or entry for `x`; `.stream()` starts a pipeline over the items; `.filter(p)` keeps the items for which `p` is true.
- `if ((double) right / signalled.size() < bar.hardAccuracyBar()) {`: runs the block below only if `(double) right / signalled.size() < bar.hardAccuracyBar()` is true. `.size()` is the number of items.
- `hardStart.put(kind, Routing.TIERS.get(index + 1));`: runs `hardStart.put(kind, Routing.TIERS.get(index + 1))`. `.get(x)` reads the item or entry for `x`; `.put(k, v)` stores value `v` under key `k`.

```java
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
```

- `return new RouterConfig(start, hardStart, "agreement", bar.requestCap(), bar.tightenAt(...`: ends the method and hands back `new RouterConfig(start, hardStart, "agreement", bar.requestCap(), bar.tighten...`.
- `public static List<Outcome> routeAll(List<Task> tasks, CostRouter router, DayBudget day) {`: declares the method `routeAll`, which takes `List<Task> tasks, CostRouter router, DayBudget day` and returns `List<Outcome>`. It belongs to the class (`static`).
- `List<Outcome> outcomes = new ArrayList<>();`: declares `outcomes` of type `List<Outcome>` and sets it to `new ArrayList<>()`. `new ArrayList<>()` makes an empty changeable list.
- `for (Task task : tasks) {`: repeats the block below once for each item `Task task` taken from `tasks`.
- `Decision decision = router.route(task, day);`: declares `decision` of type `Decision` and sets it to `router.route(task, day)`.
- `boolean correct = decision.answer() != null && Checks.isCorrect(task, decision.answer());`: declares `correct` of type `boolean` and sets it to `decision.answer() != null && Checks.isCorrect(task, decision.answer())`.
- `outcomes.add(new Outcome(decision, task.kind().value(), task.difficulty(), correct));`: runs `outcomes.add(new Outcome(decision, task.kind().value(), task.difficulty(), correct))`. `.add(x)` appends `x`.
- `return outcomes;`: ends the method and hands back `outcomes`.
- `public static Summary summarize(List<Outcome> outcomes) {`: declares the method `summarize`, which takes `List<Outcome> outcomes` and returns `Summary`. It belongs to the class (`static`).

```java
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
```

- `List<Boolean> correct = outcomes.stream().map(Outcome::correct).toList();`: declares `correct` of type `List<Boolean>` and sets it to `outcomes.stream().map(Outcome::correct).toList()`. `.stream()` starts a pipeline over the items; `.map(f)` applies `f` to each item; `.toList()` ends the pipeline with an unchangeable list.
- `List<Double> costs = outcomes.stream().map(o -> o.decision().spent()).toList();`: declares `costs` of type `List<Double>` and sets it to `outcomes.stream().map(o -> o.decision().spent()).toList()`. `.stream()` starts a pipeline over the items; `.map(f)` applies `f` to each item; `.toList()` ends the pipeline with an unchangeable list.
- `Map<String, Integer> shares = new TreeMap<>();`: declares `shares` of type `Integer>` and sets it to `new TreeMap<>()`.
- `for (Outcome o : outcomes) {`: repeats the block below once for each item `Outcome o` taken from `outcomes`.
- `shares.merge(o.decision().servedBy(), 1, Integer::sum);`: runs `shares.merge(o.decision().servedBy(), 1, Integer::sum)`.
- `double total = 0.0;`: declares `total` of type `double` and sets it to `0.0`.
- `double max = 0.0;`: declares `max` of type `double` and sets it to `0.0`.
- `for (double c : costs) {`: repeats the block below once for each item `double c` taken from `costs`.
- `total += c;`: adds `c` with `total`.
- `max = Math.max(max, c);`: stores `Math.max(max, c)` into `max`. `Math.xxx` is a standard maths function.
- `int right = (int) correct.stream().filter(c -> c).count();`: declares `right` of type `int` and sets it to `(int) correct.stream().filter(c -> c).count()`. `.stream()` starts a pipeline over the items; `.filter(p)` keeps the items for which `p` is true.
- `return new Summary( outcomes.size(), Routing.rate(right, correct.size()), total, Routin...`: ends the method and hands back `new Summary( outcomes.size(), Routing.rate(right, correct.size()), total, Rou...`. `.size()` is the number of items; `.stream()` starts a pipeline over the items; `.filter(p)` keeps the items for which `p` is true.

```java
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
```

- `public static Summary singleModelSummary(List<Task> tasks, Map<String, Map<String, Answ...`: declares the method `singleModelSummary`, which takes `List<Task> tasks, Map<String, Map<String, Answered>> answers, String tier` and returns `Summary`. It belongs to the class (`static`).
- `List<Boolean> correct = new ArrayList<>();`: declares `correct` of type `List<Boolean>` and sets it to `new ArrayList<>()`. `new ArrayList<>()` makes an empty changeable list.
- `List<Double> costs = new ArrayList<>();`: declares `costs` of type `List<Double>` and sets it to `new ArrayList<>()`. `new ArrayList<>()` makes an empty changeable list.
- `double total = 0.0;`: declares `total` of type `double` and sets it to `0.0`.
- `double max = 0.0;`: declares `max` of type `double` and sets it to `0.0`.
- `for (Task t : tasks) {`: repeats the block below once for each item `Task t` taken from `tasks`.
- `Answered a = answers.get(tier).get(t.taskId());`: declares `a` of type `Answered` and sets it to `answers.get(tier).get(t.taskId())`. `.get(x)` reads the item or entry for `x`.
- `correct.add(Checks.isCorrect(t, a.text()));`: runs `correct.add(Checks.isCorrect(t, a.text()))`. `.add(x)` appends `x`.
- `costs.add(a.cost());`: runs `costs.add(a.cost())`. `.add(x)` appends `x`.
- `total += a.cost();`: adds `a.cost()` with `total`.
- `max = Math.max(max, a.cost());`: stores `Math.max(max, a.cost())` into `max`. `Math.xxx` is a standard maths function.
- `int right = (int) correct.stream().filter(c -> c).count();`: declares `right` of type `int` and sets it to `(int) correct.stream().filter(c -> c).count()`. `.stream()` starts a pipeline over the items; `.filter(p)` keeps the items for which `p` is true.
- `Map<String, Integer> served = new TreeMap<>();`: declares `served` of type `Integer>` and sets it to `new TreeMap<>()`.

```java
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
```

- `served.put(tier, tasks.size());`: runs `served.put(tier, tasks.size())`. `.size()` is the number of items; `.put(k, v)` stores value `v` under key `k`.
- `return new Summary(tasks.size(), Routing.rate(right, correct.size()), total, Routing.co...`: ends the method and hands back `new Summary(tasks.size(), Routing.rate(right, correct.size()), total, Routing...`. `.size()` is the number of items.
- `public static Map<String, Object> compareToLarge(List<Task> tasks, Map<String, Map<Stri...`: declares the method `compareToLarge`, which takes `List<Task> tasks, Map<String, Map<String, Answered>> answers, List<Outcome> outcomes, Bar bar` and returns `Object>`. It belongs to the class (`static`).
- `Summary router = summarize(outcomes);`: declares `router` of type `Summary` and sets it to `summarize(outcomes)`.
- `Summary large = singleModelSummary(tasks, answers, "large");`: declares `large` of type `Summary` and sets it to `singleModelSummary(tasks, answers, "large")`.
- `List<Boolean> routerCorrect = outcomes.stream().map(Outcome::correct).toList();`: declares `routerCorrect` of type `List<Boolean>` and sets it to `outcomes.stream().map(Outcome::correct).toList()`. `.stream()` starts a pipeline over the items; `.map(f)` applies `f` to each item; `.toList()` ends the pipeline with an unchangeable list.
- `List<Boolean> largeCorrect = tasks.stream().map(t -> Checks.isCorrect(t, answers.get("l...`: declares `largeCorrect` of type `List<Boolean>` and sets it to `tasks.stream().map(t -> Checks.isCorrect(t, answers.get("large").get(t.taskId...`. `.get(x)` reads the item or entry for `x`; `.stream()` starts a pipeline over the items; `.map(f)` applies `f` to each item.
- `double[] diff = Routing.bootstrapAccuracyDifference(routerCorrect, largeCorrect);`: declares `diff` of type `double[]` and sets it to `Routing.bootstrapAccuracyDifference(routerCorrect, largeCorrect)`.
- `boolean matched = router.accuracy().value() >= large.accuracy().value() - bar.accuracyM...`: declares `matched` of type `boolean` and sets it to `router.accuracy().value() >= large.accuracy().value() - bar.accuracyMargin()`.
- `boolean cheaper = router.costPerCorrect() != null && large.costPerCorrect() != null && ...`: declares `cheaper` of type `boolean` and sets it to `router.costPerCorrect() != null && large.costPerCorrect() != null && router.c...`.
- `Map<String, Object> verdict = new LinkedHashMap<>();`: declares `verdict` of type `Object>` and sets it to `new LinkedHashMap<>()`. `new HashMap<>()` makes an empty map.
- `verdict.put("accuracy_difference_vs_large", diff[0]);`: runs `verdict.put("accuracy_difference_vs_large", diff[0])`. `.put(k, v)` stores value `v` under key `k`.

```java
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
```

- `verdict.put("accuracy_difference_interval", List.of(diff[1], diff[2]));`: runs `verdict.put("accuracy_difference_interval", List.of(diff[1], diff[2]))`. `.put(k, v)` stores value `v` under key `k`; `List.of(...)` makes an unchangeable list.
- `verdict.put("margin", bar.accuracyMargin());`: runs `verdict.put("margin", bar.accuracyMargin())`. `.put(k, v)` stores value `v` under key `k`.
- `verdict.put("matched_within_margin", matched);`: runs `verdict.put("matched_within_margin", matched)`. `.put(k, v)` stores value `v` under key `k`.
- `verdict.put("cheaper_per_correct", cheaper);`: runs `verdict.put("cheaper_per_correct", cheaper)`. `.put(k, v)` stores value `v` under key `k`.
- `verdict.put("verdict", matched && cheaper ? "matched" : (cheaper ? "cheaper but less ac...`: runs `verdict.put("verdict", matched && cheaper ? "matched" : (cheaper ? "cheaper but less ac...`. `.put(k, v)` stores value `v` under key `k`.
- `return verdict;`: ends the method and hands back `verdict`.
- `public static DayResult runDay(List<Task> tasks, Map<String, Map<String, Answered>> ans...`: declares the method `runDay`, which takes `List<Task> tasks, Map<String, Map<String, Answered>> answers, Supplier<CostRouter> routerFactory,...` and returns `DayResult`. It belongs to the class (`static`).
- `int[] order = Stats.shuffledIndices(tasks.size(), seed);`: declares `order` of type `int[]` and sets it to `Stats.shuffledIndices(tasks.size(), seed)`. `.size()` is the number of items.
- `List<Task> ordered = new ArrayList<>();`: declares `ordered` of type `List<Task>` and sets it to `new ArrayList<>()`. `new ArrayList<>()` makes an empty changeable list.
- `for (int i : order) {`: repeats the block below once for each item `int i` taken from `order`.
- `ordered.add(tasks.get(i));`: runs `ordered.add(tasks.get(i))`. `.get(x)` reads the item or entry for `x`; `.add(x)` appends `x`.

```java
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
```

- `double largeCost = 0.0;`: declares `largeCost` of type `double` and sets it to `0.0`.
- `for (Task t : tasks) {`: repeats the block below once for each item `Task t` taken from `tasks`.
- `largeCost += answers.get("large").get(t.taskId()).cost();`: adds `answers.get("large").get(t.taskId()).cost()` with `largeCost`. `.get(x)` reads the item or entry for `x`.
- `DayBudget day = new DayBudget(largeCost * fraction);`: declares `day` of type `DayBudget` and sets it to `new DayBudget(largeCost * fraction)`.
- `CostRouter router = routerFactory.get();`: declares `router` of type `CostRouter` and sets it to `routerFactory.get()`. `.get(x)` reads the item or entry for `x`.
- `List<Outcome> outcomes = routeAll(ordered, router, day);`: declares `outcomes` of type `List<Outcome>` and sets it to `routeAll(ordered, router, day)`.
- `Integer crossed = null;`: declares `crossed` of type `Integer` and sets it to `null`.
- `for (int i = 0; i < outcomes.size(); i++) {`: repeats the block below as the counting loop `int i = 0; i < outcomes.size(); i++` says.
- `if (outcomes.get(i).decision().shareBefore() >= router.config().tightenAt()) {`: runs the block below only if `outcomes.get(i).decision().shareBefore() >= router.config().tightenAt()` is true. `.get(x)` reads the item or entry for `x`.
- `crossed = i;`: stores `i` into `crossed`.
- `break;`: leaves the loop or switch.

```java
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
```

- `List<Outcome> before = crossed != null ? outcomes.subList(0, crossed) : outcomes;`: declares `before` of type `List<Outcome>` and sets it to `crossed != null ? outcomes.subList(0, crossed) : outcomes`.
- `List<Outcome> after = crossed != null ? outcomes.subList(crossed, outcomes.size()) : Li...`: declares `after` of type `List<Outcome>` and sets it to `crossed != null ? outcomes.subList(crossed, outcomes.size()) : List.of()`. `.size()` is the number of items; `List.of(...)` makes an unchangeable list.
- `double cap = router.config().requestCap();`: declares `cap` of type `double` and sets it to `router.config().requestCap()`.
- `int over = (int) outcomes.stream().filter(o -> o.decision().spent() > cap).count();`: declares `over` of type `int` and sets it to `(int) outcomes.stream().filter(o -> o.decision().spent() > cap).count()`. `.stream()` starts a pipeline over the items; `.filter(p)` keeps the items for which `p` is true.
- `int largeAfter = (int) after.stream().filter(o -> o.decision().servedBy().equals("large...`: declares `largeAfter` of type `int` and sets it to `(int) after.stream().filter(o -> o.decision().servedBy().equals("large")).cou...`. `.equals(x)` compares two objects by value; `.stream()` starts a pipeline over the items; `.filter(p)` keeps the items for which `p` is true.
- `return new DayResult( fraction, day.budget(), day.used(), day.used() <= day.budget(), o...`: ends the method and hands back `new DayResult( fraction, day.budget(), day.used(), day.used() <= day.budget()...`. `.size()` is the number of items; `.stream()` starts a pipeline over the items; `.filter(p)` keeps the items for which `p` is true.

```java
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
```

- `public static String checkName(String kind, RouterConfig config) {`: declares the method `checkName`, which takes `String kind, RouterConfig config` and returns `String`. It belongs to the class (`static`).
- `if (kind.equals("label")) {`: runs the block below only if `kind.equals("label")` is true. `.equals(x)` compares two objects by value.
- `return "label_" + config.labelCheck();`: ends the method and hands back `"label_" + config.labelCheck()`.
- `return kind.equals("refund") ? "refund_recompute" : "policy_" + config.policyCheck();`: ends the method and hands back `kind.equals("refund") ? "refund_recompute" : "policy_" + config.policyCheck()`. `.equals(x)` compares two objects by value.
- `public static Map<String, Object> falseAccepts(List<Outcome> outcomes, RouterConfig con...`: declares the method `falseAccepts`, which takes `List<Outcome> outcomes, RouterConfig config` and returns `Object>`. It belongs to the class (`static`).
- `Map<String, List<String>> grouped = new TreeMap<>();`: declares `grouped` of type `List<String>>` and sets it to `new TreeMap<>()`.
- `int wrong = 0;`: declares `wrong` of type `int` and sets it to `0`.
- `for (Outcome o : outcomes) {`: repeats the block below once for each item `Outcome o` taken from `outcomes`.
- `if (o.decision().answer() == null || o.correct()) {`: runs the block below only if `o.decision().answer() == null || o.correct()` is true.
- `continue;`: skips to the next round of the loop.

```java
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
```

- `wrong++;`: adds or subtracts one.
- `grouped.computeIfAbsent(o.decision().servedBy() + "/" + checkName(o.kind(), config), k ...`: runs `grouped.computeIfAbsent(o.decision().servedBy() + "/" + checkName(o.kind(), config), k ...`. `.add(x)` appends `x`; `new ArrayList<>()` makes an empty changeable list.
- `Map<String, Integer> byTier = new TreeMap<>();`: declares `byTier` of type `Integer>` and sets it to `new TreeMap<>()`.
- `Map<String, Object> detail = new LinkedHashMap<>();`: declares `detail` of type `Object>` and sets it to `new LinkedHashMap<>()`. `new HashMap<>()` makes an empty map.
- `for (Map.Entry<String, List<String>> e : grouped.entrySet()) {`: repeats the block below once for each item `Map.Entry<String, List<String>> e` taken from `grouped.entrySet()`.
- `String tier = e.getKey().split("/")[0];`: declares `tier` of type `String` and sets it to `e.getKey().split("/")[0]`. `.split(regex)` cuts text into pieces.
- `byTier.merge(tier, e.getValue().size(), Integer::sum);`: runs `byTier.merge(tier, e.getValue().size(), Integer::sum)`. `.size()` is the number of items.
- `Map<String, Object> d = new LinkedHashMap<>();`: declares `d` of type `Object>` and sets it to `new LinkedHashMap<>()`. `new HashMap<>()` makes an empty map.
- `d.put("count", e.getValue().size());`: runs `d.put("count", e.getValue().size())`. `.size()` is the number of items; `.put(k, v)` stores value `v` under key `k`.
- `d.put("tasks", e.getValue());`: runs `d.put("tasks", e.getValue())`. `.put(k, v)` stores value `v` under key `k`.
- `detail.put(e.getKey(), d);`: runs `detail.put(e.getKey(), d)`. `.put(k, v)` stores value `v` under key `k`.
- `Map<String, Object> out = new LinkedHashMap<>();`: declares `out` of type `Object>` and sets it to `new LinkedHashMap<>()`. `new HashMap<>()` makes an empty map.

```java
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
```

- `out.put("false_accepts", wrong);`: runs `out.put("false_accepts", wrong)`. `.put(k, v)` stores value `v` under key `k`.
- `out.put("by_tier_and_check", detail);`: runs `out.put("by_tier_and_check", detail)`. `.put(k, v)` stores value `v` under key `k`.
- `out.put("by_tier", byTier);`: runs `out.put("by_tier", byTier)`. `.put(k, v)` stores value `v` under key `k`.
- `return out;`: ends the method and hands back `out`.
- `public record Hardened(RouterConfig config, String description) {`: declares the record `Hardened` with the components `RouterConfig config, String description`.
- `/** ... */`: a Javadoc comment. It says: "The one change step 6 makes: start one tier higher, or run a stronger check when already at the top tier."
- `public static Hardened harden(RouterConfig config, String kind) {`: declares the method `harden`, which takes `RouterConfig config, String kind` and returns `Hardened`. It belongs to the class (`static`).
- `int index = Routing.TIERS.indexOf(config.start().get(kind));`: declares `index` of type `int` and sets it to `Routing.TIERS.indexOf(config.start().get(kind))`. `.get(x)` reads the item or entry for `x`.
- `if (index < Routing.TIERS.size() - 1) {`: runs the block below only if `index < Routing.TIERS.size() - 1` is true. `.size()` is the number of items.
- `Map<String, String> start = new LinkedHashMap<>(config.start());`: declares `start` of type `String>` and sets it to `new LinkedHashMap<>(config.start())`. `new HashMap<>()` makes an empty map.
- `start.put(kind, Routing.TIERS.get(index + 1));`: runs `start.put(kind, Routing.TIERS.get(index + 1))`. `.get(x)` reads the item or entry for `x`; `.put(k, v)` stores value `v` under key `k`.

```java
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
```

- `Map<String, String> hard = new LinkedHashMap<>();`: declares `hard` of type `String>` and sets it to `new LinkedHashMap<>()`. `new HashMap<>()` makes an empty map.
- `for (Map.Entry<String, String> e : config.hardStart().entrySet()) {`: repeats the block below once for each item `Map.Entry<String, String> e` taken from `config.hardStart().entrySet()`.
- `if (!e.getKey().equals(kind) || Routing.TIERS.indexOf(e.getValue()) > index + 1) {`: runs the block below only if `!e.getKey().equals(kind) || Routing.TIERS.indexOf(e.getValue()) > index + 1` is true. `.equals(x)` compares two objects by value.
- `hard.put(e.getKey(), e.getValue());`: runs `hard.put(e.getKey(), e.getValue())`. `.put(k, v)` stores value `v` under key `k`.
- `return new Hardened( new RouterConfig(start, hard, config.labelCheck(), config.requestC...`: ends the method and hands back `new Hardened( new RouterConfig(start, hard, config.labelCheck(), config.reque...`. `.get(x)` reads the item or entry for `x`.
- `if (kind.equals("policy")) {`: runs the block below only if `kind.equals("policy")` is true. `.equals(x)` compares two objects by value.
- `return new Hardened( new RouterConfig(config.start(), config.hardStart(), config.labelC...`: ends the method and hands back `new Hardened( new RouterConfig(config.start(), config.hardStart(), config.lab...`.

```java
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
```

- `return new Hardened(config, kind + " already starts at the top tier and has no stronger...`: ends the method and hands back `new Hardened(config, kind + " already starts at the top tier and has no stron...`.
- `public static String weakestKind(List<Outcome> outcomes) {`: declares the method `weakestKind`, which takes `List<Outcome> outcomes` and returns `String`. It belongs to the class (`static`).
- `Map<String, Integer> counts = new TreeMap<>();`: declares `counts` of type `Integer>` and sets it to `new TreeMap<>()`.
- `for (Outcome o : outcomes) {`: repeats the block below once for each item `Outcome o` taken from `outcomes`.
- `if (o.decision().answer() != null && !o.correct()) {`: runs the block below only if `o.decision().answer() != null && !o.correct()` is true.
- `counts.merge(o.kind(), 1, Integer::sum);`: runs `counts.merge(o.kind(), 1, Integer::sum)`.
- `String best = null;`: declares `best` of type `String` and sets it to `null`.
- `for (Map.Entry<String, Integer> e : counts.entrySet()) {`: repeats the block below once for each item `Map.Entry<String, Integer> e` taken from `counts.entrySet()`.
- `if (best == null || e.getValue() > counts.get(best)) {`: runs the block below only if `best == null || e.getValue() > counts.get(best)` is true. `.get(x)` reads the item or entry for `x`.
- `best = e.getKey();`: stores `e.getKey()` into `best`.

```java
        return best;
    }

    public static boolean isLabelKind(Kind kind) {
        return kind == Kind.LABEL;
    }
}
```

- `return best;`: ends the method and hands back `best`.
- `public static boolean isLabelKind(Kind kind) {`: declares the method `isLabelKind`, which takes `Kind kind` and returns `boolean`. It belongs to the class (`static`).
- `return kind == Kind.LABEL;`: ends the method and hands back `kind == Kind.LABEL`.

#### `java/src/main/java/dev/plainround/router/application/ModelTiers.java`

```java
package dev.plainround.router.application;

import dev.plainround.router.domain.Llm.ChatModel;
import dev.plainround.router.domain.Llm.ChatRequest;
import dev.plainround.router.domain.Llm.ChatResponse;
import dev.plainround.router.domain.Llm.Message;
import dev.plainround.router.domain.Routing.PriceTable;
import dev.plainround.router.domain.Tasks;
import dev.plainround.router.domain.Tasks.Kind;
import dev.plainround.router.domain.Tasks.Task;
import java.util.List;
import java.util.Map;
```

- `package dev.plainround.router.application;`: declares that this file belongs to the package `dev.plainround.router.application`.
- `import dev.plainround.router.domain.Llm.ChatModel;`: imports the class `dev.plainround.router.domain.Llm.ChatModel` so it can be used by its short name.
- `import dev.plainround.router.domain.Llm.ChatRequest;`: imports the class `dev.plainround.router.domain.Llm.ChatRequest` so it can be used by its short name.
- `import dev.plainround.router.domain.Llm.ChatResponse;`: imports the class `dev.plainround.router.domain.Llm.ChatResponse` so it can be used by its short name.
- `import dev.plainround.router.domain.Llm.Message;`: imports the class `dev.plainround.router.domain.Llm.Message` so it can be used by its short name.
- `import dev.plainround.router.domain.Routing.PriceTable;`: imports the class `dev.plainround.router.domain.Routing.PriceTable` so it can be used by its short name.
- `import dev.plainround.router.domain.Tasks;`: imports the class `dev.plainround.router.domain.Tasks` so it can be used by its short name.
- `import dev.plainround.router.domain.Tasks.Kind;`: imports the class `dev.plainround.router.domain.Tasks.Kind` so it can be used by its short name.
- `import dev.plainround.router.domain.Tasks.Task;`: imports the class `dev.plainround.router.domain.Tasks.Task` so it can be used by its short name.
- `import java.util.List;`: imports the class `java.util.List` so it can be used by its short name.
- `import java.util.Map;`: imports the class `java.util.Map` so it can be used by its short name.
- `/** ... */`: a Javadoc comment. It says: "The three model tiers: prompts, calls and cost (a port of tiers.py)."

```java
/** The three model tiers: prompts, calls and cost (a port of tiers.py). */
public final class ModelTiers {

    public record Answered(String text, double cost, int tokens, double latency) {}

    private static int maxTokens(Kind kind) {
        return kind == Kind.LABEL ? 8 : 80;
    }

    private final ChatModel model;
    private final PromptStore prompts;
    private final Map<String, String> models;
    private final PriceTable prices;

    public ModelTiers(ChatModel model, PromptStore prompts, Map<String, String> models, PriceTable prices) {
```

- `public final class ModelTiers {`: declares the class `ModelTiers` (public, final).
- `public record Answered(String text, double cost, int tokens, double latency) {`: declares the record `Answered` with the components `String text, double cost, int tokens, double latency`.
- `private static int maxTokens(Kind kind) {`: declares the method `maxTokens`, which takes `Kind kind` and returns `int`. It belongs to the class (`static`).
- `return kind == Kind.LABEL ? 8 : 80;`: ends the method and hands back `kind == Kind.LABEL ? 8 : 80`.
- `private final ChatModel model;`: declares the field `model` of type `ChatModel`.
- `private final PromptStore prompts;`: declares the field `prompts` of type `PromptStore`.
- `private final Map<String, String> models;`: declares the field `models` of type `String>`.
- `private final PriceTable prices;`: declares the field `prices` of type `PriceTable`.
- `public ModelTiers(ChatModel model, PromptStore prompts, Map<String, String> models, Pri...`: constructor of `ModelTiers`, taking `ChatModel model, PromptStore prompts, Map<String, String> models, PriceTable prices`.

```java
        this.model = model;
        this.prompts = prompts;
        this.models = models;
        this.prices = prices;
    }

    public String prompt(Task task) {
        switch (task.kind()) {
            case LABEL:
                return Templates.render(prompts.get("label.v2"), Map.of("text", task.text()));
            case REFUND:
                return Templates.render(prompts.get("refund.v2"), Map.of("policy", Tasks.REFUND_POLICY, "text", task.text()));
            default:
                StringBuilder lines = new StringBuilder();
```

- `this.model = model;`: stores `model` into `this.model`.
- `this.prompts = prompts;`: stores `prompts` into `this.prompts`.
- `this.models = models;`: stores `models` into `this.models`.
- `this.prices = prices;`: stores `prices` into `this.prices`.
- `public String prompt(Task task) {`: declares the method `prompt`, which takes `Task task` and returns `String`.
- **New idea.** A **switch expression** picks a value by comparing one value with several `case` labels; `case X -> value` gives the value for X and `default ->` covers the rest.
- `switch (task.kind()) {`: chooses between the `case` labels below by the value of `task.kind()`.
- `case LABEL: return Templates.render(prompts.get("label.v2"), Map.of("text", task.text()));`: runs `case LABEL: return Templates.render(prompts.get("label.v2"), Map.of("text", task.text()))`. `.get(x)` reads the item or entry for `x`; `Map.of(...)` makes an unchangeable map.
- `case REFUND: return Templates.render(prompts.get("refund.v2"), Map.of("policy", Tasks.R...`: runs `case REFUND: return Templates.render(prompts.get("refund.v2"), Map.of("policy", Tasks.R...`. `.get(x)` reads the item or entry for `x`; `Map.of(...)` makes an unchangeable map.
- `default: StringBuilder lines = new StringBuilder();`: runs `default: StringBuilder lines = new StringBuilder()`. `StringBuilder` builds text piece by piece.

```java
                for (int i = 0; i < Tasks.POLICY_LINES.size(); i++) {
                    if (i > 0) {
                        lines.append('\n');
                    }
                    lines.append(i + 1).append(". ").append(Tasks.POLICY_LINES.get(i));
                }
                return Templates.render(prompts.get("policy.v2"), Map.of("policy_lines", lines.toString(), "text", task.text()));
        }
    }

    public ChatRequest request(String tier, Task task, boolean secondSample) {
        double temperature = secondSample ? 0.8 : 0.0;
        Integer seed = secondSample ? 7 : null;
        return new ChatRequest(models.get(tier), List.of(new Message("user", prompt(task))), temperature, maxTokens(task.kind()), seed);
    }
```

- `for (int i = 0; i < Tasks.POLICY_LINES.size(); i++) {`: repeats the block below as the counting loop `int i = 0; i < Tasks.POLICY_LINES.size(); i++` says.
- `if (i > 0) {`: runs the block below only if `i > 0` is true.
- `lines.append('\n');`: runs `lines.append('\n')`.
- `lines.append(i + 1).append(". ").append(Tasks.POLICY_LINES.get(i));`: runs `lines.append(i + 1).append(". ").append(Tasks.POLICY_LINES.get(i))`. `.get(x)` reads the item or entry for `x`.
- `return Templates.render(prompts.get("policy.v2"), Map.of("policy_lines", lines.toString...`: ends the method and hands back `Templates.render(prompts.get("policy.v2"), Map.of("policy_lines", lines.toStr...`. `.get(x)` reads the item or entry for `x`; `Map.of(...)` makes an unchangeable map.
- `public ChatRequest request(String tier, Task task, boolean secondSample) {`: declares the method `request`, which takes `String tier, Task task, boolean secondSample` and returns `ChatRequest`.
- `double temperature = secondSample ? 0.8 : 0.0;`: declares `temperature` of type `double` and sets it to `secondSample ? 0.8 : 0.0`.
- `Integer seed = secondSample ? 7 : null;`: declares `seed` of type `Integer` and sets it to `secondSample ? 7 : null`.
- `return new ChatRequest(models.get(tier), List.of(new Message("user", prompt(task))), te...`: ends the method and hands back `new ChatRequest(models.get(tier), List.of(new Message("user", prompt(task))),...`. `.get(x)` reads the item or entry for `x`; `List.of(...)` makes an unchangeable list.

```java
    public Answered call(String tier, Task task, boolean secondSample) {
        ChatResponse response = model.complete(request(tier, task, secondSample));
        return new Answered(response.text().strip(), prices.cost(tier, response.usage().total()), response.usage().total(), response.latencySeconds());
    }

    public double estimate(String tier, Task task, int calls) {
        int tokens = (prompt(task).length() + 2) / 3 + maxTokens(task.kind());
        return prices.estimate(tier, tokens) * calls;
    }
}
```

- `public Answered call(String tier, Task task, boolean secondSample) {`: declares the method `call`, which takes `String tier, Task task, boolean secondSample` and returns `Answered`.
- `ChatResponse response = model.complete(request(tier, task, secondSample));`: declares `response` of type `ChatResponse` and sets it to `model.complete(request(tier, task, secondSample))`.
- `return new Answered(response.text().strip(), prices.cost(tier, response.usage().total()...`: ends the method and hands back `new Answered(response.text().strip(), prices.cost(tier, response.usage().tota...`.
- `public double estimate(String tier, Task task, int calls) {`: declares the method `estimate`, which takes `String tier, Task task, int calls` and returns `double`.
- `int tokens = (prompt(task).length() + 2) / 3 + maxTokens(task.kind());`: declares `tokens` of type `int` and sets it to `(prompt(task).length() + 2) / 3 + maxTokens(task.kind())`. `.length()` is the number of characters.
- `return prices.estimate(tier, tokens) * calls;`: ends the method and hands back `prices.estimate(tier, tokens) * calls`.

#### `java/src/main/java/dev/plainround/router/application/PromptStore.java`

```java
package dev.plainround.router.application;

/** Versioned prompt templates looked up by name such as label.v2. */
public interface PromptStore {
    String get(String name);
}
```

- `package dev.plainround.router.application;`: declares that this file belongs to the package `dev.plainround.router.application`.
- `/** ... */`: a Javadoc comment. It says: "Versioned prompt templates looked up by name such as label.v2."
- **New idea.** An **interface** lists methods without bodies. A class that `implements` it must supply them. Callers that only know the interface need not know which class they hold.
- `public interface PromptStore {`: declares the interface `PromptStore` (public).
- `String get(String name);`: declares the method `get`, which takes `String name` and returns `String` (no body: implementing classes supply it).

#### `java/src/main/java/dev/plainround/router/application/Templates.java`

```java
package dev.plainround.router.application;

import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** Prompt templates use {{name}} placeholders; rendering fails loudly on a missing value. */
public final class Templates {

    private Templates() {}

    private static final Pattern PLACEHOLDER = Pattern.compile("\\{\\{([a-z_]+)\\}\\}");

    public static String render(String template, Map<String, String> values) {
```

- `package dev.plainround.router.application;`: declares that this file belongs to the package `dev.plainround.router.application`.
- `import java.util.Map;`: imports the class `java.util.Map` so it can be used by its short name.
- `import java.util.regex.Matcher;`: imports the class `java.util.regex.Matcher` so it can be used by its short name.
- `import java.util.regex.Pattern;`: imports the class `java.util.regex.Pattern` so it can be used by its short name.
- `/** ... */`: a Javadoc comment. It says: "Prompt templates use {{name}} placeholders; rendering fails loudly on a missing value."
- `public final class Templates {`: declares the class `Templates` (public, final).
- `private Templates() {`: constructor of `Templates`, taking no arguments.
- `private static final Pattern PLACEHOLDER = Pattern.compile("\\{\\{([a-z_]+)\\}\\}");`: declares the field `PLACEHOLDER` of type `Pattern` and sets it to `Pattern.compile("\\{\\{([a-z_]+)\\}\\}")`. `Pattern.compile(...)` prepares a regular expression (`regular-expressions.md`).
- `public static String render(String template, Map<String, String> values) {`: declares the method `render`, which takes `String template, Map<String, String> values` and returns `String`. It belongs to the class (`static`).

```java
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
```

- `Matcher unknownCheck = PLACEHOLDER.matcher(template);`: declares `unknownCheck` of type `Matcher` and sets it to `PLACEHOLDER.matcher(template)`. `.matcher(text)` applies a pattern to a text.
- `java.util.Set<String> present = new java.util.HashSet<>();`: declares `present` of type `java.util.Set<String>` and sets it to `new java.util.HashSet<>()`.
- **New idea.** A **while loop** repeats its block as long as the condition is true.
- `while (unknownCheck.find()) {`: repeats the block below while `unknownCheck.find()` is true.
- `present.add(unknownCheck.group(1));`: runs `present.add(unknownCheck.group(1))`. `.add(x)` appends `x`; `.group(n)` is the part of the match captured by group `n`.
- `for (String name : values.keySet()) {`: repeats the block below once for each item `String name` taken from `values.keySet()`.
- `if (!present.contains(name)) {`: runs the block below only if `!present.contains(name)` is true. `.contains(x)` tests whether `x` is in it.
- **New idea.** `throw new SomeException("message")` signals an error. Unchecked exceptions (those extending `RuntimeException`) need no declaration; checked ones (such as `IOException`) must be caught or listed after `throws`.
- `throw new IllegalArgumentException("template has no placeholder for " + name);`: signals an error: `new IllegalArgumentException("template has no placeholder for " + name)`. Normal flow stops; the nearest matching `catch` takes over.
- `Matcher m = PLACEHOLDER.matcher(template);`: declares `m` of type `Matcher` and sets it to `PLACEHOLDER.matcher(template)`. `.matcher(text)` applies a pattern to a text.
- `StringBuilder out = new StringBuilder();`: declares `out` of type `StringBuilder` and sets it to `new StringBuilder()`. `StringBuilder` builds text piece by piece.
- `while (m.find()) {`: repeats the block below while `m.find()` is true.
- `String value = values.get(m.group(1));`: declares `value` of type `String` and sets it to `values.get(m.group(1))`. `.get(x)` reads the item or entry for `x`; `.group(n)` is the part of the match captured by group `n`.

```java
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
```

- `if (value == null) {`: runs the block below only if `value == null` is true.
- `throw new IllegalArgumentException("no value for placeholder {{" + m.group(1) + "}}");`: signals an error: `new IllegalArgumentException("no value for placeholder {{" + m.group(1) + "}}")`. Normal flow stops; the nearest matching `catch` takes over.
- `m.appendReplacement(out, Matcher.quoteReplacement(value));`: runs `m.appendReplacement(out, Matcher.quoteReplacement(value))`.
- `m.appendTail(out);`: runs `m.appendTail(out)`.
- `return out.toString();`: ends the method and hands back `out.toString()`.
- `/** ... */`: a Javadoc comment. It says: "Render with only the values the template actually uses."
- `public static String renderAvailable(String template, Map<String, String> values) {`: declares the method `renderAvailable`, which takes `String template, Map<String, String> values` and returns `String`. It belongs to the class (`static`).
- `Map<String, String> used = new java.util.LinkedHashMap<>();`: declares `used` of type `String>` and sets it to `new java.util.LinkedHashMap<>()`.
- `for (Map.Entry<String, String> e : values.entrySet()) {`: repeats the block below once for each item `Map.Entry<String, String> e` taken from `values.entrySet()`.
- `if (template.contains("{{" + e.getKey() + "}}")) {`: runs the block below only if `template.contains("{{" + e.getKey() + "}}")` is true. `.contains(x)` tests whether `x` is in it.
- `used.put(e.getKey(), e.getValue());`: runs `used.put(e.getKey(), e.getValue())`. `.put(k, v)` stores value `v` under key `k`.

```java
        return render(template, used);
    }
}
```

- `return render(template, used);`: ends the method and hands back `render(template, used)`.

#### `java/src/main/java/dev/plainround/router/domain/Checks.java`

```java
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
```

- `package dev.plainround.router.domain;`: declares that this file belongs to the package `dev.plainround.router.domain`.
- `import dev.plainround.router.domain.Tasks.Kind;`: imports the class `dev.plainround.router.domain.Tasks.Kind` so it can be used by its short name.
- `import dev.plainround.router.domain.Tasks.Task;`: imports the class `dev.plainround.router.domain.Tasks.Task` so it can be used by its short name.
- `import java.util.ArrayList;`: imports the class `java.util.ArrayList` so it can be used by its short name.
- `import java.util.List;`: imports the class `java.util.List` so it can be used by its short name.
- `import java.util.regex.Matcher;`: imports the class `java.util.regex.Matcher` so it can be used by its short name.
- `import java.util.regex.Pattern;`: imports the class `java.util.regex.Pattern` so it can be used by its short name.
- `/** ... */`: a Javadoc comment. It says: "Parsing answers, grading them against the truth, and the checks the router can run (a port of checks.py)."
- `public final class Checks {`: declares the class `Checks` (public, final).
- `private Checks() {`: constructor of `Checks`, taking no arguments.

```java
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
```

- `private static final String NUMBER = "\\$?\\s*(\\d{1,3}(?:,\\d{3})+|\\d+)(?:\\.(\\d{1,2...`: declares the field `NUMBER` of type `String` and sets it to `"\\$?\\s*(\\d{1,3}(?:,\\d{3})+|\\d+)(?:\\.(\\d{1,2}))?"`.
- `private static final Pattern REFUND_LINE = Pattern.compile("refund\\s*:\\s*" + NUMBER, ...`: declares the field `REFUND_LINE` of type `Pattern` and sets it to `Pattern.compile("refund\\s*:\\s*" + NUMBER, Pattern.CASE_INSENSITIVE)`. `Pattern.compile(...)` prepares a regular expression (`regular-expressions.md`).
- `private static final Pattern BARE_AMOUNT = Pattern.compile(NUMBER);`: declares the field `BARE_AMOUNT` of type `Pattern` and sets it to `Pattern.compile(NUMBER)`. `Pattern.compile(...)` prepares a regular expression (`regular-expressions.md`).
- `private static final Pattern QUOTE = Pattern.compile("quote\\s*:\\s*[\"“']?(.+?)[\"”']?...`: declares the field `QUOTE` of type `Pattern` and sets it to `Pattern.compile("quote\\s*:\\s*[\"“']?(.+?)[\"”']?\\s*$", Pattern.CASE_INSENS...`. `Pattern.compile(...)` prepares a regular expression (`regular-expressions.md`).
- `public static String normalize(String text) {`: declares the method `normalize`, which takes `String text` and returns `String`. It belongs to the class (`static`).
- `String joined = String.join(" ", text.toLowerCase().strip().split("\\s+"));`: declares `joined` of type `String` and sets it to `String.join(" ", text.toLowerCase().strip().split("\\s+"))`. `.split(regex)` cuts text into pieces; `.join(...)` glues items into one text, or waits for a thread.
- `int end = joined.length();`: declares `end` of type `int` and sets it to `joined.length()`. `.length()` is the number of characters.
- `while (end > 0 && joined.charAt(end - 1) == '.') {`: repeats the block below while `end > 0 && joined.charAt(end - 1) == '.'` is true.
- `end--;`: adds or subtracts one.
- `return joined.substring(0, end).strip();`: ends the method and hands back `joined.substring(0, end).strip()`. `.substring(a, b)` is the part of the text from `a` up to `b`.

```java
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
```

- `private static String stripChars(String text, String chars) {`: declares the method `stripChars`, which takes `String text, String chars` and returns `String`. It belongs to the class (`static`).
- `int start = 0;`: declares `start` of type `int` and sets it to `0`.
- `int end = text.length();`: declares `end` of type `int` and sets it to `text.length()`. `.length()` is the number of characters.
- `while (start < end && chars.indexOf(text.charAt(start)) >= 0) {`: repeats the block below while `start < end && chars.indexOf(text.charAt(start)) >= 0` is true.
- `start++;`: adds or subtracts one.
- `while (end > start && chars.indexOf(text.charAt(end - 1)) >= 0) {`: repeats the block below while `end > start && chars.indexOf(text.charAt(end - 1)) >= 0` is true.
- `end--;`: adds or subtracts one.
- `return text.substring(start, end);`: ends the method and hands back `text.substring(start, end)`. `.substring(a, b)` is the part of the text from `a` up to `b`.
- `public static String parseLabel(String text) {`: declares the method `parseLabel`, which takes `String text` and returns `String`. It belongs to the class (`static`).
- `String word = stripChars(normalize(text), "\"''*");`: declares `word` of type `String` and sets it to `stripChars(normalize(text), "\"''*")`.

```java
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
```

- `return Tasks.LABELS.contains(word) ? word : null;`: ends the method and hands back `Tasks.LABELS.contains(word) ? word : null`. `.contains(x)` tests whether `x` is in it.
- `private static int cents(Matcher m) {`: declares the method `cents`, which takes `Matcher m` and returns `int`. It belongs to the class (`static`).
- `int dollars = Integer.parseInt(m.group(1).replace(",", ""));`: declares `dollars` of type `int` and sets it to `Integer.parseInt(m.group(1).replace(",", ""))`. `.group(n)` is the part of the match captured by group `n`.
- `String fraction = ((m.group(2) == null ? "" : m.group(2)) + "00").substring(0, 2);`: declares `fraction` of type `String` and sets it to `((m.group(2) == null ? "" : m.group(2)) + "00").substring(0, 2)`. `.substring(a, b)` is the part of the text from `a` up to `b`; `.group(n)` is the part of the match captured by group `n`.
- `return dollars * 100 + Integer.parseInt(fraction);`: ends the method and hands back `dollars * 100 + Integer.parseInt(fraction)`.
- `public static Integer parseAmountCents(String text) {`: declares the method `parseAmountCents`, which takes `String text` and returns `Integer`. It belongs to the class (`static`).
- `Matcher m = REFUND_LINE.matcher(text);`: declares `m` of type `Matcher` and sets it to `REFUND_LINE.matcher(text)`. `.matcher(text)` applies a pattern to a text.
- `Integer last = null;`: declares `last` of type `Integer` and sets it to `null`.
- `while (m.find()) {`: repeats the block below while `m.find()` is true.
- `last = cents(m);`: stores `cents(m)` into `last`.

```java
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
```

- `if (last != null) {`: runs the block below only if `last != null` is true.
- `return last;`: ends the method and hands back `last`.
- `Matcher bare = BARE_AMOUNT.matcher(text.strip());`: declares `bare` of type `Matcher` and sets it to `BARE_AMOUNT.matcher(text.strip())`. `.matcher(text)` applies a pattern to a text.
- `return bare.matches() ? cents(bare) : null;`: ends the method and hands back `bare.matches() ? cents(bare) : null`.
- `public static String parseQuote(String text) {`: declares the method `parseQuote`, which takes `String text` and returns `String`. It belongs to the class (`static`).
- `Matcher m = QUOTE.matcher(text);`: declares `m` of type `Matcher` and sets it to `QUOTE.matcher(text)`. `.matcher(text)` applies a pattern to a text.
- `return m.find() ? normalize(m.group(1)) : null;`: ends the method and hands back `m.find() ? normalize(m.group(1)) : null`. `.group(n)` is the part of the match captured by group `n`.
- `public static Integer quotedLineIndex(String text) {`: declares the method `quotedLineIndex`, which takes `String text` and returns `Integer`. It belongs to the class (`static`).
- `String quote = parseQuote(text);`: declares `quote` of type `String` and sets it to `parseQuote(text)`.

```java
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
```

- `if (quote == null) {`: runs the block below only if `quote == null` is true.
- `return null;`: ends the method and hands back `null`.
- `for (int i = 0; i < Tasks.POLICY_LINES.size(); i++) {`: repeats the block below as the counting loop `int i = 0; i < Tasks.POLICY_LINES.size(); i++` says.
- `if (normalize(Tasks.POLICY_LINES.get(i)).equals(quote)) {`: runs the block below only if `normalize(Tasks.POLICY_LINES.get(i)).equals(quote)` is true. `.equals(x)` compares two objects by value; `.get(x)` reads the item or entry for `x`.
- `return i;`: ends the method and hands back `i`.
- `return null;`: ends the method and hands back `null`.
- `public static boolean isCorrect(Task task, String text) {`: declares the method `isCorrect`, which takes `Task task, String text` and returns `boolean`. It belongs to the class (`static`).
- `if (task.kind() == Kind.LABEL) {`: runs the block below only if `task.kind() == Kind.LABEL` is true.
- `String label = parseLabel(text);`: declares `label` of type `String` and sets it to `parseLabel(text)`.

```java
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
```

- `return label != null && label.equals(task.gold());`: ends the method and hands back `label != null && label.equals(task.gold())`. `.equals(x)` compares two objects by value.
- `if (task.kind() == Kind.REFUND) {`: runs the block below only if `task.kind() == Kind.REFUND` is true.
- `Integer amount = parseAmountCents(text);`: declares `amount` of type `Integer` and sets it to `parseAmountCents(text)`.
- `return amount != null && amount == Tasks.expectedRefundCents(task);`: ends the method and hands back `amount != null && amount == Tasks.expectedRefundCents(task)`.
- `Integer index = quotedLineIndex(text);`: declares `index` of type `Integer` and sets it to `quotedLineIndex(text)`.
- `return index != null && index.equals(task.gold());`: ends the method and hands back `index != null && index.equals(task.gold())`. `.equals(x)` compares two objects by value.
- `public static boolean checkLabelShape(String text) {`: declares the method `checkLabelShape`, which takes `String text` and returns `boolean`. It belongs to the class (`static`).
- `return parseLabel(text) != null;`: ends the method and hands back `parseLabel(text) != null`.

```java
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
```

- `public static boolean checkLabelAgreement(String text, String second) {`: declares the method `checkLabelAgreement`, which takes `String text, String second` and returns `boolean`. It belongs to the class (`static`).
- `String first = parseLabel(text);`: declares `first` of type `String` and sets it to `parseLabel(text)`.
- `return first != null && first.equals(parseLabel(second));`: ends the method and hands back `first != null && first.equals(parseLabel(second))`. `.equals(x)` compares two objects by value.
- `public static boolean checkRefund(Task task, String text) {`: declares the method `checkRefund`, which takes `Task task, String text` and returns `boolean`. It belongs to the class (`static`).
- `Integer amount = parseAmountCents(text);`: declares `amount` of type `Integer` and sets it to `parseAmountCents(text)`.
- `return amount != null && amount == Tasks.expectedRefundCents(task);`: ends the method and hands back `amount != null && amount == Tasks.expectedRefundCents(task)`.
- `private static final java.util.Set<String> STOPWORDS = java.util.Set.of( "a", "an", "th...`: declares the field `STOPWORDS` of type `java.util.Set<String>` and sets it to `java.util.Set.of( "a", "an", "the", "of", "to", "in", "on", "for", "is", "are...`. `Set.of(...)` makes an unchangeable set.

```java
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
```

- `private static final Pattern WORD = Pattern.compile("[a-z0-9]+");`: declares the field `WORD` of type `Pattern` and sets it to `Pattern.compile("[a-z0-9]+")`. `Pattern.compile(...)` prepares a regular expression (`regular-expressions.md`).
- `public static java.util.Set<String> contentWords(String text) {`: declares the method `contentWords`, which takes `String text` and returns `java.util.Set<String>`. It belongs to the class (`static`).
- `java.util.Set<String> words = new java.util.HashSet<>();`: declares `words` of type `java.util.Set<String>` and sets it to `new java.util.HashSet<>()`.
- `Matcher m = WORD.matcher(text.toLowerCase());`: declares `m` of type `Matcher` and sets it to `WORD.matcher(text.toLowerCase())`. `.matcher(text)` applies a pattern to a text.
- `while (m.find()) {`: repeats the block below while `m.find()` is true.
- `String w = m.group();`: declares `w` of type `String` and sets it to `m.group()`. `.group(n)` is the part of the match captured by group `n`.
- `if (STOPWORDS.contains(w)) {`: runs the block below only if `STOPWORDS.contains(w)` is true. `.contains(x)` tests whether `x` is in it.
- `continue;`: skips to the next round of the loop.
- `words.add(w.length() > 3 && w.endsWith("s") ? w.substring(0, w.length() - 1) : w);`: runs `words.add(w.length() > 3 && w.endsWith("s") ? w.substring(0, w.length() - 1) : w)`. `.length()` is the number of characters; `.add(x)` appends `x`; `.substring(a, b)` is the part of the text from `a` up to `b`.
- `return words;`: ends the method and hands back `words`.

```java
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
```

- `/** ... */`: a Javadoc comment. It says: "The policy line sharing the most content words with the question, or null when two lines tie for most."
- `public static Integer bestMatchingLine(String question) {`: declares the method `bestMatchingLine`, which takes `String question` and returns `Integer`. It belongs to the class (`static`).
- `java.util.Set<String> words = contentWords(question);`: declares `words` of type `java.util.Set<String>` and sets it to `contentWords(question)`.
- `int top = 0;`: declares `top` of type `int` and sets it to `0`.
- `int count = 0;`: declares `count` of type `int` and sets it to `0`.
- `int index = -1;`: declares `index` of type `int` and sets it to `-1`.
- `for (int i = 0; i < Tasks.POLICY_LINES.size(); i++) {`: repeats the block below as the counting loop `int i = 0; i < Tasks.POLICY_LINES.size(); i++` says.
- `java.util.Set<String> overlap = new java.util.HashSet<>(contentWords(Tasks.POLICY_LINES...`: declares `overlap` of type `java.util.Set<String>` and sets it to `new java.util.HashSet<>(contentWords(Tasks.POLICY_LINES.get(i)))`. `.get(x)` reads the item or entry for `x`.
- `overlap.retainAll(words);`: runs `overlap.retainAll(words)`.
- `int score = overlap.size();`: declares `score` of type `int` and sets it to `overlap.size()`. `.size()` is the number of items.
- `if (score > top) {`: runs the block below only if `score > top` is true.
- `top = score;`: stores `score` into `top`.
- `count = 1;`: stores `1` into `count`.
- `index = i;`: stores `i` into `index`.

```java
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
```

- `else if (score == top) {`: otherwise, runs the block below only if `score == top` is true.
- `count++;`: adds or subtracts one.
- `return top > 0 && count == 1 ? index : null;`: ends the method and hands back `top > 0 && count == 1 ? index : null`.
- `public static boolean checkPolicyOverlap(String question, String text) {`: declares the method `checkPolicyOverlap`, which takes `String question, String text` and returns `boolean`. It belongs to the class (`static`).
- `Integer quoted = quotedLineIndex(text);`: declares `quoted` of type `Integer` and sets it to `quotedLineIndex(text)`.
- `return quoted != null && quoted.equals(bestMatchingLine(question));`: ends the method and hands back `quoted != null && quoted.equals(bestMatchingLine(question))`. `.equals(x)` compares two objects by value.
- `public static boolean checkPolicy(String text) {`: declares the method `checkPolicy`, which takes `String text` and returns `boolean`. It belongs to the class (`static`).
- `return quotedLineIndex(text) != null;`: ends the method and hands back `quotedLineIndex(text) != null`.

```java
    public static List<String> noItems() {
        return new ArrayList<>();
    }
}
```

- `public static List<String> noItems() {`: declares the method `noItems`, which takes no arguments and returns `List<String>`. It belongs to the class (`static`).
- `return new ArrayList<>();`: ends the method and hands back `new ArrayList<>()`. `new ArrayList<>()` makes an empty changeable list.

#### `java/src/main/java/dev/plainround/router/domain/Llm.java`

```java
package dev.plainround.router.domain;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;
import java.util.List;
import java.util.Locale;
import java.util.Set;

/** Value types for talking to a chat model. Nothing here knows a vendor, an SDK or HTTP. */
public final class Llm {

    private Llm() {}
```

- `package dev.plainround.router.domain;`: declares that this file belongs to the package `dev.plainround.router.domain`.
- `import java.nio.charset.StandardCharsets;`: imports the class `java.nio.charset.StandardCharsets` so it can be used by its short name.
- `import java.security.MessageDigest;`: imports the class `java.security.MessageDigest` so it can be used by its short name.
- `import java.security.NoSuchAlgorithmException;`: imports the class `java.security.NoSuchAlgorithmException` so it can be used by its short name.
- `import java.util.HexFormat;`: imports the class `java.util.HexFormat` so it can be used by its short name.
- `import java.util.List;`: imports the class `java.util.List` so it can be used by its short name.
- `import java.util.Locale;`: imports the class `java.util.Locale` so it can be used by its short name.
- `import java.util.Set;`: imports the class `java.util.Set` so it can be used by its short name.
- `/** ... */`: a Javadoc comment. It says: "Value types for talking to a chat model."
- `public final class Llm {`: declares the class `Llm` (public, final).
- `private Llm() {`: constructor of `Llm`, taking no arguments.

```java
    /** A failure of a model call. */
    public static class ModelException extends RuntimeException {
        public ModelException(String message) {
            super(message);
        }
    }

    /** The recorded adapter has no response for this exact request. */
    public static final class FixtureMissException extends ModelException {
        public FixtureMissException(String message) {
            super(message);
        }
    }
```

- `/** ... */`: a Javadoc comment. It says: "A failure of a model call."
- `public static class ModelException extends RuntimeException {`: declares the class `ModelException` (public, static). Relations: `extends RuntimeException`.
- `public ModelException(String message) {`: constructor of `ModelException`, taking `String message`.
- `super(message);`: runs `super(message)`.
- `/** ... */`: a Javadoc comment. It says: "The recorded adapter has no response for this exact request."
- `public static final class FixtureMissException extends ModelException {`: declares the class `FixtureMissException` (public, static, final). Relations: `extends ModelException`.
- `public FixtureMissException(String message) {`: constructor of `FixtureMissException`, taking `String message`.
- `super(message);`: runs `super(message)`.

```java
    private static final Set<String> ROLES = Set.of("system", "user", "assistant");

    /** One chat message. */
    public record Message(String role, String content) {
        public Message {
            if (!ROLES.contains(role)) {
                throw new IllegalArgumentException("unknown role " + role);
            }
        }
    }

    /** Everything that decides a model's answer. */
    public record ChatRequest(String model, List<Message> messages, double temperature, int maxTokens, Integer seed) {
        public ChatRequest {
```

- `private static final Set<String> ROLES = Set.of("system", "user", "assistant");`: declares the field `ROLES` of type `Set<String>` and sets it to `Set.of("system", "user", "assistant")`. `Set.of(...)` makes an unchangeable set.
- `/** ... */`: a Javadoc comment. It says: "One chat message."
- `public record Message(String role, String content) {`: declares the record `Message` with the components `String role, String content`.
- `public Message {`: opens a block: `public Message {`.
- `if (!ROLES.contains(role)) {`: runs the block below only if `!ROLES.contains(role)` is true. `.contains(x)` tests whether `x` is in it.
- `throw new IllegalArgumentException("unknown role " + role);`: signals an error: `new IllegalArgumentException("unknown role " + role)`. Normal flow stops; the nearest matching `catch` takes over.
- `/** ... */`: a Javadoc comment. It says: "Everything that decides a model's answer."
- `public record ChatRequest(String model, List<Message> messages, double temperature, int...`: declares the record `ChatRequest` with the components `String model, List<Message> messages, double temperature, int maxTokens, Integer seed`.
- `public ChatRequest {`: opens a block: `public ChatRequest {`.

```java
            if (model == null || model.isEmpty()) {
                throw new IllegalArgumentException("model must not be empty");
            }
            if (messages.isEmpty()) {
                throw new IllegalArgumentException("a request needs at least one message");
            }
            if (temperature < 0.0 || temperature > 2.0) {
                throw new IllegalArgumentException("temperature must be between 0 and 2");
            }
            if (maxTokens <= 0) {
                throw new IllegalArgumentException("max_tokens must be positive");
            }
            messages = List.copyOf(messages);
        }
```

- `if (model == null || model.isEmpty()) {`: runs the block below only if `model == null || model.isEmpty()` is true. `.isEmpty()` is true when there is nothing in it.
- `throw new IllegalArgumentException("model must not be empty");`: signals an error: `new IllegalArgumentException("model must not be empty")`. Normal flow stops; the nearest matching `catch` takes over.
- `if (messages.isEmpty()) {`: runs the block below only if `messages.isEmpty()` is true. `.isEmpty()` is true when there is nothing in it.
- `throw new IllegalArgumentException("a request needs at least one message");`: signals an error: `new IllegalArgumentException("a request needs at least one message")`. Normal flow stops; the nearest matching `catch` takes over.
- `if (temperature < 0.0 || temperature > 2.0) {`: runs the block below only if `temperature < 0.0 || temperature > 2.0` is true.
- `throw new IllegalArgumentException("temperature must be between 0 and 2");`: signals an error: `new IllegalArgumentException("temperature must be between 0 and 2")`. Normal flow stops; the nearest matching `catch` takes over.
- `if (maxTokens <= 0) {`: runs the block below only if `maxTokens <= 0` is true.
- `throw new IllegalArgumentException("max_tokens must be positive");`: signals an error: `new IllegalArgumentException("max_tokens must be positive")`. Normal flow stops; the nearest matching `catch` takes over.
- `messages = List.copyOf(messages);`: stores `List.copyOf(messages)` into `messages`. `List.copyOf(x)` makes an unchangeable copy.

```java
        /** The same hash as the Python port, so both read one fixture file. */
        public String fixtureKey() {
            StringBuilder joined = new StringBuilder();
            joined.append(model).append('\u001e');
            joined.append(String.format(Locale.ROOT, "%.3f", temperature)).append('\u001e');
            joined.append(maxTokens).append('\u001e');
            joined.append(seed == null ? "-" : seed.toString());
            for (Message m : messages) {
                joined.append('\u001e').append(m.role()).append('\u001f').append(m.content());
            }
            try {
                byte[] digest = MessageDigest.getInstance("SHA-256").digest(joined.toString().getBytes(StandardCharsets.UTF_8));
                return HexFormat.of().formatHex(digest);
            } catch (NoSuchAlgorithmException e) {
                throw new IllegalStateException(e);
            }
        }
    }
```

- `/** ... */`: a Javadoc comment. It says: "The same hash as the Python port, so both read one fixture file."
- `public String fixtureKey() {`: declares the method `fixtureKey`, which takes no arguments and returns `String`.
- `StringBuilder joined = new StringBuilder();`: declares `joined` of type `StringBuilder` and sets it to `new StringBuilder()`. `StringBuilder` builds text piece by piece.
- `joined.append(model).append('\u001e');`: runs `joined.append(model).append('\u001e')`.
- `joined.append(String.format(Locale.ROOT, "%.3f", temperature)).append('\u001e');`: runs `joined.append(String.format(Locale.ROOT, "%.3f", temperature)).append('\u001e')`. `String.format(pattern, values)` fills `%` places of the pattern; `Locale.ROOT` fixes number and case formatting.
- `joined.append(maxTokens).append('\u001e');`: runs `joined.append(maxTokens).append('\u001e')`.
- `joined.append(seed == null ? "-" : seed.toString());`: stores `= null ? "-" : seed.toString())` into `joined.append(seed`.
- `for (Message m : messages) {`: repeats the block below once for each item `Message m` taken from `messages`.
- `joined.append('\u001e').append(m.role()).append('\u001f').append(m.content());`: runs `joined.append('\u001e').append(m.role()).append('\u001f').append(m.content())`.
- **New idea.** **try / catch** handles errors (*exceptions*). If code in `try` throws an exception of the type named in `catch`, that block runs. `finally` always runs. `try (resource)` closes the resource at the end.
- `try {`: tries the block below; an exception it throws can be caught by the `catch` that follows.
- `byte[] digest = MessageDigest.getInstance("SHA-256").digest(joined.toString().getBytes(...`: declares `digest` of type `byte[]` and sets it to `MessageDigest.getInstance("SHA-256").digest(joined.toString().getBytes(Standa...`. `MessageDigest.getInstance("SHA-256")` makes a hash calculator; `.getBytes(charset)` turns text into bytes.
- `return HexFormat.of().formatHex(digest);`: ends the method and hands back `HexFormat.of().formatHex(digest)`. `HexFormat.formatHex(bytes)` writes bytes as hexadecimal.
- `catch (NoSuchAlgorithmException e) {`: runs when the block above threw `NoSuchAlgorithmException e`.
- `throw new IllegalStateException(e);`: signals an error: `new IllegalStateException(e)`. Normal flow stops; the nearest matching `catch` takes over.

```java
    /** Billed token counts. */
    public record Usage(int inputTokens, int outputTokens) {
        public int total() {
            return inputTokens + outputTokens;
        }
    }

    /** A completed call. */
    public record ChatResponse(String text, Usage usage, String model, String finishReason, double latencySeconds) {}

    /** The one port the application needs from a model. */
    public interface ChatModel {
        ChatResponse complete(ChatRequest request);
    }
}
```

- `/** ... */`: a Javadoc comment. It says: "Billed token counts."
- `public record Usage(int inputTokens, int outputTokens) {`: declares the record `Usage` with the components `int inputTokens, int outputTokens`.
- `public int total() {`: declares the method `total`, which takes no arguments and returns `int`.
- `return inputTokens + outputTokens;`: ends the method and hands back `inputTokens + outputTokens`.
- `/** ... */`: a Javadoc comment. It says: "A completed call."
- `public record ChatResponse(String text, Usage usage, String model, String finishReason,...`: declares the record `ChatResponse` with the components `String text, Usage usage, String model, String finishReason, double latencySeconds`.
- `/** ... */`: a Javadoc comment. It says: "The one port the application needs from a model."
- `public interface ChatModel {`: declares the interface `ChatModel` (public).
- `ChatResponse complete(ChatRequest request);`: declares the method `complete`, which takes `ChatRequest request` and returns `ChatResponse` (no body: implementing classes supply it).

#### `java/src/main/java/dev/plainround/router/domain/Routing.java`

```java
package dev.plainround.router.domain;

import java.util.List;
import java.util.Map;

/** Pricing, router configuration, the daily budget, signals and metrics (ports of pricing.py, routing.py, signals.py, metrics.py). */
public final class Routing {

    private Routing() {}

    public static final List<String> TIERS = List.of("small", "medium", "large");

    public record Bar(double falseAcceptBar, double hardAccuracyBar, double accuracyMargin, double requestCap, double tightenAt, List<Double> dayBudgetFractions) {}
```

- `package dev.plainround.router.domain;`: declares that this file belongs to the package `dev.plainround.router.domain`.
- `import java.util.List;`: imports the class `java.util.List` so it can be used by its short name.
- `import java.util.Map;`: imports the class `java.util.Map` so it can be used by its short name.
- `/** ... */`: a Javadoc comment. It says: "Pricing, router configuration, the daily budget, signals and metrics (ports of pricing.py, routing.py, signals.py, metrics.py)."
- `public final class Routing {`: declares the class `Routing` (public, final).
- `private Routing() {`: constructor of `Routing`, taking no arguments.
- `public static final List<String> TIERS = List.of("small", "medium", "large");`: declares the field `TIERS` of type `List<String>` and sets it to `List.of("small", "medium", "large")`. `List.of(...)` makes an unchangeable list.
- `public record Bar(double falseAcceptBar, double hardAccuracyBar, double accuracyMargin,...`: declares the record `Bar` with the components `double falseAcceptBar, double hardAccuracyBar, double accuracyMargin, double requestCap, double tightenAt, List<Double> dayBudgetFractions`.

```java
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
```

- `public record PriceTable(String asOf, Map<String, Double> per1kTokens) {`: declares the record `PriceTable` with the components `String asOf, Map<String, Double> per1kTokens`.
- `public PriceTable {`: opens a block: `public PriceTable {`.
- `for (String tier : TIERS) {`: repeats the block below once for each item `String tier` taken from `TIERS`.
- `if (!per1kTokens.containsKey(tier)) {`: runs the block below only if `!per1kTokens.containsKey(tier)` is true.
- `throw new IllegalArgumentException("price table lacks tier " + tier);`: signals an error: `new IllegalArgumentException("price table lacks tier " + tier)`. Normal flow stops; the nearest matching `catch` takes over.
- `public double cost(String tier, int totalTokens) {`: declares the method `cost`, which takes `String tier, int totalTokens` and returns `double`.
- `return totalTokens / 1000.0 * per1kTokens.get(tier);`: ends the method and hands back `totalTokens / 1000.0 * per1kTokens.get(tier)`. `.get(x)` reads the item or entry for `x`.
- `public double estimate(String tier, int tokens) {`: declares the method `estimate`, which takes `String tier, int tokens` and returns `double`.

```java
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
```

- `return tokens / 1000.0 * per1kTokens.get(tier);`: ends the method and hands back `tokens / 1000.0 * per1kTokens.get(tier)`. `.get(x)` reads the item or entry for `x`.
- `public record RouterConfig(Map<String, String> start, Map<String, String> hardStart, St...`: declares the record `RouterConfig` with the components `Map<String, String> start, Map<String, String> hardStart, String labelCheck, double requestCap, double tightenAt, String policyCheck`.
- `public int startIndex(String kind, boolean hard) {`: declares the method `startIndex`, which takes `String kind, boolean hard` and returns `int`.
- `String tier = hard && hardStart.get(kind) != null && !hardStart.get(kind).isEmpty() ? h...`: declares `tier` of type `String` and sets it to `hard && hardStart.get(kind) != null && !hardStart.get(kind).isEmpty() ? hardS...`. `.isEmpty()` is true when there is nothing in it; `.get(x)` reads the item or entry for `x`.
- `return TIERS.indexOf(tier);`: ends the method and hands back `TIERS.indexOf(tier)`.
- `public static final class DayBudget {`: declares the class `DayBudget` (public, static, final).
- `private final double budget;`: declares the field `budget` of type `double`.
- `private double used;`: declares the field `used` of type `double`.

```java
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
```

- `public DayBudget(double budget) {`: constructor of `DayBudget`, taking `double budget`.
- `if (budget <= 0) {`: runs the block below only if `budget <= 0` is true.
- `throw new IllegalArgumentException("a budget must be positive");`: signals an error: `new IllegalArgumentException("a budget must be positive")`. Normal flow stops; the nearest matching `catch` takes over.
- `this.budget = budget;`: stores `budget` into `this.budget`.
- `public double budget() {`: declares the method `budget`, which takes no arguments and returns `double`.
- `return budget;`: ends the method and hands back `budget`.
- `public double used() {`: declares the method `used`, which takes no arguments and returns `double`.
- `return used;`: ends the method and hands back `used`.

```java
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
```

- `public double usedShare() {`: declares the method `usedShare`, which takes no arguments and returns `double`.
- `return used / budget;`: ends the method and hands back `used / budget`.
- `public void add(double amount) {`: declares the method `add`, which takes `double amount` and returns `void`.
- `used += amount;`: adds `amount` with `used`.
- `public record Attempt(String tier, boolean passed, double cost, int tokens) {`: declares the record `Attempt` with the components `String tier, boolean passed, double cost, int tokens`.
- `public record Decision(String taskId, String answer, String servedBy, List<Attempt> att...`: declares the record `Decision` with the components `String taskId, String answer, String servedBy, List<Attempt> attempts, double spent, int tokens, double shareBefore, List<String> tags`.
- `public static boolean hardSignal(Tasks.Task task) {`: declares the method `hardSignal`, which takes `Tasks.Task task` and returns `boolean`. It belongs to the class (`static`).

```java
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
```

- `String lowered = task.text().toLowerCase();`: declares `lowered` of type `String` and sets it to `task.text().toLowerCase()`.
- `java.util.Set<String> ids = new java.util.HashSet<>();`: declares `ids` of type `java.util.Set<String>` and sets it to `new java.util.HashSet<>()`.
- `java.util.regex.Matcher m = Tasks.ORDER_ID.matcher(task.text());`: declares `m` of type `java.util.regex.Matcher` and sets it to `Tasks.ORDER_ID.matcher(task.text())`. `.matcher(text)` applies a pattern to a text.
- `while (m.find()) {`: repeats the block below while `m.find()` is true.
- `ids.add(m.group());`: runs `ids.add(m.group())`. `.add(x)` appends `x`; `.group(n)` is the part of the match captured by group `n`.
- `return ids.size() >= 2 || Tasks.EXCEPTION_WORDS.stream().anyMatch(lowered::contains);`: ends the method and hands back `ids.size() >= 2 || Tasks.EXCEPTION_WORDS.stream().anyMatch(lowered::contains)`. `.size()` is the number of items; `.stream()` starts a pipeline over the items.
- `public record Rate(int successes, int trials, double value, double low, double high) {`: declares the record `Rate` with the components `int successes, int trials, double value, double low, double high`.
- `public static Rate rate(int successes, int trials) {`: declares the method `rate`, which takes `int successes, int trials` and returns `Rate`. It belongs to the class (`static`).
- `Stats.Interval w = Stats.wilson(successes, trials);`: declares `w` of type `Stats.Interval` and sets it to `Stats.wilson(successes, trials)`.
- `return new Rate(successes, trials, trials == 0 ? 0.0 : (double) successes / trials, w.l...`: ends the method and hands back `new Rate(successes, trials, trials == 0 ? 0.0 : (double) successes / trials, ...`.

```java
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
```

- `public static Double costPerCorrect(double totalCost, int correct) {`: declares the method `costPerCorrect`, which takes `double totalCost, int correct` and returns `Double`. It belongs to the class (`static`).
- `return correct == 0 ? null : totalCost / correct;`: ends the method and hands back `correct == 0 ? null : totalCost / correct`.
- `public static double[] bootstrapCostPerCorrect(List<Double> costs, List<Boolean> correc...`: declares the method `bootstrapCostPerCorrect`, which takes `List<Double> costs, List<Boolean> corrects` and returns `double[]`. It belongs to the class (`static`).
- `int n = costs.size();`: declares `n` of type `int` and sets it to `costs.size()`. `.size()` is the number of items.
- `if (n == 0) {`: runs the block below only if `n == 0` is true.
- `return new double[] {0.0, 0.0};`: ends the method and hands back `new double[] {0.0, 0.0}`.
- `int resamples = 2000;`: declares `resamples` of type `int` and sets it to `2000`.
- `Stats.SplitMix64 rng = new Stats.SplitMix64(7);`: declares `rng` of type `Stats.SplitMix64` and sets it to `new Stats.SplitMix64(7)`.
- `double[] values = new double[resamples];`: declares `values` of type `double[]` and sets it to `new double[resamples]`.
- `for (int r = 0; r < resamples; r++) {`: repeats the block below as the counting loop `int r = 0; r < resamples; r++` says.
- `double total = 0.0;`: declares `total` of type `double` and sets it to `0.0`.

```java
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
```

- `int right = 0;`: declares `right` of type `int` and sets it to `0`.
- `for (int k = 0; k < n; k++) {`: repeats the block below as the counting loop `int k = 0; k < n; k++` says.
- `int i = rng.below(n);`: declares `i` of type `int` and sets it to `rng.below(n)`.
- `total += costs.get(i);`: adds `costs.get(i)` with `total`. `.get(x)` reads the item or entry for `x`.
- `right += corrects.get(i) ? 1 : 0;`: adds `corrects.get(i) ? 1 : 0` with `right`. `.get(x)` reads the item or entry for `x`.
- `values[r] = right == 0 ? Double.POSITIVE_INFINITY : total / right;`: stores `right == 0 ? Double.POSITIVE_INFINITY : total / right` into `values[r]`.
- `java.util.Arrays.sort(values);`: runs `java.util.Arrays.sort(values)`.
- `return new double[] {values[(int) (0.025 * resamples)], values[Math.min(resamples - 1, ...`: ends the method and hands back `new double[] {values[(int) (0.025 * resamples)], values[Math.min(resamples - ...`. `Math.xxx` is a standard maths function.
- `public static double[] bootstrapAccuracyDifference(List<Boolean> a, List<Boolean> b) {`: declares the method `bootstrapAccuracyDifference`, which takes `List<Boolean> a, List<Boolean> b` and returns `double[]`. It belongs to the class (`static`).
- `int n = a.size();`: declares `n` of type `int` and sets it to `a.size()`. `.size()` is the number of items.

```java
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
```

- `if (n == 0) {`: runs the block below only if `n == 0` is true.
- `return new double[] {0.0, 0.0, 0.0};`: ends the method and hands back `new double[] {0.0, 0.0, 0.0}`.
- `double[] diffs = new double[n];`: declares `diffs` of type `double[]` and sets it to `new double[n]`.
- `double sum = 0.0;`: declares `sum` of type `double` and sets it to `0.0`.
- `for (int i = 0; i < n; i++) {`: repeats the block below as the counting loop `int i = 0; i < n; i++` says.
- `diffs[i] = (a.get(i) ? 1.0 : 0.0) - (b.get(i) ? 1.0 : 0.0);`: stores `(a.get(i) ? 1.0 : 0.0) - (b.get(i) ? 1.0 : 0.0)` into `diffs[i]`. `.get(x)` reads the item or entry for `x`.
- `sum += diffs[i];`: adds `diffs[i]` with `sum`.
- `int resamples = 2000;`: declares `resamples` of type `int` and sets it to `2000`.
- `Stats.SplitMix64 rng = new Stats.SplitMix64(7);`: declares `rng` of type `Stats.SplitMix64` and sets it to `new Stats.SplitMix64(7)`.
- `double[] means = new double[resamples];`: declares `means` of type `double[]` and sets it to `new double[resamples]`.
- `for (int r = 0; r < resamples; r++) {`: repeats the block below as the counting loop `int r = 0; r < resamples; r++` says.
- `double total = 0.0;`: declares `total` of type `double` and sets it to `0.0`.

```java
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
```

- `for (int k = 0; k < n; k++) {`: repeats the block below as the counting loop `int k = 0; k < n; k++` says.
- `total += diffs[rng.below(n)];`: adds `diffs[rng.below(n)]` with `total`.
- `means[r] = total / n;`: stores `total / n` into `means[r]`.
- `java.util.Arrays.sort(means);`: runs `java.util.Arrays.sort(means)`.
- `return new double[] {sum / n, means[(int) (0.025 * resamples)], means[Math.min(resample...`: ends the method and hands back `new double[] {sum / n, means[(int) (0.025 * resamples)], means[Math.min(resam...`. `Math.xxx` is a standard maths function.
- `public record CheckRates(int accepted, int wrong, int right, int falseAccepts, int fals...`: declares the record `CheckRates` with the components `int accepted, int wrong, int right, int falseAccepts, int falseRejects, double falseAcceptRate, double falseRejectRate, double wrongAmong...`.
- `public static CheckRates checkRates(List<Boolean> passed, List<Boolean> correct) {`: declares the method `checkRates`, which takes `List<Boolean> passed, List<Boolean> correct` and returns `CheckRates`. It belongs to the class (`static`).
- `int accepted = 0;`: declares `accepted` of type `int` and sets it to `0`.
- `int wrong = 0;`: declares `wrong` of type `int` and sets it to `0`.

```java
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
```

- `int falseAccepts = 0;`: declares `falseAccepts` of type `int` and sets it to `0`.
- `int falseRejects = 0;`: declares `falseRejects` of type `int` and sets it to `0`.
- `for (int i = 0; i < passed.size(); i++) {`: repeats the block below as the counting loop `int i = 0; i < passed.size(); i++` says.
- `boolean p = passed.get(i);`: declares `p` of type `boolean` and sets it to `passed.get(i)`. `.get(x)` reads the item or entry for `x`.
- `boolean c = correct.get(i);`: declares `c` of type `boolean` and sets it to `correct.get(i)`. `.get(x)` reads the item or entry for `x`.
- `accepted += p ? 1 : 0;`: adds `p ? 1 : 0` with `accepted`.
- `wrong += c ? 0 : 1;`: adds `c ? 0 : 1` with `wrong`.
- `falseAccepts += p && !c ? 1 : 0;`: adds `p && !c ? 1 : 0` with `falseAccepts`.
- `falseRejects += !p && c ? 1 : 0;`: adds `!p && c ? 1 : 0` with `falseRejects`.
- `int right = correct.size() - wrong;`: declares `right` of type `int` and sets it to `correct.size() - wrong`. `.size()` is the number of items.
- `return new CheckRates( accepted, wrong, right, falseAccepts, falseRejects, wrong == 0 ?...`: ends the method and hands back `new CheckRates( accepted, wrong, right, falseAccepts, falseRejects, wrong == ...`.

#### `java/src/main/java/dev/plainround/router/domain/Stats.java`

```java
package dev.plainround.router.domain;

import java.util.Arrays;
import java.util.List;

/** Small statistics, written to give the same numbers as the Python port. */
public final class Stats {

    private Stats() {}

    /** SplitMix64: the same arithmetic as the Python generator, so bootstrap intervals match. */
    public static final class SplitMix64 {
        private long state;
```

- `package dev.plainround.router.domain;`: declares that this file belongs to the package `dev.plainround.router.domain`.
- `import java.util.Arrays;`: imports the class `java.util.Arrays` so it can be used by its short name.
- `import java.util.List;`: imports the class `java.util.List` so it can be used by its short name.
- `/** ... */`: a Javadoc comment. It says: "Small statistics, written to give the same numbers as the Python port."
- `public final class Stats {`: declares the class `Stats` (public, final).
- `private Stats() {`: constructor of `Stats`, taking no arguments.
- `/** ... */`: a Javadoc comment. It says: "SplitMix64: the same arithmetic as the Python generator, so bootstrap intervals match."
- `public static final class SplitMix64 {`: declares the class `SplitMix64` (public, static, final).
- `private long state;`: declares the field `state` of type `long`.

```java
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
```

- `public SplitMix64(long seed) {`: constructor of `SplitMix64`, taking `long seed`.
- `this.state = seed;`: stores `seed` into `this.state`.
- `public long nextU64() {`: declares the method `nextU64`, which takes no arguments and returns `long`.
- `state += 0x9E3779B97F4A7C15L;`: adds `0x9E3779B97F4A7C15L` with `state`.
- `long z = state;`: declares `z` of type `long` and sets it to `state`.
- `z = (z ^ (z >>> 30)) * 0xBF58476D1CE4E5B9L;`: stores `(z ^ (z >>> 30)) * 0xBF58476D1CE4E5B9L` into `z`.
- `z = (z ^ (z >>> 27)) * 0x94D049BB133111EBL;`: stores `(z ^ (z >>> 27)) * 0x94D049BB133111EBL` into `z`.
- `return z ^ (z >>> 31);`: ends the method and hands back `z ^ (z >>> 31)`.
- `public int below(int bound) {`: declares the method `below`, which takes `int bound` and returns `int`.
- `if (bound <= 0) {`: runs the block below only if `bound <= 0` is true.
- `throw new IllegalArgumentException("bound must be positive");`: signals an error: `new IllegalArgumentException("bound must be positive")`. Normal flow stops; the nearest matching `catch` takes over.

```java
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
```

- `return (int) Long.remainderUnsigned(nextU64(), bound);`: ends the method and hands back `(int) Long.remainderUnsigned(nextU64(), bound)`.
- `public record Interval(double low, double high) {`: declares the record `Interval` with the components `double low, double high`.
- `public record PairedDifference(double mean, Interval interval) {`: declares the record `PairedDifference` with the components `double mean, Interval interval`.
- `public static double mean(List<Double> values) {`: declares the method `mean`, which takes `List<Double> values` and returns `double`. It belongs to the class (`static`).
- `if (values.isEmpty()) {`: runs the block below only if `values.isEmpty()` is true. `.isEmpty()` is true when there is nothing in it.
- `return 0.0;`: ends the method and hands back `0.0`.
- `double sum = 0.0;`: declares `sum` of type `double` and sets it to `0.0`.
- `for (double v : values) {`: repeats the block below once for each item `double v` taken from `values`.

```java
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
```

- `sum += v;`: adds `v` with `sum`.
- `return sum / values.size();`: ends the method and hands back `sum / values.size()`. `.size()` is the number of items.
- `public static Interval wilson(int successes, int trials) {`: declares the method `wilson`, which takes `int successes, int trials` and returns `Interval`. It belongs to the class (`static`).
- `if (trials <= 0) {`: runs the block below only if `trials <= 0` is true.
- `return new Interval(0.0, 1.0);`: ends the method and hands back `new Interval(0.0, 1.0)`.
- `double z = 1.96;`: declares `z` of type `double` and sets it to `1.96`.
- `double p = (double) successes / trials;`: declares `p` of type `double` and sets it to `(double) successes / trials`.
- `double denominator = 1 + z * z / trials;`: declares `denominator` of type `double` and sets it to `1 + z * z / trials`.
- `double centre = (p + z * z / (2 * trials)) / denominator;`: declares `centre` of type `double` and sets it to `(p + z * z / (2 * trials)) / denominator`.
- `double margin = z * Math.sqrt(p * (1 - p) / trials + z * z / (4.0 * trials * trials)) /...`: declares `margin` of type `double` and sets it to `z * Math.sqrt(p * (1 - p) / trials + z * z / (4.0 * trials * trials)) / denom...`. `Math.xxx` is a standard maths function.

```java
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
```

- `return new Interval(Math.max(0.0, centre - margin), Math.min(1.0, centre + margin));`: ends the method and hands back `new Interval(Math.max(0.0, centre - margin), Math.min(1.0, centre + margin))`. `Math.xxx` is a standard maths function.
- `public static Interval bootstrapMeanInterval(List<Double> values, int resamples, long s...`: declares the method `bootstrapMeanInterval`, which takes `List<Double> values, int resamples, long seed` and returns `Interval`. It belongs to the class (`static`).
- `if (values.isEmpty()) {`: runs the block below only if `values.isEmpty()` is true. `.isEmpty()` is true when there is nothing in it.
- `return new Interval(0.0, 0.0);`: ends the method and hands back `new Interval(0.0, 0.0)`.
- `SplitMix64 rng = new SplitMix64(seed);`: declares `rng` of type `SplitMix64` and sets it to `new SplitMix64(seed)`.
- `int n = values.size();`: declares `n` of type `int` and sets it to `values.size()`. `.size()` is the number of items.
- `double[] means = new double[resamples];`: declares `means` of type `double[]` and sets it to `new double[resamples]`.
- `for (int r = 0; r < resamples; r++) {`: repeats the block below as the counting loop `int r = 0; r < resamples; r++` says.
- `double sum = 0.0;`: declares `sum` of type `double` and sets it to `0.0`.
- `for (int i = 0; i < n; i++) {`: repeats the block below as the counting loop `int i = 0; i < n; i++` says.
- `sum += values.get(rng.below(n));`: adds `values.get(rng.below(n))` with `sum`. `.get(x)` reads the item or entry for `x`.

```java
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
```

- `means[r] = sum / n;`: stores `sum / n` into `means[r]`.
- `Arrays.sort(means);`: runs `Arrays.sort(means)`.
- `double tail = (1 - 0.95) / 2;`: declares `tail` of type `double` and sets it to `(1 - 0.95) / 2`.
- `return new Interval(means[(int) (tail * resamples)], means[Math.min(resamples - 1, (int...`: ends the method and hands back `new Interval(means[(int) (tail * resamples)], means[Math.min(resamples - 1, (...`. `Math.xxx` is a standard maths function.
- `public static PairedDifference pairedBootstrapDifference(List<Double> treatment, List<D...`: declares the method `pairedBootstrapDifference`, which takes `List<Double> treatment, List<Double> control, int resamples, long seed` and returns `PairedDifference`. It belongs to the class (`static`).
- `if (treatment.size() != control.size()) {`: runs the block below only if `treatment.size() != control.size()` is true. `.size()` is the number of items.
- `throw new IllegalArgumentException("a paired comparison needs the same number of items ...`: signals an error: `new IllegalArgumentException("a paired comparison needs the same number of it...`. Normal flow stops; the nearest matching `catch` takes over.
- `java.util.ArrayList<Double> differences = new java.util.ArrayList<>();`: declares `differences` of type `java.util.ArrayList<Double>` and sets it to `new java.util.ArrayList<>()`.
- `for (int i = 0; i < treatment.size(); i++) {`: repeats the block below as the counting loop `int i = 0; i < treatment.size(); i++` says.
- `differences.add(treatment.get(i) - control.get(i));`: runs `differences.add(treatment.get(i) - control.get(i))`. `.get(x)` reads the item or entry for `x`; `.add(x)` appends `x`.

```java
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
```

- `return new PairedDifference(mean(differences), bootstrapMeanInterval(differences, resam...`: ends the method and hands back `new PairedDifference(mean(differences), bootstrapMeanInterval(differences, re...`.
- `/** ... */`: a Javadoc comment. It says: "A seeded Fisher-Yates permutation of 0..n-1, the same as the Python port."
- `public static int[] shuffledIndices(int n, long seed) {`: declares the method `shuffledIndices`, which takes `int n, long seed` and returns `int[]`. It belongs to the class (`static`).
- `SplitMix64 rng = new SplitMix64(seed);`: declares `rng` of type `SplitMix64` and sets it to `new SplitMix64(seed)`.
- `int[] order = new int[n];`: declares `order` of type `int[]` and sets it to `new int[n]`.
- `for (int i = 0; i < n; i++) {`: repeats the block below as the counting loop `int i = 0; i < n; i++` says.
- `order[i] = i;`: stores `i` into `order[i]`.
- `for (int i = n - 1; i > 0; i--) {`: repeats the block below as the counting loop `int i = n - 1; i > 0; i--` says.
- `int j = rng.below(i + 1);`: declares `j` of type `int` and sets it to `rng.below(i + 1)`.
- `int t = order[i];`: declares `t` of type `int` and sets it to `order[i]`.
- `order[i] = order[j];`: stores `order[j]` into `order[i]`.

```java
            order[j] = t;
        }
        return order;
    }
}
```

- `order[j] = t;`: stores `t` into `order[j]`.
- `return order;`: ends the method and hands back `order`.

#### `java/src/main/java/dev/plainround/router/domain/Tasks.java`

```java
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
```

- `package dev.plainround.router.domain;`: declares that this file belongs to the package `dev.plainround.router.domain`.
- `import java.util.List;`: imports the class `java.util.List` so it can be used by its short name.
- `import java.util.Map;`: imports the class `java.util.Map` so it can be used by its short name.
- `import java.util.regex.Pattern;`: imports the class `java.util.regex.Pattern` so it can be used by its short name.
- `/** ... */`: a Javadoc comment. It says: "The tasks the router serves, the policy text, and the refund arithmetic (a port of tasks.py)."
- `public final class Tasks {`: declares the class `Tasks` (public, final).
- `private Tasks() {`: constructor of `Tasks`, taking no arguments.
- `public static final List<String> LABELS = List.of("billing", "shipping", "returns", "ac...`: declares the field `LABELS` of type `List<String>` and sets it to `List.of("billing", "shipping", "returns", "account")`. `List.of(...)` makes an unchangeable list.
- `public static final String REFUND_POLICY = "Refunds are 100% of the returned items' pri...`: declares the field `REFUND_POLICY` of type `String` and sets it to `"Refunds are 100% of the returned items' price for returns within 15 days of ...`.

```java
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
```

- `public static final List<String> POLICY_LINES = List.of( "Returns are accepted within 3...`: declares the field `POLICY_LINES` of type `List<String>` and sets it to `List.of( "Returns are accepted within 30 days of delivery.", "The customer pa...`. `List.of(...)` makes an unchangeable list.
- `public static final Pattern ORDER_ID = Pattern.compile("\\bPR-\\d{6}\\b");`: declares the field `ORDER_ID` of type `Pattern` and sets it to `Pattern.compile("\\bPR-\\d{6}\\b")`. `Pattern.compile(...)` prepares a regular expression (`regular-expressions.md`).
- `public static final List<String> EXCEPTION_WORDS = List.of("damaged", "broken", "except...`: declares the field `EXCEPTION_WORDS` of type `List<String>` and sets it to `List.of("damaged", "broken", "exception", "only part", "partial")`. `List.of(...)` makes an unchangeable list.

```java
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
```

- **New idea.** An **enum** is a fixed set of named constants.
- `public enum Kind {`: declares the enum `Kind`.
- `LABEL("label"), REFUND("refund"), POLICY("policy");`: runs `LABEL("label"), REFUND("refund"), POLICY("policy")`.
- `private final String value;`: declares the field `value` of type `String`.
- `Kind(String value) {`: constructor of `Kind`, taking `String value`.
- `this.value = value;`: stores `value` into `this.value`.
- `public String value() {`: declares the method `value`, which takes no arguments and returns `String`.
- `return value;`: ends the method and hands back `value`.

```java
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
```

- `public static Kind of(String value) {`: declares the method `of`, which takes `String value` and returns `Kind`. It belongs to the class (`static`).
- `for (Kind k : values()) {`: repeats the block below once for each item `Kind k` taken from `values()`.
- `if (k.value.equals(value)) {`: runs the block below only if `k.value.equals(value)` is true. `.equals(x)` compares two objects by value.
- `return k;`: ends the method and hands back `k`.
- `throw new IllegalArgumentException("unknown kind " + value);`: signals an error: `new IllegalArgumentException("unknown kind " + value)`. Normal flow stops; the nearest matching `catch` takes over.
- `public record RefundOrder(String orderId, int totalCents, int days, int returnedCents, ...`: declares the record `RefundOrder` with the components `String orderId, int totalCents, int days, int returnedCents, boolean damaged`.
- `/** ... */`: a Javadoc comment. It says: "gold is a String (label), an Integer (refund cents or policy line index)."
- `public record Task(String taskId, Kind kind, String difficulty, String split, String te...`: declares the record `Task` with the components `String taskId, Kind kind, String difficulty, String split, String text, Object gold, List<RefundOrder> orders`.

```java
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
```

- `public static int refundCents(RefundOrder order) {`: declares the method `refundCents`, which takes `RefundOrder order` and returns `int`. It belongs to the class (`static`).
- `if (order.days() > 30) {`: runs the block below only if `order.days() > 30` is true.
- `return 0;`: ends the method and hands back `0`.
- `if (order.damaged() || order.days() <= 15) {`: runs the block below only if `order.damaged() || order.days() <= 15` is true.
- `return order.returnedCents();`: ends the method and hands back `order.returnedCents()`.
- `return (order.returnedCents() * 80 + 50) / 100;`: ends the method and hands back `(order.returnedCents() * 80 + 50) / 100`.
- `public static int expectedRefundCents(Task task) {`: declares the method `expectedRefundCents`, which takes `Task task` and returns `int`. It belongs to the class (`static`).
- `int sum = 0;`: declares `sum` of type `int` and sets it to `0`.
- `for (RefundOrder o : task.orders()) {`: repeats the block below once for each item `RefundOrder o` taken from `task.orders()`.
- `sum += refundCents(o);`: adds `refundCents(o)` with `sum`.

```java
        return sum;
    }

    public static Map<String, Integer> noCounts() {
        return Map.of();
    }
}
```

- `return sum;`: ends the method and hands back `sum`.
- `public static Map<String, Integer> noCounts() {`: declares the method `noCounts`, which takes no arguments and returns `Integer>`. It belongs to the class (`static`).
- `return Map.of();`: ends the method and hands back `Map.of()`. `Map.of(...)` makes an unchangeable map.

#### `java/src/main/java/dev/plainround/router/infrastructure/DataFiles.java`

```java
package dev.plainround.router.infrastructure;

import dev.plainround.router.domain.Routing.Bar;
import dev.plainround.router.domain.Routing.PriceTable;
import dev.plainround.router.domain.Tasks.Kind;
import dev.plainround.router.domain.Tasks.RefundOrder;
import dev.plainround.router.domain.Tasks.Task;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
```

- `package dev.plainround.router.infrastructure;`: declares that this file belongs to the package `dev.plainround.router.infrastructure`.
- `import dev.plainround.router.domain.Routing.Bar;`: imports the class `dev.plainround.router.domain.Routing.Bar` so it can be used by its short name.
- `import dev.plainround.router.domain.Routing.PriceTable;`: imports the class `dev.plainround.router.domain.Routing.PriceTable` so it can be used by its short name.
- `import dev.plainround.router.domain.Tasks.Kind;`: imports the class `dev.plainround.router.domain.Tasks.Kind` so it can be used by its short name.
- `import dev.plainround.router.domain.Tasks.RefundOrder;`: imports the class `dev.plainround.router.domain.Tasks.RefundOrder` so it can be used by its short name.
- `import dev.plainround.router.domain.Tasks.Task;`: imports the class `dev.plainround.router.domain.Tasks.Task` so it can be used by its short name.
- `import java.io.IOException;`: imports the class `java.io.IOException` so it can be used by its short name.
- `import java.io.UncheckedIOException;`: imports the class `java.io.UncheckedIOException` so it can be used by its short name.
- `import java.nio.charset.StandardCharsets;`: imports the class `java.nio.charset.StandardCharsets` so it can be used by its short name.
- `import java.nio.file.Files;`: imports the class `java.nio.file.Files` so it can be used by its short name.
- `import java.nio.file.Path;`: imports the class `java.nio.file.Path` so it can be used by its short name.
- `import java.util.ArrayList;`: imports the class `java.util.ArrayList` so it can be used by its short name.
- `import java.util.LinkedHashMap;`: imports the class `java.util.LinkedHashMap` so it can be used by its short name.

```java
import java.util.List;
import java.util.Map;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

/** Reads the same data and configuration files as the Python port. */
public final class DataFiles {

    private DataFiles() {}

    private static final JsonMapper JSON = JsonMapper.builder().build();

    public static List<Task> loadTasks(Path dataDir) {
        try {
```

- `import java.util.List;`: imports the class `java.util.List` so it can be used by its short name.
- `import java.util.Map;`: imports the class `java.util.Map` so it can be used by its short name.
- `import tools.jackson.databind.JsonNode;`: imports the class `tools.jackson.databind.JsonNode` so it can be used by its short name.
- `import tools.jackson.databind.json.JsonMapper;`: imports the class `tools.jackson.databind.json.JsonMapper` so it can be used by its short name.
- `/** ... */`: a Javadoc comment. It says: "Reads the same data and configuration files as the Python port."
- `public final class DataFiles {`: declares the class `DataFiles` (public, final).
- `private DataFiles() {`: constructor of `DataFiles`, taking no arguments.
- `private static final JsonMapper JSON = JsonMapper.builder().build();`: declares the field `JSON` of type `JsonMapper` and sets it to `JsonMapper.builder().build()`.
- `public static List<Task> loadTasks(Path dataDir) {`: declares the method `loadTasks`, which takes `Path dataDir` and returns `List<Task>`. It belongs to the class (`static`).
- `try {`: tries the block below; an exception it throws can be caught by the `catch` that follows.

```java
            List<Task> tasks = new ArrayList<>();
            for (String line : Files.readAllLines(dataDir.resolve("tasks.jsonl"), StandardCharsets.UTF_8)) {
                if (line.isBlank()) {
                    continue;
                }
                JsonNode row = JSON.readTree(line);
                List<RefundOrder> orders = new ArrayList<>();
                if (row.has("orders")) {
                    for (JsonNode o : row.get("orders")) {
                        orders.add(new RefundOrder(
                                o.get("order_id").asString(), o.get("total_cents").asInt(), o.get("days").asInt(), o.get("returned_cents").asInt(), o.get("damaged").asBoolean()));
                    }
                }
                JsonNode gold = row.get("gold");
                tasks.add(new Task(
                        row.get("task_id").asString(),
                        Kind.of(row.get("kind").asString()),
                        row.get("difficulty").asString(),
                        row.get("split").asString(),
                        row.get("text").asString(),
                        gold.isString() ? gold.asString() : (Object) gold.asInt(),
                        orders));
            }
```

- `List<Task> tasks = new ArrayList<>();`: declares `tasks` of type `List<Task>` and sets it to `new ArrayList<>()`. `new ArrayList<>()` makes an empty changeable list.
- `for (String line : Files.readAllLines(dataDir.resolve("tasks.jsonl"), StandardCharsets....`: repeats the block below once for each item `String line` taken from `Files.readAllLines(dataDir.resolve("tasks.jsonl...`.
- `if (line.isBlank()) {`: runs the block below only if `line.isBlank()` is true. `.isBlank()` is true when the text is empty or only spaces.
- `continue;`: skips to the next round of the loop.
- `JsonNode row = JSON.readTree(line);`: declares `row` of type `JsonNode` and sets it to `JSON.readTree(line)`. `.readTree(text)` parses JSON text into a tree of nodes.
- `List<RefundOrder> orders = new ArrayList<>();`: declares `orders` of type `List<RefundOrder>` and sets it to `new ArrayList<>()`. `new ArrayList<>()` makes an empty changeable list.
- `if (row.has("orders")) {`: runs the block below only if `row.has("orders")` is true. `.has("x")` tests whether a JSON field exists.
- `for (JsonNode o : row.get("orders")) {`: repeats the block below once for each item `JsonNode o` taken from `row.get("orders")`.
- `orders.add(new RefundOrder( o.get("order_id").asString(), o.get("total_cents").asInt(),...`: runs `orders.add(new RefundOrder( o.get("order_id").asString(), o.get("total_cents").asInt(),...`. `.get(x)` reads the item or entry for `x`; `.add(x)` appends `x`; `.asString()`, `.asInt()`, `.asDouble()` read a JSON value as that type.
- `JsonNode gold = row.get("gold");`: declares `gold` of type `JsonNode` and sets it to `row.get("gold")`. `.get(x)` reads the item or entry for `x`.
- `tasks.add(new Task( row.get("task_id").asString(), Kind.of(row.get("kind").asString()),...`: runs `tasks.add(new Task( row.get("task_id").asString(), Kind.of(row.get("kind").asString()),...`. `.get(x)` reads the item or entry for `x`; `.add(x)` appends `x`; `.asString()`, `.asInt()`, `.asDouble()` read a JSON value as that type.

```java
            return tasks;
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    public static Bar loadBar(Path configDir) {
        try {
            JsonNode raw = JSON.readTree(Files.readString(configDir.resolve("bar.json"), StandardCharsets.UTF_8));
            List<Double> fractions = new ArrayList<>();
            for (JsonNode f : raw.get("day_budget_fractions")) {
                fractions.add(f.asDouble());
            }
            return new Bar(
                    raw.get("false_accept_bar").asDouble(),
                    raw.get("hard_accuracy_bar").asDouble(),
                    raw.get("accuracy_margin").asDouble(),
                    raw.get("request_cap").asDouble(),
                    raw.get("tighten_at").asDouble(),
                    fractions);
```

- `return tasks;`: ends the method and hands back `tasks`.
- `catch (IOException e) {`: runs when the block above threw `IOException e`.
- `throw new UncheckedIOException(e);`: signals an error: `new UncheckedIOException(e)`. Normal flow stops; the nearest matching `catch` takes over.
- `public static Bar loadBar(Path configDir) {`: declares the method `loadBar`, which takes `Path configDir` and returns `Bar`. It belongs to the class (`static`).
- `try {`: tries the block below; an exception it throws can be caught by the `catch` that follows.
- `JsonNode raw = JSON.readTree(Files.readString(configDir.resolve("bar.json"), StandardCh...`: declares `raw` of type `JsonNode` and sets it to `JSON.readTree(Files.readString(configDir.resolve("bar.json"), StandardCharset...`. `Files.readString(path)` reads a whole file as text; `.readTree(text)` parses JSON text into a tree of nodes.
- `List<Double> fractions = new ArrayList<>();`: declares `fractions` of type `List<Double>` and sets it to `new ArrayList<>()`. `new ArrayList<>()` makes an empty changeable list.
- `for (JsonNode f : raw.get("day_budget_fractions")) {`: repeats the block below once for each item `JsonNode f` taken from `raw.get("day_budget_fractions")`.
- `fractions.add(f.asDouble());`: runs `fractions.add(f.asDouble())`. `.add(x)` appends `x`; `.asString()`, `.asInt()`, `.asDouble()` read a JSON value as that type.
- `return new Bar( raw.get("false_accept_bar").asDouble(), raw.get("hard_accuracy_bar").as...`: ends the method and hands back `new Bar( raw.get("false_accept_bar").asDouble(), raw.get("hard_accuracy_bar")...`. `.get(x)` reads the item or entry for `x`; `.asString()`, `.asInt()`, `.asDouble()` read a JSON value as that type.

```java
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    public static PriceTable loadPrices(Path configDir) {
        try {
            JsonNode raw = JSON.readTree(Files.readString(configDir.resolve("prices.json"), StandardCharsets.UTF_8));
            Map<String, Double> prices = new LinkedHashMap<>();
            for (String tier : raw.get("per_1k_tokens").propertyNames()) {
                prices.put(tier, raw.get("per_1k_tokens").get(tier).asDouble());
            }
            return new PriceTable(raw.get("as_of").asString(), prices);
        } catch (IOException e) {
```

- `catch (IOException e) {`: runs when the block above threw `IOException e`.
- `throw new UncheckedIOException(e);`: signals an error: `new UncheckedIOException(e)`. Normal flow stops; the nearest matching `catch` takes over.
- `public static PriceTable loadPrices(Path configDir) {`: declares the method `loadPrices`, which takes `Path configDir` and returns `PriceTable`. It belongs to the class (`static`).
- `try {`: tries the block below; an exception it throws can be caught by the `catch` that follows.
- `JsonNode raw = JSON.readTree(Files.readString(configDir.resolve("prices.json"), Standar...`: declares `raw` of type `JsonNode` and sets it to `JSON.readTree(Files.readString(configDir.resolve("prices.json"), StandardChar...`. `Files.readString(path)` reads a whole file as text; `.readTree(text)` parses JSON text into a tree of nodes.
- `Map<String, Double> prices = new LinkedHashMap<>();`: declares `prices` of type `Double>` and sets it to `new LinkedHashMap<>()`. `new HashMap<>()` makes an empty map.
- `for (String tier : raw.get("per_1k_tokens").propertyNames()) {`: repeats the block below once for each item `String tier` taken from `raw.get("per_1k_tokens").propertyNames()`.
- `prices.put(tier, raw.get("per_1k_tokens").get(tier).asDouble());`: runs `prices.put(tier, raw.get("per_1k_tokens").get(tier).asDouble())`. `.get(x)` reads the item or entry for `x`; `.put(k, v)` stores value `v` under key `k`; `.asString()`, `.asInt()`, `.asDouble()` read a JSON value as that type.
- `return new PriceTable(raw.get("as_of").asString(), prices);`: ends the method and hands back `new PriceTable(raw.get("as_of").asString(), prices)`. `.get(x)` reads the item or entry for `x`; `.asString()`, `.asInt()`, `.asDouble()` read a JSON value as that type.
- `catch (IOException e) {`: runs when the block above threw `IOException e`.

```java
            throw new UncheckedIOException(e);
        }
    }
}
```

- `throw new UncheckedIOException(e);`: signals an error: `new UncheckedIOException(e)`. Normal flow stops; the nearest matching `catch` takes over.

#### `java/src/main/java/dev/plainround/router/infrastructure/FilePrompts.java`

```java
package dev.plainround.router.infrastructure;

import dev.plainround.router.application.PromptStore;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

/** Prompt templates from versioned files; the trailing newlines are removed, as in the Python port. */
public final class FilePrompts implements PromptStore {

    private final Path directory;
```

- `package dev.plainround.router.infrastructure;`: declares that this file belongs to the package `dev.plainround.router.infrastructure`.
- `import dev.plainround.router.application.PromptStore;`: imports the class `dev.plainround.router.application.PromptStore` so it can be used by its short name.
- `import java.io.IOException;`: imports the class `java.io.IOException` so it can be used by its short name.
- `import java.io.UncheckedIOException;`: imports the class `java.io.UncheckedIOException` so it can be used by its short name.
- `import java.nio.charset.StandardCharsets;`: imports the class `java.nio.charset.StandardCharsets` so it can be used by its short name.
- `import java.nio.file.Files;`: imports the class `java.nio.file.Files` so it can be used by its short name.
- `import java.nio.file.Path;`: imports the class `java.nio.file.Path` so it can be used by its short name.
- `/** ... */`: a Javadoc comment. It says: "Prompt templates from versioned files; the trailing newlines are removed, as in the Python port."
- `public final class FilePrompts implements PromptStore {`: declares the class `FilePrompts` (public, final). Relations: `implements PromptStore`.
- `private final Path directory;`: declares the field `directory` of type `Path`.

```java
    public FilePrompts(Path directory) {
        this.directory = directory;
    }

    @Override
    public String get(String name) {
        Path path = directory.resolve(name + ".md");
        if (!Files.isRegularFile(path)) {
            throw new IllegalArgumentException("no prompt named " + name + " in " + directory);
        }
        try {
            String text = Files.readString(path, StandardCharsets.UTF_8);
            int end = text.length();
            while (end > 0 && text.charAt(end - 1) == '\n') {
                end--;
            }
```

- `public FilePrompts(Path directory) {`: constructor of `FilePrompts`, taking `Path directory`.
- `this.directory = directory;`: stores `directory` into `this.directory`.
- **New idea.** An **annotation** is a label starting with `@` placed before a class, method or field. Tools and the compiler read it; `@Override` says the method replaces one from a parent type, `@Test` marks a test method.
- `public String get(String name) {`: declares the method `get`, which takes `String name` and returns `String`. Annotation(s): `@Override`.
- `Path path = directory.resolve(name + ".md");`: declares `path` of type `Path` and sets it to `directory.resolve(name + ".md")`.
- `if (!Files.isRegularFile(path)) {`: runs the block below only if `!Files.isRegularFile(path)` is true.
- `throw new IllegalArgumentException("no prompt named " + name + " in " + directory);`: signals an error: `new IllegalArgumentException("no prompt named " + name + " in " + directory)`. Normal flow stops; the nearest matching `catch` takes over.
- `try {`: tries the block below; an exception it throws can be caught by the `catch` that follows.
- `String text = Files.readString(path, StandardCharsets.UTF_8);`: declares `text` of type `String` and sets it to `Files.readString(path, StandardCharsets.UTF_8)`. `Files.readString(path)` reads a whole file as text.
- `int end = text.length();`: declares `end` of type `int` and sets it to `text.length()`. `.length()` is the number of characters.
- `while (end > 0 && text.charAt(end - 1) == '\n') {`: repeats the block below while `end > 0 && text.charAt(end - 1) == '\n'` is true.
- `end--;`: adds or subtracts one.

```java
            return text.substring(0, end);
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }
}
```

- `return text.substring(0, end);`: ends the method and hands back `text.substring(0, end)`. `.substring(a, b)` is the part of the text from `a` up to `b`.
- `catch (IOException e) {`: runs when the block above threw `IOException e`.
- `throw new UncheckedIOException(e);`: signals an error: `new UncheckedIOException(e)`. Normal flow stops; the nearest matching `catch` takes over.

#### `java/src/main/java/dev/plainround/router/infrastructure/RecordedChatModel.java`

```java
package dev.plainround.router.infrastructure;

import dev.plainround.router.domain.Llm.ChatModel;
import dev.plainround.router.domain.Llm.ChatRequest;
import dev.plainround.router.domain.Llm.ChatResponse;
import dev.plainround.router.domain.Llm.FixtureMissException;
import dev.plainround.router.domain.Llm.Usage;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.List;
```

- `package dev.plainround.router.infrastructure;`: declares that this file belongs to the package `dev.plainround.router.infrastructure`.
- `import dev.plainround.router.domain.Llm.ChatModel;`: imports the class `dev.plainround.router.domain.Llm.ChatModel` so it can be used by its short name.
- `import dev.plainround.router.domain.Llm.ChatRequest;`: imports the class `dev.plainround.router.domain.Llm.ChatRequest` so it can be used by its short name.
- `import dev.plainround.router.domain.Llm.ChatResponse;`: imports the class `dev.plainround.router.domain.Llm.ChatResponse` so it can be used by its short name.
- `import dev.plainround.router.domain.Llm.FixtureMissException;`: imports the class `dev.plainround.router.domain.Llm.FixtureMissException` so it can be used by its short name.
- `import dev.plainround.router.domain.Llm.Usage;`: imports the class `dev.plainround.router.domain.Llm.Usage` so it can be used by its short name.
- `import java.io.IOException;`: imports the class `java.io.IOException` so it can be used by its short name.
- `import java.io.UncheckedIOException;`: imports the class `java.io.UncheckedIOException` so it can be used by its short name.
- `import java.nio.charset.StandardCharsets;`: imports the class `java.nio.charset.StandardCharsets` so it can be used by its short name.
- `import java.nio.file.Files;`: imports the class `java.nio.file.Files` so it can be used by its short name.
- `import java.nio.file.Path;`: imports the class `java.nio.file.Path` so it can be used by its short name.
- `import java.util.HashMap;`: imports the class `java.util.HashMap` so it can be used by its short name.
- `import java.util.List;`: imports the class `java.util.List` so it can be used by its short name.

```java
import java.util.Map;
import java.util.stream.Stream;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

/** Replays the same JSONL fixtures as the Python recorded adapter; an unknown request is an error. */
public final class RecordedChatModel implements ChatModel {

    private final Map<String, ChatResponse> responses = new HashMap<>();

    public RecordedChatModel(Path fixtures) {
        JsonMapper json = JsonMapper.builder().build();
        try (Stream<Path> files = Files.isDirectory(fixtures) ? Files.list(fixtures) : Stream.of(fixtures)) {
            for (Path file : files.filter(p -> p.toString().endsWith(".jsonl")).sorted().toList()) {
                List<String> lines = Files.readAllLines(file, StandardCharsets.UTF_8);
                for (String line : lines) {
                    if (line.isBlank()) {
                        continue;
                    }
                    JsonNode row = json.readTree(line);
                    JsonNode r = row.get("response");
                    responses.put(
                            row.get("key").asString(),
                            new ChatResponse(
                                    r.get("text").asString(),
                                    new Usage(r.get("input_tokens").asInt(), r.get("output_tokens").asInt()),
                                    r.get("model").asString(),
                                    r.has("finish_reason") ? r.get("finish_reason").asString() : "stop",
                                    r.has("latency_s") ? r.get("latency_s").asDouble() : 0.0));
                }
            }
```

- `import java.util.Map;`: imports the class `java.util.Map` so it can be used by its short name.
- `import java.util.stream.Stream;`: imports the class `java.util.stream.Stream` so it can be used by its short name.
- `import tools.jackson.databind.JsonNode;`: imports the class `tools.jackson.databind.JsonNode` so it can be used by its short name.
- `import tools.jackson.databind.json.JsonMapper;`: imports the class `tools.jackson.databind.json.JsonMapper` so it can be used by its short name.
- `/** ... */`: a Javadoc comment. It says: "Replays the same JSONL fixtures as the Python recorded adapter; an unknown request is an error."
- `public final class RecordedChatModel implements ChatModel {`: declares the class `RecordedChatModel` (public, final). Relations: `implements ChatModel`.
- `private final Map<String, ChatResponse> responses = new HashMap<>();`: declares the field `responses` of type `ChatResponse>` and sets it to `new HashMap<>()`. `new HashMap<>()` makes an empty map.
- `public RecordedChatModel(Path fixtures) {`: constructor of `RecordedChatModel`, taking `Path fixtures`.
- `JsonMapper json = JsonMapper.builder().build();`: declares `json` of type `JsonMapper` and sets it to `JsonMapper.builder().build()`.
- `try (Stream<Path> files = Files.isDirectory(fixtures) ? Files.list(fixtures) : Stream.o...`: tries the block below; an exception it throws can be caught by the `catch` that follows. The resource(s) `Stream<Path> files = Files.isDirectory(fixtures) ? Files.list(fixtures) : Str...` are closed automatically at the end.
- `for (Path file : files.filter(p -> p.toString().endsWith(".jsonl")).sorted().toList()) {`: repeats the block below once for each item `Path file` taken from `files.filter(p -> p.toString().endsWith(".jsonl...`.
- `List<String> lines = Files.readAllLines(file, StandardCharsets.UTF_8);`: declares `lines` of type `List<String>` and sets it to `Files.readAllLines(file, StandardCharsets.UTF_8)`. `Files.readAllLines(path)` reads a file as a list of lines.
- `for (String line : lines) {`: repeats the block below once for each item `String line` taken from `lines`.
- `if (line.isBlank()) {`: runs the block below only if `line.isBlank()` is true. `.isBlank()` is true when the text is empty or only spaces.
- `continue;`: skips to the next round of the loop.
- `JsonNode row = json.readTree(line);`: declares `row` of type `JsonNode` and sets it to `json.readTree(line)`. `.readTree(text)` parses JSON text into a tree of nodes.
- `JsonNode r = row.get("response");`: declares `r` of type `JsonNode` and sets it to `row.get("response")`. `.get(x)` reads the item or entry for `x`.
- `responses.put( row.get("key").asString(), new ChatResponse( r.get("text").asString(), n...`: runs `responses.put( row.get("key").asString(), new ChatResponse( r.get("text").asString(), n...`. `.get(x)` reads the item or entry for `x`; `.put(k, v)` stores value `v` under key `k`; `.asString()`, `.asInt()`, `.asDouble()` read a JSON value as that type.

```java
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    public int size() {
        return responses.size();
    }

    @Override
    public ChatResponse complete(ChatRequest request) {
        ChatResponse found = responses.get(request.fixtureKey());
        if (found == null) {
            throw new FixtureMissException("no recorded response for model=" + request.model() + " key="
                    + request.fixtureKey().substring(0, 12) + " (" + request.messages().size() + " messages)");
        }
```

- `catch (IOException e) {`: runs when the block above threw `IOException e`.
- `throw new UncheckedIOException(e);`: signals an error: `new UncheckedIOException(e)`. Normal flow stops; the nearest matching `catch` takes over.
- `public int size() {`: declares the method `size`, which takes no arguments and returns `int`.
- `return responses.size();`: ends the method and hands back `responses.size()`. `.size()` is the number of items.
- `public ChatResponse complete(ChatRequest request) {`: declares the method `complete`, which takes `ChatRequest request` and returns `ChatResponse`. Annotation(s): `@Override`.
- `ChatResponse found = responses.get(request.fixtureKey());`: declares `found` of type `ChatResponse` and sets it to `responses.get(request.fixtureKey())`. `.get(x)` reads the item or entry for `x`.
- `if (found == null) {`: runs the block below only if `found == null` is true.
- `throw new FixtureMissException("no recorded response for model=" + request.model() + " ...`: signals an error: `new FixtureMissException("no recorded response for model=" + request.model() ...`. Normal flow stops; the nearest matching `catch` takes over.

```java
        return found;
    }
}
```

- `return found;`: ends the method and hands back `found`.

#### `java/src/main/java/dev/plainround/router/infrastructure/SpringAiChatModel.java`

```java
package dev.plainround.router.infrastructure;

import dev.plainround.router.domain.Llm.ChatModel;
import dev.plainround.router.domain.Llm.ChatRequest;
import dev.plainround.router.domain.Llm.ChatResponse;
import dev.plainround.router.domain.Llm.Message;
import dev.plainround.router.domain.Llm.ModelException;
import dev.plainround.router.domain.Llm.Usage;
import java.util.ArrayList;
import java.util.List;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.openai.OpenAiChatModel;
import org.springframework.ai.openai.OpenAiChatOptions;
```

- `package dev.plainround.router.infrastructure;`: declares that this file belongs to the package `dev.plainround.router.infrastructure`.
- `import dev.plainround.router.domain.Llm.ChatModel;`: imports the class `dev.plainround.router.domain.Llm.ChatModel` so it can be used by its short name.
- `import dev.plainround.router.domain.Llm.ChatRequest;`: imports the class `dev.plainround.router.domain.Llm.ChatRequest` so it can be used by its short name.
- `import dev.plainround.router.domain.Llm.ChatResponse;`: imports the class `dev.plainround.router.domain.Llm.ChatResponse` so it can be used by its short name.
- `import dev.plainround.router.domain.Llm.Message;`: imports the class `dev.plainround.router.domain.Llm.Message` so it can be used by its short name.
- `import dev.plainround.router.domain.Llm.ModelException;`: imports the class `dev.plainround.router.domain.Llm.ModelException` so it can be used by its short name.
- `import dev.plainround.router.domain.Llm.Usage;`: imports the class `dev.plainround.router.domain.Llm.Usage` so it can be used by its short name.
- `import java.util.ArrayList;`: imports the class `java.util.ArrayList` so it can be used by its short name.
- `import java.util.List;`: imports the class `java.util.List` so it can be used by its short name.
- `import org.springframework.ai.chat.client.ChatClient;`: imports the class `org.springframework.ai.chat.client.ChatClient` so it can be used by its short name.
- `import org.springframework.ai.openai.OpenAiChatModel;`: imports the class `org.springframework.ai.openai.OpenAiChatModel` so it can be used by its short name.
- `import org.springframework.ai.openai.OpenAiChatOptions;`: imports the class `org.springframework.ai.openai.OpenAiChatOptions` so it can be used by its short name.

```java
/**
 * The live adapter: Spring AI's ChatClient pointed at an OpenAI-compatible endpoint (a local ollama or llama.cpp
 * server, or a hosted provider). The domain never sees Spring AI; only this class does.
 */
public final class SpringAiChatModel implements ChatModel {

    private final ChatClient client;

    public SpringAiChatModel(String baseUrl, String apiKey) {
        String root = baseUrl.endsWith("/v1") ? baseUrl.substring(0, baseUrl.length() - 3) : baseUrl;
        OpenAiChatModel model = OpenAiChatModel.builder()
                .options(OpenAiChatOptions.builder().baseUrl(root).apiKey(apiKey == null || apiKey.isBlank() ? "none" : apiKey).build())
                .build();
        this.client = ChatClient.builder(model).build();
    }
```

- `/** ... */`: a Javadoc comment. It says: "The live adapter: Spring AI's ChatClient pointed at an OpenAI-compatible endpoint (a local ollama or llama.cpp server, or a hosted provider)."
- `public final class SpringAiChatModel implements ChatModel {`: declares the class `SpringAiChatModel` (public, final). Relations: `implements ChatModel`.
- `private final ChatClient client;`: declares the field `client` of type `ChatClient`. Spring AI classes (`spring-ai.md`).
- `public SpringAiChatModel(String baseUrl, String apiKey) {`: constructor of `SpringAiChatModel`, taking `String baseUrl, String apiKey`.
- `String root = baseUrl.endsWith("/v1") ? baseUrl.substring(0, baseUrl.length() - 3) : ba...`: declares `root` of type `String` and sets it to `baseUrl.endsWith("/v1") ? baseUrl.substring(0, baseUrl.length() - 3) : baseUrl`. `.length()` is the number of characters; `.substring(a, b)` is the part of the text from `a` up to `b`.
- `OpenAiChatModel model = OpenAiChatModel.builder() .options(OpenAiChatOptions.builder()....`: declares `model` of type `OpenAiChatModel` and sets it to `OpenAiChatModel.builder() .options(OpenAiChatOptions.builder().baseUrl(root)....`. `.isBlank()` is true when the text is empty or only spaces; Spring AI classes (`spring-ai.md`).
- `this.client = ChatClient.builder(model).build();`: stores `ChatClient.builder(model).build()` into `this.client`. Spring AI classes (`spring-ai.md`).

```java
    @Override
    public ChatResponse complete(ChatRequest request) {
        long started = System.nanoTime();
        List<org.springframework.ai.chat.messages.Message> messages = new ArrayList<>();
        for (Message m : request.messages()) {
            messages.add(switch (m.role()) {
                case "system" -> new org.springframework.ai.chat.messages.SystemMessage(m.content());
                case "assistant" -> new org.springframework.ai.chat.messages.AssistantMessage(m.content());
                default -> new org.springframework.ai.chat.messages.UserMessage(m.content());
            });
        }
        OpenAiChatOptions.Builder options = OpenAiChatOptions.builder()
                .model(request.model())
                .temperature(request.temperature())
                .maxTokens(request.maxTokens());
```

- `public ChatResponse complete(ChatRequest request) {`: declares the method `complete`, which takes `ChatRequest request` and returns `ChatResponse`. Annotation(s): `@Override`.
- `long started = System.nanoTime();`: declares `started` of type `long` and sets it to `System.nanoTime()`. `System.nanoTime()` is a precise clock in nanoseconds.
- `List<org.springframework.ai.chat.messages.Message> messages = new ArrayList<>();`: declares `messages` of type `List<org.springframework.ai.chat.messages.Message>` and sets it to `new ArrayList<>()`. `new ArrayList<>()` makes an empty changeable list.
- `for (Message m : request.messages()) {`: repeats the block below once for each item `Message m` taken from `request.messages()`.
- `messages.add(switch (m.role()) { case "system" -> new org.springframework.ai.chat.messa...`: runs `messages.add(switch (m.role()) { case "system" -> new org.springframework.ai.chat.messa...`. `.add(x)` appends `x`.
- `OpenAiChatOptions.Builder options = OpenAiChatOptions.builder() .model(request.model())...`: declares `options` of type `OpenAiChatOptions.Builder` and sets it to `OpenAiChatOptions.builder() .model(request.model()) .temperature(request.temp...`. Spring AI classes (`spring-ai.md`).

```java
        if (request.seed() != null) {
            options.seed(request.seed());
        }
        try {
            org.springframework.ai.chat.client.ChatClientResponse response =
                    client.prompt().messages(messages).options(options).call().chatClientResponse();
            org.springframework.ai.chat.model.ChatResponse chat = response.chatResponse();
            String text = chat.getResult().getOutput().getText();
            var usage = chat.getMetadata().getUsage();
            return new ChatResponse(
                    text == null ? "" : text,
                    new Usage(usage.getPromptTokens() == null ? 0 : usage.getPromptTokens(), usage.getCompletionTokens() == null ? 0 : usage.getCompletionTokens()),
                    request.model(),
                    "stop",
                    (System.nanoTime() - started) / 1e9);
```

- `if (request.seed() != null) {`: runs the block below only if `request.seed() != null` is true.
- `options.seed(request.seed());`: runs `options.seed(request.seed())`.
- `try {`: tries the block below; an exception it throws can be caught by the `catch` that follows.
- `org.springframework.ai.chat.client.ChatClientResponse response = client.prompt().messag...`: declares `response` of type `org.springframework.ai.chat.client.ChatClientResponse` and sets it to `client.prompt().messages(messages).options(options).call().chatClientResponse()`.
- `org.springframework.ai.chat.model.ChatResponse chat = response.chatResponse();`: declares `chat` of type `org.springframework.ai.chat.model.ChatResponse` and sets it to `response.chatResponse()`.
- `String text = chat.getResult().getOutput().getText();`: declares `text` of type `String` and sets it to `chat.getResult().getOutput().getText()`.
- `var usage = chat.getMetadata().getUsage();`: declares `usage` of type `var` and sets it to `chat.getMetadata().getUsage()`.
- `return new ChatResponse( text == null ? "" : text, new Usage(usage.getPromptTokens() ==...`: ends the method and hands back `new ChatResponse( text == null ? "" : text, new Usage(usage.getPromptTokens()...`. `System.nanoTime()` is a precise clock in nanoseconds.

```java
        } catch (RuntimeException e) {
            throw new ModelException("model call failed: " + e.getClass().getSimpleName());
        }
    }
}
```

- `catch (RuntimeException e) {`: runs when the block above threw `RuntimeException e`.
- `throw new ModelException("model call failed: " + e.getClass().getSimpleName());`: signals an error: `new ModelException("model call failed: " + e.getClass().getSimpleName())`. Normal flow stops; the nearest matching `catch` takes over.

#### `java/src/main/java/dev/plainround/router/interfaces/Main.java`

```java
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
```

- `package dev.plainround.router.interfaces;`: declares that this file belongs to the package `dev.plainround.router.interfaces`.
- `import dev.plainround.router.application.AnswerChecks;`: imports the class `dev.plainround.router.application.AnswerChecks` so it can be used by its short name.
- `import dev.plainround.router.application.CostRouter;`: imports the class `dev.plainround.router.application.CostRouter` so it can be used by its short name.
- `import dev.plainround.router.application.Experiments;`: imports the class `dev.plainround.router.application.Experiments` so it can be used by its short name.
- `import dev.plainround.router.application.Experiments.DayResult;`: imports the class `dev.plainround.router.application.Experiments.DayResult` so it can be used by its short name.
- `import dev.plainround.router.application.Experiments.Outcome;`: imports the class `dev.plainround.router.application.Experiments.Outcome` so it can be used by its short name.
- `import dev.plainround.router.application.Experiments.Summary;`: imports the class `dev.plainround.router.application.Experiments.Summary` so it can be used by its short name.
- `import dev.plainround.router.application.ModelTiers;`: imports the class `dev.plainround.router.application.ModelTiers` so it can be used by its short name.
- `import dev.plainround.router.application.ModelTiers.Answered;`: imports the class `dev.plainround.router.application.ModelTiers.Answered` so it can be used by its short name.
- `import dev.plainround.router.domain.Llm.ChatModel;`: imports the class `dev.plainround.router.domain.Llm.ChatModel` so it can be used by its short name.
- `import dev.plainround.router.domain.Routing;`: imports the class `dev.plainround.router.domain.Routing` so it can be used by its short name.
- `import dev.plainround.router.domain.Routing.Bar;`: imports the class `dev.plainround.router.domain.Routing.Bar` so it can be used by its short name.
- `import dev.plainround.router.domain.Routing.PriceTable;`: imports the class `dev.plainround.router.domain.Routing.PriceTable` so it can be used by its short name.

```java
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
```

- `import dev.plainround.router.domain.Routing.Rate;`: imports the class `dev.plainround.router.domain.Routing.Rate` so it can be used by its short name.
- `import dev.plainround.router.domain.Routing.RouterConfig;`: imports the class `dev.plainround.router.domain.Routing.RouterConfig` so it can be used by its short name.
- `import dev.plainround.router.domain.Tasks.Task;`: imports the class `dev.plainround.router.domain.Tasks.Task` so it can be used by its short name.
- `import dev.plainround.router.infrastructure.DataFiles;`: imports the class `dev.plainround.router.infrastructure.DataFiles` so it can be used by its short name.
- `import dev.plainround.router.infrastructure.FilePrompts;`: imports the class `dev.plainround.router.infrastructure.FilePrompts` so it can be used by its short name.
- `import dev.plainround.router.infrastructure.RecordedChatModel;`: imports the class `dev.plainround.router.infrastructure.RecordedChatModel` so it can be used by its short name.
- `import dev.plainround.router.infrastructure.SpringAiChatModel;`: imports the class `dev.plainround.router.infrastructure.SpringAiChatModel` so it can be used by its short name.
- `import java.nio.charset.StandardCharsets;`: imports the class `java.nio.charset.StandardCharsets` so it can be used by its short name.
- `import java.nio.file.Files;`: imports the class `java.nio.file.Files` so it can be used by its short name.
- `import java.nio.file.Path;`: imports the class `java.nio.file.Path` so it can be used by its short name.
- `import java.util.ArrayList;`: imports the class `java.util.ArrayList` so it can be used by its short name.
- `import java.util.LinkedHashMap;`: imports the class `java.util.LinkedHashMap` so it can be used by its short name.
- `import java.util.List;`: imports the class `java.util.List` so it can be used by its short name.
- `import java.util.Map;`: imports the class `java.util.Map` so it can be used by its short name.

```java
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
```

- `import tools.jackson.databind.SerializationFeature;`: imports the class `tools.jackson.databind.SerializationFeature` so it can be used by its short name.
- `import tools.jackson.databind.json.JsonMapper;`: imports the class `tools.jackson.databind.json.JsonMapper` so it can be used by its short name.
- `/** ... */`: a Javadoc comment. It says: "Runs steps 1 to 6 on the same data, prompts and fixtures as Python and writes router.json, day.json and audit.json."
- `public final class Main {`: declares the class `Main` (public, final).
- `private Main() {`: constructor of `Main`, taking no arguments.
- `public static void main(String[] args) throws Exception {`: declares the method `main`, which takes `String[] args` and returns `void`. It belongs to the class (`static`). It may throw `Exception `.
- `Map<String, String> flags = new LinkedHashMap<>();`: declares `flags` of type `String>` and sets it to `new LinkedHashMap<>()`. `new HashMap<>()` makes an empty map.
- `for (int i = 0; i + 1 < args.length; i += 2) {`: repeats the block below as the counting loop `int i = 0; i + 1 < args.length; i += 2` says.
- `flags.put(args[i].replaceFirst("^--", ""), args[i + 1]);`: adds or subtracts one.
- `Path data = Path.of(flags.getOrDefault("data", "data"));`: declares `data` of type `Path` and sets it to `Path.of(flags.getOrDefault("data", "data"))`. `Path.of(...)` makes a file path.

```java
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
```

- `Path configDir = Path.of(flags.getOrDefault("config", "config"));`: declares `configDir` of type `Path` and sets it to `Path.of(flags.getOrDefault("config", "config"))`. `Path.of(...)` makes a file path.
- `Path out = Path.of(flags.getOrDefault("out", "reports/java"));`: declares `out` of type `Path` and sets it to `Path.of(flags.getOrDefault("out", "reports/java"))`. `Path.of(...)` makes a file path.
- `ChatModel model = "recorded".equals(env("LLM_PROVIDER", "recorded")) ? new RecordedChat...`: declares `model` of type `ChatModel` and sets it to `"recorded".equals(env("LLM_PROVIDER", "recorded")) ? new RecordedChatModel(Pa...`. `.equals(x)` compares two objects by value; `Path.of(...)` makes a file path.
- `Map<String, String> models = Map.of("small", env("TIER_SMALL", "qwen2.5:0.5b"), "medium...`: declares `models` of type `String>` and sets it to `Map.of("small", env("TIER_SMALL", "qwen2.5:0.5b"), "medium", env("TIER_MEDIUM...`. `Map.of(...)` makes an unchangeable map.
- `PriceTable prices = DataFiles.loadPrices(configDir);`: declares `prices` of type `PriceTable` and sets it to `DataFiles.loadPrices(configDir)`.
- `Bar bar = DataFiles.loadBar(configDir);`: declares `bar` of type `Bar` and sets it to `DataFiles.loadBar(configDir)`.
- `ModelTiers tiers = new ModelTiers(model, new FilePrompts(Path.of(flags.getOrDefault("pr...`: declares `tiers` of type `ModelTiers` and sets it to `new ModelTiers(model, new FilePrompts(Path.of(flags.getOrDefault("prompts", "...`. `Path.of(...)` makes a file path.
- `List<Task> tasks = DataFiles.loadTasks(data);`: declares `tasks` of type `List<Task>` and sets it to `DataFiles.loadTasks(data)`.
- `List<Task> build = tasks.stream().filter(t -> t.split().equals("build")).toList();`: declares `build` of type `List<Task>` and sets it to `tasks.stream().filter(t -> t.split().equals("build")).toList()`. `.equals(x)` compares two objects by value; `.stream()` starts a pipeline over the items; `.filter(p)` keeps the items for which `p` is true.
- `List<Task> test = tasks.stream().filter(t -> t.split().equals("test")).toList();`: declares `test` of type `List<Task>` and sets it to `tasks.stream().filter(t -> t.split().equals("test")).toList()`. `.equals(x)` compares two objects by value; `.stream()` starts a pipeline over the items; `.filter(p)` keeps the items for which `p` is true.
- `Map<String, Map<String, Answered>> answers = Experiments.collectAnswers(tasks, tiers);`: declares `answers` of type `Answered>>` and sets it to `Experiments.collectAnswers(tasks, tiers)`.

```java
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
```

- `var rates = Experiments.checkResults(build, answers, tiers);`: declares `rates` of type `var` and sets it to `Experiments.checkResults(build, answers, tiers)`.
- `RouterConfig config = Experiments.tune(build, answers, rates, bar);`: declares `config` of type `RouterConfig` and sets it to `Experiments.tune(build, answers, rates, bar)`.
- `RouterConfig noBar = Experiments.tune(build, answers, rates, new Bar(1.0, bar.hardAccur...`: declares `noBar` of type `RouterConfig` and sets it to `Experiments.tune(build, answers, rates, new Bar(1.0, bar.hardAccuracyBar(), b...`.
- `List<Outcome> outcomes = Experiments.routeAll(test, router(tiers, config), null);`: declares `outcomes` of type `List<Outcome>` and sets it to `Experiments.routeAll(test, router(tiers, config), null)`.
- `Map<String, Summary> methods = new LinkedHashMap<>();`: declares `methods` of type `Summary>` and sets it to `new LinkedHashMap<>()`. `new HashMap<>()` makes an empty map.
- `methods.put("router", Experiments.summarize(outcomes));`: runs `methods.put("router", Experiments.summarize(outcomes))`. `.put(k, v)` stores value `v` under key `k`.
- `methods.put("router_no_bar", Experiments.summarize(Experiments.routeAll(test, router(ti...`: runs `methods.put("router_no_bar", Experiments.summarize(Experiments.routeAll(test, router(ti...`. `.put(k, v)` stores value `v` under key `k`.
- `for (String tier : Routing.TIERS) {`: repeats the block below once for each item `String tier` taken from `Routing.TIERS`.
- `methods.put(tier, Experiments.singleModelSummary(test, answers, tier));`: runs `methods.put(tier, Experiments.singleModelSummary(test, answers, tier))`. `.put(k, v)` stores value `v` under key `k`.
- `Map<String, Object> byKind = new LinkedHashMap<>();`: declares `byKind` of type `Object>` and sets it to `new LinkedHashMap<>()`. `new HashMap<>()` makes an empty map.
- `for (String kind : Experiments.KINDS) {`: repeats the block below once for each item `String kind` taken from `Experiments.KINDS`.
- `List<Outcome> subset = outcomes.stream().filter(o -> o.kind().equals(kind)).toList();`: declares `subset` of type `List<Outcome>` and sets it to `outcomes.stream().filter(o -> o.kind().equals(kind)).toList()`. `.equals(x)` compares two objects by value; `.stream()` starts a pipeline over the items; `.filter(p)` keeps the items for which `p` is true.

```java
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
```

- `Map<String, Object> m = new LinkedHashMap<>();`: declares `m` of type `Object>` and sets it to `new LinkedHashMap<>()`. `new HashMap<>()` makes an empty map.
- `m.put("n", subset.size());`: runs `m.put("n", subset.size())`. `.size()` is the number of items; `.put(k, v)` stores value `v` under key `k`.
- `m.put("accuracy", (double) subset.stream().filter(Outcome::correct).count() / subset.si...`: runs `m.put("accuracy", (double) subset.stream().filter(Outcome::correct).count() / subset.si...`. `.size()` is the number of items; `.put(k, v)` stores value `v` under key `k`; `.stream()` starts a pipeline over the items.
- `m.put("cost", subset.stream().mapToDouble(o -> o.decision().spent()).sum());`: runs `m.put("cost", subset.stream().mapToDouble(o -> o.decision().spent()).sum())`. `.put(k, v)` stores value `v` under key `k`; `.stream()` starts a pipeline over the items.
- `byKind.put(kind, m);`: runs `byKind.put(kind, m)`. `.put(k, v)` stores value `v` under key `k`.
- `Map<String, Object> router = new LinkedHashMap<>();`: declares `router` of type `Object>` and sets it to `new LinkedHashMap<>()`. `new HashMap<>()` makes an empty map.
- `router.put("config", configJson(config));`: runs `router.put("config", configJson(config))`. `.put(k, v)` stores value `v` under key `k`.
- `router.put("config_no_bar", configJson(noBar));`: runs `router.put("config_no_bar", configJson(noBar))`. `.put(k, v)` stores value `v` under key `k`.
- `Map<String, Object> methodJson = new LinkedHashMap<>();`: declares `methodJson` of type `Object>` and sets it to `new LinkedHashMap<>()`. `new HashMap<>()` makes an empty map.
- `methods.forEach((k, v) -> methodJson.put(k, summaryJson(v)));`: runs `methods.forEach((k, v) -> methodJson.put(k, summaryJson(v)))`. `.put(k, v)` stores value `v` under key `k`; `.forEach(f)` runs `f` for every item.
- `router.put("methods", methodJson);`: runs `router.put("methods", methodJson)`. `.put(k, v)` stores value `v` under key `k`.
- `router.put("by_kind", byKind);`: runs `router.put("by_kind", byKind)`. `.put(k, v)` stores value `v` under key `k`.
- `router.put("verdict", Experiments.compareToLarge(test, answers, outcomes, bar));`: runs `router.put("verdict", Experiments.compareToLarge(test, answers, outcomes, bar))`. `.put(k, v)` stores value `v` under key `k`.

```java
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
```

- `List<Object> days = new ArrayList<>();`: declares `days` of type `List<Object>` and sets it to `new ArrayList<>()`. `new ArrayList<>()` makes an empty changeable list.
- `for (double fraction : bar.dayBudgetFractions()) {`: repeats the block below once for each item `double fraction` taken from `bar.dayBudgetFractions()`.
- `days.add(dayJson(Experiments.runDay(test, answers, () -> router(tiers, config), fractio...`: runs `days.add(dayJson(Experiments.runDay(test, answers, () -> router(tiers, config), fractio...`. `.add(x)` appends `x`.
- `Map<String, Object> day = new LinkedHashMap<>();`: declares `day` of type `Object>` and sets it to `new LinkedHashMap<>()`. `new HashMap<>()` makes an empty map.
- `day.put("days", days);`: runs `day.put("days", days)`. `.put(k, v)` stores value `v` under key `k`.
- `Map<String, Object> before = Experiments.falseAccepts(outcomes, config);`: declares `before` of type `Object>` and sets it to `Experiments.falseAccepts(outcomes, config)`.
- `String kind = Experiments.weakestKind(outcomes);`: declares `kind` of type `String` and sets it to `Experiments.weakestKind(outcomes)`.
- `Map<String, Object> change = null;`: declares `change` of type `Object>` and sets it to `null`.
- `if (kind != null) {`: runs the block below only if `kind != null` is true.
- `Experiments.Hardened hardened = Experiments.harden(config, kind);`: declares `hardened` of type `Experiments.Hardened` and sets it to `Experiments.harden(config, kind)`.
- `RouterConfig changed = hardened.config();`: declares `changed` of type `RouterConfig` and sets it to `hardened.config()`.
- `List<Outcome> after = Experiments.routeAll(test, router(tiers, changed), null);`: declares `after` of type `List<Outcome>` and sets it to `Experiments.routeAll(test, router(tiers, changed), null)`.

```java
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
```

- `Summary a = Experiments.summarize(outcomes);`: declares `a` of type `Summary` and sets it to `Experiments.summarize(outcomes)`.
- `Summary b = Experiments.summarize(after);`: declares `b` of type `Summary` and sets it to `Experiments.summarize(after)`.
- `change = new LinkedHashMap<>();`: stores `new LinkedHashMap<>()` into `change`. `new HashMap<>()` makes an empty map.
- `change.put("kind", kind);`: runs `change.put("kind", kind)`. `.put(k, v)` stores value `v` under key `k`.
- `change.put("description", hardened.description());`: runs `change.put("description", hardened.description())`. `.put(k, v)` stores value `v` under key `k`.
- `change.put("config_after", configJson(changed));`: runs `change.put("config_after", configJson(changed))`. `.put(k, v)` stores value `v` under key `k`.
- `change.put("accuracy_before", a.accuracy().value());`: runs `change.put("accuracy_before", a.accuracy().value())`. `.put(k, v)` stores value `v` under key `k`.
- `change.put("accuracy_after", b.accuracy().value());`: runs `change.put("accuracy_after", b.accuracy().value())`. `.put(k, v)` stores value `v` under key `k`.
- `change.put("cost_per_correct_before", a.costPerCorrect());`: runs `change.put("cost_per_correct_before", a.costPerCorrect())`. `.put(k, v)` stores value `v` under key `k`.
- `change.put("cost_per_correct_after", b.costPerCorrect());`: runs `change.put("cost_per_correct_after", b.costPerCorrect())`. `.put(k, v)` stores value `v` under key `k`.
- `change.put("false_accepts_before", before.get("false_accepts"));`: runs `change.put("false_accepts_before", before.get("false_accepts"))`. `.get(x)` reads the item or entry for `x`; `.put(k, v)` stores value `v` under key `k`.
- `change.put("false_accepts_after", Experiments.falseAccepts(after, changed).get("false_a...`: runs `change.put("false_accepts_after", Experiments.falseAccepts(after, changed).get("false_a...`. `.get(x)` reads the item or entry for `x`; `.put(k, v)` stores value `v` under key `k`.
- `Map<String, Object> audit = new LinkedHashMap<>();`: declares `audit` of type `Object>` and sets it to `new LinkedHashMap<>()`. `new HashMap<>()` makes an empty map.

```java
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
```

- `audit.put("before", before);`: runs `audit.put("before", before)`. `.put(k, v)` stores value `v` under key `k`.
- `audit.put("change", change);`: runs `audit.put("change", change)`. `.put(k, v)` stores value `v` under key `k`.
- `Files.createDirectories(out);`: runs `Files.createDirectories(out)`.
- `JsonMapper json = JsonMapper.builder().enable(SerializationFeature.INDENT_OUTPUT).enabl...`: declares `json` of type `JsonMapper` and sets it to `JsonMapper.builder().enable(SerializationFeature.INDENT_OUTPUT).enable(Serial...`.
- `Files.writeString(out.resolve("router.json"), json.writeValueAsString(router) + "\n", S...`: runs `Files.writeString(out.resolve("router.json"), json.writeValueAsString(router) + "\n", S...`. `Files.writeString(path, text)` writes text to a file.
- `Files.writeString(out.resolve("day.json"), json.writeValueAsString(day) + "\n", Standar...`: runs `Files.writeString(out.resolve("day.json"), json.writeValueAsString(day) + "\n", Standar...`. `Files.writeString(path, text)` writes text to a file.
- `Files.writeString(out.resolve("audit.json"), json.writeValueAsString(audit) + "\n", Sta...`: runs `Files.writeString(out.resolve("audit.json"), json.writeValueAsString(audit) + "\n", Sta...`. `Files.writeString(path, text)` writes text to a file.
- `System.out.println("java: router accuracy " + methods.get("router").accuracy().value() ...`: runs `System.out.println("java: router accuracy " + methods.get("router").accuracy().value() ...`. `.get(x)` reads the item or entry for `x`.
- `private static CostRouter router(ModelTiers tiers, RouterConfig config) {`: declares the method `router`, which takes `ModelTiers tiers, RouterConfig config` and returns `CostRouter`. It belongs to the class (`static`).
- `return new CostRouter(tiers, new AnswerChecks(tiers, config.labelCheck(), config.policy...`: ends the method and hands back `new CostRouter(tiers, new AnswerChecks(tiers, config.labelCheck(), config.pol...`.

```java
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
```

- `private static String env(String name, String fallback) {`: declares the method `env`, which takes `String name, String fallback` and returns `String`. It belongs to the class (`static`).
- `String value = System.getenv(name);`: declares `value` of type `String` and sets it to `System.getenv(name)`.
- `return value == null || value.isBlank() ? fallback : value;`: ends the method and hands back `value == null || value.isBlank() ? fallback : value`. `.isBlank()` is true when the text is empty or only spaces.
- `private static Map<String, Object> configJson(RouterConfig c) {`: declares the method `configJson`, which takes `RouterConfig c` and returns `Object>`. It belongs to the class (`static`).
- `Map<String, Object> m = new LinkedHashMap<>();`: declares `m` of type `Object>` and sets it to `new LinkedHashMap<>()`. `new HashMap<>()` makes an empty map.
- `m.put("start", c.start());`: runs `m.put("start", c.start())`. `.put(k, v)` stores value `v` under key `k`.
- `m.put("hard_start", c.hardStart());`: runs `m.put("hard_start", c.hardStart())`. `.put(k, v)` stores value `v` under key `k`.
- `m.put("label_check", c.labelCheck());`: runs `m.put("label_check", c.labelCheck())`. `.put(k, v)` stores value `v` under key `k`.
- `m.put("policy_check", c.policyCheck());`: runs `m.put("policy_check", c.policyCheck())`. `.put(k, v)` stores value `v` under key `k`.
- `m.put("request_cap", c.requestCap());`: runs `m.put("request_cap", c.requestCap())`. `.put(k, v)` stores value `v` under key `k`.
- `m.put("tighten_at", c.tightenAt());`: runs `m.put("tighten_at", c.tightenAt())`. `.put(k, v)` stores value `v` under key `k`.
- `return m;`: ends the method and hands back `m`.

```java
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
```

- `private static Object finite(double v) {`: declares the method `finite`, which takes `double v` and returns `Object`. It belongs to the class (`static`).
- `return Double.isInfinite(v) ? null : v;`: ends the method and hands back `Double.isInfinite(v) ? null : v`.
- `private static Map<String, Object> rateJson(Rate r) {`: declares the method `rateJson`, which takes `Rate r` and returns `Object>`. It belongs to the class (`static`).
- `Map<String, Object> m = new LinkedHashMap<>();`: declares `m` of type `Object>` and sets it to `new LinkedHashMap<>()`. `new HashMap<>()` makes an empty map.
- `m.put("successes", r.successes());`: runs `m.put("successes", r.successes())`. `.put(k, v)` stores value `v` under key `k`.
- `m.put("trials", r.trials());`: runs `m.put("trials", r.trials())`. `.put(k, v)` stores value `v` under key `k`.
- `m.put("value", r.value());`: runs `m.put("value", r.value())`. `.put(k, v)` stores value `v` under key `k`.
- `m.put("low", r.low());`: runs `m.put("low", r.low())`. `.put(k, v)` stores value `v` under key `k`.
- `m.put("high", r.high());`: runs `m.put("high", r.high())`. `.put(k, v)` stores value `v` under key `k`.
- `return m;`: ends the method and hands back `m`.

```java
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
```

- `private static Map<String, Object> summaryJson(Summary s) {`: declares the method `summaryJson`, which takes `Summary s` and returns `Object>`. It belongs to the class (`static`).
- `Map<String, Object> m = new LinkedHashMap<>();`: declares `m` of type `Object>` and sets it to `new LinkedHashMap<>()`. `new HashMap<>()` makes an empty map.
- `m.put("n", s.n());`: runs `m.put("n", s.n())`. `.put(k, v)` stores value `v` under key `k`.
- `m.put("accuracy", rateJson(s.accuracy()));`: runs `m.put("accuracy", rateJson(s.accuracy()))`. `.put(k, v)` stores value `v` under key `k`.
- `m.put("total_cost", s.totalCost());`: runs `m.put("total_cost", s.totalCost())`. `.put(k, v)` stores value `v` under key `k`.
- `m.put("cost_per_correct", s.costPerCorrect());`: runs `m.put("cost_per_correct", s.costPerCorrect())`. `.put(k, v)` stores value `v` under key `k`.
- `List<Object> interval = new ArrayList<>();`: declares `interval` of type `List<Object>` and sets it to `new ArrayList<>()`. `new ArrayList<>()` makes an empty changeable list.
- `interval.add(finite(s.costPerCorrectInterval()[0]));`: runs `interval.add(finite(s.costPerCorrectInterval()[0]))`. `.add(x)` appends `x`.
- `interval.add(finite(s.costPerCorrectInterval()[1]));`: runs `interval.add(finite(s.costPerCorrectInterval()[1]))`. `.add(x)` appends `x`.
- `m.put("cost_per_correct_interval", interval);`: runs `m.put("cost_per_correct_interval", interval)`. `.put(k, v)` stores value `v` under key `k`.
- `m.put("served_by", s.servedBy());`: runs `m.put("served_by", s.servedBy())`. `.put(k, v)` stores value `v` under key `k`.
- `m.put("escalated", s.escalated());`: runs `m.put("escalated", s.escalated())`. `.put(k, v)` stores value `v` under key `k`.
- `m.put("max_request_spend", s.maxRequestSpend());`: runs `m.put("max_request_spend", s.maxRequestSpend())`. `.put(k, v)` stores value `v` under key `k`.
- `return m;`: ends the method and hands back `m`.

```java
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
```

- `private static Map<String, Object> dayJson(DayResult d) {`: declares the method `dayJson`, which takes `DayResult d` and returns `Object>`. It belongs to the class (`static`).
- `Map<String, Object> m = new LinkedHashMap<>();`: declares `m` of type `Object>` and sets it to `new LinkedHashMap<>()`. `new HashMap<>()` makes an empty map.
- `m.put("fraction", d.fraction());`: runs `m.put("fraction", d.fraction())`. `.put(k, v)` stores value `v` under key `k`.
- `m.put("budget", d.budget());`: runs `m.put("budget", d.budget())`. `.put(k, v)` stores value `v` under key `k`.
- `m.put("spent", d.spent());`: runs `m.put("spent", d.spent())`. `.put(k, v)` stores value `v` under key `k`.
- `m.put("under_budget", d.underBudget());`: runs `m.put("under_budget", d.underBudget())`. `.put(k, v)` stores value `v` under key `k`.
- `m.put("requests_over_cap", d.requestsOverCap());`: runs `m.put("requests_over_cap", d.requestsOverCap())`. `.put(k, v)` stores value `v` under key `k`.
- `m.put("crossed_at", d.crossedAt());`: runs `m.put("crossed_at", d.crossedAt())`. `.put(k, v)` stores value `v` under key `k`.
- `m.put("accuracy_before", rateJson(d.accuracyBefore()));`: runs `m.put("accuracy_before", rateJson(d.accuracyBefore()))`. `.put(k, v)` stores value `v` under key `k`.
- `m.put("accuracy_after", rateJson(d.accuracyAfter()));`: runs `m.put("accuracy_after", rateJson(d.accuracyAfter()))`. `.put(k, v)` stores value `v` under key `k`.
- `m.put("large_served_after", d.largeServedAfter());`: runs `m.put("large_served_after", d.largeServedAfter())`. `.put(k, v)` stores value `v` under key `k`.
- `m.put("outcomes", List.of());`: runs `m.put("outcomes", List.of())`. `.put(k, v)` stores value `v` under key `k`; `List.of(...)` makes an unchangeable list.
- `return m;`: ends the method and hands back `m`.

## Try it yourself

1. `cd java && ./mvnw -q -B -DskipTests package` builds the jar (needs the Maven download the first time).
2. `ls java/target/*.jar` lists the jar.
3. `grep -c "class\|record\|interface" java/src/main/java/dev/plainround/*/domain/*.java` counts type declarations in the domain classes.
4. `cd java && ./mvnw -q -B test -Dtest=ArchitectureTest` proves the layer rules hold (`archunit.md`).

## Mistakes people make

- Comparing text with `==` instead of `.equals(...)`.
- Integer division: `1 / 2` is `0`.
- Calling a method on `null`.
- Forgetting that a record's components are read with `name()`, not `getName()`.
- Catching an exception and ignoring it.

## Check yourself

1. **What does `javac` do?**  
   Compiles the source into bytecode.
2. **What is a record?**  
   A compact immutable data class.
3. **How does the JVM start a program?**  
   By calling `public static void main(String[] args)`.
4. **How do the layers talk?**  
   Through interfaces defined in the inner layers.
5. **What does `final` on a class mean?**  
   No class may extend it.

## Further reading

The Java Language Specification: https://docs.oracle.com/javase/specs/jls/se21/html/index.html ; the API: https://docs.oracle.com/en/java/javase/21/docs/api/
