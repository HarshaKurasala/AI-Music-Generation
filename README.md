# AI Music Generation

Generate original MIDI music with an LSTM neural network. This full-stack app lets you upload MIDI files, train a model on them, generate new music, and store project metadata plus trained model files in MongoDB Atlas.

## Tech Stack

**Frontend**
- React + Vite
- Tailwind CSS
- Axios
- React Router
- Recharts

**Backend**
- FastAPI
- TensorFlow/Keras
- music21
- PrettyMIDI
- MongoDB Atlas with GridFS

## Project Structure

```txt
Music Generation with AI/
|-- frontend/
|   |-- src/
|   |   |-- components/
|   |   |-- pages/
|   |   `-- services/
|   `-- package.json
|
`-- backend/
    |-- app.py
    |-- database.py
    |-- requirements.txt
    |-- dataset/
    |-- generated_music/
    |-- models/
    |-- routes/
    |-- services/
    `-- utils/
```

## Setup

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload
```

If you use the project virtual environment on Windows:

```bash
cd backend
..\.venv\Scripts\python.exe -m uvicorn app:app --reload
```

Backend URL:

```txt
http://127.0.0.1:8000
```

The backend root page shows the backend status and available API routes:

```txt
http://127.0.0.1:8000/
```

Health check:

```txt
http://127.0.0.1:8000/health
```

FastAPI docs are intentionally disabled:

```txt
/docs         -> 404
/redoc        -> 404
/openapi.json -> 404
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

On Windows PowerShell, if `npm.ps1` is blocked, use:

```bash
npm.cmd run dev
```

Frontend URL:

```txt
http://127.0.0.1:5173
```

## MongoDB Setup

Create `backend/.env`:

```env
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster-url>/?appName=<cluster-name>
MONGODB_DB=music_generation_ai
UPLOAD_DIR=dataset
OUTPUT_DIR=generated_music
```

In MongoDB Atlas:

1. Create a cluster.
2. Create a database user.
3. Add your current IP address in Network Access.
4. Copy the Python driver connection string.
5. Put it in `backend/.env` as `MONGODB_URI`.

The app uses MongoDB for:

- Uploaded MIDI metadata
- Generated music metadata
- Trained model metadata
- Trained `.keras` model and `vocab.json` files through GridFS

MongoDB collections used:

```txt
midi_files
generated_files
model_metadata
model_files.files
model_files.chunks
```

## How To Use

### 1. Upload MIDI Files

Open the frontend upload page and upload `.mid` or `.midi` files. Files are saved locally in `backend/dataset/` so the training pipeline can parse them, and metadata is saved in MongoDB when available.

### 2. Train The Model

Open the training page and start training. The backend trains an LSTM model and saves:

```txt
backend/models/music_model.keras
backend/models/vocab.json
backend/models/model_metadata.json
```

After training finishes, the backend also tries to upload the trained model and vocabulary to MongoDB GridFS.

### 3. Sync Existing Trained Model To MongoDB

If you trained before MongoDB was connected, run:

```txt
POST /api/sync-trained-model
```

Example with PowerShell:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/sync-trained-model
```

Successful response includes:

```txt
stored_in_mongodb: true
model_file_id: ...
vocab_file_id: ...
metadata_id: ...
```

### 4. Generate Music

Open the generate page and choose:

- Style
- Key
- Tempo
- Instrument
- Creativity/temperature
- Density
- Harmony on/off
- Number of notes

Generated files are saved in:

```txt
backend/generated_music/
```

Generated file metadata is saved in MongoDB when available.

## API Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/` | Backend status and route list |
| GET | `/health` | Backend health check |
| POST | `/api/upload-midi` | Upload MIDI files |
| GET | `/api/dataset-info` | List uploaded MIDI files |
| POST | `/api/delete-dataset-files` | Delete selected dataset files |
| POST | `/api/train-model` | Start model training |
| GET | `/api/training-status` | Get training progress |
| POST | `/api/reset-training` | Reset stuck training state |
| GET | `/api/trained-model-info` | Get saved model metadata |
| POST | `/api/sync-trained-model` | Upload saved trained model to MongoDB GridFS |
| POST | `/api/generate-music` | Generate a new MIDI file |
| GET | `/api/generated-files` | List generated MIDI files |
| GET | `/api/download/{filename}` | Download a generated MIDI file |
| POST | `/api/delete-generated-files` | Delete selected generated files |

## Notes About Storage

The app still keeps MIDI files and trained models on disk because TensorFlow, music21, and PrettyMIDI work best with normal files. MongoDB stores metadata and GridFS copies of trained model artifacts.

For large model files, MongoDB GridFS is required because normal MongoDB documents have a 16 MB document limit.

## Troubleshooting

**Backend shows `{"detail":"Not Found"}`**

Use the root URL:

```txt
http://127.0.0.1:8000/
```

`/docs` is disabled intentionally.

**MongoDB sync says `stored_in_mongodb: false`**

Check MongoDB Atlas Network Access and add your current IP address. Then retry:

```txt
POST /api/sync-trained-model
```

**PowerShell blocks npm**

Use:

```bash
npm.cmd run dev
```

**Model not found**

Train the model first from the frontend training page.

**No MIDI files found**

Upload `.mid` or `.midi` files from the frontend upload page.

**MIDI playback does not work in browser**

Download the generated MIDI and open it in a MIDI player or DAW. WAV conversion needs FluidSynth installed separately.

## Training Tips

- Use MIDI files with a clear, consistent style.
- Start with 5-10 files.
- Use 50 epochs for a first run.
- Use sequence length 50 for most datasets.
- Loss should generally decrease during training.

## License

Educational and personal use.
