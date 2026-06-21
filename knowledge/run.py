"""Dev entry: python -m knowledge.run or uv run python knowledge/run.py"""

from knowledge.wiring import build_trio


def main() -> None:
    trio = build_trio()
    print("PRAXIS knowledge trio ready:", list(trio.keys()))


if __name__ == "__main__":
    main()
