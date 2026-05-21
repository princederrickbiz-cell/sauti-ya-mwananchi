from google import genai

client = genai.Client(
    vertexai=True, 
    project='gen-lang-client-0889212655', 
    location='us-central1'
)

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Say Habari! in English, Kiswahili, and Sheng'
)

print(response.text)