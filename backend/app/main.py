from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db import engine, Base, SessionLocal
from app.db_seed import seed_db
from app.api import ussd, queues, tickets, notifications

app = FastAPI(
    title=settings.APP_NAME,
    description="Q-Less Virtual Queue API for Africa's Talking Telecom Integration",
    version="1.0.0"
)

# CORS middleware
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
if "*" in origins:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event to auto-create tables & seed database
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_db(db)
    finally:
        db.close()

# Include routers
app.include_router(ussd.router)
app.include_router(queues.router)
app.include_router(tickets.router)
app.include_router(notifications.router)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Q-Less API"}

@app.get("/")
def root():
    return {"message": "Welcome to Q-Less API", "docs": "/docs"}
