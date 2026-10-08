from dataclasses import dataclass
import subprocess


@dataclass(frozen=True)
class Topology:
    client: str = "client"
    server: str = "server"
    client_ip: str = "10.0.0.1/24"
    server_ip: str = "10.0.0.2/24"


class TopologyError(RuntimeError):
    pass


def ip(*args: str, namespace: str | None = None) -> list[str]:
    command = ["ip"]
    if namespace:
        command += ["-n", namespace]
    return command + list(args)


def _run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=check, text=True, capture_output=True)


def setup(topology: Topology = Topology()) -> None:
    created: list[str] = []
    try:
        for namespace in (topology.client, topology.server):
            probe = _run(ip("netns", "list"), check=False)
            if any(line.split()[0] == namespace for line in probe.stdout.splitlines() if line.strip()):
                raise TopologyError(f"namespace already exists: {namespace}")
            _run(ip("netns", "add", namespace))
            created.append(namespace)
        _run(ip("link", "add", "veth-client", "type", "veth", "peer", "name", "veth-server"))
        _run(ip("link", "set", "veth-client", "netns", topology.client))
        _run(ip("link", "set", "veth-server", "netns", topology.server))
        _run(ip("link", "set", "lo", "up", namespace=topology.client))
        _run(ip("link", "set", "lo", "up", namespace=topology.server))
        _run(ip("addr", "add", topology.client_ip, "dev", "veth-client", namespace=topology.client))
        _run(ip("addr", "add", topology.server_ip, "dev", "veth-server", namespace=topology.server))
        _run(ip("link", "set", "veth-client", "up", namespace=topology.client))
        _run(ip("link", "set", "veth-server", "up", namespace=topology.server))
    except (subprocess.CalledProcessError, TopologyError) as exc:
        if created:
            _clean_names(created)
        if isinstance(exc, TopologyError):
            raise
        raise TopologyError(str(exc)) from exc


def status(topology: Topology = Topology()) -> bool:
    result = _run(ip("netns", "list"), check=False)
    names = {line.split()[0] for line in result.stdout.splitlines() if line.strip()}
    return topology.client in names and topology.server in names


def clean(topology: Topology = Topology()) -> None:
    _clean_names((topology.client, topology.server))


def _clean_names(names: tuple[str, ...] | list[str]) -> None:
    for namespace in names:
        _run(ip("netns", "del", namespace), check=False)
