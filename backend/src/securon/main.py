"""FastAPI main application with platform orchestration"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .interfaces import *
from .platform import PlatformOrchestrator, PlatformConfig
from .api.routes import router

# Global platform orchestrator
platform: PlatformOrchestrator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global platform
    
    # Startup
    try:
        # Load configuration
        config = PlatformConfig.from_environment()
        
        # Initialize platform
        platform = PlatformOrchestrator(config)
        await platform.initialize()
        
        # Make platform available to routes
        app.state.platform = platform
        
        yield
        
    finally:
        # Shutdown
        if platform:
            await platform.shutdown()


app = FastAPI(
    title="Securon Platform API",
    description="Cloud security platform with IaC scanning and ML-based runtime analysis",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server (default)
        "http://localhost:3001",  # React dev server (alternate port)
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Securon Platform API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint with platform status"""
    global platform
    
    if not platform or not platform.initialized:
        return {"status": "initializing"}
    
    try:
        # Get detailed health status from platform monitor
        health_status = await platform.get_monitor().get_health_status()
        platform_status = await platform.get_platform_status()
        
        return {
            "status": health_status["overall_status"],
            "platform": platform_status,
            "components": health_status["components"],
            "timestamp": health_status["timestamp"]
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.get("/metrics")
async def get_metrics():
    """Get platform metrics"""
    global platform
    
    if not platform or not platform.initialized:
        return {"error": "Platform not initialized"}
    
    try:
        metrics = await platform.get_monitor().get_metrics()
        return metrics
        
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    
    # Load configuration for standalone run
    config = PlatformConfig.from_environment()
    
    uvicorn.run(
        app, 
        host=config.api_host, 
        port=config.api_port,
        log_level=config.logging.level.lower()
    )