from fastapi import FastAPI
from contextlib import asynccontextmanager

from api import WireGuardRouter, RcloneRouter
from core import WireGuardManager, RcloneManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    with WireGuardManager() as wgm, RcloneManager() as rcm:
        app.state.wgm = wgm
        app.state.rcm = rcm
        yield


app = FastAPI(lifespan=lifespan)
app.include_router(WireGuardRouter, prefix="/vpn", tags=["vpn"])
app.include_router(RcloneRouter, prefix="/rclone", tags=["rclone"])
