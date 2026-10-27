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
            throw new UncheckedIOException(e);
        }
    }
}
