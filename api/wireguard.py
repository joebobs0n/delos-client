from fastapi import APIRouter, Request


router = APIRouter()

@router.post("/add")
def add(request: Request, config: str, autostart: bool = False) -> dict:
    if request.app.state.wgm.add(config=config):
        if autostart:
            retval = start(request=request, config=config)
            retval["action"] = "add"
            return retval
        else:
            return {"action": "add", "success": True, "message": f"VPN [ {config} ] added."}
    return {"action": "add", "success": False, "message": f"Failed to add VPN [ {config} ]"}

@router.post("/start")
def start(request: Request, config: str) -> dict:
    if request.app.state.wgm.start(config=config):
        return {"action": "start", "success": True, "message": f"VPN [ {config} ] started."}
    return {"action": "start", "success": False, "message": f"Failed to start VPN [ {config} ]"}

@router.post("/stop")
def stop(request: Request, config: str) -> dict:
    if request.app.state.wgm.stop(config=config):
        return {"action": "stop", "success": True, "message": f"VPN [ {config} ] stopped."}
    return {"action": "stop", "success": False, "message": f"Failed to stop VPN [ {config} ]"}

@router.post("/remove")
def remove(request: Request, config: str) -> dict:
    if request.app.state.wgm.remove(config=config):
        return {"action": "remove", "success": True, "message": f"VPN [ {config} ] removed."}
    return {"action": "remove", "success": False, "message": f"Failed to remove VPN [ {config} ]"}

@router.get("/status")
def status(request: Request) -> dict:
    status = request.app.state.wgm.status
    return {"action": "status", "status": status}
