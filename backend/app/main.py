"""
Path Payment Terminal API Emulator - Main FastAPI Application
"""
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .routers import auth, payment, reversal, completion, loyalty, auto_reversal, websocket


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events"""
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title="Path Payment Terminal API Emulator",
    description="API emulator for testing iOS/Android payment terminal integrations",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(payment.router)
app.include_router(reversal.router)
app.include_router(completion.router)
app.include_router(loyalty.router)
app.include_router(auto_reversal.router)
app.include_router(websocket.router)

# Serve frontend
frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
if os.path.exists(frontend_path):
    @app.get("/", response_class=HTMLResponse)
    async def read_root():
        index_path = os.path.join(frontend_path, "index.html")
        if os.path.exists(index_path):
            with open(index_path, "r") as f:
                content = f.read()
                # Replace /assets with correct path
                content = content.replace('/assets/', '/static/')
                return content
        return "<html><body><h1>Path Payment Terminal API Emulator</h1><p>Frontend not found</p></body></html>"
    
    # Serve static files from frontend directory (only mount once)
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Path Payment Terminal API Emulator"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)

