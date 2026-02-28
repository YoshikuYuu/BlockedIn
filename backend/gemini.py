from dotenv import load_dotenv
import json
from google import genai
from typing import List

# The client gets the API key from the environment variable `GEMINI_API_KEY`.

class ExampleGenerator:
    def __init__(self):
        load_dotenv()
        try:
            self.client = genai.Client()
        except Exception as e:
            print("Error initializing Gemini client:", e)
            raise
    
    def generate_examples(self, category_description: str) -> List[str]:
        """
        Generates examples based on the given prompt using Gemini.
        """
        if not category_description.strip():
            raise ValueError("Topic must be a non-empty string.")

        min_cases, max_cases = 3, 6
        prompt = (
            "You are helping define the boundary of a semantic category that will be used to describe websites.\n"
            "Category description:\n"
            f"\"\"\"{category_description.strip()}\"\"\"\n"
            f"Task: Generate {min_cases} to {max_cases} DISTINCT borderline cases. Each case should:\n"
            "Be ambiguous or edge-case\n"
            "- Possibly belong to the category, but not clearly\n"
            "- Be realistic (e.g. webpage topics, titles, short descriptions)\n"
            "- Not be obvious examples or clear negatives\n"
            "Return ONLY a JSON array of short strings. No explanation."
        )

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": min_cases,
                    "maxItems": max_cases,
                },
            },
        )

        try:
            data = json.loads(response.text or "[]")
        except json.JSONDecodeError as e:
            raise ValueError("Gemini returned non-JSON output.") from e

        if not isinstance(data, list):
            raise ValueError("Gemini returned JSON that is not a list.")

        normalized = [item.strip() for item in data if isinstance(item, str) and item.strip()]
        return normalized
