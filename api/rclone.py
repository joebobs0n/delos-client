from fastapi import APIRouter, Request


router = APIRouter()

@router.post("/add")
def add(request: Request, remote_name: str, mount_path: str, automount: bool = False) -> dict:
    if request.app.state.rcm.add(remote_name=remote_name, mount_path=mount_path):
        if automount:
            retval = mount(request=request, remote_name=remote_name)
            retval["action"] = "add"
            return retval
        else:
            return {"action": "add", "success": True, "message": f"Drive [ {remote_name} ] added"}
    return {"action": "add", "success": False, "message": f"Failed to mount [ {remote_name} ]"}

@router.post("/mount")
def mount(request: Request, remote_name: str) -> dict:
    if request.app.state.rcm[remote_name].mount():
        return {"action": "mount", "success": True, "message": f"Drive [ {remote_name} ] mounted"}
    return {"action": "mount", "success": False, "message": f"Failed to mount [ {remote_name} ]"}

@router.post("/unmount")
def unmount(request: Request, remote_name: str) -> dict:
    if request.app.state.rcm[remote_name].unmount():
        return {"action": "unmount", "success": True, "message": f"Drive [ {remote_name} ] unmounted"}
    return {"action": "unmount", "success": False, "message": f"Failed to unmount [ {remote_name} ]"}

@router.post("/remove")
def remove(request: Request, remote_name: str) -> dict:
    if request.app.state.rcm.remove(remote_name=remote_name):
        return {"action": "remove", "success": True, "message": f"Drive [ {remote_name} ] removed"}
    return {"action": "remove", "success": False, "message": f"Failed to remove [ {remote_name} ]"}

@router.get("/status")
def list_drives(request: Request) -> dict:
    drives = request.app.state.rcm.status
    return {"action": "status", "remotes": drives}
