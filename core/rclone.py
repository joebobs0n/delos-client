import subprocess as sp
from pathlib import Path
from utils import Format, LogParent as log
from core import RcloneCmds

class RcloneManager:
    class _RcloneInstance:
        def __init__(self, remote_name: str, mount_path: Path) -> None:
            self.__remote_name = remote_name
            self.__mount_path = mount_path
            self.__mount_proc = None

        def mount(self) -> Path | None:
            log.info("\n{}{}Mounting{} {}{}{} to {}{}{}".format(
                Format.BOLD, Format.DARK_GREEN, Format.END,
                Format.PURPLE, self.__remote_name, Format.END,
                Format.DARK_CYAN, self.__mount_path, Format.END
            ), called_name="rclone", timestamp=True)

            try:
                self.__mount_proc = sp.Popen(
                    RcloneCmds.mount(self.__remote_name, str(self.__mount_path)).split(),
                    stdout=sp.PIPE, stderr=sp.STDOUT
                )
            except sp.CalledProcessError as e:
                log.warning("Error mounting {}{}{}: {}{}{}".format(
                    Format.PURPLE, self.__remote_name, Format.END,
                    Format.RED, e, Format.END
                ), called_name="rclone")
                return None

            log.info("Mounted {}{}{} to {}{}{} successfully.".format(
                Format.PURPLE, self.__remote_name, Format.END,
                Format.DARK_CYAN, self.__mount_path, Format.END
            ), called_name="rclone")
            return self.__mount_path

        def __force_kill(self) -> None:
            log.info("Process {}{}{} running. Attempting to kill.".format(
                Format.UNDERLINE, self.__mount_proc.pid, Format.END
            ), called_name="rclone")

            self.__mount_proc.kill()
            if self.__mount_proc.poll() is None:
                raise TimeoutError(f"Process {self.__mount_proc.pid} failed to kill. Please kill it manually.")

        def __try_terminate(self) -> None:
            log.info("Process {}{}{} running. Attempting to terminate.".format(
                Format.UNDERLINE, self.__mount_proc.pid, Format.END
            ), called_name="rclone")

            self.__mount_proc.terminate()
            try:
                self.__mount_proc.wait(timeout=5)
            except sp.TimeoutExpired:
                self.__force_kill()

        def __ensure_stopped(self) -> None:
            if self.__mount_proc is not None:
                if self.__mount_proc.poll() is None:
                    self.__try_terminate()
                else:
                    log.info("Process {}{}{} is dead.".format(
                        Format.UNDERLINE, self.__mount_proc.pid, Format.END
                    ), called_name="rclone")

        def unmount(self) -> bool:
            log.info("\n{}{}Unmounting{} {}{}{} from {}{}{}".format(
                Format.BOLD, Format.DARK_GREEN, Format.END,
                Format.PURPLE, self.__remote_name, Format.END,
                Format.DARK_CYAN, self.__mount_path, Format.END
            ), called_name="rclone", timestamp=True)

            unmount_proc = sp.run(
                RcloneCmds.unmount(self.__mount_path),
                shell=True, stdout=sp.PIPE, stderr=sp.STDOUT
            )
            self.__ensure_stopped()
            self.__mount_proc = None

            if unmount_proc.returncode == 0:
                log.info("Unmounted {}{}{} from {}{}{} successfully.".format(
                    Format.PURPLE, self.__remote_name, Format.END,
                    Format.DARK_CYAN, self.__mount_path, Format.END
                ), called_name="rclone")
                return True
            else:
                log.warning("Error unmounting {}{}{}: {}{}{}".format(
                    Format.PURPLE, self.__remote_name, Format.END,
                    Format.RED, unmount_proc.stdout.decode().strip(), Format.END
                ), called_name="rclone")
            return False

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

    #! --------------------------------------------------------------------------------------------

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

    def add(self, remote_name: str, mount_path: Path = None) -> _RcloneInstance | None:
        if remote_name not in self.__instances.keys():
            self.__instances[remote_name] = self._RcloneInstance(remote_name, mount_path)
            return self.__instances[remote_name]
        else:
            log.warning("Rclone instance for {}{}{} already exists.".format(
                Format.YELLOW, remote_name, Format.END
            ), called_name="rclone")
        return None

    def mount(self, remote_name: str) -> Path | None:
        if remote_name in self.__instances.keys():
            return self.__instances[remote_name].mount()
        else:
            log.warning("Rclone instance for {}{}{} not found.".format(
                Format.YELLOW, remote_name, Format.END
            ), called_name="rclone")

    def unmount(self, remote_name: str) -> bool:
        if remote_name in self.__instances.keys():
            return self.__instances[remote_name].unmount()
        else:
            log.warning("Rclone instance for {}{}{} not found.".format(
                Format.YELLOW, remote_name, Format.END
            ), called_name="rclone")
        return False

    def remove(self, remote_name: str) -> bool:
        if remote_name in self.__instances.keys():
            retval = True
            if self.__instances[remote_name].mounted:
                retval &= self.__instances[remote_name].unmount()
            del self.__instances[remote_name]
            return retval
        else:
            log.warning("Rclone instance for {}{}{} not found.".format(
                Format.YELLOW, remote_name, Format.END
            ), called_name="rclone")
        return False

    @property
    def remotes(self) -> list[str]:
        return list(self.__instances.keys())

    @property
    def status(self) -> list[tuple[str, Path]]:
        return {
            remote_name: {"mount_path": instance.mount_path, "mounted": instance.mounted}
            for remote_name, instance in self.__instances.items()
        }
