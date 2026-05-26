import os
import json
import logging
import uuid
import numpy as np
import pretty_midi
import subprocess
import platform
from dataclasses import dataclass

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

KEYS = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5,
    "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11,
}

SCALES = {
    "cinematic": [0, 2, 3, 5, 7, 8, 10],
    "ambient": [0, 2, 4, 7, 9],
    "classical": [0, 2, 4, 5, 7, 9, 11],
    "jazz": [0, 2, 3, 5, 7, 9, 10],
    "electronic": [0, 2, 3, 5, 7, 10],
}

STYLE_PROFILES = {
    "cinematic": {"tempo": 92, "swing": 0.03, "rest": 0.08, "chord": 0.35, "duration": [0.5, 0.75, 1.0, 1.5]},
    "ambient": {"tempo": 74, "swing": 0.0, "rest": 0.18, "chord": 0.42, "duration": [1.0, 1.5, 2.0]},
    "classical": {"tempo": 104, "swing": 0.01, "rest": 0.06, "chord": 0.22, "duration": [0.25, 0.5, 0.75, 1.0]},
    "jazz": {"tempo": 118, "swing": 0.09, "rest": 0.1, "chord": 0.38, "duration": [0.25, 0.5, 0.75, 1.0]},
    "electronic": {"tempo": 128, "swing": 0.02, "rest": 0.04, "chord": 0.28, "duration": [0.25, 0.5, 1.0]},
}


@dataclass
class MusicalEvent:
    pitches: list[int]
    duration: float
    velocity: int
    gap: float = 0.0


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
        scaled = np.log(probs + 1e-8) / max(temperature, 0.05)
        probs = np.exp(scaled - np.max(scaled))
        probs = probs / np.sum(probs)
        
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
    def generate(
        self,
        num_notes: int,
        temperature: float,
        instrument: str,
        style: str = "cinematic",
        key: str = "C",
        tempo: int = 92,
        density: float = 0.7,
        harmony: bool = True,
    ) -> str:
        model, vocab, note_to_int, seq_length = self._load_model_and_vocab()
        n_vocab = len(vocab)
        int_to_note = {i: n for n, i in note_to_int.items()}

        pattern = self._build_seed(vocab, note_to_int, seq_length)
        generated = []

        for step in range(num_notes):
            x = np.reshape(pattern, (1, seq_length, 1)) / float(n_vocab)
            probs = model.predict(x, verbose=0)[0]
            
            phrase_lift = 1.12 if step % 16 in (0, 1, 14, 15) else 1.0
            idx = self._sample(probs, temperature * phrase_lift, top_k=18)
            
            generated_note = int_to_note[idx]
            generated.append(generated_note)
            pattern.append(idx)
            pattern = pattern[1:]

        processed = self._arrange_events(generated, style, key, density, harmony)
        filename = self._events_to_midi(processed, instrument, style, tempo)
        self._convert_midi_to_wav(filename)
        return filename

    def _build_seed(self, vocab: list[str], note_to_int: dict[str, int], seq_length: int) -> list[int]:
        usable = [note_to_int[n] for n in vocab if self._parse_note_token(n)]
        if not usable:
            usable = list(note_to_int.values())

        if len(usable) >= seq_length:
            start = np.random.randint(0, len(usable) - seq_length + 1)
            return usable[start:start + seq_length]

        seed = list(np.random.choice(usable, size=min(len(usable), seq_length), replace=True))
        while len(seed) < seq_length:
            seed.append(seed[-1])
        return seed

    def _parse_note_token(self, token: str) -> list[int]:
        if token in {"0", "-"}:
            return []

        pitches = []
        for part in str(token).split("."):
            try:
                if part.strip("-").isdigit():
                    raw = int(part)
                    pitch = raw if raw >= 21 else raw + 60
                else:
                    pitch = pretty_midi.note_name_to_number(part)
                pitches.append(max(21, min(108, pitch)))
            except (ValueError, TypeError):
                logger.debug("Skipping invalid token component: %s", part)
        return pitches

    def _snap_to_scale(self, pitch: int, style: str, key: str) -> int:
        root = KEYS.get(key, 0)
        scale = SCALES.get(style, SCALES["cinematic"])
        octave = pitch // 12
        candidates = []
        for octave_shift in (-1, 0, 1):
            candidates.extend((octave + octave_shift) * 12 + root + step for step in scale)
        return max(21, min(108, min(candidates, key=lambda candidate: abs(candidate - pitch))))

    def _make_chord(self, root: int, style: str, key: str) -> list[int]:
        third = 3 if style in {"cinematic", "jazz", "electronic"} else 4
        chord = [root, root + third, root + 7]
        if style == "jazz":
            chord.append(root + 10)
        return sorted({self._snap_to_scale(p, style, key) for p in chord if 21 <= p <= 108})

    def _arrange_events(
        self,
        notes: list[str],
        style: str,
        key: str,
        density: float,
        harmony: bool,
    ) -> list[MusicalEvent]:
        profile = STYLE_PROFILES.get(style, STYLE_PROFILES["cinematic"])
        events = []
        motif = []

        for i, token in enumerate(notes):
            raw_pitches = self._parse_note_token(token)
            if not raw_pitches or np.random.random() > density:
                events.append(MusicalEvent([], 0.25, 0, gap=0.25))
                continue

            primary = self._snap_to_scale(raw_pitches[0], style, key)
            pitches = [primary]

            if harmony and (len(raw_pitches) > 1 or np.random.random() < profile["chord"]):
                pitches = self._make_chord(primary, style, key)
            elif len(raw_pitches) > 1:
                pitches = [self._snap_to_scale(p, style, key) for p in raw_pitches[:4]]

            duration = float(np.random.choice(profile["duration"]))
            if i % 16 == 15:
                duration *= 1.5
            if np.random.random() < profile["rest"]:
                gap = 0.25
            else:
                gap = 0.0

            phrase_accent = 12 if i % 8 in (0, 4) else 0
            velocity = int(np.random.normal(78 + phrase_accent, 9))
            velocity = max(42, min(118, velocity))

            event = MusicalEvent(pitches, duration, velocity, gap)
            events.append(event)

            if len(motif) < 8:
                motif.append(event)
            elif i % 32 in range(8) and motif:
                source = motif[i % len(motif)]
                events[-1] = MusicalEvent(source.pitches[:], source.duration, max(45, source.velocity - 8), source.gap)

        return events

    def _events_to_midi(self, events: list[MusicalEvent], instrument: str, style: str, tempo: int) -> str:
        profile = STYLE_PROFILES.get(style, STYLE_PROFILES["cinematic"])
        midi = pretty_midi.PrettyMIDI(initial_tempo=tempo or profile["tempo"])
        program = INSTRUMENT_MAP.get(instrument, 0)
        inst = pretty_midi.Instrument(program=program, name=instrument)

        offset = 0.0
        skipped_count = 0

        for i, event in enumerate(events):
            if not event.pitches:
                offset += event.duration + event.gap
                continue

            swing = profile["swing"] if i % 2 else 0
            start = max(0, offset + swing + np.random.uniform(-0.015, 0.018))
            end = max(start + 0.1, start + event.duration * np.random.uniform(0.9, 1.04))

            for pitch in event.pitches:
                try:
                    inst.notes.append(pretty_midi.Note(
                        velocity=event.velocity,
                        pitch=int(pitch),
                        start=start,
                        end=end,
                    ))
                except (ValueError, TypeError):
                    skipped_count += 1

            offset += event.duration + event.gap

        midi.instruments.append(inst)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        filename = f"{style}_{instrument}_{uuid.uuid4().hex[:8]}.mid"
        midi.write(os.path.join(OUTPUT_DIR, filename))
        logger.info("Generated advanced MIDI: %s (%s events, %s skipped)", filename, len(events), skipped_count)
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
