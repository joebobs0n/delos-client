import sys, os, signal, _io
import time, datetime
from pathlib import Path
from .logging import LogParent, Format


class Timer:
    def __init__(self, name: str = None, plain: bool = False, color: str = Format.BOLD) -> None:
        self.name, self.color, self.plain = name, color, plain

    def __enter__(self) -> None:
        self.tic = time.perf_counter()

    def __exit__(self, type, value, traceback) -> None:
        pre = "" if not self.name else f"{self.name}: "
        self.toc = time.perf_counter()
        time_diff = datetime.timedelta(seconds=(self.toc - self.tic))
        time_formatted = f"{self.color}{time_diff}{Format.END}"
        print(time_formatted, flush=True) if self.plain else LogParent.info(f"\n{pre}{time_formatted}", flush=True, scriptname="Timer")


class DoNotInterrupt:
    def __init__(self, enable: bool = True, message: str = "", overwrite: bool = True) -> None:
        self.prev = signal.getsignal(signal.SIGINT)
        self.enabled = enable
        self.triggered = False
        self.msg = "\r" + message + "\n" if not overwrite else "\r" + message
        self.pname = "DNI"

    def __enter__(self) -> None:
        if self.enabled:
            signal.signal(signal.SIGINT, self.handler)

    def __exit__(self, type, value, traceback) -> None:
        if self.triggered: LogParent._base("\r", stream=sys.stderr, flush=True, end="", plain=True, scriptname=self.pname)
        signal.signal(signal.SIGINT, self.prev)

    def handler(self, signum, frame) -> None:
        if self.msg:
            self.triggered = True
            LogParent.warning(self.msg, end="", flush=True, scriptname=self.pname)


class RedirectPrintouts:
    def __init__(
        self,
        stdout: str | Path | _io._TextIOBase = None,
        stderr: str | Path | _io._TextIOBase = "stdout"
    ) -> None:
        self.stdout_prev, self.stdout, self.close_stdout = sys.stdout, stdout, False
        self.stderr_prev, self.stderr, self.close_stderr = sys.stderr, stderr, False

        if isinstance(stdout, Path): stdout=str(stdout)
        if isinstance(stderr, Path): stderr=str(stderr)

        if isinstance(stdout, str):
            self.stdout = open(stdout, "w+")
            self.close_stdout = True
        if isinstance(stderr, str):
            if stderr.lower() == "stdout":
                self.stderr = self.stdout
            else:
                self.stderr = open(stderr, "w+")
                self.close_stderr = True

    def __enter__(self) -> None:
        if self.stdout is not None: sys.stdout = self.stdout
        if self.stderr is not None: sys.stderr = self.stderr

    def __exit__(self, type, value, traceback) -> None:
        sys.stdout = self.stdout_prev
        sys.stderr = self.stderr_prev

        if self.close_stdout: self.stdout.close()
        if self.close_stderr: self.stderr.close()


class SuppressPrintouts(RedirectPrintouts):
    def __init__(self, stdout: bool = True, stderr: bool = True) -> None:
        self.stdout = str(os.devnull) if stdout else None
        self.stderr = str(os.devnull) if stderr else None
        super().__init__(stdout=self.stdout, stderr=self.stderr)

    def __enter__(self) -> None:
        super().__enter__()

    def __exit__(self, type, value, traceback) -> None:
        super().__exit__(type=type, value=value, traceback=traceback)
