from fastapi import APIRouter
from core import WireGuardManager


router = APIRouter()
with WireGuardManager() as wgm:
    @router.post("/wireguard/start")
    def start_wireguard(config: str, start: bool = True) -> dict:
        if (instance := wgm.add(config=config, start=start)):
            return {"success": True, "message": f"WireGuard instance {config} {'started' if start else 'added'}."}
        return {"success": False, "message": f"Failed to start WireGuard instance {config}."}

    @router.post("/wireguard/stop")
    def stop_wireguard(config: str) -> dict:
        if (success := wgm.stop(config=config)):
            return {"success": True, "message": f"WireGuard instance {config} stopped."}
        return {"success": False, "message": f"Failed to stop WireGuard instance {config}."}

    @router.post("/wireguard/stop_all")
    def stop_all_wireguard() -> dict:
        if (success := wgm.stop_all()):
            return {"success": True, "message": "All WireGuard instances stopped."}
        return {"success": False, "message": "Failed to stop all WireGuard instances."}

    # @router.get("/wireguard/status")
    # def
