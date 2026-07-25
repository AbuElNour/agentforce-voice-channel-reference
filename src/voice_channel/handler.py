from __future__ import annotations

import hashlib
import hmac
import json


def sign_payload(secret: bytes, payload: bytes) -> str:
    return hmac.new(secret, payload, hashlib.sha256).hexdigest()


class VoiceChannelHandler:
    def __init__(self, signing_secret: bytes):
        self.signing_secret = signing_secret
        self.processed: set[str] = set()
        self.trace: list[dict] = []

    def handle(self, payload: bytes, signature: str) -> dict:
        expected = sign_payload(self.signing_secret, payload)
        if not hmac.compare_digest(expected, signature):
            self.trace.append({"step": "webhook.rejected", "reason": "invalid signature"})
            return {"status": 401, "error": "invalid_signature", "trace": list(self.trace)}
        event = json.loads(payload)
        message_id = str(event.get("message_id", ""))
        if not message_id:
            return {"status": 400, "error": "missing_message_id", "trace": list(self.trace)}
        if message_id in self.processed:
            self.trace.append({"step": "webhook.duplicate", "message_id": message_id})
            return {"status": 200, "result": "duplicate_ignored", "trace": list(self.trace)}
        self.processed.add(message_id)
        self.trace.append({"step": "webhook.verified", "message_id": message_id})
        kind = event.get("kind", "text")
        if kind == "voice":
            transcript = str(event.get("synthetic_transcript", "")).strip()
            self.trace.append({"step": "speech.transcribed", "characters": len(transcript)})
        else:
            transcript = str(event.get("text", "")).strip()
        if not transcript:
            return {"status": 422, "error": "empty_message", "trace": list(self.trace)}
        response = f"Agent received: {transcript}"
        self.trace.append({"step": "agent.completed", "mode": kind})
        return {"status": 200, "result": response, "mode": kind, "trace": list(self.trace)}

