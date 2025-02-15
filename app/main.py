# FastAPI Imports
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

# SlowAPI Rate Limiter
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

# Database Imports
from app.database.tables import table_users, table_blacklist_tokens
from app.database.database import engine

# Routers Import
from app.routers import routers

# ENV Variables
from app.config import settings


# FastAPI app Init
app = FastAPI(
    title="Template FastAPI Backend",
    version=settings.environment,
    openapi_url=f"/api/{settings.environment}/openapi.json",
    docs_url=f"/api/{settings.environment}/docs",
    redoc_url=f"/api/{settings.environment}/redoc",
)


# Middleware

# CORS
origins = ["*"]
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTTPS Redirect
if settings.https:
    app.add_middleware(HTTPSRedirectMiddleware)

# Session Middleware
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

# Rate Limiter
limiter = Limiter(key_func=get_remote_address,
                  default_limits=[settings.rate_limit])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Routers
app.include_router(routers.router)

# Create Tables
table_users.Base.metadata.create_all(bind=engine)
table_blacklist_tokens.Base.metadata.create_all(bind=engine)


# Backend Healthcheck Route


@app.get("/api/{settings.environment}/healthcheck", status_code=status.HTTP_200_OK)
def current_status():
    return {"status": "Backend Server Active"}
