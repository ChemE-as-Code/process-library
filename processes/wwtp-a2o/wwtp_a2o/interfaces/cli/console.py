"""Console logging and progress belong to the interface, not the calculation."""

import sys
import threading
import time
from contextlib import contextmanager


class Tee:
    def __init__(self, terminal, log):
        self.terminal, self.log = terminal, log

    def write(self, text):
        self.terminal.write(text)
        self.log.write(text)
        self.flush()
        return len(text)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def __getattr__(self, key):
        return getattr(self.terminal, key)


@contextmanager
def recorded_console(run):
    original_output = (sys.stdout, sys.stderr)
    stop = threading.Event()
    started = time.perf_counter()

    def heartbeat():
        while not stop.wait(20):
            print(
                f"  Still running ({time.perf_counter() - started:.0f} seconds elapsed)...",
                flush=True,
            )

    with (run / "run.log").open("w", encoding="utf-8", buffering=1) as log:
        sys.stdout, sys.stderr = (Tee(output, log) for output in original_output)
        thread = threading.Thread(target=heartbeat, daemon=True)
        thread.start()
        try:
            yield
        finally:
            stop.set()
            thread.join(timeout=1)
            sys.stdout, sys.stderr = original_output
