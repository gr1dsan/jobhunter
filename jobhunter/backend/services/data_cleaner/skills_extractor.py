import json, re
from google import genai

client = genai.Client(api_key="api-key")


def extract_skills(text: str):
    try:
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=(
                "Extract skills from this job description.\n"
                "Return ONLY valid JSON:\n"
                '{"soft_skills": [], "hard_skills": []}\n\n'
                f"Text:\n{text}"
            )
        )

        raw = re.sub(r"```json|```", "", response.text.strip())
        match = re.search(r"\{.*\}", raw, re.DOTALL)

        return json.loads(match.group(0)) if match else {
            "soft_skills": [],
            "hard_skills": []
        }

    except Exception:
        return {"soft_skills": [], "hard_skills": []}