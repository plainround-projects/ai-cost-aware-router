# Environment variables and .env files

## What it is

An **environment variable** is a named piece of text that every program started from a terminal can read, such as `HOME` or `PATH`. A `.env` file is a plain text file with one `NAME=value` per line that a tool loads into the environment before starting the program. `.env.example` is the committed template: it lists every variable and a safe default, and you copy it to `.env` for your own settings.

## Why this repository uses it

The program needs settings that change from machine to machine (which model server to call, which port, which key). Hard-coding them would mean editing code to change a port. Reading them from the environment is the standard way (the "twelve-factor" method) to keep code the same and settings separate, and it keeps secrets out of the repository.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `.env.example` | The committed template of every variable with a safe default and no secret. |
| `src/cost_router/infrastructure/env.py` | Reads and validates variables. |
| `src/cost_router/infrastructure/settings.py` | Turns variables into a typed settings object. |
| `Makefile` | `-include .env` and `export` hand the variables to every command. |


## How it works underneath

When a program starts, the operating system gives it a copy of its parent's environment: a table of text names and text values. In Python you read it with `os.environ`, which behaves like a dictionary of strings. Everything is text, so a number such as `LLM_ATTEMPTS=3` arrives as the string `"3"` and the program must convert and check it.

A `.env` file is not a feature of the operating system. Something has to read it. Here **make** does it: `-include .env` reads the lines as make variables, and `export` hands them to every command make runs. So `make run` sees them but a plain `python` in another terminal does not.

Order of precedence matters. A value written on the make command line (`make record SERVE_PORT=8765`) beats `.env`, which beats a variable already in your shell. This repository has met that rule the hard way: a value set only in the shell lost to `.env`.

## Walkthrough of this repository's use

The content below is the content of `.env.example` as it was written by the repository's generator (this note quotes it from that source because the file itself is a settings file that tools in this workspace do not open).

```bash
# Which chat model adapter to use: recorded (default, offline), local (ollama or llama.cpp), openai, anthropic.
```

A comment: it explains the variable that follows.

```bash
LLM_PROVIDER=recorded
```

`LLM_PROVIDER`: Which chat-model adapter to use: `recorded` replays saved answers (default, offline, free), `local` calls a model server on this computer, `openai` calls an OpenAI-compatible hosted server, `anthropic` calls Anthropic's API. The default value is `recorded`.

```bash
LLM_BASE_URL=http://localhost:11434/v1
```

`LLM_BASE_URL`: The web address of the OpenAI-compatible server used when the provider is `local` or `openai`. `/v1` is the path prefix of that API. A port number follows the colon. The default value is `http://localhost:11434/v1`.

```bash
# Set only for a live run. Never commit a value.
```

A comment: it explains the variable that follows.

```bash
OPENAI_API_KEY=
```

`OPENAI_API_KEY`: A secret key for a hosted OpenAI-compatible provider. Empty here on purpose: never commit a value. Put a real key in your own `.env` or your shell, which are not committed. The value is empty.

```bash
ANTHROPIC_API_KEY=
```

`ANTHROPIC_API_KEY`: A secret key for Anthropic's API. Empty here for the same reason. The value is empty.

```bash
# Append every real exchange to this fixture file (used by `make record`).
```

A comment: it explains the variable that follows.

```bash
LLM_RECORD_TO=
```

`LLM_RECORD_TO`: If set, every real model exchange is appended to this file (this is how fixtures are recorded). The value is empty.

```bash
LLM_ATTEMPTS=3
```

`LLM_ATTEMPTS`: How many times a model call is tried before giving up (a failed call is retried with a growing pause). The default value is `3`.

```bash
# The three tiers, cheapest first. For Claude: claude-haiku-5-5, claude-sonnet-5-5, claude-opus-5-5.
```

A comment: it explains the variable that follows.

```bash
TIER_SMALL=qwen2.5:0.5b
```

`TIER_SMALL`: The cheapest model tier. The default value is `qwen2.5:0.5b`.

```bash
TIER_MEDIUM=llama3.2:1b
```

`TIER_MEDIUM`: The middle tier. The default value is `llama3.2:1b`.

```bash
TIER_LARGE=qwen2.5:1.5b
```

`TIER_LARGE`: The most capable and most expensive tier. The default value is `qwen2.5:1.5b`.

```bash
WORKERS=1
```

`WORKERS`: How many calls the program makes at the same time (threads). The default value is `1`.

```bash
LOG_LEVEL=INFO
```

`LOG_LEVEL`: How chatty the logs are (`DEBUG`, `INFO`, `WARNING`, `ERROR`). The default value is `INFO`.


The Python side is in `src/cost_router/infrastructure/env.py` (`read_str`, `read_int`, `read_float` turn text into checked values and raise `ConfigError` on a bad value) and in `settings.py` (which collects them into one frozen object). `python.md` quotes `env.py`.

## Try it yourself

1. `cp -n .env.example .env` (or `make env`) creates your `.env` if missing; it prints `created .env from .env.example` when it does.
2. `grep -v '^#' .env.example | grep -v '^$'` lists the variables without comments.
3. `LOG_LEVEL=DEBUG make -n run` shows that a value placed before `make` is exported to the commands.
4. `python3 -c "import os; print(os.environ.get('LOG_LEVEL', 'not set'))"` prints `not set` in a fresh terminal, but `env LOG_LEVEL=DEBUG python3 -c "..."` prints `DEBUG`: a variable exists only for the process it was given to.

## Mistakes people make

- **Committing a real key.** `.env` is in `.gitignore`; only `.env.example` (with empty key variables) is committed.
- **Forgetting that values are text.** `WORKERS=4` is the string `"4"` until `read_int` converts it and checks the minimum.
- **Expecting the shell to see `.env`.** Only commands run by `make` get it.
- **Quoting problems.** Inside `.env.example` values are written without quotes.

## Check yourself

1. **Why is `.env.example` committed but `.env` not?**  
   The example lists the variables with safe defaults and no secrets; `.env` holds your own values and possibly keys.
2. **What type is an environment variable's value?**  
   Always text. The program converts it, and validates it, itself.
3. **Which beats which: `.env` or a value on the `make` command line?**  
   The command line wins.
4. **What does `LLM_PROVIDER=recorded` mean?**  
   Model calls are answered from saved recordings, so no server and no key are needed.
5. **Why is `OPENAI_API_KEY=` empty in the example?**  
   A key is a secret; the template must never contain one.

## Further reading

The Twelve-Factor App, section on configuration: https://12factor.net/config . GNU Make manual on `include` and `export`: https://www.gnu.org/software/make/manual/
