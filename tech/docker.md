# Docker

## What it is

Docker packages a program together with everything it needs (the operating-system files, the language runtime, the libraries) into an **image**. Starting an image gives a **container**: an isolated process that sees only the image's files. A **Dockerfile** is the recipe that builds an image, one instruction per line.

## Why this repository uses it

An image proves that the repository can be built and started from nothing but its own files, and it gives you a way to run the program without installing Python or Java. The images here start as an unprivileged user and report their health, which are the habits of a deployable service.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `Dockerfile` | Image of the Python program. |
| `.dockerignore` | Files that must not be sent to the build. |
| `Makefile` | `make docker-build` builds the image(s). |


## How it works underneath

**Image layers.** Each instruction (`FROM`, `COPY`, `RUN`, ...) produces a **layer**: a set of file changes. Docker caches layers; if an instruction and everything before it is unchanged, the cached layer is reused. This is why the Dockerfile copies the lock file and installs libraries *before* copying the source: source changes often, libraries rarely.

**Build context.** `docker build .` sends the folder (minus `.dockerignore` entries) to the Docker daemon, which is the background service that builds and runs containers. `COPY` can only read from that context.

**Containers are processes.** A container is an ordinary process with its own view of the file system, process table and network (Linux features called *namespaces* and *cgroups*). It stops when its main process (`CMD`) ends. On macOS, Docker runs a small Linux virtual machine to provide the Linux kernel.

**Multi-stage builds.** A Dockerfile can have several `FROM` lines. Each starts a new stage; `COPY --from=build` takes files from an earlier stage. The final image keeps only what is copied, so compilers stay out.

**Non-root.** By default processes in a container are root. The image creates a user with id 10001 and switches with `USER`, so a compromised program has fewer rights.

## Walkthrough of this repository's use

### `Dockerfile`

`Dockerfile`

```dockerfile
# The command-line program as an image. Nothing here serves traffic; the health command is the image's check.
#   docker run --rm cost-router:dev cost-router all     (replays the recorded fixtures)
FROM python:3.13.1-slim-bookworm
```

- `# The command-line program as an image. Nothing here serves traffic; the health command is the image`: a comment written by the author; the tool ignores it. It explains the lines below.
- `#   docker run --rm cost-router:dev cost-router all     (replays the recorded fixtures)`: a comment written by the author; the tool ignores it. It explains the lines below.
- `FROM python:3.13.1-slim-bookworm`: The base image: a minimal Debian 12 ("bookworm") with Python 3.13.1 installed. The exact tag is pinned, so a rebuild next month starts from the same base.

```dockerfile
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PROJECT_ROOT=/app
```

- `ENV PYTHONDONTWRITEBYTECODE=1 \`: Sets environment variables inside the image (an environment variable is a named string every process can read): `PYTHONDONTWRITEBYTECODE` stops Python writing `.pyc` cache files into the image; `PYTHONUNBUFFERED` prints output at once instead of in batches, so `docker logs` is live; `PIP_NO_CACHE_DIR` stops pip keeping downloaded files, which keeps the image small; `PIP_DISABLE_PIP_VERSION_CHECK` stops pip asking the internet whether a newer pip exists; `PROJECT_ROOT` tells the program where its `data/`, `prompts/` and `config/` folders are (the code otherwise guesses from its own location; see `python.md`).

```dockerfile
WORKDIR /app
COPY requirements.lock ./
RUN pip install --require-hashes -r requirements.lock
```

- `WORKDIR /app`: Sets the working directory for the following instructions and for the running container, creating it if needed.
- `COPY requirements.lock ./`: Copies only the lock file first. Docker caches each instruction's result; because the lock file changes rarely, the slow install below is reused from cache when only source code changed.
- `RUN pip install --require-hashes -r requirements.lock`: Installs the exact, hash-checked libraries (see `pip-and-venv.md`).

```dockerfile
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-deps .
COPY data ./data
COPY prompts ./prompts
COPY config ./config
COPY tests/fixtures ./tests/fixtures
```

- `COPY pyproject.toml README.md ./`: Copies what the package build needs.
- `COPY src ./src`: Copies the source code.
- `RUN pip install --no-deps .`: Installs the project itself without touching the already-installed libraries.
- `COPY data ./data`: Copies a data folder the program reads at run time.
- `COPY prompts ./prompts`: Copies a data folder the program reads at run time.
- `COPY config ./config`: Copies a data folder the program reads at run time.
- `COPY tests/fixtures ./tests/fixtures`: Copies a data folder the program reads at run time.

```dockerfile
RUN useradd --system --uid 10001 --home-dir /app app && mkdir -p /app/reports && chown app /app/reports
USER app
```

- `RUN useradd --system --uid 10001 --home-dir /app app && mkdir -p /app/reports && chown ...`: Creates a system user with a fixed id 10001 and home `/app`, creates the folders that must be writable and gives them to that user. `chown` changes the owner of files.
- `USER app`: From here on, and when the container runs, processes run as the unprivileged user `app`, not as root. If the program were hijacked, it could do less damage.

```dockerfile
HEALTHCHECK --interval=60s --timeout=20s --retries=3 CMD ["cost-router", "health"]
CMD ["cost-router", "health"]
```

- `HEALTHCHECK --interval=60s --timeout=20s --retries=3 CMD ["cost-router", "health"]`: A command Docker runs at intervals inside the container; exit status 0 means healthy, 1 unhealthy. `--interval` how often, `--timeout` how long to wait, `--retries` how many failures before "unhealthy".
- `CMD ["cost-router", "health"]`: The default command when the container starts. The square-bracket form is the "exec form": no shell in between, so signals such as SIGTERM reach the program directly.

### `.dockerignore`

`.dockerignore`

```text
.git
.venv
__pycache__
.pytest_cache
.mypy_cache
.ruff_cache
.env
logs
```

- `.git`: Keeps the repository history out of the build context, so it is never sent to Docker or copied into an image.
- `.venv`: Keeps the virtual environment out of the build context, so it is never sent to Docker or copied into an image.
- `__pycache__`: Keeps bytecode folders out of the build context, so it is never sent to Docker or copied into an image.
- `.pytest_cache`: Keeps pytest cache out of the build context, so it is never sent to Docker or copied into an image.
- `.mypy_cache`: Keeps mypy cache out of the build context, so it is never sent to Docker or copied into an image.
- `.ruff_cache`: Keeps ruff cache out of the build context, so it is never sent to Docker or copied into an image.
- `.env`: Keeps local settings (may hold keys) out of the build context, so it is never sent to Docker or copied into an image.
- `logs`: Keeps log files out of the build context, so it is never sent to Docker or copied into an image.

### The Makefile target

`Makefile`

```make
docker-build: ## build the container image
	docker build -t ai-cost-aware-router:dev .

clean: down
```

Builds the image(s) and gives each a name and tag (`name:tag`). `-f` names the Dockerfile and the final `.` is the build context.

## Try it yourself

Docker must be running. These commands are the ones the repository's checks used; the expected output is from the last time they ran.

1. `docker --version` prints the client version.
2. `make docker-build` builds the image; the last line reads `naming to docker.io/library/<name>:dev` (or similar).
3. `docker run --rm <image> id -u` prints `10001`: the program does not run as root.
4. `docker image ls | head` lists images with their size.
5. `docker inspect --format '{{.State.Health.Status}}' <container>` prints `healthy` for a running container once its health command succeeded.

The exact `docker run` commands for this repository are in its README and in the comment at the top of the Dockerfile.

## Mistakes people make

- **`COPY . .` before installing libraries**: every code change invalidates the slow install layer.
- **Running as root** in the container.
- **Secrets in the image.** Anything copied in (even deleted later) stays in a layer. `.dockerignore` keeps `.env` and `.git` out.
- **Large build context** because `.dockerignore` is missing.
- **Unpinned base image** (`python:latest`): a rebuild can silently change Python.

## Check yourself

1. **What is the difference between an image and a container?**  
   An image is the packaged files; a container is a running process started from an image.
2. **Why copy the lock file before the source?**  
   So Docker's layer cache reuses the library install when only code changed.
3. **What does `USER app` achieve?**  
   The program runs without root rights.
4. **What is a multi-stage build good for?**  
   Compiling in one stage and shipping only the result in a small final image.
5. **What does `.dockerignore` do?**  
   Keeps listed files out of the build context.

## Further reading

Docker documentation: https://docs.docker.com/ (Dockerfile reference: https://docs.docker.com/reference/dockerfile/ , multi-stage builds, build cache). Base images are pinned in the Dockerfile `FROM` lines.
