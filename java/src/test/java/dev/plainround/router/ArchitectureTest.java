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

    @ArchTest
    static final ArchRule applicationKnowsNeitherInfrastructureNorSpring = noClasses()
            .that().resideInAPackage("..application..")
            .should().dependOnClassesThat().resideInAnyPackage("..infrastructure..", "..interfaces..", "org.springframework..", "com.openai..");

    @ArchTest
    static final ArchRule nothingDependsOnInterfaces = noClasses()
            .that().resideOutsideOfPackage("..interfaces..")
            .should().dependOnClassesThat().resideInAPackage("..interfaces..");
}
