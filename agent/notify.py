"""Telegram side effect, isolated so the act tool stays about policy.

Secrets are read here from env and never pass through the model's context or a
tool argument. Retries transient failures only (network, 429, 5xx); a 4xx that
isn't 429 is a permanent error and is not retried.
"""
import time

import requests

from . import config
from .logging_setup import jlog


def telegram_post(message: str) -> bool:
    token = config.TELEGRAM_TOKEN
    chat_id = config.TELEGRAM_CHAT_ID
    if not (token and chat_id):
        jlog("notify_error", reason="missing_telegram_env")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}

    for attempt in range(4):                     # up to 4 tries: 1,2,4,8s backoff
        try:
            r = requests.post(url, json=payload, timeout=10)
            if r.status_code < 400:
                return True
            if r.status_code != 429 and r.status_code < 500:
                jlog("notify_error", status=r.status_code, body=r.text[:200])
                return False                     # permanent client error
            jlog("notify_retry", status=r.status_code, attempt=attempt)
        except requests.RequestException as e:
            jlog("notify_retry", error=str(e), attempt=attempt)
        time.sleep(2 ** attempt)
    return False
