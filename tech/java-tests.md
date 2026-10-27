# Java tests, file by file

## What it is

These are the JUnit test classes of the Java half: the unit tests, the architecture rules (ArchUnit) and, where present, the parity test that checks the Java program reproduces the Python reports. `junit.md` and `archunit.md` introduce the tools.

## Why this repository uses it

The Java half is only trustworthy if it is tested as strictly as the Python half. The tests state the same facts in Java.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `java/src/test/java/dev/plainround/router/ArchitectureTest.java` | Quoted and explained in the walkthrough below. |
| `java/src/test/java/dev/plainround/router/DomainTest.java` | Quoted and explained in the walkthrough below. |
| `java/src/test/java/dev/plainround/router/ParityTest.java` | Quoted and explained in the walkthrough below. |


## How it works underneath

Maven's surefire plug-in finds classes with `@Test` methods, creates a new object of the class for each test, runs the method and reports failures. `assertEquals(expected, actual)` throws when the values differ. A parity test runs the real `Main` on the recorded data and compares the JSON it writes with the committed Python reports.

## Walkthrough of this repository's use

### Files in this note

| File | Lines | What it is |
| --- | --- | --- |
| `java/src/test/java/dev/plainround/router/ArchitectureTest.java` | 29 | The dependency rule: domain depends on nothing, application on domain, nothing on interfaces. |
| `java/src/test/java/dev/plainround/router/DomainTest.java` | 97 | The domain behaves exactly like the Python port; reference values were printed by Python. |
| `java/src/test/java/dev/plainround/router/ParityTest.java` | 52 | Step 7: from the same fixtures the Java port writes the same three reports as the committed Python reports. |

Each file below is quoted exactly, in order, in pieces of about a dozen lines. Under each piece, a bullet list explains every statement in the order it appears. The first time an idea shows up in this note it is explained in a bullet that begins **New idea**.

#### `java/src/test/java/dev/plainround/router/ArchitectureTest.java`

```java
package dev.plainround.router;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;

import com.tngtech.archunit.core.importer.ImportOption;
import com.tngtech.archunit.junit.AnalyzeClasses;
import com.tngtech.archunit.junit.ArchTest;
import com.tngtech.archunit.lang.ArchRule;

/** The dependency rule: domain depends on nothing, application on domain, nothing on interfaces. */
@AnalyzeClasses(packages = "dev.plainround.router", importOptions = ImportOption.DoNotIncludeTests.class)
class ArchitectureTest {

    @ArchTest
    static final ArchRule domainKnowsNoOuterLayerAndNoSdk = noClasses()
            .that().resideInAPackage("..domain..")
            .should().dependOnClassesThat().resideInAnyPackage(
                    "..application..", "..infrastructure..", "..interfaces..", "org.springframework..", "com.openai..", "tools.jackson..");
```

- **New idea.** A **package** is the address of a class: a dotted name that matches the folder path under `src/main/java` (or `src/test/java`). Packages group classes and control who may see them.
- `package dev.plainround.router;`: declares that this file belongs to the package `dev.plainround.router`.
- **New idea.** An **import** lets the file use a class from another package by its short name. `import static` brings in a static method, so it can be called without the class name.
- `import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;`: imports the static member `com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses` so it can be used by its short name.
- `import com.tngtech.archunit.core.importer.ImportOption;`: imports the class `com.tngtech.archunit.core.importer.ImportOption` so it can be used by its short name.
- `import com.tngtech.archunit.junit.AnalyzeClasses;`: imports the class `com.tngtech.archunit.junit.AnalyzeClasses` so it can be used by its short name.
- `import com.tngtech.archunit.junit.ArchTest;`: imports the class `com.tngtech.archunit.junit.ArchTest` so it can be used by its short name.
- `import com.tngtech.archunit.lang.ArchRule;`: imports the class `com.tngtech.archunit.lang.ArchRule` so it can be used by its short name.
- **New idea.** A comment starting with `/**` is **Javadoc**: documentation that tools turn into pages. Ordinary `//` and `/* */` comments are ignored by the compiler.
- `/** ... */`: a Javadoc comment. It says: "The dependency rule: domain depends on nothing, application on domain, nothing on interfaces."
- **New idea.** A **class** describes a kind of object: its data (fields) and behaviour (methods). `final` forbids subclasses; `public` makes it visible to every package.
- **New idea.** An **annotation** is a label starting with `@` placed before a class, method or field. Tools and the compiler read it; `@Override` says the method replaces one from a parent type, `@Test` marks a test method.
- `class ArchitectureTest {`: declares the class `ArchitectureTest` (package-private). Annotation(s): `@AnalyzeClasses(packages = "dev.plainround.router", impor...`.
- **New idea.** A **field** is a variable that belongs to an object (or, if `static`, to the class). `final` means it can be assigned once. `private` hides it from other classes.
- `static final ArchRule domainKnowsNoOuterLayerAndNoSdk = noClasses() .that().resideInAPa...`: declares the field `domainKnowsNoOuterLayerAndNoSdk` of type `ArchRule` and sets it to `noClasses() .that().resideInAPackage("..domain..") .should().dependOnClassesT...`. Annotation(s): `@ArchTest`.

```java
    @ArchTest
    static final ArchRule applicationKnowsNeitherInfrastructureNorSpring = noClasses()
            .that().resideInAPackage("..application..")
            .should().dependOnClassesThat().resideInAnyPackage("..infrastructure..", "..interfaces..", "org.springframework..", "com.openai..");

    @ArchTest
    static final ArchRule nothingDependsOnInterfaces = noClasses()
            .that().resideOutsideOfPackage("..interfaces..")
            .should().dependOnClassesThat().resideInAPackage("..interfaces..");
}
```

- `static final ArchRule applicationKnowsNeitherInfrastructureNorSpring = noClasses() .tha...`: declares the field `applicationKnowsNeitherInfrastructureNorSpring` of type `ArchRule` and sets it to `noClasses() .that().resideInAPackage("..application..") .should().dependOnCla...`. Annotation(s): `@ArchTest`.
- `static final ArchRule nothingDependsOnInterfaces = noClasses() .that().resideOutsideOfP...`: declares the field `nothingDependsOnInterfaces` of type `ArchRule` and sets it to `noClasses() .that().resideOutsideOfPackage("..interfaces..") .should().depend...`. Annotation(s): `@ArchTest`.

#### `java/src/test/java/dev/plainround/router/DomainTest.java`

```java
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
```

- `package dev.plainround.router;`: declares that this file belongs to the package `dev.plainround.router`.
- `import static org.junit.jupiter.api.Assertions.assertEquals;`: imports the static member `org.junit.jupiter.api.Assertions.assertEquals` so it can be used by its short name.
- `import static org.junit.jupiter.api.Assertions.assertFalse;`: imports the static member `org.junit.jupiter.api.Assertions.assertFalse` so it can be used by its short name.
- `import static org.junit.jupiter.api.Assertions.assertNull;`: imports the static member `org.junit.jupiter.api.Assertions.assertNull` so it can be used by its short name.
- `import static org.junit.jupiter.api.Assertions.assertThrows;`: imports the static member `org.junit.jupiter.api.Assertions.assertThrows` so it can be used by its short name.
- `import static org.junit.jupiter.api.Assertions.assertTrue;`: imports the static member `org.junit.jupiter.api.Assertions.assertTrue` so it can be used by its short name.
- `import dev.plainround.router.domain.Checks;`: imports the class `dev.plainround.router.domain.Checks` so it can be used by its short name.
- `import dev.plainround.router.domain.Llm.ChatRequest;`: imports the class `dev.plainround.router.domain.Llm.ChatRequest` so it can be used by its short name.
- `import dev.plainround.router.domain.Llm.Message;`: imports the class `dev.plainround.router.domain.Llm.Message` so it can be used by its short name.
- `import dev.plainround.router.domain.Routing;`: imports the class `dev.plainround.router.domain.Routing` so it can be used by its short name.
- `import dev.plainround.router.domain.Routing.CheckRates;`: imports the class `dev.plainround.router.domain.Routing.CheckRates` so it can be used by its short name.
- `import dev.plainround.router.domain.Routing.DayBudget;`: imports the class `dev.plainround.router.domain.Routing.DayBudget` so it can be used by its short name.

```java
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
```

- `import dev.plainround.router.domain.Stats;`: imports the class `dev.plainround.router.domain.Stats` so it can be used by its short name.
- `import dev.plainround.router.domain.Tasks;`: imports the class `dev.plainround.router.domain.Tasks` so it can be used by its short name.
- `import dev.plainround.router.domain.Tasks.Kind;`: imports the class `dev.plainround.router.domain.Tasks.Kind` so it can be used by its short name.
- `import dev.plainround.router.domain.Tasks.RefundOrder;`: imports the class `dev.plainround.router.domain.Tasks.RefundOrder` so it can be used by its short name.
- `import dev.plainround.router.domain.Tasks.Task;`: imports the class `dev.plainround.router.domain.Tasks.Task` so it can be used by its short name.
- `import java.util.List;`: imports the class `java.util.List` so it can be used by its short name.
- `import java.util.Map;`: imports the class `java.util.Map` so it can be used by its short name.
- `import org.junit.jupiter.api.Test;`: imports the class `org.junit.jupiter.api.Test` so it can be used by its short name.
- `/** ... */`: a Javadoc comment. It says: "The domain behaves exactly like the Python port; reference values were printed by Python."
- `class DomainTest {`: declares the class `DomainTest` (package-private).
- **New idea.** A **method** is a function that belongs to a class. Its header gives, in order, who may call it (`public`, `private`), whether it belongs to the class (`static`), the type it returns (`void` means nothing), its name, and its parameters with their types.
- **New idea.** `static` means the member belongs to the class itself, not to one object; it is called as `ClassName.method()`.
- `private static Task refundTask(String text, RefundOrder... orders) {`: declares the method `refundTask`, which takes `String text, RefundOrder... orders` and returns `Task`. It belongs to the class (`static`).
- **New idea.** `return value;` ends the method and hands the value to the caller.
- `return new Task("t", Kind.REFUND, "easy", "test", text, 0, List.of(orders));`: ends the method and hands back `new Task("t", Kind.REFUND, "easy", "test", text, 0, List.of(orders))`. `List.of(...)` makes an unchangeable list.

```java
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
```

- **New idea.** A **JUnit test** is a method marked `@Test`. It passes if it finishes without an exception; the `assert...` methods throw when what they check is false (`junit.md`).
- `void fixtureKeysEqualThePythonKeys() {`: declares the method `fixtureKeysEqualThePythonKeys`, which takes no arguments and returns `void`. Annotation(s): `@Test`.
- **New idea.** A **local variable** exists only inside the method (or block) where it is declared. Its type comes first (`var` lets the compiler infer it).
- **New idea.** `new ClassName(args)` creates an object by calling the constructor.
- `ChatRequest full = new ChatRequest("m", List.of(new Message("system", "sys é"), new Mes...`: declares `full` of type `ChatRequest` and sets it to `new ChatRequest("m", List.of(new Message("system", "sys é"), new Message("use...`. `List.of(...)` makes an unchangeable list.
- `assertEquals("a9ac1dcf4c0607c0fe3ef520314f34301f1b7abe8c1c3847e43d884143adb4f5", full.f...`: runs `assertEquals("a9ac1dcf4c0607c0fe3ef520314f34301f1b7abe8c1c3847e43d884143adb4f5", full.f...`. `assertEquals(expected, actual)` fails the test when they differ.
- `void shuffleMatchesPython() {`: declares the method `shuffleMatchesPython`, which takes no arguments and returns `void`. Annotation(s): `@Test`.
- `assertEquals(List.of(1, 9, 8, 6, 7, 2, 0, 5, 4, 3), java.util.stream.IntStream.of(Stats...`: runs `assertEquals(List.of(1, 9, 8, 6, 7, 2, 0, 5, 4, 3), java.util.stream.IntStream.of(Stats...`. `.toList()` ends the pipeline with an unchangeable list; `List.of(...)` makes an unchangeable list; `assertEquals(expected, actual)` fails the test when they differ.
- `void refundRulesFollowThePolicy() {`: declares the method `refundRulesFollowThePolicy`, which takes no arguments and returns `void`. Annotation(s): `@Test`.
- `assertEquals(5000, Tasks.refundCents(new RefundOrder("o", 5000, 10, 5000, false)));`: runs `assertEquals(5000, Tasks.refundCents(new RefundOrder("o", 5000, 10, 5000, false)))`. `assertEquals(expected, actual)` fails the test when they differ.

```java
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
```

- `assertEquals(4000, Tasks.refundCents(new RefundOrder("o", 5000, 20, 5000, false)));`: runs `assertEquals(4000, Tasks.refundCents(new RefundOrder("o", 5000, 20, 5000, false)))`. `assertEquals(expected, actual)` fails the test when they differ.
- `assertEquals(0, Tasks.refundCents(new RefundOrder("o", 5000, 31, 5000, false)));`: runs `assertEquals(0, Tasks.refundCents(new RefundOrder("o", 5000, 31, 5000, false)))`. `assertEquals(expected, actual)` fails the test when they differ.
- `assertEquals(2500, Tasks.refundCents(new RefundOrder("o", 5000, 20, 2500, true)));`: runs `assertEquals(2500, Tasks.refundCents(new RefundOrder("o", 5000, 20, 2500, true)))`. `assertEquals(expected, actual)` fails the test when they differ.
- `assertEquals(1000, Tasks.refundCents(new RefundOrder("o", 5000, 16, 1250, false)));`: runs `assertEquals(1000, Tasks.refundCents(new RefundOrder("o", 5000, 16, 1250, false)))`. `assertEquals(expected, actual)` fails the test when they differ.
- `void answersAreParsedLikePython() {`: declares the method `answersAreParsedLikePython`, which takes no arguments and returns `void`. Annotation(s): `@Test`.
- `assertEquals("billing", Checks.parseLabel(" Billing. "));`: runs `assertEquals("billing", Checks.parseLabel(" Billing. "))`. `assertEquals(expected, actual)` fails the test when they differ.
- `assertEquals("shipping", Checks.parseLabel("\"shipping\""));`: runs `assertEquals("shipping", Checks.parseLabel("\"shipping\""))`. `assertEquals(expected, actual)` fails the test when they differ.
- `assertNull(Checks.parseLabel("customer support"));`: runs `assertNull(Checks.parseLabel("customer support"))`. `assertNull(x)` fails the test unless `x` is `null`.
- `assertEquals(4000, Checks.parseAmountCents("$40.00"));`: runs `assertEquals(4000, Checks.parseAmountCents("$40.00"))`. `assertEquals(expected, actual)` fails the test when they differ.
- `assertEquals(1200, Checks.parseAmountCents("12"));`: runs `assertEquals(1200, Checks.parseAmountCents("12"))`. `assertEquals(expected, actual)` fails the test when they differ.
- `assertEquals(123450, Checks.parseAmountCents("1,234.5"));`: runs `assertEquals(123450, Checks.parseAmountCents("1,234.5"))`. `assertEquals(expected, actual)` fails the test when they differ.

```java
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
```

- `assertEquals(4000, Checks.parseAmountCents("Worked out: 50 - 10 = 40\nRefund: 40.00"));`: runs `assertEquals(4000, Checks.parseAmountCents("Worked out: 50 - 10 = 40\nRefund: 40.00"))`. `assertEquals(expected, actual)` fails the test when they differ.
- `assertEquals(725, Checks.parseAmountCents("Refund: $5.00 ... then\nRefund: $7.25"));`: runs `assertEquals(725, Checks.parseAmountCents("Refund: $5.00 ... then\nRefund: $7.25"))`. `assertEquals(expected, actual)` fails the test when they differ.
- `assertNull(Checks.parseAmountCents("The refund is 40.00 dollars"));`: runs `assertNull(Checks.parseAmountCents("The refund is 40.00 dollars"))`. `assertNull(x)` fails the test unless `x` is `null`.
- `String reply = "Answer: yes\nQuote: \"" + Tasks.POLICY_LINES.get(2) + "\"\n\nQuestion: ...`: declares `reply` of type `String` and sets it to `"Answer: yes\nQuote: \"" + Tasks.POLICY_LINES.get(2) + "\"\n\nQuestion: and t...`. `.get(x)` reads the item or entry for `x`.
- `assertEquals(2, Checks.quotedLineIndex(reply));`: runs `assertEquals(2, Checks.quotedLineIndex(reply))`. `assertEquals(expected, actual)` fails the test when they differ.
- `assertNull(Checks.quotedLineIndex("no quote at all"));`: runs `assertNull(Checks.quotedLineIndex("no quote at all"))`. `assertNull(x)` fails the test unless `x` is `null`.
- `assertTrue(Checks.checkPolicy(reply));`: runs `assertTrue(Checks.checkPolicy(reply))`. `assertTrue(x)` fails the test unless `x` is true.
- `assertTrue(Checks.checkLabelAgreement("billing", "Billing."));`: runs `assertTrue(Checks.checkLabelAgreement("billing", "Billing."))`. `assertTrue(x)` fails the test unless `x` is true.
- `assertFalse(Checks.checkLabelAgreement("billing", "returns"));`: runs `assertFalse(Checks.checkLabelAgreement("billing", "returns"))`. `assertFalse(x)` fails the test unless `x` is false.
- `void gradingAndTheRefundCheckUseTheRecomputedAmount() {`: declares the method `gradingAndTheRefundCheckUseTheRecomputedAmount`, which takes no arguments and returns `void`. Annotation(s): `@Test`.
- `Task task = refundTask("Order PR-100001 arrived 20 days ago.", new RefundOrder("PR-1000...`: declares `task` of type `Task` and sets it to `refundTask("Order PR-100001 arrived 20 days ago.", new RefundOrder("PR-100001...`.

```java
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
```

- `assertTrue(Checks.isCorrect(task, "40.00"));`: runs `assertTrue(Checks.isCorrect(task, "40.00"))`. `assertTrue(x)` fails the test unless `x` is true.
- `assertFalse(Checks.checkRefund(task, "50.00"));`: runs `assertFalse(Checks.checkRefund(task, "50.00"))`. `assertFalse(x)` fails the test unless `x` is false.
- `void theHardSignalSeesTwoOrdersOrAnExceptionWord() {`: declares the method `theHardSignalSeesTwoOrdersOrAnExceptionWord`, which takes no arguments and returns `void`. Annotation(s): `@Test`.
- `assertTrue(Routing.hardSignal(refundTask("Order PR-100001 and PR-200002 are returned.")));`: runs `assertTrue(Routing.hardSignal(refundTask("Order PR-100001 and PR-200002 are returned.")))`. `assertTrue(x)` fails the test unless `x` is true.
- `assertTrue(Routing.hardSignal(refundTask("The item was damaged.")));`: runs `assertTrue(Routing.hardSignal(refundTask("The item was damaged.")))`. `assertTrue(x)` fails the test unless `x` is true.
- `assertFalse(Routing.hardSignal(refundTask("I was charged twice for PR-100001.")));`: runs `assertFalse(Routing.hardSignal(refundTask("I was charged twice for PR-100001.")))`. `assertFalse(x)` fails the test unless `x` is false.
- `void checkRatesAndTheDayBudget() {`: declares the method `checkRatesAndTheDayBudget`, which takes no arguments and returns `void`. Annotation(s): `@Test`.
- `CheckRates r = Routing.checkRates(List.of(true, true, false, true), List.of(true, false...`: declares `r` of type `CheckRates` and sets it to `Routing.checkRates(List.of(true, true, false, true), List.of(true, false, tru...`. `List.of(...)` makes an unchangeable list.

```java
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
```

- `assertEquals(1.0, r.falseAcceptRate());`: runs `assertEquals(1.0, r.falseAcceptRate())`. `assertEquals(expected, actual)` fails the test when they differ.
- `assertEquals(0.5, r.falseRejectRate());`: runs `assertEquals(0.5, r.falseRejectRate())`. `assertEquals(expected, actual)` fails the test when they differ.
- `assertEquals(2.0 / 3.0, r.wrongAmongAccepted(), 1e-12);`: runs `assertEquals(2.0 / 3.0, r.wrongAmongAccepted(), 1e-12)`. `assertEquals(expected, actual)` fails the test when they differ.
- `DayBudget day = new DayBudget(2.0);`: declares `day` of type `DayBudget` and sets it to `new DayBudget(2.0)`.
- `day.add(1.5);`: runs `day.add(1.5)`. `.add(x)` appends `x`.
- `assertEquals(0.75, day.usedShare());`: runs `assertEquals(0.75, day.usedShare())`. `assertEquals(expected, actual)` fails the test when they differ.
- **New idea.** A **lambda** `x -> x + 1` is a small unnamed function; `(a, b) -> a + b` takes two parameters. A method reference `Class::method` is a shorthand for one.
- `assertThrows(IllegalArgumentException.class, () -> new DayBudget(0));`: runs `assertThrows(IllegalArgumentException.class, () -> new DayBudget(0))`. `assertThrows(Type.class, code)` passes only if the code throws that exception.
- `assertThrows(IllegalArgumentException.class, () -> new Routing.PriceTable("x", Map.of("...`: runs `assertThrows(IllegalArgumentException.class, () -> new Routing.PriceTable("x", Map.of("...`. `Map.of(...)` makes an unchangeable map; `assertThrows(Type.class, code)` passes only if the code throws that exception.
- `assertEquals(1.2, new Routing.PriceTable("x", Map.of("small", 1.0, "medium", 1.0, "larg...`: runs `assertEquals(1.2, new Routing.PriceTable("x", Map.of("small", 1.0, "medium", 1.0, "larg...`. `Map.of(...)` makes an unchangeable map; `assertEquals(expected, actual)` fails the test when they differ.

#### `java/src/test/java/dev/plainround/router/ParityTest.java`

```java
package dev.plainround.router;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.plainround.router.interfaces.Main;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

/** Step 7: from the same fixtures the Java port writes the same three reports as the committed Python reports. */
class ParityTest {
```

- `package dev.plainround.router;`: declares that this file belongs to the package `dev.plainround.router`.
- `import static org.junit.jupiter.api.Assertions.assertEquals;`: imports the static member `org.junit.jupiter.api.Assertions.assertEquals` so it can be used by its short name.
- `import static org.junit.jupiter.api.Assertions.assertTrue;`: imports the static member `org.junit.jupiter.api.Assertions.assertTrue` so it can be used by its short name.
- `import dev.plainround.router.interfaces.Main;`: imports the class `dev.plainround.router.interfaces.Main` so it can be used by its short name.
- `import java.nio.file.Files;`: imports the class `java.nio.file.Files` so it can be used by its short name.
- `import java.nio.file.Path;`: imports the class `java.nio.file.Path` so it can be used by its short name.
- `import org.junit.jupiter.api.Test;`: imports the class `org.junit.jupiter.api.Test` so it can be used by its short name.
- `import tools.jackson.databind.JsonNode;`: imports the class `tools.jackson.databind.JsonNode` so it can be used by its short name.
- `import tools.jackson.databind.json.JsonMapper;`: imports the class `tools.jackson.databind.json.JsonMapper` so it can be used by its short name.
- `/** ... */`: a Javadoc comment. It says: "Step 7: from the same fixtures the Java port writes the same three reports as the committed Python reports."
- `class ParityTest {`: declares the class `ParityTest` (package-private).

```java
    private static final JsonMapper JSON = JsonMapper.builder().build();

    private static void assertSame(JsonNode expected, JsonNode actual, String path) {
        if (expected.isObject()) {
            assertEquals(expected.size(), actual.size(), path + " has different keys");
            for (String name : expected.propertyNames()) {
                assertTrue(actual.has(name), path + "." + name + " is missing");
                assertSame(expected.get(name), actual.get(name), path + "." + name);
            }
        } else if (expected.isArray()) {
            assertEquals(expected.size(), actual.size(), path + " has a different length");
            for (int i = 0; i < expected.size(); i++) {
                assertSame(expected.get(i), actual.get(i), path + "[" + i + "]");
            }
```

- `private static final JsonMapper JSON = JsonMapper.builder().build();`: declares the field `JSON` of type `JsonMapper` and sets it to `JsonMapper.builder().build()`.
- `private static void assertSame(JsonNode expected, JsonNode actual, String path) {`: declares the method `assertSame`, which takes `JsonNode expected, JsonNode actual, String path` and returns `void`. It belongs to the class (`static`).
- **New idea.** **if / else** runs a block only when the condition in brackets is true. Conditions use `==`, `!=`, `<`, `>`, `&&` (and), `||` (or) and `!` (not). Compare text with `.equals(...)`, never with `==`.
- `if (expected.isObject()) {`: runs the block below only if `expected.isObject()` is true.
- `assertEquals(expected.size(), actual.size(), path + " has different keys");`: runs `assertEquals(expected.size(), actual.size(), path + " has different keys")`. `.size()` is the number of items; `assertEquals(expected, actual)` fails the test when they differ.
- **New idea.** A **for loop** repeats a block. `for (int i = 0; i < n; i++)` counts; `for (Item x : items)` visits every item of a collection.
- `for (String name : expected.propertyNames()) {`: repeats the block below once for each item `String name` taken from `expected.propertyNames()`.
- `assertTrue(actual.has(name), path + "." + name + " is missing");`: runs `assertTrue(actual.has(name), path + "." + name + " is missing")`. `assertTrue(x)` fails the test unless `x` is true; `.has("x")` tests whether a JSON field exists.
- `assertSame(expected.get(name), actual.get(name), path + "." + name);`: runs `assertSame(expected.get(name), actual.get(name), path + "." + name)`. `.get(x)` reads the item or entry for `x`.
- `else if (expected.isArray()) {`: otherwise, runs the block below only if `expected.isArray()` is true.
- `assertEquals(expected.size(), actual.size(), path + " has a different length");`: runs `assertEquals(expected.size(), actual.size(), path + " has a different length")`. `.size()` is the number of items; `assertEquals(expected, actual)` fails the test when they differ.
- `for (int i = 0; i < expected.size(); i++) {`: repeats the block below as the counting loop `int i = 0; i < expected.size(); i++` says.
- `assertSame(expected.get(i), actual.get(i), path + "[" + i + "]");`: runs `assertSame(expected.get(i), actual.get(i), path + "[" + i + "]")`. `.get(x)` reads the item or entry for `x`.

```java
        } else if (expected.isNumber()) {
            assertEquals(expected.asDouble(), actual.asDouble(), 1e-6, path);
        } else {
            assertEquals(expected, actual, path);
        }
    }

    @Test
    void javaReportsEqualPythonReports() throws Exception {
        Path root = Path.of("..");
        Path out = Path.of("target", "parity");
        Main.main(new String[] {
            "--data", root.resolve("data").toString(),
            "--prompts", root.resolve("prompts").toString(),
            "--fixtures", root.resolve("tests/fixtures").toString(),
            "--config", root.resolve("config").toString(),
            "--out", out.toString()
        });
```

- `else if (expected.isNumber()) {`: otherwise, runs the block below only if `expected.isNumber()` is true.
- `assertEquals(expected.asDouble(), actual.asDouble(), 1e-6, path);`: runs `assertEquals(expected.asDouble(), actual.asDouble(), 1e-6, path)`. `assertEquals(expected, actual)` fails the test when they differ; `.asString()`, `.asInt()`, `.asDouble()` read a JSON value as that type.
- `else {`: runs the block below when none of the conditions above held.
- `assertEquals(expected, actual, path);`: runs `assertEquals(expected, actual, path)`. `assertEquals(expected, actual)` fails the test when they differ.
- `void javaReportsEqualPythonReports() throws Exception {`: declares the method `javaReportsEqualPythonReports`, which takes no arguments and returns `void`. It may throw `Exception `. Annotation(s): `@Test`.
- `Path root = Path.of("..");`: declares `root` of type `Path` and sets it to `Path.of("..")`. `Path.of(...)` makes a file path.
- `Path out = Path.of("target", "parity");`: declares `out` of type `Path` and sets it to `Path.of("target", "parity")`. `Path.of(...)` makes a file path.
- **New idea.** `=` stores a value in a variable; `+=` adds to it; `++` adds one.
- `Main.main(new String[] { "--data", root.resolve("data").toString(), "--prompts", root.r...`: adds or subtracts one.

```java
        for (String name : new String[] {"router.json", "day.json", "audit.json"}) {
            assertSame(JSON.readTree(Files.readString(root.resolve("reports").resolve(name))), JSON.readTree(Files.readString(out.resolve(name))), name);
        }
    }
}
```

- `for (String name : new String[] {"router.json", "day.json", "audit.json"}) {`: repeats the block below once for each item `String name` taken from `new String[] {"router.json", "day.json", "audit...`.
- `assertSame(JSON.readTree(Files.readString(root.resolve("reports").resolve(name))), JSON...`: runs `assertSame(JSON.readTree(Files.readString(root.resolve("reports").resolve(name))), JSON...`. `Files.readString(path)` reads a whole file as text; `.readTree(text)` parses JSON text into a tree of nodes.

## Try it yourself

1. `make java-test` builds and runs all tests (the build needs the Maven download the first time); a quiet run prints nothing when all pass.
2. `cd java && ./mvnw -B test | grep "Tests run"` prints one line per test class and a total with `Failures: 0, Errors: 0`.
3. `cd java && ./mvnw -q -B test -Dtest=ArchitectureTest` runs one class.

## Mistakes people make

- Swapping the expected and actual values in `assertEquals`.
- Comparing decimals exactly.
- Tests that depend on the order of other tests.
- Forgetting `@Test`, so the method never runs.

## Check yourself

1. **What marks a test method?**  
   `@Test` (or `@ParameterizedTest`).
2. **What does `assertThrows` check?**  
   That the given code throws the given exception type.
3. **Why does JUnit create a new object per test?**  
   So tests cannot share state by accident.
4. **What does the parity test compare?**  
   The JSON reports written by Java and by Python from the same recorded data.
5. **Which rules does ArchUnit check?**  
   That the layers depend on each other only in the allowed direction.

## Further reading

JUnit 5: https://junit.org/junit5/docs/current/user-guide/ ; ArchUnit: https://www.archunit.org/userguide/html/000_Index.html
