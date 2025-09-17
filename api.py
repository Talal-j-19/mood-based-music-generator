gemini = GeminiClient()
lyrica = LyricaClient()
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
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
        # Step 2: Generate music file from Lyria
        output_path = f"generated_{uuid.uuid4().hex}.wav"
        result_path = lyrica.generate_music(
            prompt=lyria_prompt,
            negative_prompt="no vocals, no lyrics, instrumental only",
            output_path=output_path
        )
        if not result_path or not os.path.exists(result_path):
            raise HTTPException(
                status_code=500,
                detail="Music generation failed."
            )
        return FileResponse(
            result_path,
            media_type="audio/wav",
            filename=os.path.basename(result_path)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
