# Sauti ya Mwananchi

Sauti ya Mwananchi is a neutral civic participation agent for the GDG Nairobi Agentathon 2026 TukoKadi challenge.

It uses a simple multi-agent structure:

- `Msaidizi`: orchestrator for SMS/WhatsApp-style messages
- `Mwalimu`: civic educator using approved source snippets
- `Kiongozi`: IEBC registration/polling centre helper using public registration-centre data
- `Ukweli`: misinformation checker that can return `Unverified`
- `Mwenza`: USSD election-day companion

## Step 1: Add Your Gemini Credentials

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash

AFRICASTALKING_USERNAME=sandbox
AFRICASTALKING_API_KEY=your_africastalking_api_key_here
AFRICASTALKING_SENDER_ID=
```

If you are using Vertex AI instead:

```env
GOOGLE_CLOUD_PROJECT=your-google-cloud-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GEMINI_MODEL=gemini-2.5-flash
```

Never commit `.env` to GitHub.

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 3: Run A Local Demo

```bash
python main.py --demo
```

## Step 4: Chat With The Agent Locally

```bash
python main.py --test
```

Try:

```text
Ni haki gani ninazopata siku ya uchaguzi?
Is it true that you need a party card to vote?
Wapi nipigie kura Westlands?
```

## Step 5: Run The Webhook Server

```bash
python main.py
```

Then open the web UI:

```text
http://127.0.0.1:8000/
```

API health check:

```text
http://127.0.0.1:8000/health
```

API test:

```bash
curl -X POST http://localhost:8000/message \
  -H "Content-Type: application/json" \
  -d "{\"phone\":\"+254700000000\",\"message\":\"What are my voting rights?\"}"
```

Africa's Talking SMS webhook:

```text
POST http://localhost:8000/africastalking/sms
```

Africa's Talking USSD webhook:

```text
POST http://localhost:8000/africastalking/ussd
```

If port `8000` is busy:

```bash
PORT=8001 python main.py
```

## Expanding Polling Station Coverage

`Kiongozi` reads public IEBC registration-centre data from:

```text
data/polling_stations.csv
```

Use this CSV format:

```csv
county,constituency,ward,station,source,source_date
Nairobi,Westlands,Kangemi,Kangemi Primary School,IEBC,2026-05-21
```

The required columns are:

```text
county,constituency,ward,station
```

`source` and `source_date` are optional but strongly recommended. Use official IEBC data where possible. Do not store voter names, ID numbers, phone numbers, or any other personal voter data.

The current dataset is sourced from IEBC's public registration-centre page. Registration centres become polling centres during elections, but users should still confirm their final official polling station through IEBC.

### Importing An Official IEBC Bulk File

1. Go to the official IEBC website:

```text
https://www.iebc.or.ke/
```

2. Check the polling-stations/downloads sections for an official public polling-station or register publication.

3. If the file is PDF or Excel, open it and export/save the public polling-station table as CSV.

4. Run the importer:

```bash
python tools/import_polling_stations.py path/to/iebc_polling_stations.csv --source IEBC --source-date 2026-05-21
```

The importer writes the normalized file to:

```text
data/polling_stations.csv
```

The input CSV must contain columns equivalent to:

```text
county,constituency,ward,polling_station
```

### Fetching Public IEBC Registration-Centre Data

The IEBC registration page uses public non-personal endpoints for counties, constituencies, wards, and registration centres. Test with one county first:

```bash
python tools/fetch_iebc_registration_centres.py --county "NAIROBI"
```

For a smaller test:

```bash
python tools/fetch_iebc_registration_centres.py --county "NAIROBI" --constituency "WESTLANDS"
```

If your local Python reports an IEBC certificate verification error, retry the same public data fetch with:

```bash
python tools/fetch_iebc_registration_centres.py --county "NAIROBI" --constituency "WESTLANDS" --insecure
```

For troubleshooting, add:

```bash
python tools/fetch_iebc_registration_centres.py --county "NAIROBI" --constituency "WESTLANDS" --insecure --debug
```

If the test looks correct, fetch all counties:

```bash
python tools/fetch_iebc_registration_centres.py --delay 0.5
```

For a long full-country fetch, use resume mode so temporary IEBC disconnects do not lose progress:

```bash
python tools/fetch_iebc_registration_centres.py --delay 1 --insecure --resume --continue-on-error
```

This writes:

```text
data/polling_stations.csv
```

Use this only for public registration-centre listings. Do not automate any IEBC flow that asks for ID numbers, passport numbers, birth dates, phone numbers, or other personal voter details.

## Guardrails

- The agent must remain politically neutral.
- Civic claims must cite IEBC, the Constitution, or an Act.
- Unsupported misinformation claims should be marked `Unverified`.
- Voter ID numbers must not be stored.
- Registration-centre matches must be presented as possible matches, with a reminder to confirm final official polling-station details through IEBC.

## Cloud Run Deployment

Build locally:

```bash
docker build -t sauti-ya-mwananchi .
docker run --env-file .env -p 8080:8080 sauti-ya-mwananchi
```

Open:

```text
http://127.0.0.1:8080/
```

Deploy manually to Cloud Run:

```bash
gcloud run deploy sauti-ya-mwananchi \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_MODEL=gemini-2.5-flash
```

Then add secrets/environment variables in Cloud Run:

```text
GEMINI_API_KEY
AFRICASTALKING_USERNAME
AFRICASTALKING_API_KEY
AFRICASTALKING_SENDER_ID
```

Do not commit `.env`.

## Next Improvements

- Replace `data/polling_stations.csv` with official IEBC polling-station data.
- Add RAG ingestion for Constitution, IEBC, and Elections Act documents.
- Add image upload support for `Ukweli` using Gemini Vision.
- Connect `/message` to WhatsApp/SMS through Africa's Talking.
- Deploy the FastAPI app to Cloud Run.
