from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import FileResponse, JSONResponse
from pydub import AudioSegment
from pydub.utils import mediainfo
from pydub.utils import which
import tempfile
import os
import traceback
import time

# -------------------------------
# 🎧 Ensure FFmpeg is available
# -------------------------------
AudioSegment.converter = which("ffmpeg")
AudioSegment.ffprobe = which("ffprobe")

if not AudioSegment.converter:
    raise RuntimeError("❌ FFmpeg not found! Please install and add it to PATH.")

app = FastAPI(
    title="🎧 Audio Remix API",
    description="Upload a song and apply remix styles (party, slowjam, echo, chipmunk, deepbass)",
    version="1.0.0"
)


# -------------------------------
# 🪩 Debug Helper
# -------------------------------
def debug_log(message: str):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG {timestamp}] {message}")


# -------------------------------
# 🎵 Remix Function
# -------------------------------
def remix_audio_file(audio_path: str, remix_type: str = "party"):
    debug_log(f"Starting remix process: path={audio_path}, type={remix_type}")

    # Auto-detect format using ffprobe
    info = mediainfo(audio_path)
    fmt = info.get("format_name", "wav").split(",")[0]  # e.g. 'mp3', 'wav', etc.
    debug_log(f"Detected format: {fmt}")

    # Load the file safely
    song = AudioSegment.from_file(audio_path, format=fmt)
    debug_log(f"Loaded audio file ({fmt}) duration={len(song) / 1000:.2f}s")

    # --- Remix logic ---
    if remix_type == "party":
        remixed = song.speedup(playback_speed=1.25).fade_in(2000).fade_out(2000)
    elif remix_type == "slowjam":
    # Reduce playback speed by lowering the frame rate
        slowed = song._spawn(song.raw_data, overrides={
            "frame_rate": int(song.frame_rate * 0.85)
        })
        remixed = slowed.set_frame_rate(44100).low_pass_filter(3000)
    elif remix_type == "echo":
        echo = song - 6
        remixed = song.overlay(echo, position=200)
    elif remix_type == "chipmunk":
        remixed = song._spawn(
            song.raw_data,
            overrides={"frame_rate": int(song.frame_rate * 1.4)}
        ).set_frame_rate(44100)
    elif remix_type == "deepbass":
        remixed = song.low_pass_filter(150).apply_gain(6)
    else:
        debug_log(f"⚠️ Unknown remix type '{remix_type}', returning original file.")
        remixed = song

    # Export remixed audio
    output_path = tempfile.mktemp(suffix=f"_{remix_type}.wav")
    remixed.export(output_path, format="wav")
    debug_log(f"✅ Remix complete. Output saved at {output_path}")
    return output_path


# -------------------------------
# 🚀 Remix Endpoint
# -------------------------------
@app.post("/remix")
async def remix_audio(
    request: Request,
    song: UploadFile = File(...),
    remix_type: str = Form("party")
):
    try:
        debug_log(f"🎧 Received request from {request.client.host}")
        debug_log(f"Uploaded file: {song.filename} ({song.content_type}), remix type={remix_type}")

        # Save uploaded file
        temp_input = tempfile.mktemp(suffix=os.path.splitext(song.filename)[-1])
        with open(temp_input, "wb") as f:
            content = await song.read()
            f.write(content)
        debug_log(f"Saved temporary input file: {temp_input} ({len(content)} bytes)")

        # Process remix
        output_path = remix_audio_file(temp_input, remix_type)

        # Return remixed file
        debug_log(f"Sending response: remix_{remix_type}.wav")
        return FileResponse(
            path=output_path,
            media_type="audio/wav",
            filename=f"remix_{remix_type}.wav",
            headers={"X-Remix-Status": f"Remix type: {remix_type}"}
        )
    except Exception as e:
        error_trace = traceback.format_exc()
        debug_log(f"❌ Error processing remix: {e}\n{error_trace}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


# -------------------------------
# 🧩 Root Route
# -------------------------------
@app.get("/")
def home():
    debug_log("GET / — Health check called")
    return {
        "message": "🎶 Welcome to the Audio Remix API!",
        "usage": "POST /remix with form-data: song=<file>, remix_type=<party|slowjam|echo|chipmunk|deepbass>"
    }
