import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


def _get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set.")
    return Groq(api_key=api_key)


class ContentBrain:
    def get_trending_topic(self):
        """
        In a full build, this would scrape Google Trends or Twitter.
        For now, we ask the model to pick a viral niche topic.
        """
        prompt = (
            "Give me 1 specific, viral, and engaging topic for a Short "
            "Documentary. It should be a 'Engaging Did you know' fact or a "
            "'Fun/intriguing Engaging News'. return ONLY the topic name."
        )
        client = _get_client()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        topic = response.choices[0].message.content.strip()
        print(f"🎯 Selected Topic: {topic}")
        return topic

    def generate_script(self, topic):
        """
        Generates a structured JSON script with visual cues.
        """
        print(f"📝 Writing script for: {topic}...")
        prompt = f"""
You are the lead scriptwriter for a high-retention "Edutainment" YouTube Shorts channel.
Topic: {topic}

### GOAL:
Create a script where every sentence has a "Visual Switch".
To keep retention high, we need TWO different stock videos for every single scene.

### 1. SCRIPT REQUIREMENTS (The Voiceover):
- **Perspective:** Strictly **3rd Person** ("Scientists found...", "The ocean hides...").
- **Tone:** Engaging, fast-paced, logical. No fluff.
- **Structure:** 8-9 Scenes total.
- **Flow:** Hook -> Context -> Mechanism (How it works) -> Twist -> Outro.

### 2. VISUAL REQUIREMENTS (Dual Visuals):
- For EVERY scene, provide TWO distinct search terms:
  - **visual_1:** Matches the *start* of the sentence.
  - **visual_2:** Matches the *end* of the sentence or provides a reaction/context.
- **Strictly Literal:** If the text is "The economy crashed," do NOT search "sad man". Search "Stock market red chart".

### OUTPUT FORMAT (Strict JSON):
[
    {{
        "id": 1,
        "text": "In 1995, fourteen wolves were released into Yellowstone Park, and they changed the rivers.",
        "visual_1": "wolves running snow aerial",
        "visual_2": "river flowing forest drone",
        "mood": "intriguing"
    }},
    {{
        "id": 2,
        "text": "It sounds impossible, but the biology is actually simple math.",
        "visual_1": "person shocked looking at camera",
        "visual_2": "blackboard math equations chalk",
        "mood": "educational"
    }}
]
### IMPORTANT
Return ONLY valid JSON.

Do NOT write any explanation.

Do NOT use markdown.

Do NOT wrap the JSON inside ```json.

Return ONLY the JSON array.
"""

        client = _get_client()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        clean_text = (
            response.choices[0].message.content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        try:
            script = json.loads(clean_text)
        except json.JSONDecodeError as e:
            print("⚠️ JSON parse edilemedi, model çıktısı:")
            print(clean_text)
            raise e

        return script


# --- TESTING THE MODULE ---
if __name__ == "__main__":
    brain = ContentBrain()
    topic = brain.get_trending_topic()
    script = brain.generate_script(topic)

    # Save to file to verify
    with open("script.json", "w") as f:
        json.dump(script, f, indent=4)
        print("✅ Script saved to script.json")
