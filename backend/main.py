"""
Trading Simulator FastAPI Application
Main entry point for the trading simulator backend
"""

import asyncio

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from dependencies import (
    gbm_manager,
    instrument_manager,
    lb_manager,
    news_engine,
    order_generator,
    price_engine,
)

# Setup logging
setup_logging()

app = FastAPI(
    title="Trading Simulator API",
    description="A web-based stock trading simulator for live competitions",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Trading Simulator API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/version")
async def version_check():
    return {"version": "1.0.0"}


@app.on_event("startup")
async def startup_event():
    """
    Initialize GBM manager
    """
    asyncio.create_task(gbm_manager.run())

    """
    Start price engine for GBM
    """
    asyncio.create_task(price_engine.run())

    """
    Start news engine to adjust add. drift
    """
    asyncio.create_task(news_engine.add_news_on_tick())

    """
    Start liquidity bots
    """
    asyncio.create_task(lb_manager.run())

    """
    Start order generator to place orders every 5 seconds
    """
    asyncio.create_task(order_generator.run())


@app.websocket("/ws/market")
async def websocket_market(websocket: WebSocket):
    import time

    await price_engine.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()  # ping
            if data == "ping":
                await websocket.send_json(
                    {"type": "pong", "timestamp": time.time()}
                )  # pong
    except Exception as e:
        pass
    finally:
        price_engine.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
