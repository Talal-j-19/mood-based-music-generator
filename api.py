from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import uuid
from gemini_client import GeminiClient
from lyrica_client import LyricaClient
from pydub import AudioSegment  # ✅ Added for audio conversion

app = FastAPI()

gemini = GeminiClient()
lyrica = LyricaClient()


class MusicRequest(BaseModel):
    mood: str
    style: str


@app.post("/generate-music")
def generate_music(request: MusicRequest):
    try:
        # Step 1: Generate Lyria prompt from Gemini
        lyria_prompt = gemini.generate_prompt(request.mood, request.style)
        print(f"[DEBUG] Lyria prompt: {lyria_prompt}")

        # Step 2: Generate music file from Lyria (WAV)
        wav_output_path = f"generated_{uuid.uuid4().hex}.wav"
        result_path = lyrica.generate_music(
            prompt=lyria_prompt,
            negative_prompt=(
                "no vocals, no lyrics, instrumental only, no recitation, "
                "instrumental only, only describe instruments, mood, and style"
            ),
            output_path=wav_output_path
        )

        if not result_path or not os.path.exists(result_path):
            raise HTTPException(
                status_code=500,
                detail=f"Music generation failed. Lyria prompt: {lyria_prompt}"
            )

        # Step 3: Convert WAV to MP3
        mp3_output_path = result_path.replace(".wav", ".mp3")
        audio = AudioSegment.from_wav(result_path)
        audio.export(mp3_output_path, format="mp3")

        # Optional: Delete the original .wav file to save space
        os.remove(result_path)

        # Step 4: Return MP3 as response
        return FileResponse(
            mp3_output_path,
            media_type="audio/mpeg",
            filename=os.path.basename(mp3_output_path)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
