import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


_FALLBACK = "Secure and quantum-resistant, I am listening."


class AIModel:

    def __init__(self, name):

        self.name = name

        api_key = os.getenv("OPENAI_API_KEY")

        self.client = None
        if api_key:
            self.client = OpenAI(
                api_key=api_key
            )

    def chat(self, message):

        if self.client is None:
            print(f"[AI:{self.name}] No API key - using offline fallback reply")
            return _FALLBACK

        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-nano",

                messages=[
                    {
                        "role": "system",
                        "content": (
                            f"You are {self.name}. "
                            "You are communicating with another AI agent over a quantum-secure encrypted protocol. "
                            "Reply naturally in exactly one short sentence. "
                            "Do not use markdown. "
                            "Do not use bullet points. "
                            "Do not leave the response empty."
                        ),
                    },
                    {
                        "role": "user",
                        "content": message,
                    },
                ],

                max_tokens=80,
                timeout=20.0,
            )

            content = response.choices[0].message.content

            if content is None or not content.strip():
                return _FALLBACK

            return content.strip()

        except Exception as exc:
            print(f"[AI:{self.name}] Error ({exc}) - using fallback reply")
            return _FALLBACK