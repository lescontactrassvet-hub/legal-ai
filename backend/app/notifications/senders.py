import os, time
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "logs")
LOG_DIR = os.path.abspath(LOG_DIR)
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "notifications.log")

def _write(line: str):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {line}\n")

def send_sms(phone: str, text: str):
    _write(f"SMS to {phone}: {text}")

def send_email(email: str, subject: str, text: str):
    _write(f"EMAIL to {email}: {subject} | {text}")
