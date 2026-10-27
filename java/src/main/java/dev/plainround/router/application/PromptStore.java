package dev.plainround.router.application;

/** Versioned prompt templates looked up by name such as label.v2. */
public interface PromptStore {
    String get(String name);
}
