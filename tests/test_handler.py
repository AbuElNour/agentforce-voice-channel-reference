import json
import unittest

from voice_channel import VoiceChannelHandler, sign_payload


class HandlerTests(unittest.TestCase):
    def setUp(self):
        self.secret = b"not-a-production-secret"
        self.handler = VoiceChannelHandler(self.secret)

    def payload(self, body):
        raw = json.dumps(body).encode()
        return raw, sign_payload(self.secret, raw)

    def test_rejects_invalid_signature(self):
        raw, _ = self.payload({"message_id": "one", "text": "hello"})
        self.assertEqual(self.handler.handle(raw, "invalid")["status"], 401)

    def test_text_message(self):
        raw, signature = self.payload({"message_id": "one", "text": "hello"})
        self.assertEqual(self.handler.handle(raw, signature)["mode"], "text")

    def test_voice_message(self):
        raw, signature = self.payload({"message_id": "one", "kind": "voice", "synthetic_transcript": "hello"})
        self.assertEqual(self.handler.handle(raw, signature)["mode"], "voice")

    def test_duplicate_is_idempotent(self):
        raw, signature = self.payload({"message_id": "one", "text": "hello"})
        self.handler.handle(raw, signature)
        self.assertEqual(self.handler.handle(raw, signature)["result"], "duplicate_ignored")

    def test_empty_message_rejected(self):
        raw, signature = self.payload({"message_id": "one", "text": ""})
        self.assertEqual(self.handler.handle(raw, signature)["status"], 422)


if __name__ == "__main__":
    unittest.main()

