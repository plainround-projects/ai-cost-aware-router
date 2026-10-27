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
            return text.substring(0, end);
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }
}
