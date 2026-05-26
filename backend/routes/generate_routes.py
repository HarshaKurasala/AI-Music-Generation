import os
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from services.generation_service import GenerationService

logger = logging.getLogger(__name__)
router = APIRouter()
generation_service = GenerationService()

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "generated_music")


class GenerateRequest(BaseModel):
    num_notes: int = Field(default=100, ge=20, le=500)
    temperature: float = Field(default=1.0, ge=0.1, le=2.0)
    instrument: str = Field(default="piano")
    style: str = Field(default="cinematic")
    key: str = Field(default="C")
    tempo: int = Field(default=92, ge=55, le=170)
    density: float = Field(default=0.7, ge=0.2, le=1.0)
    harmony: bool = Field(default=True)


# Generate new MIDI music sequence using trained LSTM model
# Creates a new composition based on generation parameters
# Parameters: request (generation configuration with num_notes, temperature, instrument)
# Returns: JSON with generated filename and download URL
@router.post("/generate-music")
def generate_music(request: GenerateRequest):
    try:
        filename = generation_service.generate(
            num_notes=request.num_notes,
            temperature=request.temperature,
            instrument=request.instrument,
            style=request.style,
            key=request.key,
            tempo=request.tempo,
            density=request.density,
            harmony=request.harmony
        )
        return JSONResponse({
            "filename": filename,
            "download_url": f"/api/download/{filename}",
            "stream_url": f"/generated_music/{filename}",
            "message": "Music generated successfully"
        })
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Download a generated MIDI file
# Allows users to download generated music files
# Parameters: filename (name of file to download)
# Returns: MIDI file as attachment
@router.get("/download/{filename}")
def download_file(filename: str):
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, media_type="audio/midi", filename=filename)


# List all generated music files
# Returns list of all generated MIDI files sorted by newest first
# Returns: JSON with list of generated files
@router.get("/generated-files")
def list_generated():
    if not os.path.exists(OUTPUT_DIR):
        return {"files": []}
    files = sorted(
        [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".mid")],
        reverse=True
    )
    return {"files": files}


class DeleteFilesRequest(BaseModel):
    files: list[str] = Field(..., description="List of filenames to delete")


# Delete specified generated music files
# Removes files from the generated_music directory
# Parameters: request (list of filenames to delete)
# Returns: JSON with deleted files and any errors
@router.post("/delete-generated-files")
def delete_generated_files(request: DeleteFilesRequest):
    if not request.files:
        raise HTTPException(status_code=400, detail="No files specified for deletion")
    
    deleted = []
    errors = []
    
    for filename in request.files:
        try:
            if ".." in filename or "/" in filename or "\\" in filename:
                errors.append(f"{filename}: Invalid filename")
                continue
            
            path = os.path.join(OUTPUT_DIR, filename)
            if not os.path.exists(path):
                errors.append(f"{filename}: File not found")
                continue
            
            os.remove(path)
            deleted.append(filename)
            logger.info(f"Deleted file: {filename}")
        except Exception as e:
            errors.append(f"{filename}: {str(e)}")
            logger.error(f"Failed to delete {filename}: {e}")
    
    return JSONResponse({
        "deleted": deleted,
        "errors": errors,
        "message": f"Deleted {len(deleted)} file(s)"
    })
