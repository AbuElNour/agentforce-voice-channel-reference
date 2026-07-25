# Security

Webhooks require an HMAC-SHA256 signature and a unique message identifier. Duplicate deliveries are ignored, empty messages fail closed, and the demo processes only synthetic transcripts in memory.

