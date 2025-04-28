import subprocess as sp
from pathlib import Path
from utils import Format, LogParent as log
from core import RcloneCmds
import time

class RcloneManager:
    class _RcloneInstance:
        def __init__(self, remote_name: str, mount_path: Path) -> None:
            self.__remote_name = remote_name
            self.__mount_path = mount_path
            self.__mount_proc = None

        def mount(self) -> None:
            try:
                self.__mount_proc = sp.Popen(
                    RcloneCmds.mount(self.__remote_name, str(self.__mount_path)).split(),
                    stdout=sp.PIPE, stderr=sp.STDOUT
                )
                time.sleep(1)  # Give the proc time to start/settle
            except sp.CalledProcessError as e:
                e.add_note(f"Error mounting [ {self.__remote_name} ]: {e.stdout.decode().strip()}")
                raise e

        def __force_kill(self) -> None:
            self.__mount_proc.kill()
            if self.__mount_proc.poll() is None:
                raise TimeoutError(f"Process {self.__mount_proc.pid} failed to kill. Please kill it manually.")

        def __try_terminate(self) -> None:
            self.__mount_proc.terminate()
            try:
                self.__mount_proc.wait(timeout=5)
            except sp.TimeoutExpired:
                self.__force_kill()

        def __ensure_stopped(self) -> None:
            if self.__mount_proc is not None:
                if self.__mount_proc.poll() is None:
                    self.__try_terminate()

        def unmount(self) -> None:
            try:
                if self.mounted:
                    sp.run(
                        RcloneCmds.unmount(self.__mount_path),
                        shell=True, stdout=sp.PIPE, stderr=sp.STDOUT, check=True
                    )
                    self.__ensure_stopped()
                    self.__mount_proc = None
            except sp.CalledProcessError as e:
                print()
                e.add_note(f"Error unmounting [ {self.__remote_name} ]: {e.stdout.decode().strip()}")
                raise e
            except TimeoutError as e:
                e.add_note(f"Unable to kill process [ {self.__mount_proc.pid} ]: {e.stdout.decode().strip()}")
                raise e

        @property
        def remote_name(self) -> str:
            return self.__remote_name

        @property
        def mount_path(self) -> Path:
            return self.__mount_path

        @property
        def mounted(self) -> bool:
            if self.__mount_proc is None or self.__mount_proc.poll() is not None:
                return False
            return True


    def __init__(self) -> None:
        log.info("{}Starting Rclone Manager{}".format(
            Format.PURPLE, Format.END
        ), called_name="rclone", timestamp=True)

        self.__instances = {}

    def __enter__(self) -> None:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        for instance in list(self.__instances.keys()):
            self.remove(instance)

    def __getitem__(self, remote_name: str) -> _RcloneInstance:
        return self.__instances.get(remote_name, None)

    def __delitem__(self, remote_name: str) -> None:
        self.remove(remote_name)

    def add(self, remote_name: str, mount_path: Path = None) -> None:
        if remote_name in self.__instances.keys():
            raise KeyError(f"Rclone instance for {remote_name} already exists")
        self.__instances[remote_name] = self._RcloneInstance(remote_name, mount_path)

    def mount(self, remote_name: str) -> Path | None:
        try:
            self.__instances[remote_name].mount()
        except KeyError as e:
            e.add_note(f"Rclone instance for {remote_name} not found")
            raise e

    def unmount(self, remote_name: str) -> bool:
        try:
            self.__instances[remote_name].unmount()
        except KeyError as e:
            e.add_note(f"Rclone instance for {remote_name} not found")
            raise e

    def remove(self, remote_name: str) -> bool:
        try:
            self.__instances[remote_name].unmount()
            del self.__instances[remote_name]
        except KeyError as e:
            e.add_note(f"Rclone instance for {remote_name} not found")
            raise e

    @property
    def remotes(self) -> list[str]:
        return list(self.__instances.keys())

    @property
    def status(self) -> dict:
        return {
            remote_name: {"mounted": instance.mounted, "mount_path": instance.mount_path}
            for remote_name, instance in self.__instances.items()
        }
