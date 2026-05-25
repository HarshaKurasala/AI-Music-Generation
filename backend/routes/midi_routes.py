import os
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import aiofiles

logger = logging.getLogger(__name__)
router = APIRouter()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "dataset")


# Upload one or more MIDI files to the dataset directory
# Validates file extensions and saves files to disk
# Parameters: files (list of uploaded files)
# Returns: JSON with uploaded files, errors, and total count
@router.post("/upload-midi")
async def upload_midi(files: list[UploadFile] = File(...)):
    uploaded = []
    errors = []

    for file in files:
        if not file.filename.endswith((".mid", ".midi")):
            errors.append(f"{file.filename}: Only .mid/.midi files are accepted")
            continue

        dest = os.path.join(UPLOAD_DIR, file.filename)
        try:
            async with aiofiles.open(dest, "wb") as f:
                content = await file.read()
                await f.write(content)
            uploaded.append(file.filename)
            logger.info(f"Uploaded: {file.filename}")
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")

    if not uploaded:
        raise HTTPException(status_code=400, detail={"errors": errors})

    midi_files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith((".mid", ".midi"))]
    return JSONResponse({
        "uploaded": uploaded,
        "errors": errors,
        "total_files": len(midi_files),
        "message": f"Successfully uploaded {len(uploaded)} file(s)"
    })


# Get information about uploaded MIDI files
# Returns list of all MIDI files in dataset directory and count
# Returns: JSON with files list and count
@router.get("/dataset-info")
def dataset_info():
    if not os.path.exists(UPLOAD_DIR):
        return {"files": [], "count": 0}

    files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith((".mid", ".midi"))]
    return {"files": files, "count": len(files)}
