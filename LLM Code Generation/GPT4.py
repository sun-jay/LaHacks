import os
from openai import OpenAI


class GPT4:
    def __init__(self):
        self.client = OpenAI(api_key = os.environ.get("OPENAI_API_KEY"))