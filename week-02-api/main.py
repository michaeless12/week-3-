import os
import sys
import json
import requests

API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "openai/gpt-oss-20b"


def load_api_key():
    try:
        from google.colab import userdata
        return userdata.get("GROQ_API_KEY")
    except Exception:
        pass
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    return os.getenv("GROQ_API_KEY")


def ask(prompt, label):
    value = ""
    while not value:
        value = input(prompt).strip()
        if not value:
            print(f"{label} cannot be empty.")
    return value


def main():
    api_key = load_api_key()
    if not api_key:
        print("Error: GROQ_API_KEY is missing. Add it to Colab Secrets or a .env file.")
        sys.exit(1)

    industry = ask("Business type / industry: ", "Industry")
    audience = ask("Target audience: ", "Audience")
    location = ask("Location: ", "Location")

    prompt = (
        f"Create a business idea in the {industry} industry for {audience} in {location}. "
        "Reply with ONLY valid JSON, no extra text, using exactly these keys: "
        '"business_name" (a creative name), '
        '"description" (a 2-sentence summary), '
        '"marketing_idea" (a high-impact launch tactic).'
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")
        return
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return

    try:
        text = data["choices"][0]["message"]["content"].strip()
        text = text.replace("`json", "").replace("```", "").strip()
        idea = json.loads(text)
        tokens = data["usage"]["total_tokens"]
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"Could not read the response: {e}")
        return

    print("\n--- Your Business Idea ---")
    print(f"Name: {idea.get('business_name')}")
    print(f"Description: {idea.get('description')}")
    print(f"Marketing idea: {idea.get('marketing_idea')}")
    print(f"\nTotal tokens used: {tokens}")

main()