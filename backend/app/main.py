from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.limiter import limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler
from app.routers import (
    auth,
    users,
    ticket,
    comment,
    attachments,
    dashboard,
    notification,
    activity_log,
)

app = FastAPI(
    title="Ticketing System API",
    version="1.0.0",
)
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(ticket.router)
app.include_router(comment.router)
app.include_router(attachments.router)
app.include_router(dashboard.router)
app.include_router(notification.router)
app.include_router(activity_log.router)

@app.get("/")
def root():
    return {
        "message": "Ticketing System API is running"
    }