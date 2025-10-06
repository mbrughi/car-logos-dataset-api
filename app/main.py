from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

from app.config import settings
from app.routers import health, brands, logos, admin  

from app.middleware.request_log import RequestLogMiddleware
from app.middleware.ratelimit_headers import RateLimitHeadersMiddleware

app = FastAPI(title=settings.APP_NAME, version="0.1.0")

# CORS (per WP e frontends)
app.add_middleware(
    CORSMiddleware,
    allow_origins=(settings.cors_origins or ["*"]) if settings.APP_ENV == "dev" else settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="app/templates")

app.add_middleware(
    RequestLogMiddleware, 
    max_items=settings.REQLOG_MAX_ITEMS,
    ttl_seconds=settings.REQLOG_TTL_SECONDS
)

app.add_middleware(RateLimitHeadersMiddleware)

# Routers
app.include_router(health.router)
app.include_router(brands.router)
app.include_router(logos.router)  
app.include_router(admin.router)



# === MOUNT STATIC dal fork (robusto) ===
def safe_mount_static(app: FastAPI) -> None:
    root = Path(settings.STORAGE_ROOT)
    mounts = [
        ("logos", root / "logos"),             # include /logos/original, /logos/optimized, /logos/thumb
        ("local-logos", root / "local-logos"), # override locali
    ]
    for name, folder in mounts:
        if folder.exists():
            app.mount(f"/static/{name}", StaticFiles(directory=str(folder)), name=name)

safe_mount_static(app)

@app.get("/")
def root():
    return {"name": settings.APP_NAME, "env": settings.APP_ENV}
