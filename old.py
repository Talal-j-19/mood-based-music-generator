import base64
import requests
import os
from google.oauth2 import service_account
from google.auth.transport.requests import Request

KEY_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "key.json")
SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]


class LyricaClient:
    def __init__(
        self,
        key_path=KEY_PATH,
        location="us-central1",
        model="lyria-002"
    ):
        self.key_path = key_path
        self.location = location
        self.model = model
        self.credentials = service_account.Credentials.from_service_account_file(
            self.key_path,
            scopes=SCOPES
        )
        self.credentials.refresh(Request())
        self.token = self.credentials.token
        self.project_id = self.credentials.project_id

    def generate_music(
        self,
        prompt,
        negative_prompt=None,
        duration_seconds=None,
        sample_count=1,
        output_path="generated_music.wav"
    ):
        url = (
            f"https://{self.location}-aiplatform.googleapis.com/v1/projects/"
            f"{self.project_id}/locations/{self.location}/"
            "publishers/google/models/"
            f"{self.model}:predict"
        )
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        instance = {"prompt": prompt}
        if negative_prompt:
            instance["negative_prompt"] = negative_prompt
        if duration_seconds:
            instance["duration_seconds"] = duration_seconds
        body = {
            "instances": [instance],
            "parameters": {"sample_count": sample_count}
        }
        resp = requests.post(url, headers=headers, json=body)
        if resp.status_code != 200:
            print("❌ Error:", resp.status_code, resp.text)
            return None
        response_json = resp.json()
        try:
            audio_b64 = response_json["predictions"][0]["bytesBase64Encoded"]
            audio_bytes = base64.b64decode(audio_b64)
            with open(output_path, "wb") as f:
                f.write(audio_bytes)
            print(f"🎶 Music saved as {output_path}")
            return output_path
        except Exception as e:
            print("❌ Failed to extract audio:", e)
            print(response_json)
            return None
