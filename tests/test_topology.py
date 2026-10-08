import unittest
from unittest.mock import patch

from netlab.topology import Topology, setup, status


class TopologyTests(unittest.TestCase):
    def test_setup_builds_namespace_and_veth_commands(self):
        calls = []

        def fake_run(command, **kwargs):
            calls.append(command)
            class Result:
                stdout = ""
            return Result()

        with patch("netlab.topology._run", side_effect=fake_run):
            setup(Topology())
        self.assertIn(["ip", "netns", "add", "client"], calls)
        self.assertIn(["ip", "link", "add", "veth-client", "type", "veth", "peer", "name", "veth-server"], calls)
        self.assertIn(["ip", "-n", "client", "addr", "add", "10.0.0.1/24", "dev", "veth-client"], calls)

    def test_status_uses_namespace_list(self):
        result = type("Result", (), {"stdout": "client\nserver\n"})()
        with patch("netlab.topology._run", return_value=result):
            self.assertTrue(status())
