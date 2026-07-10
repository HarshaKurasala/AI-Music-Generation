import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from services.training_service import TrainingService

logger = logging.getLogger(__name__)
router = APIRouter()
training_service = TrainingService()


class TrainRequest(BaseModel):
    epochs: int = Field(default=50, ge=1, le=500)
    batch_size: int = Field(default=64, ge=8, le=256)
    seq_length: int = Field(default=50, ge=10, le=200)
    files: list[str] = Field(default=None, description="Specific MIDI files to train on (optional)")


# Start LSTM model training on uploaded MIDI dataset
# Validates parameters and schedules training as background task
# Parameters: request (training configuration), background_tasks (FastAPI task manager)
# Returns: JSON with training start confirmation
@router.post("/train-model")
async def train_model(request: TrainRequest, background_tasks: BackgroundTasks):
    if training_service.is_training:
        raise HTTPException(status_code=409, detail="Training already in progress")

    training_service.begin_training(
        epochs=request.epochs,
        files=request.files
    )

    background_tasks.add_task(
        training_service.train,
        epochs=request.epochs,
        batch_size=request.batch_size,
        seq_length=request.seq_length,
        files=request.files
    )

    return JSONResponse({
        "message": "Training started",
        "config": request.model_dump()
    })


# Get current training status and progress
# Returns current epoch, loss, accuracy, and status message
# Returns: JSON with training status
@router.get("/training-status")
def training_status():
    return training_service.get_status()


# Reset training state for recovery from stuck state
# Resets training flag and status to idle
# Returns: JSON with reset confirmation
@router.post("/reset-training")
def reset_training():
    training_service.is_training = False
    training_service._status = {"state": "idle", "epoch": 0, "total_epochs": 0, "loss": [], "accuracy": [], "message": "Training reset", "files": None}
    return JSONResponse({"message": "Training state reset successfully"})


# Get information about the currently trained model
# Returns metadata about last trained model including timestamp and files used
# Returns: JSON with model metadata
@router.get("/trained-model-info")
def get_trained_model_info():
    return training_service.get_trained_model_info()


@router.post("/sync-trained-model")
def sync_trained_model():
    return training_service.sync_trained_model_to_mongodb()
