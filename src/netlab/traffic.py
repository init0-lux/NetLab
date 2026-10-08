from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
from typing import Any


@dataclass(frozen=True)
class TrafficResult:
    protocol: str
    raw_json: dict[str, Any]
    stderr: str


class TrafficError(RuntimeError):
    pass


def run_iperf(
    protocol: str,
    server_ip: str,
    duration_seconds: int,
    output_dir: Path,
    udp_offered_rate_mbps: int | None = None,
    timeout_seconds: int | None = None,
) -> TrafficResult:
    if protocol not in {"tcp", "udp"}:
        raise ValueError("protocol must be tcp or udp")
    if duration_seconds <= 0:
        raise ValueError("duration_seconds must be positive")
    if protocol == "udp" and (udp_offered_rate_mbps is None or udp_offered_rate_mbps <= 0):
        raise ValueError("UDP requires positive offered rate")

    output_dir.mkdir(parents=True, exist_ok=True)
    server = subprocess.Popen(
        ["iperf3", "-s", "-1", "-J"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    command = ["iperf3", "-c", server_ip, "-t", str(duration_seconds), "-J"]
    if protocol == "udp":
        command += ["-u", "-b", f"{udp_offered_rate_mbps}M"]
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout_seconds or duration_seconds + 10,
        )
        raw = json.loads(result.stdout)
        (output_dir / "iperf3.json").write_text(json.dumps(raw, indent=2) + "\n")
        (output_dir / "iperf3.stderr").write_text(result.stderr)
        return TrafficResult(protocol, raw, result.stderr)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        raise TrafficError(str(exc)) from exc
    finally:
        if server.poll() is None:
            server.terminate()
            try:
                server.wait(timeout=2)
            except subprocess.TimeoutExpired:
                server.kill()
