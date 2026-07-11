import json

from google import genai
from google.genai import types

from app.core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)



class GeminiDiseaseService:

    @staticmethod
    def detect_disease(
        image_bytes: bytes,
        mime_type: str,
        crop_name: str,
        growth_stage: str |None,
        soil_type: str,
        irrigation: str,
        language: str,
    ):

        prompt = f"""
You are an expert agricultural plant pathologist.

Analyze the uploaded crop image carefully.

Crop:
{crop_name}

Growth Stage:
{growth_stage}

Soil Type:
{soil_type}

Irrigation:
{irrigation}

Respond ONLY with valid JSON.

All text fields must be written in {language}.

Return EXACTLY this JSON:

{{
  "disease_name": "",
  "confidence": 0,
  "severity": "Low",
  "recommendation": [
    ""
  ],
  "consult_expert": false
}}

Rules:

1. confidence must be between 0 and 100.

2. severity must be one of:
- Low
- Medium
- High

3. If the crop appears healthy:
   disease_name = "Healthy"

4. recommendation must contain 4-8 short bullet points.

Recommendations should include:
- probable symptoms
- treatment
- prevention
- irrigation advice
- fertilizer advice

5. If confidence < 80:
consult_expert = true

Otherwise:
consult_expert = false

6. Never use Markdown.

7. Never explain outside JSON.

8. If uncertain, reduce confidence instead of guessing.
"""

        response = client.models.generate_content(
            model="models/gemini-3.1-flash-lite",
            contents=[
                prompt,
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime_type,
                ),
            ],
        )

        text = response.text.strip()

        if text.startswith("```json"):
            text = text.replace("```json", "").replace("```", "").strip()

        elif text.startswith("```"):
            text = text.replace("```", "").strip()

        return json.loads(text)