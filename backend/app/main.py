import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base, SessionLocal
from .seed.seed_data import seed_database
from .services.calendar_engine import compute_client_obligations
from .routers import clients, calendar, notifications, rules, dashboard

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables and seed data
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seeded = seed_database(db)
        if seeded:
            logger.info("Database seeded with initial data")
            compute_client_obligations(db)
            logger.info("Client obligations computed")
    finally:
        db.close()
    yield


app = FastAPI(
    title="Systém daňových notifikací",
    description="MVP prototyp systému automatizovaných daňových notifikací pro účetní firmu",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clients.router)
app.include_router(calendar.router)
app.include_router(notifications.router)
app.include_router(rules.router)
app.include_router(dashboard.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "danove-notifikace"}
