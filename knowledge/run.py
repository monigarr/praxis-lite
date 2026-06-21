"""Dev entry: python -m knowledge.run  (starts FastAPI candidate server)

uv run python -m knowledge.run
"""

import uvicorn

from knowledge.serve.app import app
from knowledge.wiring import build_trio


def main() -> None:
    trio = build_trio()
    print("PRAXIS knowledge trio ready:", list(trio.keys()))
    print("Starting PRAXIS Candidate API at http://0.0.0.0:8000 (health: /health)")
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
