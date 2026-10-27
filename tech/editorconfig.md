# EditorConfig

## What it is

EditorConfig is a tiny file format, `.editorconfig`, that tells text editors how to save files in a project: which character encoding, which line endings, tabs or spaces. Most editors read it automatically or with a small plug-in. It is not a program; it is a set of instructions that editors follow.

## Why this repository uses it

Several people (and several tools) edit the same files. If one editor saves with tabs and another with spaces, or adds trailing spaces, every change shows up as noise in the history. The file also protects the one place where a tab is mandatory: the Makefile.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `.editorconfig` | The editor settings for every file type in the repository. |


## How it works underneath

An editor looks for `.editorconfig` in the folder of the file you are editing, then in each parent folder, until it finds one with `root = true`. Inside the file, **sections** in square brackets are patterns for file names (`[*.md]` is every Markdown file). Later sections override earlier ones. Settings are `key = value` lines. The editor applies them when you open and save a file. Nothing checks them later, so a tool that writes files directly can still break them (the formatter `ruff` is set to the same line-ending and indent rules in `pyproject.toml`).

## Walkthrough of this repository's use

`.editorconfig`

```text
root = true
```

- `root = true`: Stop looking for more `.editorconfig` files in parent folders.

```text
[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 4
```

- `[*]`: A section: the settings below apply to every file.
- `charset = utf-8`: Save files as UTF-8.
- `end_of_line = lf`: Line endings are a single line feed (`\n`), as on macOS and Linux, never Windows' `\r\n`.
- `insert_final_newline = true`: Every file ends with a newline.
- `trim_trailing_whitespace = true`: Remove spaces at the end of lines when saving.
- `indent_style = space`: Indent with spaces.
- `indent_size = 4`: Four spaces per indent level.

```text
[*.{yml,yaml,json,toml}]
indent_size = 2
```

- `[*.{yml,yaml,json,toml}]`: A section for YAML, JSON and TOML files only.
- `indent_size = 2`: Two spaces per level in those formats.

```text
[Makefile]
indent_style = tab
```

- `[Makefile]`: A section for Makefiles.
- `indent_style = tab`: Makefile recipes must start with a tab character, so use tabs there.

```text
[*.md]
trim_trailing_whitespace = false
```

- `[*.md]`: A section for Markdown files.
- `trim_trailing_whitespace = false`: Two spaces at the end of a Markdown line mean a line break, so they must be kept.

## Try it yourself

1. `cat .editorconfig` shows the file.
2. `grep -c $'\t' Makefile` counts Makefile lines that contain a tab: a large number, because recipes need tabs.
3. `grep -rn ' $' --include=*.py src | head` looks for trailing spaces in Python files: expect no output.
4. `file README.md Makefile` shows the files as text with `LF` line endings (no `CRLF`).

## Mistakes people make

- Thinking the file *enforces* anything: it only informs editors. Use a formatter or a CI check for enforcement.
- Setting `indent_style = space` for everything and breaking the Makefile. This file has a `[Makefile]` section.
- Letting an editor trim trailing spaces in Markdown, where two trailing spaces mean a line break. This file turns trimming off for `*.md`.

## Check yourself

1. **What does `root = true` mean?**  
   Stop searching parent folders for more `.editorconfig` files.
2. **Why does the Makefile section say `indent_style = tab`?**  
   Make recipes must start with a tab character.
3. **Which line ending is used?**  
   `lf`, a single line feed, as on macOS and Linux.
4. **Why is JSON indented by two spaces but Python by four?**  
   The `[*.{yml,yaml,json,toml}]` section overrides the default `indent_size = 4` for those formats.
5. **Does EditorConfig stop a bad file from being committed?**  
   No. It only tells editors how to save; checks happen in `ruff`, CI and review.

## Further reading

EditorConfig specification and file format: https://editorconfig.org/ (the format has no version number that this repository pins).
