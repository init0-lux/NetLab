import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="netlab")
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    parser.add_argument("command", nargs="?", choices=["setup", "status", "clean", "run"])
    return parser


def main() -> int:
    build_parser().parse_args()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
