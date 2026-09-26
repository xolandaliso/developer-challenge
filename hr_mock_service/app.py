'''
    - a deliberately tiny stand-in for "System A - HR System".

    - it serves the mock employee dataset (including the awkward records) as
    a real REST endpoint over HTTP, so the integration service genuinely
    consumes a REST API rather than reading a local file.
'''

import json
from pathlib import Path

from flask import Flask, jsonify

app = Flask(__name__)
DATA_FILE = Path(__file__).resolve().parent / "data" / "employees_source.json"


@app.get("/employees")
def list_employees():
    with open(DATA_FILE) as f:
        return jsonify(json.load(f))


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
