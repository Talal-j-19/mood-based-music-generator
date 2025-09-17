import base64
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# -------------------------------
# 1. Load service account from key.json
# -------------------------------
KEY_PATH = "key.json"  # path to your downloaded service account file

SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]
credentials = service_account.Credentials.from_service_account_file(KEY_PATH, scopes=SCOPES)

# Refresh token
credentials.refresh(Request())
token = credentials.token

# -------------------------------
# 2. Config
# -------------------------------
PROJECT_ID = credentials.project_id  # gets project id directly from key.json
LOCATION = "us-central1"
MODEL = "lyria-002"
OUTPUT_FILE = "generated_music.wav"

url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{MODEL}:predict"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
}

# -------------------------------
# 3. Request body
# -------------------------------
body = {
    "instances": [
        {
            "prompt": "Epic orchestral soundtrack with strings, brass, and percussion for a movie trailer.",
            # "negative_prompt": "vocals, electronic synths",
            # "seed": 42
        }
    ],
    "parameters": {
        "sample_count": 1
    }
}

# -------------------------------
# 4. Call API
# -------------------------------
resp = requests.post(url, headers=headers, json=body)

if resp.status_code != 200:
    print("❌ Error:", resp.status_code, resp.text)
    exit()

response_json = resp.json()
print("✅ Response received.")

# -------------------------------
# 5. Extract and save audio
# -------------------------------
try:
    audio_b64 = response_json["predictions"][0]["bytesBase64Encoded"]
    audio_bytes = base64.b64decode(audio_b64)

    with open(OUTPUT_FILE, "wb") as f:
        f.write(audio_bytes)

    print(f"🎶 Music saved as {OUTPUT_FILE}")

except Exception as e:
    print("❌ Failed to extract audio:", e)
    print(response_json)
