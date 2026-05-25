import os
import json
import logging
import uuid
import numpy as np
import pretty_midi
import subprocess
import platform
from collections import Counter

logger = logging.getLogger(__name__)

MODEL_PATH = os.getenv("MODEL_PATH", "models/music_model.keras")
VOCAB_PATH = "models/vocab.json"
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "generated_music")

INSTRUMENT_MAP = {
    "piano": 0,
    "guitar": 25,
    "violin": 40,
    "flute": 73,
    "trumpet": 56,
    "organ": 19,
}


class GenerationService:
    """Service for generating new music using trained LSTM model."""
    
    # Load trained model and vocabulary from disk
    # Reads the saved model and vocabulary files
    # Returns: Tuple of (model, vocab, note_to_int, seq_length)
    def _load_model_and_vocab(self):
        from tensorflow import keras
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError("Trained model not found. Please train the model first.")
        if not os.path.exists(VOCAB_PATH):
            raise FileNotFoundError("Vocabulary file not found. Please train the model first.")

        model = keras.models.load_model(MODEL_PATH)
        with open(VOCAB_PATH) as f:
            data = json.load(f)
        return model, data["vocab"], data["note_to_int"], data["seq_length"]

    # Sample next note using temperature-based sampling with top-k filtering
    # Controls randomness in note selection for music generation
    # Parameters: probs (probability distribution), temperature (sampling temperature), top_k (number of top candidates)
    # Returns: Index of sampled note
    def _sample(self, probs: np.ndarray, temperature: float, top_k: int = 10) -> int:
        probs = np.log(probs + 1e-8) / temperature
        probs = np.exp(probs) / np.sum(np.exp(probs))
        
        if top_k > 0:
            top_indices = np.argsort(probs)[-top_k:]
            mask = np.zeros_like(probs)
            mask[top_indices] = 1
            probs = probs * mask
            probs = probs / np.sum(probs)
        
        return np.random.choice(len(probs), p=probs)

    # Generate new music composition using trained LSTM model
    # Creates a sequence of notes by predicting next note iteratively
    # Parameters: num_notes (number of notes to generate), temperature (sampling temperature), instrument (MIDI instrument)
    # Returns: Filename of generated MIDI file
    def generate(self, num_notes: int, temperature: float, instrument: str) -> str:
        model, vocab, note_to_int, seq_length = self._load_model_and_vocab()
        n_vocab = len(vocab)
        int_to_note = {i: n for n, i in note_to_int.items()}

        common_notes = [n for n in vocab if n.isdigit()]
        seed_note = np.random.choice(common_notes) if common_notes else list(vocab)[0]
        seed_idx = note_to_int[seed_note]
        seed_indices = [seed_idx] * seq_length
        pattern = seed_indices[:]
        generated = []

        for step in range(num_notes):
            x = np.reshape(pattern, (1, seq_length, 1)) / float(n_vocab)
            probs = model.predict(x, verbose=0)[0]
            
            dynamic_temp = temperature if step % 5 != 0 else temperature * 1.2
            idx = self._sample(probs, dynamic_temp, top_k=15)
            
            generated_note = int_to_note[idx]
            generated.append(generated_note)
            pattern.append(idx)
            pattern = pattern[1:]

        processed = self._post_process_notes(generated, instrument)
        filename = self._notes_to_midi(processed, instrument)
        self._convert_midi_to_wav(filename)
        return filename

    # Post-process generated notes to add musicality
    # Adds rests for phrasing and repeats themes for structure
    # Parameters: notes (generated note sequence), instrument (instrument name)
    # Returns: Post-processed note sequence
    def _post_process_notes(self, notes: list[str], instrument: str) -> list[str]:
        if len(notes) < 2:
            return notes
        
        processed = []
        phrase_length = 8
        
        for i, note in enumerate(notes):
            if i > 0 and i % phrase_length == 0 and np.random.random() < 0.4:
                processed.append("0")
            
            if i > phrase_length and i % (phrase_length * 2) == 0 and np.random.random() < 0.3:
                phrase_start = max(0, i - phrase_length)
                phrase = processed[phrase_start:i]
                if phrase:
                    processed.extend(phrase)
                    i += len(phrase)
                    continue
            
            processed.append(note)
        
        return processed

    # Convert note sequence to MIDI file with professional features
    # Creates MIDI file with dynamic velocity and duration variations
    # Parameters: notes (list of note strings), instrument (MIDI instrument name)
    # Returns: Filename of generated MIDI file
    def _notes_to_midi(self, notes: list[str], instrument: str) -> str:
        midi = pretty_midi.PrettyMIDI(initial_tempo=90)
        program = INSTRUMENT_MAP.get(instrument, 0)
        inst = pretty_midi.Instrument(program=program, name=instrument)

        offset = 0.0
        velocity_base = 85
        skipped_count = 0
        
        note_counter = Counter(n for n in notes if n not in ["0", "-"])
        avg_velocity = velocity_base

        for i, note_str in enumerate(notes):
            try:
                if note_str == "0":
                    offset += 0.25
                    continue
                elif note_str == "-":
                    offset += 0.25
                    continue
                
                if (i + 1) % 8 == 0:
                    duration = 1.0
                else:
                    duration_options = [0.25, 0.5, 0.75]
                    duration = np.random.choice(duration_options, p=[0.3, 0.5, 0.2])
                
                if i > 0:
                    velocity = int(velocity_base + (i / len(notes)) * 30)
                    velocity += np.random.randint(-10, 15)
                else:
                    velocity = velocity_base
                
                velocity = max(40, min(127, velocity))
                
                if "." in note_str:
                    pitches = []
                    for p in note_str.split("."):
                        try:
                            pitch = int(p) + 60
                            pitch = max(0, min(127, int(pitch)))
                            pitches.append(pitch)
                        except (ValueError, TypeError) as e:
                            logger.debug(f"Invalid pitch component {p}: {e}")
                            skipped_count += 1
                            continue
                    
                    for pitch in pitches:
                        n = pretty_midi.Note(
                            velocity=velocity, 
                            pitch=int(pitch), 
                            start=offset, 
                            end=offset + duration
                        )
                        inst.notes.append(n)
                else:
                    try:
                        pitch = int(note_str) + 60
                        pitch = max(0, min(127, int(pitch)))
                        n = pretty_midi.Note(
                            velocity=velocity, 
                            pitch=int(pitch), 
                            start=offset, 
                            end=offset + duration
                        )
                        inst.notes.append(n)
                    except (ValueError, TypeError) as e:
                        logger.debug(f"Skipping invalid note {note_str}: {e}")
                        skipped_count += 1
                
                offset += duration

            except (ValueError, TypeError) as e:
                logger.debug(f"Skipping invalid note {note_str}: {e}")
                skipped_count += 1
            except Exception as e:
                logger.error(f"Unexpected error with note {note_str}: {e}")
                skipped_count += 1

        midi.instruments.append(inst)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        filename = f"generated_{uuid.uuid4().hex[:8]}.mid"
        midi.write(os.path.join(OUTPUT_DIR, filename))
        logger.info(f"Generated professional MIDI: {filename} ({len(notes)} notes, {skipped_count} skipped)")
        return filename

    # Convert MIDI to WAV for browser playback using FluidSynth
    # Optional conversion - if FluidSynth not installed, MIDI still works
    # Parameters: midi_filename (name of MIDI file to convert)
    def _convert_midi_to_wav(self, midi_filename: str) -> None:
        try:
            midi_path = os.path.join(OUTPUT_DIR, midi_filename)
            wav_filename = midi_filename.replace('.mid', '.wav')
            wav_path = os.path.join(OUTPUT_DIR, wav_filename)
            
            if platform.system() == "Windows":
                cmd = ["fluidsynth", "-ni", "-F", wav_path, "C:\\soundfonts\\default.sf2", midi_path]
            else:
                cmd = ["fluidsynth", "-ni", "-F", wav_path, "/usr/share/sounds/sf2/FluidR3_GM.sf2", midi_path]
            
            result = subprocess.run(cmd, capture_output=True, timeout=10)
            if result.returncode == 0 and os.path.exists(wav_path):
                logger.info(f"Converted MIDI to WAV: {wav_filename}")
            else:
                logger.warning(f"FluidSynth conversion failed: {result.stderr.decode() if result.stderr else 'Unknown error'}")
        except FileNotFoundError:
            logger.warning("FluidSynth not installed. MIDI playback in browser may not work.")
        except Exception as e:
            logger.warning(f"MIDI to WAV conversion error: {e}")
