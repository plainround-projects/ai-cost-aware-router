# Concurrency: threads, locks and processes

## What it is

**Concurrency** means more than one thing in progress at the same time. A **process** is a running program with its own memory. A **thread** is a line of execution inside a process; threads of one process share memory. A **lock** is a token that only one thread can hold at a time. A computer with several cores can run several threads truly in parallel; with one core, the operating system switches quickly between them.

## Why this repository uses it

A model call mostly waits for the network or the GPU. While one thread waits, another can send its request, so a list of 200 prompts finishes much sooner. A load test must create many simultaneous clients on purpose. Both need threads, and anything shared between threads needs a lock.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `src/cost_router/infrastructure/parallel.py` | `thread_mapper`: run a function over items on a pool of threads. |
| `src/cost_router/infrastructure/llm/recorded.py` | A lock around appending recorded answers. |
| `src/cost_router/application/experiments.py` | Timed requests and the outage thread. |
| `java/src/main/**/*.java (16 files)` | Java concurrency: synchronized, atomic counters, concurrent maps. |


## How it works underneath

**Python threads and the GIL.** In the standard CPython interpreter only one thread runs Python bytecode at a time, because of the *global interpreter lock* (GIL). Threads still help when the work is waiting: a thread blocked on the network or on `time.sleep` releases the GIL. They do not speed up pure calculation.

**Race conditions.** `counter += 1` is really three steps (read, add, write). Two threads can both read 5 and both write 6; one increment is lost. Wrapping the steps in `with lock:` makes them one unit. The lock is released automatically when the `with` block ends, even after an error.

**Thread pools.** Creating a thread costs time and memory, so a `ThreadPoolExecutor` keeps `max_workers` threads and hands them tasks. `pool.map(f, items)` returns results in input order.

**Events.** `threading.Event` is a flag: `set()` raises it, `is_set()` reads it and `wait(timeout)` sleeps until it is raised or the time is up. It is the clean way to tell a thread to stop.

**Processes.** `subprocess.Popen` starts another program. Processes do not share memory; they talk through files, pipes or the network (this repository uses HTTP). A process can run on another core without any GIL.

**Closed vs open loop.** The load generator is a *closed loop*: each worker sends a request, waits for its end, and sends the next, so the number of requests in flight equals the number of workers.

## Walkthrough of this repository's use

### Mapping over items

The helper `thread_mapper` is quoted and explained in `python.md`. It is the one place that creates a thread pool for the experiments' model calls, so the number of threads is a setting (`WORKERS`, see `dotenv.md`).

### A lock around a file append

`src/cost_router/infrastructure/llm/recorded.py`

<!-- fmt: off -->
```python
    def __init__(self, inner: ChatModel, path: Path) -> None:
        self._inner = inner
        self._path = path
        self._lock = threading.Lock()
        path.parent.mkdir(parents=True, exist_ok=True)
        self._seen = load_fixtures(path) if path.exists() else {}

    def complete(self, request: ChatRequest, timeout_s: float = 60.0) -> ChatResponse:
        """Answer from the file when the request is known, else call the inner model and store the exchange."""
        key = request.fixture_key()
        with self._lock:
            known = self._seen.get(key)
        if known is not None:
            return known
        response = self._inner.complete(request, timeout_s)
        with self._lock:
            if key not in self._seen:
                row = {"key": key, "request": summarize_request(request), "response": response_to_json(response)}
                with self._path.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
                self._seen[key] = response
        return response
```
<!-- fmt: on -->

`threading.Lock()` makes a **lock**: only one thread at a time can be inside a `with self._lock:` block. Without it, two threads could both find a request unknown, both call the model and both append a line, or interleave the bytes of two lines. The pattern used in `complete`: take the lock briefly to look up, release it for the slow model call, take it again to write, and check once more that no other thread wrote the same key meanwhile.

## Try it yourself

1. `.venv/bin/python -c "import os; print(os.cpu_count())"` prints the number of cores.
2. `.venv/bin/python -c "import threading; print(threading.active_count())"` prints `1`: the main thread.
3. Run this to see a lost update (it may print less than 400000 on some Python versions, and exactly 400000 on others; the point is that nothing guarantees it):
   `.venv/bin/python -c "import threading; n=0
def f():
    global n
    for _ in range(100000): n+=1
ts=[threading.Thread(target=f) for _ in range(4)]
[t.start() for t in ts]; [t.join() for t in ts]; print(n)"`
4. `grep -rn "threading.Lock" src | head` lists every lock in the Python source.

## Mistakes people make

- **Sharing a list or dictionary between threads without a lock.**
- **Holding a lock during a slow call** (the recording model releases it while the model answers).
- **Deadlock:** thread A holds lock 1 and waits for lock 2, thread B the reverse. Keep one lock per structure and avoid nested locks.
- **Using threads to speed up calculation** in CPython; use processes.
- **Forgetting to join threads**, so results are read before the work is done.

## Check yourself

1. **What is the difference between a process and a thread?**  
   A process has its own memory; threads of a process share it.
2. **Why do threads still speed up model calls in Python?**  
   Waiting for the network releases the global interpreter lock, so other threads can run.
3. **What does `with lock:` guarantee?**  
   Only one thread executes the block at a time, and the lock is released afterwards even on an error.
4. **What does `pool.map` return, and in which order?**  
   The results of the function, in the order of the input items.
5. **What is a closed-loop load generator?**  
   Each worker sends the next request only after the previous one finished, so concurrency equals the number of workers.

## Further reading

Python `threading`: https://docs.python.org/3/library/threading.html . `concurrent.futures`: https://docs.python.org/3/library/concurrent.futures.html . `subprocess`: https://docs.python.org/3/library/subprocess.html
