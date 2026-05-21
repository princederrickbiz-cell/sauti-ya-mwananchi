"""
Manual Gemini smoke test.

Run directly when you want to verify credentials:
  python test_gemini.py

This file is intentionally safe to import so automated tests do not call Gemini.
"""
from google import genai


def main():
    client = genai.Client(
        vertexai=True,
        project="gen-lang-client-0889212655",
        location="us-central1",
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Say Habari! in English, Kiswahili, and Sheng",
    )

    print(response.text)


if __name__ == "__main__":
    main()
