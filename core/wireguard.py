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

        def start(self) -> None:
            try:
                sp.run(
                    WireGuardCmds.start(self.config_name),
                    shell=True, stdout=sp.PIPE, stderr=sp.STDOUT, check=True,
                )
            except sp.CalledProcessError as e:
                e.add_note(f"Error starting WireGuard [ {self.config_name} ]: {e.stdout.decode().strip()}")
                raise e

        def stop(self) -> None:
            try:
                sp.run(
                    WireGuardCmds.stop(self.config_name),
                    shell=True, stdout=sp.PIPE, stderr=sp.STDOUT, check=True,
                )
            except sp.CalledProcessError as e:
                e.add_note(f"Error stopping WireGuard [ {self.config_name} ]: {e.stdout.decode().strip()}")
                raise e

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
        self.remove(config)

    def add(self, config: str) -> None:
        if config in self.__instances.keys():
            raise KeyError(f"WireGuard instance for {config} already exists")
        self.__instances[config] = self._WireGuardInstance(config)

    def start(self, config: str) -> None:
        try:
            self.__instances[config].start()
        except KeyError as e:
            e.add_note(f"WireGuard instance for {config} not found")
            raise e

    def stop(self, config: str) -> None:
        try:
            self.__instances[config].stop()
        except KeyError as e:
            e.add_note(f"WireGuard instance for {config} not found")
            raise e

    def remove(self, config: str) -> None:
        try:
            if self.__instances[config].status != "":
                self.__instances[config].stop()
            del self.__instances[config]
        except KeyError as e:
            e.add_note(f"WireGuard instance for {config} not found")
            raise e

    @property
    def status(self) -> dict:
        return {
            config: {"started": bool(instance.status != "")}
            for config, instance in self.__instances.items()
        }
