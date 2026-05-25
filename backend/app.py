# FastAPI backend server for AI Music Generation
# Handles MIDI uploads, model training, and music generation

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from routes.midi_routes import router as midi_router
from routes.train_routes import router as train_router
from routes.generate_routes import router as generate_router

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title="AI Music Generation API",
    description="Upload MIDI files, train LSTM models, and generate new music sequences.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(os.getenv("UPLOAD_DIR", "dataset"), exist_ok=True)
os.makedirs(os.getenv("OUTPUT_DIR", "generated_music"), exist_ok=True)
os.makedirs("models", exist_ok=True)

app.mount("/generated_music", StaticFiles(directory="generated_music"), name="generated_music")

app.include_router(midi_router, prefix="/api", tags=["MIDI Upload"])
app.include_router(train_router, prefix="/api", tags=["Model Training"])
app.include_router(generate_router, prefix="/api", tags=["Music Generation"])


# Health check endpoint to verify API is running
# Returns status and message indicating the API is operational
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "AI Music Generation API is running"}
