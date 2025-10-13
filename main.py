# main.py
from fastapi import FastAPI

import crud
from auth import router as auth_router
from database import Base, engine

app = FastAPI(title="FastAPI CRUD with Basic Auth")

# Create database tables
Base.metadata.create_all(bind=engine)

# Register routers
app.include_router(auth_router)
app.include_router(crud.router)
