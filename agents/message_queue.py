"""
Message queue for handling bulk SMS/WhatsApp sends.
Implements simple in-memory queue with persistence to JSONL.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from threading import Lock

from agents.africastalking_client import send_sms, send_whatsapp
from agents.settings import ROOT_DIR

logger = logging.getLogger(__name__)

QUEUE_FILE = ROOT_DIR / "data" / "message_queue.jsonl"
SENT_FILE = ROOT_DIR / "data" / "messages_sent.jsonl"

# In-memory queue
_queue: List[Dict] = []
_queue_lock = Lock()


def _ensure_queue_files():
    """Ensure queue files exist."""
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)


def add_to_queue(recipients: List[str], message: str, channel: str = "sms") -> Dict:
    """Add messages to queue for bulk sending.
    
    Args:
        recipients: List of phone numbers
        message: Message text
        channel: "sms" or "whatsapp"
    
    Returns:
        Dict with queue_id and count of messages added
    """
    _ensure_queue_files()
    queue_id = datetime.utcnow().isoformat()
    
    with _queue_lock:
        for phone in recipients:
            queue_item = {
                "queue_id": queue_id,
                "phone": phone,
                "message": message,
                "channel": channel,
                "created_at": datetime.utcnow().isoformat(),
                "sent_at": None,
                "status": "pending",
            }
            _queue.append(queue_item)
            
            # Persist to file
            try:
                with open(QUEUE_FILE, "a", encoding="utf-8") as f:
                    f.write(json.dumps(queue_item) + "\n")
            except Exception as e:
                logger.error(f"Failed to persist queue item: {e}")
    
    return {"queue_id": queue_id, "count": len(recipients)}


def process_queue(max_items: Optional[int] = None) -> Dict:
    """Process pending queue items.
    
    Args:
        max_items: Max items to process (None = all)
    
    Returns:
        Dict with success/failure counts
    """
    _ensure_queue_files()
    success_count = 0
    failure_count = 0
    
    with _queue_lock:
        items_to_process = _queue[:max_items] if max_items else list(_queue)
        
        for item in items_to_process:
            if item["status"] != "pending":
                continue
            
            try:
                if item["channel"] == "whatsapp":
                    result = send_whatsapp(item["phone"], item["message"])
                else:
                    result = send_sms(item["phone"], item["message"])
                
                if result.get("sent"):
                    item["status"] = "sent"
                    item["sent_at"] = datetime.utcnow().isoformat()
                    success_count += 1
                else:
                    item["status"] = "failed"
                    failure_count += 1
                
                # Log to sent file
                try:
                    with open(SENT_FILE, "a", encoding="utf-8") as f:
                        f.write(json.dumps(item) + "\n")
                except Exception as e:
                    logger.error(f"Failed to log sent message: {e}")
            
            except Exception as e:
                logger.error(f"Error processing queue item: {e}")
                item["status"] = "error"
                failure_count += 1
        
        # Remove processed items from queue
        _queue[:] = [item for item in _queue if item["status"] == "pending"]
    
    return {
        "success": success_count,
        "failure": failure_count,
        "total": success_count + failure_count,
    }


def get_queue_status() -> Dict:
    """Get current queue status."""
    with _queue_lock:
        return {
            "pending": len(_queue),
            "items": _queue.copy(),
        }


def clear_queue() -> Dict:
    """Clear all pending queue items."""
    with _queue_lock:
        count = len(_queue)
        _queue.clear()
    return {"cleared": count}


def load_queue_from_file() -> Dict:
    """Load pending items from queue file."""
    _ensure_queue_files()
    loaded_count = 0
    
    if not QUEUE_FILE.exists():
        return {"loaded": 0}
    
    with _queue_lock:
        try:
            with open(QUEUE_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    item = json.loads(line)
                    if item.get("status") == "pending":
                        _queue.append(item)
                        loaded_count += 1
        except Exception as e:
            logger.error(f"Failed to load queue from file: {e}")
    
    return {"loaded": loaded_count}
