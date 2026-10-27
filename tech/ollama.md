# ollama (local model server)

## What it is

**ollama** is a program that downloads open-weight language models, keeps them on your computer, and serves them over HTTP on `http://localhost:11434`. You pull a model once (`ollama pull qwen2.5:1.5b`) and then any program can send it chat requests, without an account or a key. It uses the llama.cpp engine underneath and the GPU if there is one.

## Why this repository uses it

Recording real answers needs a real model. A local model is free, private and reproducible enough, and it speaks the OpenAI-compatible protocol, so the repository's `local` provider needs no extra code. ollama is needed only for `make record`; the tests and the default run replay recordings.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `src/cost_router/infrastructure/llm/factory.py` | `LOCAL_BASE_URL` is `http://localhost:11434/v1`. |
| `.env.example` | Model names and addresses. |
| `Makefile` | `make record`. |
| `README.md` | States the ollama version and the models needed. |


## How it works underneath

ollama is a small HTTP server (a background process, `ollama serve`) plus a model store under `~/.ollama`. A **model name** has the form `name:tag`; `qwen2.5:1.5b` is the Qwen 2.5 model with 1.5 billion parameters, stored quantized (numbers saved with fewer bits to save memory, see `gguf.md`). When a request names a model, ollama loads it into memory (the first request is slow), runs the tokens through it one at a time, and streams or returns the text. It keeps the model loaded for a few minutes, then unloads it. Two APIs: its own (`/api/chat`, `/api/embed`) and the OpenAI-compatible one under `/v1`.

## Walkthrough of this repository's use

### The Makefile target that uses it

`Makefile`

```make
record: $(STAMP) ## re-run everything against local models and append the exchanges to $(RECORD)
	LLM_PROVIDER=local LLM_RECORD_TO=$(RECORD) WORKERS=$${WORKERS:-3} $(CLI) all
```

`make record` runs the study with `LLM_PROVIDER=local` (so the OpenAI-compatible adapter talks to ollama) and `LLM_RECORD_TO` set (so every new exchange is appended to the fixture file; known exchanges are not repeated). It needs ollama running with the models named in `.env.example`.

### The default address

`src/cost_router/infrastructure/llm/factory.py`

<!-- fmt: off -->
```python
LOCAL_BASE_URL = "http://localhost:11434/v1"
```
<!-- fmt: on -->

`11434` is the port ollama listens on and `/v1` selects its OpenAI-compatible API; `localhost` means this computer.

## Try it yourself

1. `ollama --version` prints the client and server version (the repositories were recorded with 0.40.x).
2. `ollama list` lists the models on disk.
3. `ollama pull qwen2.5:1.5b` downloads that model (about 1 GB).
4. `curl -s http://localhost:11434/api/tags | python3 -m json.tool | head` lists the same models over HTTP.
5. `ollama run qwen2.5:1.5b "Say hi in three words"` prints a short reply.

## Mistakes people make

- **Starting a record run without the model pulled**: the server answers 404 and the adapter raises a permanent error.
- **Forgetting that the first call is slow** while the model loads.
- **Assuming the answer is identical on another machine.** That is why the answers are recorded.
- **Using a tag that moves.** `latest` changes over time; the repository names exact tags.

## Check yourself

1. **On which port does ollama listen?**  
   11434.
2. **What does `qwen2.5:1.5b` mean?**  
   The model family and size (name:tag).
3. **Do the tests need ollama?**  
   No, they replay recorded answers.
4. **Which Makefile target needs ollama?**  
   `make record`.
5. **Why is the OpenAI-compatible path `/v1`?**  
   It is the prefix of the API version that ollama copies.

## Further reading

ollama: https://ollama.com/ and https://github.com/ollama/ollama (API reference: docs/api.md; OpenAI compatibility: docs/openai.md). Version used here: 0.40 or newer.
