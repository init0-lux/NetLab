import argparse
from pathlib import Path

from . import topology
from .traffic import run_iperf


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="netlab")
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    parser.add_argument("command", nargs="?", choices=["setup", "status", "clean", "run"])
    parser.add_argument("--protocol", choices=["tcp", "udp"], default="tcp")
    parser.add_argument("--server-ip", default="10.0.0.2")
    parser.add_argument("--duration", type=int, default=10)
    parser.add_argument("--udp-rate", type=int)
    parser.add_argument("--output", type=Path, default=Path("data/raw/manual"))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "setup":
        topology.setup()
    elif args.command == "status":
        print("ready" if topology.status() else "absent")
    elif args.command == "clean":
        topology.clean()
    elif args.command == "run":
        run_iperf(args.protocol, args.server_ip, args.duration, args.output, args.udp_rate)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
