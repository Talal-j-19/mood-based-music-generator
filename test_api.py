import requests

API_URL = "http://147.182.254.9:8002/generate-music"

payload = {
    "mood": "Energetic",
    "style": "Upbeat"
}

response = requests.post(API_URL, json=payload)

if response.status_code == 200:
    with open("test.wav", "wb") as f:
        f.write(response.content)
    print("Music file saved as test.wav")
else:
    print(f"Error: {response.status_code}\n{response.text}")
