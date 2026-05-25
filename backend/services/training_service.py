import os
import json
import logging
import numpy as np
import threading
from datetime import datetime
from tensorflow import keras

from utils.midi_utils import load_all_notes, build_sequences
from models.lstm_model import build_lstm_model

logger = logging.getLogger(__name__)

MODEL_PATH = os.getenv("MODEL_PATH", "models/music_model.keras")
VOCAB_PATH = "models/vocab.json"
MODEL_METADATA_PATH = "models/model_metadata.json"


class TrainingService:
    """Service for managing LSTM model training and status tracking."""
    
    # Initialize training service with default state
    # Sets up flags and status tracking for training sessions
    def __init__(self):
        self.is_training = False
        self._status = {"state": "idle", "epoch": 0, "total_epochs": 0, "loss": [], "accuracy": [], "message": ""}
        self.trained_files = None

    # Get current training status
    # Returns a copy of the status dictionary to prevent external modification
    def get_status(self) -> dict:
        return self._status.copy()

    # Train LSTM model on MIDI dataset
    # Loads MIDI files, builds sequences, trains model, and saves results
    # Parameters: epochs (number of epochs), batch_size (batch size), seq_length (sequence length), files (optional specific files)
    def train(self, epochs: int, batch_size: int, seq_length: int, files: list[str] = None):
        self.is_training = True
        self._status = {"state": "preparing", "epoch": 0, "total_epochs": epochs, "loss": [], "accuracy": [], "message": "Loading MIDI files..."}

        try:
            notes = load_all_notes(files=files)
            if len(notes) < seq_length:
                raise ValueError(f"Not enough notes in dataset. Got {len(notes)}, need at least {seq_length}.")
            
            self._status["message"] = f"Building sequences from {len(notes)} notes..."

            X, y, vocab, note_to_int = build_sequences(notes, seq_length)
            
            if len(X) < 10:
                raise ValueError("Not enough training sequences. Upload more MIDI files or reduce sequence length.")
            
            n_vocab = len(vocab)

            os.makedirs("models", exist_ok=True)
            with open(VOCAB_PATH, "w") as f:
                json.dump({"vocab": vocab, "note_to_int": note_to_int, "seq_length": seq_length}, f)

            model = build_lstm_model(seq_length, n_vocab)
            self._status["message"] = "Training started..."
            self._status["state"] = "training"

            # Custom callback to track training progress
            # Updates status after each epoch with loss and accuracy
            class ProgressCallback(keras.callbacks.Callback):
                def __init__(cb_self):
                    super().__init__()
                    cb_self.best_loss = float('inf')

                def on_epoch_end(cb_self, epoch, logs=None):
                    logs = logs or {}
                    loss = logs.get("loss", 0)
                    self._status["epoch"] = epoch + 1
                    self._status["loss"].append(round(float(loss), 4))
                    self._status["accuracy"].append(round(float(logs.get("accuracy", 0)), 4))
                    self._status["message"] = f"Epoch {epoch+1}/{epochs} — loss: {loss:.4f}"
                    
                    if loss < cb_self.best_loss:
                        cb_self.best_loss = loss
                        model.save(MODEL_PATH)

            model.fit(
                X, y,
                epochs=epochs,
                batch_size=batch_size,
                callbacks=[ProgressCallback()],
                verbose=0
            )

            self._status["state"] = "completed"
            self._status["message"] = "Training complete. Model saved."
            
            self._save_model_metadata(files)
            
            logger.info("Training completed successfully")

        except Exception as e:
            self._status["state"] = "error"
            self._status["message"] = str(e)
            logger.error(f"Training failed: {e}")
        finally:
            self.is_training = False

    # Save metadata about the trained model
    # Stores training timestamp, files used, and model paths
    # Parameters: trained_files (optional list of files used for training)
    def _save_model_metadata(self, trained_files: list[str] = None):
        try:
            metadata = {
                "trained_at": datetime.now().isoformat(),
                "files": trained_files or "all",
                "model_path": MODEL_PATH,
                "vocab_path": VOCAB_PATH
            }
            os.makedirs("models", exist_ok=True)
            with open(MODEL_METADATA_PATH, "w") as f:
                json.dump(metadata, f, indent=2)
            self.trained_files = trained_files
            logger.info(f"Saved model metadata: {metadata}")
        except Exception as e:
            logger.warning(f"Failed to save model metadata: {e}")

    # Get information about the currently trained model
    # Reads metadata from file if it exists, otherwise returns default values
    # Returns: Dictionary with model metadata
    def get_trained_model_info(self) -> dict:
        try:
            if os.path.exists(MODEL_METADATA_PATH):
                with open(MODEL_METADATA_PATH) as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load model metadata: {e}")
        
        return {
            "trained_at": None,
            "files": None,
            "model_path": MODEL_PATH,
            "vocab_path": VOCAB_PATH
        }
