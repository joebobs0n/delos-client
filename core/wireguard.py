import subprocess as sp
from utils import (
    Format,
    LogParent as log
)
from core import WireGuardCmds

class WireGuardManager:
    class _WireGuardInstance:
        def __init__(self, config: str) -> None:
            self.config_name = config

        def start(self) -> sp.CompletedProcess | None:
            log.info("\n{}Starting{} WireGuard with config: {}{}{}".format(
                Format.DARK_GREEN, Format.END,
                Format.DARK_CYAN, self.config_name, Format.END
            ), called_name="wireguard", timestamp=True)

            try:
                start_process = sp.run(
                    WireGuardCmds.start(self.config_name),
                    shell=True, stdout=sp.PIPE, stderr=sp.STDOUT, check=True,
                )
            except sp.CalledProcessError as e:
                log.warning("Error starting WireGuard: {}{}{}".format(
                    Format.RED, e, Format.END
                ), called_name="wireguard")
                return None

            log.info("WireGuard started {}successfully{}.".format(
                Format.GREEN, Format.END
            ), called_name="wireguard")
            return start_process

        def stop(self) -> sp.CompletedProcess | None:
            log.info("\n{}Stopping{} WireGuard with config: {}{}{}".format(
                Format.DARK_GREEN, Format.END,
                Format.DARK_CYAN, self.config_name, Format.END
            ), called_name="wireguard", timestamp=True)

            try:
                stop_process = sp.run(
                    WireGuardCmds.stop(self.config_name),
                    shell=True, stdout=sp.PIPE, stderr=sp.STDOUT, check=True,
                )
            except sp.CalledProcessError as e:
                log.warning("Error stopping WireGuard: {}{}{}".format(
                    Format.RED, e, Format.END
                ), called_name="wireguard")
                return None

            log.info("WireGuard stopped {}successfully{}.".format(
                Format.GREEN, Format.END
            ), called_name="wireguard")
            return stop_process

        @property
        def status(self) -> str:
            status_process = sp.run(
                WireGuardCmds.status(self.config_name),
                shell=True, stdout=sp.PIPE, stderr=sp.STDOUT
            )
            retval = status_process.stdout.decode().strip()
            if self.config_name not in retval:
                retval = ""
            return retval


    def __init__(self) -> None:
        log.info("{}Starting WireGuard Manager{}".format(
            Format.PURPLE, Format.END
        ), called_name="wireguard", timestamp=True)
        self.__instances = {}

    def __enter__(self) -> None:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        for config in list(self.__instances.keys()):
            self.remove(config)

    def __getitem__(self, config: str) -> _WireGuardInstance:
        return self.__instances.get(config, None)

    def __delitem__(self, config: str) -> None:
        if config in self.__instances.keys():
            self.__instances[config].stop()
            del self.__instances[config]
        else:
            log.warning("WireGuard instance for {}{}{} not found.".format(
                Format.YELLOW, config, Format.END
            ), called_name="wireguard")

    def add(self, config: str) -> _WireGuardInstance:
        if config not in self.__instances.keys():
            self.__instances[config] = self._WireGuardInstance(config)
            return self.__instances[config]
        else:
            log.warning("WireGuard instance for {}{}{} already exists.".format(
                Format.YELLOW, config, Format.END
            ), called_name="wireguard")
        return None

    def start(self, config: str) -> sp.CompletedProcess | None:
        if config in self.__instances.keys():
            return self.__instances[config].start()
        else:
            log.warning("WireGuard instance for {}{}{} not found.".format(
                Format.YELLOW, config, Format.END
            ), called_name="wireguard")

    def stop(self, config: str) -> bool:
        if config in self.__instances.keys():
            return (self.__instances[config].stop().returncode == 0)
        else:
            log.warning("WireGuard instance for {}{}{} not found.".format(
                Format.YELLOW, config, Format.END
            ), called_name="wireguard")
        return False

    def remove(self, config: str) -> bool:
        if config in self.__instances.keys():
            retval = True
            if self.__instances[config].status != "":
                if (stop_proc := self.__instances[config].stop()) is not None:
                    retval &= bool(stop_proc.returncode == 0)
            del self.__instances[config]
            return retval
        else:
            log.warning("WireGuard instance for {}{}{} not found.".format(
                Format.YELLOW, config, Format.END
            ), called_name="wireguard")
        return False

    @property
    def status(self) -> list[str]:
        return {
            config: {"started": bool(instance.status != "")}
            for config, instance in self.__instances.items()
        }
