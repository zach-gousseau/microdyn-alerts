from pydantic import BaseModel
from typing import Optional
import dotenv
import json

from openai import OpenAI

dotenv.load_dotenv()

class Response(BaseModel):
    is_update: bool
    summary: Optional[str] = None

class ClassifierAndSummarizer:
    def __init__(self):
        self.client = OpenAI()

    def classify_and_summarize(self, text):
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": """Your job is to determine whether the input text contains a regulatory update, and if so, give a one-sentence summary of the update. Format your response using the JSON format: {{"is_update": true, "summary": <summary> if is_update is true, else None }}}. """},
                {"role": "user", "content": text}
            ]
        )
        return Response.model_validate_json(completion.choices[0].message.content)