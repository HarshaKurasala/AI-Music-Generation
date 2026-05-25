# 🎵 AI Music Generation

Generate original MIDI music compositions using deep learning! This full-stack web application uses LSTM neural networks to learn from your MIDI dataset and create new, unique musical pieces.

## 🎯 What This Does

Upload your favorite MIDI files → Train an AI model on them → Generate brand new music in the same style. It's like teaching a musician to compose in your favorite genre!

## 🛠️ Tech Stack

**Frontend:**
- React + Vite (fast, modern UI)
- Tailwind CSS (beautiful styling)
- Axios (API communication)
- React Router (page navigation)
- Recharts (training progress visualization)

**Backend:**
- FastAPI (high-performance Python API)
- TensorFlow/Keras (deep learning)
- music21 (MIDI parsing)
- PrettyMIDI (MIDI generation)

## 📁 Project Structure

```
music-generation-ai/
├── frontend/                    # React web interface
│   ├── src/
│   │   ├── components/         # UI components (upload, player, progress)
│   │   ├── pages/              # App pages (home, upload, train, generate, results)
│   │   └── services/           # API communication (api.js)
│   └── package.json
│
└── backend/                     # Python FastAPI server
    ├── routes/                 # API endpoints
    │   ├── midi_routes.py      # Upload & dataset management
    │   ├── train_routes.py     # Model training
    │   └── generate_routes.py  # Music generation
    ├── models/                 # Neural network & saved models
    │   └── lstm_model.py       # LSTM architecture
    ├── services/               # Business logic
    │   ├── training_service.py # Training pipeline
    │   └── generation_service.py # Music generation
    ├── utils/                  # Helper functions
    │   └── midi_utils.py       # MIDI parsing & sequence building
    ├── dataset/                # Your uploaded MIDI files
    ├── generated_music/        # Generated MIDI outputs
    ├── app.py                  # Main FastAPI app
    └── requirements.txt        # Python dependencies
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- Git

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload
```

The API will be available at `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5173`

## 📖 How to Use

### 1. **Upload MIDI Files** (`/upload`)
- Drag & drop or click to select `.mid` or `.midi` files
- Upload your training dataset (5-10 files recommended for good results)
- The app will extract all notes from your files

### 2. **Train the Model** (`/train`)
- Configure training parameters:
  - **Epochs**: How many times to train (50 is a good start)
  - **Batch Size**: How many sequences to process at once (64 is standard)
  - **Sequence Length**: How many notes the model looks at to predict the next one (50 is good)
- Click "Start Training"
- Watch real-time progress: loss decreasing = model improving
- Training runs in the background; you can close the page

### 3. **Generate Music** (`/generate`)
- Set generation parameters:
  - **Number of Notes**: How long the composition should be (100-200 is nice)
  - **Temperature**: Controls creativity
    - Low (0.5): Predictable, structured music
    - Medium (1.0): Balanced
    - High (1.5+): Creative, experimental
  - **Instrument**: Choose from piano, guitar, violin, flute, trumpet, organ
- Click "Generate"
- Your new composition will be created!

### 4. **Listen & Download** (`/results`)
- Play generated MIDI files in the browser
- Download files to use in your DAW (Ableton, FL Studio, etc.)
- Delete files you don't want to keep

## 🧠 How It Works

### The AI Model
- **LSTM (Long Short-Term Memory)**: A type of neural network that's great at learning sequences
- **3-Layer Architecture**: 
  - Layer 1: Learns basic note transitions
  - Layer 2: Learns melodic phrases
  - Layer 3: Learns overall composition structure
- **Dropout & Batch Normalization**: Prevents overfitting and stabilizes training

### The Process
1. **Extract**: Parse MIDI files to get individual notes
2. **Sequence**: Create sliding windows of notes (e.g., "predict note 51 from notes 1-50")
3. **Train**: Model learns patterns from your data
4. **Generate**: Model predicts next note based on previous notes, creating new sequences
5. **Post-Process**: Add rests, vary velocity, create musical phrasing

## 🎛️ API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Check if API is running |
| POST | `/api/upload-midi` | Upload MIDI files |
| GET | `/api/dataset-info` | List uploaded files |
| POST | `/api/train-model` | Start training |
| GET | `/api/training-status` | Get training progress |
| POST | `/api/generate-music` | Generate new music |
| GET | `/api/generated-files` | List generated files |
| GET | `/api/download/{filename}` | Download MIDI file |
| POST | `/api/delete-generated-files` | Delete files |

## 💡 Tips for Best Results

- **Dataset Quality**: Use MIDI files with clear, consistent musical style
- **Dataset Size**: 5-10 files minimum; 20+ files for better variety
- **Training Time**: 50-100 epochs usually works well (takes 5-15 minutes)
- **Temperature**: Start at 1.0, adjust based on results
- **Sequence Length**: 50 is good for most music; lower for simpler patterns
- **Post-Processing**: Generated music may need cleanup in a DAW

## 🔧 Troubleshooting

**"No MIDI files found"**
- Make sure you uploaded files to `/upload` first
- Check file extensions are `.mid` or `.midi`

**"Model not found"**
- Train the model first on `/train`
- Wait for training to complete

**"Not enough training sequences"**
- Upload more MIDI files
- Reduce sequence length
- Ensure MIDI files have enough notes

**MIDI playback not working in browser**
- Download the file and open in a MIDI player (VLC, GarageBand, MuseScore)
- Install FluidSynth for WAV conversion support

## 📊 Training Metrics

- **Loss**: How wrong the model is (lower is better)
- **Accuracy**: How often the model predicts correctly
- Watch for loss decreasing over epochs = model learning

## 🎼 Generated Music Quality

The quality depends on:
- Your training data (garbage in = garbage out)
- Training duration (more epochs = better learning)
- Model parameters (sequence length, batch size)
- Temperature setting (affects creativity vs. coherence)

## 🚀 Future Improvements

- Multi-instrument support
- Real-time MIDI playback in browser
- Model comparison and versioning
- Advanced post-processing
- Export to MusicXML
- Web-based MIDI editor

## 📝 License

This project is open source and available for educational and personal use.

## 🤝 Contributing

Found a bug or have an idea? Feel free to open an issue or submit a pull request!

---

**Happy composing! 🎵**
