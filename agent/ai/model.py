import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class AIModel:

    def __init__(self, name):

        self.name = name

        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

    def chat(self, message):

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
        )

        print("\n========== OPENAI RESPONSE ==========")
        print(response)
        print("=====================================\n")

        content = response.choices[0].message.content

        if content is None:
            return "Hello."

        return content.strip()