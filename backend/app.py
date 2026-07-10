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
from database import ping_mongodb

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title="AI Music Generation API",
    description="Upload MIDI files, train LSTM models, and generate new music sequences.",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None
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


@app.on_event("startup")
async def startup_event():
    await ping_mongodb()


@app.get("/", tags=["Home"])
def home():
    return {
        "status": "ok",
        "message": "AI Music Generation backend is running",
        "database": "MongoDB connection is configured",
        "frontend": "http://127.0.0.1:5173",
        "docs": "disabled",
        "health_check": "/health",
        "api_routes": {
            "upload_midi": "POST /api/upload-midi",
            "dataset_info": "GET /api/dataset-info",
            "delete_dataset_files": "POST /api/delete-dataset-files",
            "train_model": "POST /api/train-model",
            "training_status": "GET /api/training-status",
            "reset_training": "POST /api/reset-training",
            "trained_model_info": "GET /api/trained-model-info",
            "generate_music": "POST /api/generate-music",
            "generated_files": "GET /api/generated-files",
            "download_generated_file": "GET /api/download/{filename}",
            "delete_generated_files": "POST /api/delete-generated-files"
        }
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "AI Music Generation API is running"}
