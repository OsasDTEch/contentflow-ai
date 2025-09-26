from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.db import Base, engine
from routes import auth_routes, onboarding_routes, company_routes, agent_routes

app = FastAPI(title="CONTENTFLOW AI BACKEND")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB iniT
# Base.metadata.drop_all(engine)
Base.metadata.create_all(bind=engine)


# Routers
app.include_router(auth_routes.router)
app.include_router(onboarding_routes.router)
app.include_router(company_routes.router)
app.include_router(agent_routes.router)


@app.get("/")
def root():
    return {"message": "Welcome to Contentflow AI"}


