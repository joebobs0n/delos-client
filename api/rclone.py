from fastapi import APIRouter, Request, HTTPException
from .response import PostResponse, GetResponse, HttpCodes as codes


router = APIRouter()

@router.post("/add", response_model=PostResponse, status_code=201)
def add(request: Request, remote_name: str, mount_path: str, automount: bool = False) -> dict:
    try:
        request.app.state.rcm.add(remote_name=remote_name, mount_path=mount_path)
        if automount:
            retval = mount(request=request, remote_name=remote_name)
            retval["action"] = "add"
            return retval
        else:
            return {"action": "add", "message": f"Remote [ {remote_name} ] added"}
    except KeyError as e:
        raise HTTPException(status_code=codes.CONFLICT, detail=str(e))

@router.post("/mount", response_model=PostResponse, status_code=200)
def mount(request: Request, remote_name: str) -> dict:
    try:
        request.app.state.rcm[remote_name].mount()
        return {"action": "mount", "message": f"Drive [ {remote_name} ] mounted"}
    except KeyError as e:
        raise HTTPException(status_code=codes.NOT_FOUND, detail=str(e))

@router.post("/unmount", response_model=PostResponse, status_code=200)
def unmount(request: Request, remote_name: str) -> dict:
    try:
        request.app.state.rcm[remote_name].unmount()
        return {"action": "unmount", "message": f"Drive [ {remote_name} ] unmounted"}
    except KeyError as e:
        raise HTTPException(status_code=codes.NOT_FOUND, detail=str(e))

@router.post("/remove", response_model=PostResponse, status_code=201)
def remove(request: Request, remote_name: str) -> dict:
    try:
        request.app.state.rcm.remove(remote_name=remote_name)
        return {"action": "remove", "message": f"Drive [ {remote_name} ] removed"}
    except KeyError as e:
        raise HTTPException(status_code=codes.NOT_FOUND, detail=str(e))

@router.get("/status", response_model=GetResponse, status_code=200)
def list_drives(request: Request) -> dict:
    drives = request.app.state.rcm.status
    return {"action": "status", "instances": drives}
