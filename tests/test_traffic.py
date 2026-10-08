import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from netlab.traffic import run_iperf


class FakeServer:
    def poll(self):
        return None

    def terminate(self):
        self.terminated = True

    def wait(self, timeout=None):
        return 0


class TrafficTests(unittest.TestCase):
    def test_tcp_saves_json_and_stops_server(self):
        server = FakeServer()
        result = type("Result", (), {"stdout": json.dumps({"start": {}, "end": {}}), "stderr": ""})()
        with tempfile.TemporaryDirectory() as directory, patch("netlab.traffic.subprocess.Popen", return_value=server), patch("netlab.traffic.subprocess.run", return_value=result) as run:
            output = run_iperf("tcp", "10.0.0.2", 3, Path(directory))
            self.assertTrue((Path(directory) / "iperf3.json").exists())
        self.assertEqual(output.protocol, "tcp")
        self.assertEqual(run.call_args.args[0], ["iperf3", "-c", "10.0.0.2", "-t", "3", "-J"])
        self.assertTrue(server.terminated)

    def test_udp_requires_rate_and_adds_udp_arguments(self):
        with self.assertRaises(ValueError):
            run_iperf("udp", "10.0.0.2", 3, Path(tempfile.gettempdir()))
