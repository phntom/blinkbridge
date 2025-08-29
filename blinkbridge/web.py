from __future__ import annotations
from typing import TYPE_CHECKING
from fastapi import FastAPI, APIRouter, HTTPException
import logging

log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from blinkbridge.main import Application


def create_router(app: "Application") -> APIRouter:
    router = APIRouter()

    @router.post("/motion_detected_event/{camera_name}")
    async def motion_detected_event(camera_name: str):
        log.info(f"Received motion detected event for {camera_name}")
        if camera_name not in app.cam_manager.get_cameras():
            raise HTTPException(status_code=404, detail="Camera not found")

        await app.handle_event(camera_name)
        return {"message": f"Motion detected event processed for {camera_name}"}

    return router


def get_app(app: "Application") -> FastAPI:
    fast_api_app = FastAPI(
        title="BlinkBridge",
        description="BlinkBridge API",
        version="0.1.0",
    )
    fast_api_app.include_router(create_router(app))
    return fast_api_app
