from contextlib import asynccontextmanager # contextlib helps mananges the resources that need setup and cleanup

from fastapi import FastAPI # FastAPI is a web framework

from app.db import Base, engine
from app.routers import queues, tickets, resolve


@asynccontextmanager #The decorator @asynccontextmanager transforms the function into something FastAPI can use to manage the application's lifetime
async def lifespan(app: FastAPI): #Run this function when the application starts, and finish it when the application shuts down."
    Base.metadata.create_all(bind=engine)
    yield
#every database model inherits from Base
# metadata contains all models related info  that we define
#create_all() method creates all the tables in the database that are defined by the models
# engine is the database connection that we defined in db.py
#bind=engine means "Use this database connection when creating the tables.
#Everything before yield happens at startup.

#Everything after yield (there isn't any in this file) would happen during shutdown.
app = FastAPI(title="Support Ticket API", lifespan=lifespan)
#this creates an FastAPI application instance with the title "Support Ticket API" and the lifespan function we defined earlier. This instance will be used to define routes, middleware, and other application settings.
app.include_router(queues.router)
app.include_router(tickets.router)
app.include_router(resolve.router)
#include_router() method adds a router to the application
#Instead of putting every endpoint in main.py, they're organized into separate router files.
#include_router() tells FastAPI:
#Load the routes defined in this router."
@app.get("/health")
def health():
    return {"status": "ok"}
#when some one requestd /health health() function runs and repies with status:ok
