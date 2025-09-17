import google.generativeai as genai
from config import GEMINI_API_KEY


class GeminiClient:
    def __init__(self, api_key=GEMINI_API_KEY):
        genai.configure(api_key=api_key)
        system_instructions = (
            "You are an expert in generating safe, strictly instrumental music prompts "
            "for Google Lyria API, according to the user's mood and style. "
            "Never include lyrics, vocals, recitation, or anything that could be "
            "interpreted as singing or spoken word. "
            "Avoid any language that could trigger content or "
            "recitation filters. "
            "Return ONLY the Lyria prompt, with no extra text."
        )
        self.model = genai.GenerativeModel(
            'gemini-2.5-flash',
            system_instruction=system_instructions
        )

    def generate_prompt(self, user_mood, user_style):
        user_prompt = (
            f"Mood: {user_mood}\n"
            f"Style: {user_style}\n"
            "Generate a Lyrica prompt for this."
        )
        response = self.model.generate_content(user_prompt)
        return response.text.strip()
