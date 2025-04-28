from fastapi import APIRouter, Request, HTTPException
from .response import PostResponse, GetResponse, HttpCodes as codes


router = APIRouter()

@router.post("/add", response_model=PostResponse, status_code=201)
def add(request: Request, config: str, autostart: bool = False) -> dict:
    try:
        request.app.state.wgm.add(config=config)
        if autostart:
            retval = start(request=request, config=config)
            retval["action"] = "add"
            return retval
        else:
            return {"action": "add", "message": f"VPN [ {config} ] added."}
    except KeyError as e:
        raise HTTPException(status_code=codes.CONFLICT, detail=str(e))

@router.post("/start", response_model=PostResponse, status_code=200)
def start(request: Request, config: str) -> dict:
    try:
        request.app.state.wgm.start(config=config)
        return {"action": "start", "message": f"VPN [ {config} ] started."}
    except KeyError as e:
        raise HTTPException(status_code=codes.NOT_FOUND, detail=str(e))

@router.post("/stop", response_model=PostResponse, status_code=200)
def stop(request: Request, config: str) -> dict:
    try:
        request.app.state.wgm.stop(config=config)
        return {"action": "stop", "message": f"VPN [ {config} ] stopped."}
    except KeyError as e:
        raise HTTPException(status_code=codes.NOT_FOUND, detail=str(e))

@router.post("/remove", response_model=PostResponse, status_code=201)
def remove(request: Request, config: str) -> dict:
    try:
        request.app.state.wgm.remove(config=config)
        return {"action": "remove", "message": f"VPN [ {config} ] removed."}
    except KeyError as e:
        raise HTTPException(status_code=codes.NOT_FOUND, detail=str(e))

@router.get("/status", response_model=GetResponse, status_code=200)
def status(request: Request) -> dict:
    return {"action": "status", "instances": request.app.state.wgm.status}
