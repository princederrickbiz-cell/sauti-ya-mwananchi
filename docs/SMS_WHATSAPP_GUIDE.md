# SMS/WhatsApp Integration Guide

This document describes the enhanced SMS and WhatsApp messaging capabilities in Sauti ya Mwananchi.

## Features

### 1. SMS Delivery
- Retry logic with exponential backoff (attempts: 3, delays: 2s, 4s, 8s)
- Error handling and timeout support
- Message logging to `data/message_log.jsonl`
- Support for custom sender IDs

### 2. WhatsApp Delivery
- Native WhatsApp API support via Africa's Talking
- Same retry logic and error handling as SMS
- Automatic channel switching

### 3. Message Logging
- Timestamp, phone number, channel, status
- Response tracking for debugging
- Persistent JSONL format in `data/message_log.jsonl`

### 4. Bulk Messaging
- Queue-based system for sending to multiple recipients
- Persistent queue stored in `data/message_queue.jsonl`
- In-memory queue with file persistence
- Thread-safe operations

### 5. Message Queue Management
- Add messages to queue
- Process queue (with max items limit)
- Check queue status
- Clear pending messages
- Load queue from file on startup

## API Endpoints

### Direct Messaging

#### Send SMS
```bash
POST /send-sms
Content-Type: application/json

{
  "phone": "+254700000000",
  "message": "Your voting rights message here"
}
```

Response:
```json
{
  "sent": true,
  "channel": "sms",
  "response": { ... }
}
```

#### Send WhatsApp
```bash
POST /send-whatsapp
Content-Type: application/json

{
  "phone": "+254700000000",
  "message": "Your WhatsApp message here"
}
```

#### Send Message (Auto Channel)
```bash
POST /send-message
Content-Type: application/json

{
  "phone": "+254700000000",
  "message": "Your message",
  "channel": "sms"  # or "whatsapp"
}
```

### Bulk Messaging

#### Add to Queue
```bash
POST /bulk-message/add
Content-Type: application/json

{
  "recipients": ["+254700000000", "+254711111111", "+254722222222"],
  "message": "Civic education message for all",
  "channel": "sms"  # or "whatsapp"
}
```

Response:
```json
{
  "queue_id": "2026-05-21T10:30:45.123456",
  "count": 3
}
```

#### Process Queue
```bash
POST /bulk-message/process
# Optional: ?max_items=100 to limit processing
```

Response:
```json
{
  "success": 95,
  "failure": 5,
  "total": 100
}
```

#### Get Queue Status
```bash
GET /bulk-message/status
```

Response:
```json
{
  "pending": 250,
  "items": [
    {
      "queue_id": "2026-05-21T10:30:45.123456",
      "phone": "+254700000000",
      "message": "...",
      "channel": "sms",
      "created_at": "2026-05-21T10:30:45.123456",
      "sent_at": null,
      "status": "pending"
    },
    ...
  ]
}
```

#### Clear Queue
```bash
POST /bulk-message/clear
```

Response:
```json
{
  "cleared": 250
}
```

#### Load Queue from File
```bash
POST /bulk-message/load
```

Response:
```json
{
  "loaded": 50
}
```

## Configuration

Add to `.env`:

```env
# Africa's Talking SMS/WhatsApp
AFRICASTALKING_USERNAME=your_username
AFRICASTALKING_API_KEY=your_api_key_here
AFRICASTALKING_SENDER_ID=SautiYaMwananchi  # Optional
```

## Usage Examples

### Example 1: Reply to citizen via SMS
```python
from agents.africastalking_client import send_sms

reply = "Your voting information:\n- Register at IEBC office\n- Vote on election day"
result = send_sms(to="+254700000000", message=reply)
```

### Example 2: Queue civic education for all users
```python
from agents.message_queue import add_to_queue, process_queue

# Add to queue
queue_result = add_to_queue(
    recipients=["+254700000000", "+254711111111"],
    message="Sauti ya Mwananchi: Check your voting rights",
    channel="sms"
)
print(f"Queued {queue_result['count']} messages")

# Process queue
process_result = process_queue(max_items=100)
print(f"Sent: {process_result['success']}, Failed: {process_result['failure']}")
```

### Example 3: Adaptive messaging (SMS or WhatsApp)
```python
from agents.africastalking_client import send_message

# Try WhatsApp first if available
result = send_message(
    to="+254700000000",
    message="Your voting information",
    channel="whatsapp"
)
```

## Message Logs

Message logs are stored in `data/message_log.jsonl`:

```json
{
  "timestamp": "2026-05-21T10:30:45.123456",
  "phone": "+254700000000",
  "channel": "sms",
  "message_length": 156,
  "status": "success",
  "response": { ... }
}
```

View recent messages:
```bash
# Last 10 messages
tail -n 10 data/message_log.jsonl

# Count by status
grep '"status": "success"' data/message_log.jsonl | wc -l
```

## Error Handling

The system automatically handles:
- Network timeouts (20-second timeout per request)
- Missing credentials (graceful fallback with error info)
- API rate limits (exponential backoff)
- Temporary failures (retry up to 3 times)
- Missing log files (auto-created)

## Thread Safety

The message queue uses locks for thread-safe operations:
- Safe for concurrent reads/writes
- Proper synchronization for queue modifications
- File I/O is protected

## Performance Tips

1. **For bulk sends**: Use `/bulk-message/add` + `/bulk-message/process` instead of individual SMS
2. **For real-time replies**: Use `/send-sms` or `/send-whatsapp` directly
3. **Process in batches**: Call `/bulk-message/process?max_items=100` to avoid overwhelming the service
4. **Monitor queue**: Check `/bulk-message/status` regularly during campaigns

## Troubleshooting

### Messages not sending
- Check `.env` has valid `AFRICASTALKING_API_KEY`
- Verify phone numbers are in E.164 format: `+254XXXXXXXXX`
- Check message length (SMS: max 160 chars, concatenated allowed)

### Queue not processing
- Call `/bulk-message/load` to reload from file
- Check `data/message_queue.jsonl` file exists
- Verify Africa's Talking credentials are active

### High failure rate
- Check network connectivity
- Review Africa's Talking account status/balance
- Check `/bulk-message/status` for error details
