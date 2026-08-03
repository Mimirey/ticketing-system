from fastapi import FastAPI
from app.routers import auth, users, ticket, comment, attachments, dashboard, notification, activity_log
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(
    title="Ticketing System API",
    version="1.0.0"
)
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