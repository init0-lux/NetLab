# netlab

Controlled TCP/UDP network performance experiments using Linux namespaces,
`tc netem`, and iperf3.

Development:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
python -m unittest discover
```

Privileged networking and iperf3 are added in later commits.
