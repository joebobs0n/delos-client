from platform import system

class OsCmds:
    @classmethod
    def _return_cmd(cls, cmd: str | None) -> str:
        if cmd is not None:
            return cmd
        raise NotImplementedError(f"Command not supported on {system()}")


class WireGuard(OsCmds):
    @classmethod
    def start(cls, config: str) -> str:
            return super()._return_cmd({
            "Linux": f"sudo wg-quick up {config}",
            "Darwin": f"sudo wg-quick up {config}",
            "Windows": f"wg-quick up {config}",
        }.get(system(), None))

    @classmethod
    def stop(cls, config: str) -> str:
        return super()._return_cmd({
            "Linux": f"sudo wg-quick down {config}",
            "Darwin": f"sudo wg-quick down {config}",
            "Windows": f"wg-quick down {config}",
        }.get(system(), None))

    @classmethod
    def status(cls, config: str) -> str:
        return super()._return_cmd({
            "Linux": f"sudo wg show {config}",
            "Darwin": f"sudo wg show {config}",
            "Windows": f"wg show {config}",
        }.get(system(), None))


class Rclone(OsCmds):
    @classmethod
    def mount(cls, name: str, path: str) -> str:
        return super()._return_cmd(
            f"rclone mount {name} {path} --vfs-cache-mode writes"
        )

    @classmethod
    def unmount(cls, path: str) -> str:
        return super()._return_cmd({
            "Linux": f"fusermount -u {path}",
            "Darwin": f"umount {path}",
        }.get(system(), None))
