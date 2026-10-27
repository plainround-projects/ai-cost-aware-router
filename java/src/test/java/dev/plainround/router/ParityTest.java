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
        for (String name : new String[] {"router.json", "day.json", "audit.json"}) {
            assertSame(JSON.readTree(Files.readString(root.resolve("reports").resolve(name))), JSON.readTree(Files.readString(out.resolve(name))), name);
        }
    }
}
