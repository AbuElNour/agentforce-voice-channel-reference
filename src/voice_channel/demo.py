import json

from .handler import VoiceChannelHandler, sign_payload


def main():
    secret = b"not-a-production-secret"
    payload = json.dumps({"message_id": "msg-demo-1", "kind": "voice", "synthetic_transcript": "hello agent"}).encode()
    handler = VoiceChannelHandler(secret)
    print(json.dumps(handler.handle(payload, sign_payload(secret, payload)), indent=2))


if __name__ == "__main__":
    main()

