from fastapi import FastAPI
from app.routers import auth, users, ticket, comment, attachments, dashboard, notification, activity_log
app = FastAPI(
    title="Ticketing System API",
    version="1.0.0"
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