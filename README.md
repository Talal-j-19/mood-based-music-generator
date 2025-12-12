# Mood-Based Music Generator (MusicGen)

Short description
-----------------
This project generates instrumental music tailored to a user's mood and style by combining two AI services:
- Gemini (to produce a music prompt based on mood/style)
- Lyria (to generate audio from the prompt)

It includes a CLI flow, multiple FastAPI endpoints for generation and remixing, and utilities for remixing user-uploaded audio.

Key Features
- Uses Google AI (Gemini and Lyria) via both API keys and service account credentials
- Comfortable CLI + FastAPI server supporting WAV and MP3 responses

Models
------
- Gemini model used in repo: `gemini-2.5-flash` (via google.generativeai wrapper)
- Lyria model used in repo: `lyria-002` (Vertex AI via service account)
Prerequisites
-------------
- A Google Cloud project enabled for the Vertex AI Lyria model, with a service account with the necessary permissions
  - Ensure the service account has `roles/aiplatform.admin` or minimal Vertex AI endpoints access
Running Locally
---------------
- CLI mode (interactive):
  ```powershell
  python main.py
  ```
- FastAPI server for generation (WAV) and remix endpoints:
  ```powershell
  uvicorn api:app --reload --host 0.0.0.0 --port 8002
  # or run `newapi` for the MP3 output variant
  uvicorn newapi:app --reload --host 0.0.0.0 --port 8002
  ```
Files and Temporary Files
-------------------------
- `api.py` and `newapi.py` both write temporary files when generating music (e.g., `generated_<uuid>.wav`), which are returned via the response.
- Remove these generated files periodically in your environment or extend the code to use an object store (Cloud Storage) and automatic cleanup.

------------
- Generate AI music from a mood and style input
- Expose REST endpoints to generate and remix music
- Multiple remix effects (party, slowjam, echo, chipmunk, deepbass)
- Uses Google AI (Gemini and Lyria) via both API keys and service account credentials

Repository structure
--------------------
- `main.py` — CLI example: ask for mood/style and generate music via Gemini->Lyria
- `gemini_client.py` — Wrapper for Gemini API calls to generate Lyria-compatible prompts
- `lyrica_client.py` — Wrapper for Lyria API: handles service account, authorized session, call to the model and audio extraction
- `lyria.py` — Small standalone example of calling the Lyria API directly
- `api.py` — FastAPI implementation for both generation and remixing endpoints (WAV)
- `newapi.py` — Alternative FastAPI endpoint implementation that converts WAV to MP3
- `fastapi_remix_app-1.py` — FastAPI app focusing on remixing user-uploaded audio files
- `config.py` — Loads environment variables (GEMINI_API_KEY and LYRICA_API_KEY if used)
- `test_api.py` — Simple test client script for the `/generate-music` endpoint
- `requirements.txt` — Python package dependencies (see Setup below)
- `key.json` — Example service account JSON (DO NOT commit a real key; see Security below)

Prerequisites
-------------
- Python 3.10+ recommended
- System `ffmpeg` installed and on `PATH` (required for `pydub` and audio conversions)
- A Google Cloud project enabled for the Vertex AI Lyria model, with a service account with the necessary permissions
- A Gemini API key (Gemini requires an API key / library credential)

Security note: Service Account Credentials
----------------------------------------
Do not keep a working `key.json` in your repository. The sample repository here contains a key as an example; ensure that you remove it and use safer mechanisms such as:
- environment variables
- local developer `.env` files that are in `.gitignore`
- cloud provider secret managers (Google Secret Manager, Cloud Run service account) for production

Recommended `.gitignore` lines (add to `.gitignore`):

```
# Python
venv/
__pycache__/
*.pyc

# Local secrets and credentials
key.json
.env
```

Setup — Local Development
-------------------------
1) Clone the repo and create a virtual environment:

```powershell
python -m venv venv
venv\Scripts\activate
```

2) Install dependencies:

```powershell
pip install -r requirements.txt
# The repo includes extra dependencies used by the code that may not be listed in `requirements.txt`:
pip install pydub google-auth imageio-ffmpeg google-auth-oauthlib python-dotenv

Optional: If you want to freeze these into `requirements.txt` after creating your environment:

```powershell
pip freeze > requirements.txt
```
```

3) Install `ffmpeg` on your OS and ensure it is on the `PATH`.

4) Configure credentials and env variables:
- Create a `.env` file or export env variables for `GEMINI_API_KEY`.
- For Lyria (Vertex AI) set `GOOGLE_APPLICATION_CREDENTIALS` to the path of your service account JSON file, or copy the service account JSON to `key.json` and use it locally (NOT recommended for production).

Example `.env` (add to `.gitignore`):

```
GEMINI_API_KEY=your_gemini_api_key_here
# LYRICA_API_KEY is optional and not used in current code; service account key is used instead
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
```

5) Verify environment:

```powershell
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('GEMINI_API_KEY' in os.environ)
"
```

Running Locally
---------------
- CLI mode (interactive):
  ```powershell
  python main.py
  ```

- FastAPI server for generation (WAV) and remix endpoints:
  ```powershell
  uvicorn api:app --reload --host 0.0.0.0 --port 8002
  # or run `newapi` for the MP3 output variant
  uvicorn newapi:app --reload --host 0.0.0.0 --port 8002
  ```

- Remix-only endpoint server:
  ```powershell
  uvicorn fastapi_remix_app-1:app --reload --host 0.0.0.0 --port 8003
  ```

Testing endpoints
-----------------
- Local test using `test_api.py` (update `API_URL` to your local host + port):

```powershell
python test_api.py
```

- CURL example for the generation endpoint (MP3 conversion in `newapi`):

```bash
curl -X POST "http://localhost:8002/generate-music" -H "Content-Type: application/json" -d '{"mood": "happy", "style": "upbeat electronic"}' --output generated_music.mp3
```

- CURL example for remix endpoint in `fastapi_remix_app-1.py`:

```bash
curl -F "song=@./path/to/myfile.mp3" -F "remix_type=party" http://localhost:8003/remix --output remix_party.wav
```

Detailed Deployment Guide
-------------------------
This project can be deployed in several ways. The following list is a pragmatic guide for a secure production deployment.

1) PM2 (simple process manager - use venv python interpreter)

Use PM2 to run the application using the project's virtual environment Python interpreter so the correct environment is used without extra configuration files.

Prereqs:
- Node.js and npm installed
- Install pm2: `npm install -g pm2`
- Create and populate a Python virtual environment in the repo root (ex: `venv`)

Linux/macOS example (single command, inherits current env):

```bash
# set necessary env vars before starting PM2 in the same shell (or use your system's env manager)
export GEMINI_API_KEY="your_gemini_key_here"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"

# Start using venv python interpreter; `--` separates pm2 args from script args
pm2 start ./venv/bin/python --name musicgen -- -m uvicorn newapi:app --host 0.0.0.0 --port 8080

# Check status and logs
pm2 status
pm2 logs musicgen

# Make PM2 persistent across reboots
pm2 startup
pm2 save
```

Windows PowerShell example (use the venv interpreter path):

```powershell
# Set environment variables for the current session
$env:GEMINI_API_KEY="your_gemini_key_here"
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\key.json"

# Start the process using the venv python.exe
pm2 start .\venv\Scripts\python.exe --name musicgen -- -m uvicorn newapi:app --host 0.0.0.0 --port 8080

pm2 status
pm2 logs musicgen

# On Windows, to run PM2 as a Windows service, consider using `pm2-windows-service`:
# npm i -g pm2-windows-service
# pm2-service-install -n musicgen
```

2) Google Cloud Run (recommended for GCP):
- Build and push container image to Google Container Registry or Artifact Registry.
- Use Cloud Run to deploy the container.
- Use Workload Identity or Cloud Run's service account binding to avoid embedding `key.json`; if you must, store the service account JSON in Secret Manager and mount it into the container.

3) Google Compute Engine / Kubernetes
- Similar steps; use workload identity or Kubernetes secrets for key management.

4) Systemd or VM
- Install system `ffmpeg` and Python runtime; run `uvicorn` as a systemd service.

Environment Variables & Secrets
-------------------------------
- `GEMINI_API_KEY` — Gemini API key for prompt generation
- `GOOGLE_APPLICATION_CREDENTIALS` — Path to a service account JSON file for Vertex AI (Lyria)
- Avoid hardcoding `key.json` in your repo. Instead use:
  - `.env` files (local dev) and gitignore
  - Secret Manager in cloud
  - Environment variables in your deployment environment

Optional: Add GOOGLE_API_* keys or custom settings as you evolve the deployment.

Troubleshooting
---------------
- FFmpeg not found: confirm `ffmpeg` is installed and `which('ffmpeg')` resolves
- 401/403 from Lyria: verify the service account has necessary IAM roles (e.g., Vertex AI access) and that the `GOOGLE_APPLICATION_CREDENTIALS` variable points to a valid JSON file
- Gemini errors: check that `GEMINI_API_KEY` is set and valid
- Lyria (audio decode/export) errors: check the model name and response payload for `bytesBase64Encoded` existence

Extending the project
----------------------
- Add authentication to the FastAPI endpoints
- Add caching or queueing for long-running generation tasks
- Add support for more Lyria parameters (e.g., seeds, instrument mix, tempo)
- Add more remix styles and better audio post-processing

Contributing
------------
If you'd like to contribute:
- Fork the repo and create a PR
- Keep `key.json` out of commits
- Add tests for new endpoints and behavior

License
-------
This project is provided as-is for demonstration and development. Add a license of your choosing.

Acknowledgements
----------------
- Built using Google Gemini and Lyria AI models
- Uses `pydub` for audio processing and `ffmpeg` for conversion

Contact
-------
For questions or help, open an Issue in this repository.
