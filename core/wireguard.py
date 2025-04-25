import subprocess as sp
from utils import (
    Format,
    LogParent as log
)
from platform import system as platform_os
from core import WireGuardCmds

class WireGuardManager:
    class _WireGuardInstance:
        def __init__(self, config: str) -> None:
            self.config_name = config

        def start(self) -> sp.CompletedProcess | None:
            log.info(
                "{}Starting{} WireGuard with config: {}{}{}".format(
                    Format.DARK_GREEN, Format.END,
                    Format.DARK_CYAN, self.config_name, Format.END
                ), called_name="wireguard")

            try:
                start_process = sp.run(
                    WireGuardCmds.start(self.config_name),
                    shell=True, stdout=sp.PIPE, stderr=sp.STDOUT, check=True,
                )
            except sp.CalledProcessError as e:
                log.warning(
                    "Error starting WireGuard: {}{}{}".format(
                        Format.RED, e, Format.END
                    ), called_name="wireguard")
                return None

            log.info(
                "WireGuard started {}successfully{}.".format(
                    Format.GREEN, Format.END
                ), called_name="wireguard")
            return start_process

        def stop(self) -> sp.CompletedProcess | None:
            log.info(
                "{}Stopping{} WireGuard with config: {}{}{}".format(
                    Format.DARK_GREEN, Format.END,
                    Format.DARK_CYAN, self.config_name, Format.END
                ), called_name="wireguard")

            try:
                stop_process = sp.run(
                    WireGuardCmds.stop(self.config_name),
                    shell=True, stdout=sp.PIPE, stderr=sp.STDOUT, check=True,
                )
            except sp.CalledProcessError as e:
                log.warning(
                    "Error stopping WireGuard: {}{}{}".format(
                        Format.RED, e, Format.END
                    ), called_name="wireguard")
                return None

            log.info(
                "WireGuard stopped {}successfully{}.".format(
                    Format.GREEN, Format.END
                ), called_name="wireguard")
            return stop_process


    def __init__(self) -> None:
        log.info(
            "{}Starting WireGuard Manager{}".format(
                Format.PURPLE, Format.END
            ), called_name="wireguard")
        self.__instances = {}

    def __enter__(self) -> None:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._stop_all()

    def __getitem__(self, config: str) -> _WireGuardInstance:
        return self.__instances.get(config, None)

    def __delitem__(self, config: str) -> None:
        if config in self.__instances.keys():
            self.__instances[config].stop()
            del self.__instances[config]
        else:
            log.warning(
                "WireGuard instance for {}{}{} not found.".format(
                    Format.YELLOW, config, Format.END
                ), called_name="wireguard")

    def add(self, config: str, start: bool = False) -> _WireGuardInstance:
        if config not in self.__instances.keys():
            self.__instances[config] = self._WireGuardInstance(config)
            if start:
                self.__instances[config].start()
            return self.__instances[config]
        else:
            log.warning(
                "WireGuard instance for {}{}{} already exists.".format(
                    Format.YELLOW, config, Format.END
                ), called_name="wireguard")
        return None

    def stop(self, config: str) -> None:
        if config in self.__instances.keys():
            self.__instances[config].stop()
            del self.__instances[config]
        else:
            log.warning(
                "WireGuard instance for {}{}{} not found.".format(
                    Format.YELLOW, config, Format.END
                ), called_name="wireguard")

    def _stop_all(self) -> None:
        for config in list(self.__instances.keys()):
            self.stop(config)

    @property
    def configs(self) -> list[str]:
        return list(self.__instances.keys())
