from gemini_client import GeminiClient
from lyrica_client import LyricaClient


def main():
    print("Welcome to Mood-Based Music Generator!")
    user_mood = input("Enter your current mood: ")
    user_style = input("What style/genre of music do you want?: ")

    gemini = GeminiClient()
    lyrica = LyricaClient()

    print("Generating music prompt using Gemini...")
    lyrica_prompt = gemini.generate_prompt(user_mood, user_style)
    print(f"Prompt for Lyrica: {lyrica_prompt}")

    print("Generating music using Lyrica...")
    music_url = lyrica.generate_music(lyrica_prompt)
    if music_url:
        print(f"Your music is ready! Listen here: {music_url}")
    else:
        print("Failed to generate music.")

if __name__ == "__main__":
    main()
