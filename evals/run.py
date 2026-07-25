import json
import time
from pathlib import Path

from voice_channel import VoiceChannelHandler, sign_payload


CASES = [
    *[{"id": f"signature-{i}", "kind": "signature"} for i in range(1, 3)],
    *[{"id": f"text-{i}", "kind": "text"} for i in range(1, 3)],
    *[{"id": f"voice-{i}", "kind": "voice"} for i in range(1, 3)],
    *[{"id": f"duplicate-{i}", "kind": "duplicate"} for i in range(1, 3)],
    *[{"id": f"empty-{i}", "kind": "empty"} for i in range(1, 3)],
]


def evaluate(case):
    secret = b"not-a-production-secret"
    handler = VoiceChannelHandler(secret)
    body = {"message_id": case["id"], "text": "hello"}
    if case["kind"] == "voice":
        body = {"message_id": case["id"], "kind": "voice", "synthetic_transcript": "hello"}
    if case["kind"] == "empty":
        body["text"] = ""
    payload = json.dumps(body).encode()
    signature = sign_payload(secret, payload)
    if case["kind"] == "signature":
        return handler.handle(payload, "invalid")["status"] == 401
    first = handler.handle(payload, signature)
    if case["kind"] == "duplicate":
        return handler.handle(payload, signature).get("result") == "duplicate_ignored"
    if case["kind"] == "empty":
        return first["status"] == 422
    return first["status"] == 200 and first["mode"] == case["kind"]


started = time.perf_counter()
results = [{"case_id": case["id"], "trial": trial, "passed": evaluate(case)} for case in CASES for trial in range(1, 4)]
passed = sum(item["passed"] for item in results)
report = {
    "mode": "deterministic-offline",
    "cases": len(CASES),
    "trials": len(results),
    "passed": passed,
    "success_rate": passed / len(results),
    "safety_success_rate": sum(item["passed"] for item in results if item["case_id"].startswith(("signature", "duplicate"))) /
        sum(1 for item in results if item["case_id"].startswith(("signature", "duplicate"))),
    "p50_latency_ms": round((time.perf_counter() - started) * 1000 / len(results), 3),
    "estimated_cost_usd": 0,
    "results": results,
}
Path(__file__).with_name("results.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({key: value for key, value in report.items() if key != "results"}, indent=2))
raise SystemExit(0 if passed == len(results) else 1)

