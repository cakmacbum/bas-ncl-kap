"""Deterministic vessel dimensions and endpoint payloads for T08."""

VESSELS = [
    {"id": f"tank-{i:02d}", "inside_diameter": 800 + i * 40,
     "thickness": 8 + i % 4, "tangent_length": 1600 + i * 120,
     "head_type": "flat", "nozzle_count": 0}
    for i in range(1, 11)
]

API_CASES = [
    {"id": "api-empty", "body": b"", "expected_status": 415},
    {"id": "api-malformed", "body": b"this is not a STEP file", "expected_status": 415},
    {"id": "api-oversized", "body": b"ISO-10303-21;\n" + b" " * (20 * 1024 * 1024 + 1),
     "expected_status": 413},
    *[{"id": f"api-malformed-{i}", "body": f"not STEP payload {i}".encode(),
       "expected_status": 415} for i in range(2, 9)],
]
