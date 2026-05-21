# Quick Start: WhatsApp Testing Guide

This guide shows you how to test Sauti ya Mwananchi on WhatsApp with Africa's Talking.

## 🚀 Quick Setup (5 minutes)

### Option 1: Using the Automated Script (Recommended)

**Windows:**
```bash
# Method 1: Double-click
setup-ngrok.bat

# Method 2: PowerShell
.\setup-ngrok.ps1
```

The script will:
- ✅ Check if ngrok is installed
- ✅ Download ngrok if needed
- ✅ Verify your Sauti ya Mwananchi server
- ✅ Start the tunnel automatically
- ✅ Display your public URL

### Option 2: Manual Setup

**Step 1: Install ngrok**
- Download: https://ngrok.com/download
- Extract to a folder
- Add to PATH or use full path

**Step 2: Start Sauti ya Mwananchi server**
```bash
python main.py
```
(Runs on http://localhost:8000)

**Step 3: Start ngrok tunnel**
```bash
ngrok http 8000
```

You'll see output like:
```
Session Status                online
Account                       your-account
Version                       3.x.x
Region                        us (United States)
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123def456.ngrok.io -> http://localhost:8000
```

**Copy the forwarding URL** (e.g., `https://abc123def456.ngrok.io`)

## 📱 Configure Africa's Talking

### Step 1: Get Africa's Talking Account
1. Go to https://africastalking.com
2. Sign up and verify your account
3. Get your API credentials

### Step 2: Set Webhook URL

1. Log in to Africa's Talking Dashboard
2. Navigate to **Settings → SMS/WhatsApp**
3. Find **Webhook URL** section
4. Set callback URL to:
   ```
   https://your-ngrok-url/africastalking/sms
   ```
   
   Replace `your-ngrok-url` with your ngrok public URL (e.g., `https://abc123def456.ngrok.io`)

5. Save/Confirm

### Step 3: Get Your WhatsApp Number
- In Africa's Talking Dashboard, find your test WhatsApp number
- It's usually provided in sandbox mode

## 🧪 Test Your Setup

### Test 1: Local API Test (No WhatsApp needed)

```bash
# Test the /message endpoint
curl -X POST http://localhost:8000/message \
  -H "Content-Type: application/json" \
  -d '{"phone":"+254700000000","message":"What are my voting rights?"}'
```

Expected response:
```json
{
  "reply": "Karibu. Adult citizens have the right to be registered as a voter..."
}
```

### Test 2: Send WhatsApp Message

Use the `/send-whatsapp` endpoint:

```bash
curl -X POST http://localhost:8000/send-whatsapp \
  -H "Content-Type: application/json" \
  -d '{"phone":"+254700000000","message":"Sauti ya Mwananchi online!"}'
```

### Test 3: Receive WhatsApp via Africa's Talking

1. **Start the server** with ngrok running
2. **Send a WhatsApp message** from your phone to the Africa's Talking number
3. **Check the response** - you should get a reply automatically!

Try these messages:
- `"What are my voting rights?"` - Gets civic education
- `"Is it true you need a party card to vote?"` - Gets fact-check
- `"Where do I vote in Westlands?"` - Gets polling location
- `"Ni haki gani ninazopata?"` - Kiswahili version

## 📊 Monitor Your Tunnel

While ngrok is running, you can view:
- **Requests**: http://localhost:4040
- **Status**: http://localhost:4040/status

This shows every WhatsApp message hitting your server!

## 🔧 Troubleshooting

### "Connection refused"
- ✅ Make sure `python main.py` is running
- ✅ Make sure port 8000 is not blocked

### "ngrok: command not found"
- ✅ Download ngrok from https://ngrok.com/download
- ✅ Add to PATH or use full path: `C:\path\to\ngrok.exe http 8000`

### "Auth token invalid"
- ✅ Go to https://dashboard.ngrok.com/auth/your-authtoken
- ✅ Copy your auth token
- ✅ Run: `ngrok config add-authtoken YOUR_TOKEN`

### "No messages received"
- ✅ Check webhook URL in Africa's Talking dashboard
- ✅ Verify webhook format: `https://your-ngrok-url/africastalking/sms`
- ✅ Check ngrok logs (http://localhost:4040)
- ✅ Verify credentials in `.env` file

### "Messages sent but no reply"
- ✅ Check server logs: `python main.py` output
- ✅ Check Gemini API key in `.env`
- ✅ Check Africa's Talking configuration

## 📋 Configuration Checklist

- [ ] Python installed
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] `.env` file created with:
  - [ ] `GEMINI_API_KEY=your_key`
  - [ ] `GEMINI_MODEL=gemini-2.5-flash`
  - [ ] `AFRICASTALKING_USERNAME=sandbox`
  - [ ] `AFRICASTALKING_API_KEY=your_key`
- [ ] ngrok installed and authenticated
- [ ] Africa's Talking webhook configured
- [ ] Server running: `python main.py`
- [ ] ngrok tunnel active: `ngrok http 8000`
- [ ] ngrok URL copied and verified

## 🚀 Next Steps

Once working:
1. **Deploy to cloud** (Heroku, Google Cloud, AWS)
2. **Get production Africa's Talking account**
3. **Configure real WhatsApp numbers**
4. **Monitor with analytics** (`data/message_log.jsonl`)
5. **Scale messaging** with `/bulk-message/` endpoints

## 📞 Help & Support

- Africa's Talking Docs: https://africastalking.com/
- ngrok Docs: https://ngrok.com/docs
- Project GitHub: https://github.com/princederrickbiz-cell/sauti-ya-mwananchi

## 💡 Pro Tips

1. **Keep ngrok window open** while testing
2. **Check ngrok web interface** at http://localhost:4040 for request logs
3. **Use different test messages** to explore different agents
4. **Monitor logs** in `data/message_log.jsonl` for delivery tracking
5. **Queue bulk messages** with `/bulk-message/add` for campaigns
