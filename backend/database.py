import logging
import os
import time
from datetime import datetime, timezone

import certifi
from dotenv import load_dotenv
from gridfs import GridFSBucket
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pymongo.errors import ConfigurationError, PyMongoError

load_dotenv()

logger = logging.getLogger(__name__)

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "music_generation_ai")

client = None
db = None
midi_files_collection = None
generated_files_collection = None
training_runs_collection = None
model_metadata_collection = None
sync_client = None
sync_db = None
sync_model_metadata_collection = None
sync_model_files_bucket = None
_retry_after = 0
_RETRY_COOLDOWN_SECONDS = 30


def init_mongodb() -> bool:
    global client
    global db
    global midi_files_collection
    global generated_files_collection
    global training_runs_collection
    global model_metadata_collection
    global _retry_after

    if client is not None:
        return True

    if time.monotonic() < _retry_after:
        return False

    if not MONGODB_URI:
        logger.warning("MONGODB_URI is not configured; MongoDB features are disabled.")
        _retry_after = time.monotonic() + _RETRY_COOLDOWN_SECONDS
        return False

    try:
        client = AsyncIOMotorClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            tlsCAFile=certifi.where(),
        )
        db = client[MONGODB_DB]
        midi_files_collection = db["midi_files"]
        generated_files_collection = db["generated_files"]
        training_runs_collection = db["training_runs"]
        model_metadata_collection = db["model_metadata"]
        return True
    except ConfigurationError as exc:
        logger.error("MongoDB client configuration failed: %s", exc)
        client = None
        db = None
        _retry_after = time.monotonic() + _RETRY_COOLDOWN_SECONDS
        return False


def mongodb_configured() -> bool:
    return bool(MONGODB_URI)


def init_sync_mongodb() -> bool:
    global sync_client
    global sync_db
    global sync_model_metadata_collection
    global sync_model_files_bucket
    global _retry_after

    if sync_client is not None:
        return True

    if time.monotonic() < _retry_after:
        return False

    if not MONGODB_URI:
        logger.warning("MONGODB_URI is not configured; MongoDB features are disabled.")
        _retry_after = time.monotonic() + _RETRY_COOLDOWN_SECONDS
        return False

    try:
        sync_client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            tlsCAFile=certifi.where(),
        )
        sync_client.admin.command("ping")
        sync_db = sync_client[MONGODB_DB]
        sync_model_metadata_collection = sync_db["model_metadata"]
        sync_model_files_bucket = GridFSBucket(sync_db, bucket_name="model_files")
        return True
    except PyMongoError as exc:
        logger.error("MongoDB sync connection failed: %s", exc)
        sync_client = None
        sync_db = None
        _retry_after = time.monotonic() + _RETRY_COOLDOWN_SECONDS
        return False


def store_trained_model_files(model_path: str, vocab_path: str, metadata: dict) -> dict:
    if not init_sync_mongodb():
        return {"stored_in_mongodb": False, "reason": "MongoDB is not available"}

    if not os.path.exists(model_path):
        return {"stored_in_mongodb": False, "reason": f"Model file not found: {model_path}"}
    if not os.path.exists(vocab_path):
        return {"stored_in_mongodb": False, "reason": f"Vocabulary file not found: {vocab_path}"}

    try:
        now = datetime.now(timezone.utc)
        base_metadata = {
            "trained_at": metadata.get("trained_at"),
            "files": metadata.get("files"),
            "created_at": now,
        }

        with open(model_path, "rb") as model_file:
            model_file_id = sync_model_files_bucket.upload_from_stream(
                os.path.basename(model_path),
                model_file,
                metadata={**base_metadata, "kind": "keras_model"},
            )

        with open(vocab_path, "rb") as vocab_file:
            vocab_file_id = sync_model_files_bucket.upload_from_stream(
                os.path.basename(vocab_path),
                vocab_file,
                metadata={**base_metadata, "kind": "vocabulary"},
            )

        record = {
            **metadata,
            "model_file_id": model_file_id,
            "vocab_file_id": vocab_file_id,
            "model_filename": os.path.basename(model_path),
            "vocab_filename": os.path.basename(vocab_path),
            "stored_at": now,
            "status": "trained",
        }
        result = sync_model_metadata_collection.insert_one(record)

        return {
            "stored_in_mongodb": True,
            "metadata_id": str(result.inserted_id),
            "model_file_id": str(model_file_id),
            "vocab_file_id": str(vocab_file_id),
        }
    except PyMongoError as exc:
        logger.error("Failed to store trained model in MongoDB: %s", exc)
        return {"stored_in_mongodb": False, "reason": str(exc)}


async def ping_mongodb() -> bool:
    if not init_mongodb():
        return False

    try:
        await client.admin.command("ping")
        logger.info("Connected to MongoDB database: %s", MONGODB_DB)
        return True
    except PyMongoError as exc:
        logger.error("MongoDB connection failed: %s", exc)
        global _retry_after
        _retry_after = time.monotonic() + _RETRY_COOLDOWN_SECONDS
        return False
