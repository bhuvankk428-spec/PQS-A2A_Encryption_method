import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")


class AIModel:

    def __init__(self, name):

        self.name = name

        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            timeout=20.0,
            max_retries=1,
        )

    def chat(self, message):

        try:
            response = self.client.chat.completions.create(
                model=MODEL,

                messages=[
                    {
                        "role": "system",
                        "content": (
                            f"You are {self.name}. "
                            "You are communicating with another AI agent over a quantum-secure encrypted protocol. "
                            "Reply naturally in exactly one short sentence with ur name {self.name}.take a topic and talk about it. "
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

                max_completion_tokens=80,
            )

        except Exception as e:

            print(f"[AI ERROR] {type(e).__name__}: {e}")

            return "Hello."

        print("\n========== OPENAI RESPONSE ==========")
        print(response)
        print("=====================================\n")

        content = response.choices[0].message.content

        if content is None:
            return "Hello."

        return content.strip()