import os
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import aiofiles
from pymongo.errors import PyMongoError

import database

logger = logging.getLogger(__name__)
router = APIRouter()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "dataset")


class DeleteDatasetFilesRequest(BaseModel):
    files: list[str] = Field(..., description="List of dataset MIDI filenames to delete")


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

            if database.init_mongodb() and database.midi_files_collection is not None:
                await database.midi_files_collection.update_one(
                    {"filename": file.filename},
                    {
                        "$set": {
                            "filename": file.filename,
                            "content_type": file.content_type,
                            "size": len(content),
                            "storage": "filesystem",
                            "path": dest,
                            "status": "uploaded",
                            "updated_at": datetime.now(timezone.utc),
                        },
                        "$setOnInsert": {
                            "uploaded_at": datetime.now(timezone.utc),
                        },
                    },
                    upsert=True,
                )

            uploaded.append(file.filename)
            logger.info(f"Uploaded: {file.filename}")
        except PyMongoError as e:
            errors.append(f"{file.filename}: Saved file, but MongoDB insert failed: {str(e)}")
            logger.error(f"MongoDB insert failed for {file.filename}: {e}")
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
async def dataset_info():
    if database.init_mongodb() and database.midi_files_collection is not None:
        try:
            cursor = database.midi_files_collection.find(
                {"status": {"$ne": "deleted"}},
                {"_id": 0, "filename": 1},
            ).sort("uploaded_at", -1)
            records = await cursor.to_list(length=500)
            files = [
                record["filename"]
                for record in records
                if record.get("filename", "").endswith((".mid", ".midi"))
            ]
            return {"files": files, "count": len(files)}
        except PyMongoError as e:
            logger.error(f"MongoDB dataset-info failed, falling back to disk: {e}")

    if not os.path.exists(UPLOAD_DIR):
        return {"files": [], "count": 0}

    files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith((".mid", ".midi"))]
    return {"files": files, "count": len(files)}


# Delete selected MIDI files from the training dataset
# Validates filenames to prevent deleting files outside the dataset directory
@router.post("/delete-dataset-files")
async def delete_dataset_files(request: DeleteDatasetFilesRequest):
    if not request.files:
        raise HTTPException(status_code=400, detail="No files specified for deletion")

    deleted = []
    errors = []

    for filename in request.files:
        try:
            if (
                ".." in filename
                or "/" in filename
                or "\\" in filename
                or not filename.endswith((".mid", ".midi"))
            ):
                errors.append(f"{filename}: Invalid filename")
                continue

            path = os.path.join(UPLOAD_DIR, filename)
            if not os.path.exists(path):
                errors.append(f"{filename}: File not found")
                continue

            os.remove(path)
            if database.init_mongodb() and database.midi_files_collection is not None:
                await database.midi_files_collection.update_one(
                    {"filename": filename},
                    {
                        "$set": {
                            "status": "deleted",
                            "deleted_at": datetime.now(timezone.utc),
                        }
                    },
                )
            deleted.append(filename)
            logger.info(f"Deleted dataset file: {filename}")
        except PyMongoError as e:
            errors.append(f"{filename}: File deleted, but MongoDB update failed: {str(e)}")
            logger.error(f"Failed to update MongoDB for dataset file {filename}: {e}")
        except Exception as e:
            errors.append(f"{filename}: {str(e)}")
            logger.error(f"Failed to delete dataset file {filename}: {e}")

    remaining_files = []
    if os.path.exists(UPLOAD_DIR):
        remaining_files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith((".mid", ".midi"))]

    return JSONResponse({
        "deleted": deleted,
        "errors": errors,
        "remaining_files": remaining_files,
        "total_files": len(remaining_files),
        "message": f"Deleted {len(deleted)} file(s)"
    })
