# app/main.py

from fastapi import FastAPI
from app.api.v1.endpoints import discord_interactions

app = FastAPI()

app.include_router(discord_interactions.router, prefix="/api/v1")