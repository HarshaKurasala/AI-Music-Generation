import os
import logging
import numpy as np
from music21 import converter, chord, note, stream

logger = logging.getLogger(__name__)

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "dataset")


# Parse MIDI file and extract note/chord strings
# Converts MIDI note objects into string representations
# Parameters: filepath (path to MIDI file)
# Returns: List of note strings extracted from the file
def extract_notes_from_midi(filepath: str) -> list[str]:
    """Parse a MIDI file and extract note/chord strings."""
    notes = []
    try:
        midi = converter.parse(filepath)
        parts = midi.flatten().notes
        for element in parts:
            if isinstance(element, note.Note):
                notes.append(str(element.pitch))
            elif isinstance(element, chord.Chord):
                notes.append("." .join(str(n) for n in element.normalOrder))
    except Exception as e:
        logger.warning(f"Failed to parse {filepath}: {e}")
    return notes


# Load and extract notes from all MIDI files in dataset directory
# Finds all MIDI files, extracts notes from each, and combines them
# Parameters: files (optional list of specific filenames to load)
# Returns: List of all note strings extracted from MIDI files
def load_all_notes(files: list[str] = None) -> list[str]:
    """
    Load and extract notes from all MIDI files in the dataset directory.
    
    Args:
        files: Optional list of specific filenames to load. If None, loads all files.
    
    Returns:
        List of all note strings extracted from the MIDI files.
    
    Raises:
        FileNotFoundError: If dataset directory or MIDI files don't exist
        ValueError: If no valid notes can be extracted
    """
    all_notes = []
    
    if not os.path.exists(UPLOAD_DIR):
        raise FileNotFoundError("Dataset directory does not exist. Please upload MIDI files first.")
    
    midi_files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith((".mid", ".midi"))]

    if not midi_files:
        raise FileNotFoundError("No MIDI files found in dataset directory. Please upload at least one .mid or .midi file to train the model.")

    if files:
        midi_files = [f for f in midi_files if f in files]
        if not midi_files:
            raise ValueError("None of the specified files were found in the dataset directory.")

    for filename in midi_files:
        path = os.path.join(UPLOAD_DIR, filename)
        notes = extract_notes_from_midi(path)
        if not notes:
            logger.warning(f"No notes extracted from {filename} - file may be empty or unsupported")
        all_notes.extend(notes)
        logger.info(f"Extracted {len(notes)} notes from {filename}")

    if not all_notes:
        raise ValueError("No valid notes extracted from any MIDI files. Ensure your MIDI files contain valid note data.")
    
    logger.info(f"Total notes extracted: {len(all_notes)}")
    return all_notes


# Build input/output sequences for LSTM training
# Creates sliding windows of notes where input is seq_length notes and output is next note
# Also creates vocabulary mappings for encoding/decoding
# Parameters: notes (list of note strings), seq_length (length of sequences)
# Returns: Tuple of (X, y, vocab, note_to_int)
def build_sequences(notes: list[str], seq_length: int):
    """Build input/output sequences and vocabulary mappings."""
    vocab = sorted(set(notes))
    note_to_int = {n: i for i, n in enumerate(vocab)}

    inputs, outputs = [], []
    for i in range(len(notes) - seq_length):
        seq_in = notes[i:i + seq_length]
        seq_out = notes[i + seq_length]
        inputs.append([note_to_int[n] for n in seq_in])
        outputs.append(note_to_int[seq_out])

    n_vocab = len(vocab)
    X = np.reshape(inputs, (len(inputs), seq_length, 1)) / float(n_vocab)
    y = np.array(outputs)

    return X, y, vocab, note_to_int
