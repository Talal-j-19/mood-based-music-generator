
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
import os
import uuid
from gemini_client import GeminiClient
from lyrica_client import LyricaClient

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
        # Step 2: Generate music file from Lyria
        output_path = f"generated_{uuid.uuid4().hex}.wav"
        result_path = lyrica.generate_music(
            prompt=lyria_prompt,
            negative_prompt="no vocals, no lyrics, instrumental only, no recitation, instrumental only, only describe instruments, mood, and style",
            output_path=output_path
        )
        if not result_path or not os.path.exists(result_path):
            raise HTTPException(
                status_code=500,
                detail=f"Music generation failed. Lyria prompt: {lyria_prompt}"
            )
        with open(result_path, "rb") as f:
            audio_data = f.read()
        return Response(
            content=audio_data,
            media_type="audio/wav"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

