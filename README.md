# NetLab — Controlled TCP/UDP Network Performance Laboratory

> A reproducible Linux networking laboratory for experimentally evaluating TCP and UDP under controlled network impairments.

NetLab creates an isolated virtual network on a Linux host, generates controlled TCP and UDP traffic, introduces configurable network conditions such as latency and packet loss, captures measurements, analyzes the results, and produces reproducible visualizations and reports.

The goal is not to simulate the Internet. The goal is to create a **controlled experimental environment** in which transport-layer behavior can be measured and explained.

---

## Overview

```text
                         Linux Host
┌──────────────────────────────────────────────────────────┐
│                                                          │
│   ┌──────────────────┐        ┌──────────────────┐       │
│   │ Client Namespace │        │ Server Namespace │       │
│   │                  │        │                  │       │
│   │   10.0.0.1       │        │   10.0.0.2       │       │
│   │                  │        │                  │       │
│   │   iperf3 client  │        │   iperf3 server  │       │
│   └────────┬─────────┘        └─────────┬────────┘       │
│            │                            │                │
│            └─────────── veth ───────────┘                │
│                         │                                │
│                       tc/netem                           │
│                   delay / loss                           │
│                         │                                │
│                 Measurements                             │
│                         │                                │
│              ┌──────────┴──────────┐                     │
│              │                     │                     │
│            iperf3                 ping                   │
│              │                     │                     │
│              └──────────┬──────────┘                     │
│                         ↓                                │
│                 Raw experimental data                    │
│                         ↓                                │
│                  Python analysis                         │
│                         ↓                                │
│                  Statistics + plots                      │
└──────────────────────────────────────────────────────────┘
```

### Core technologies

- **Linux network namespaces** — isolated network endpoints
- **veth pairs** — virtual Ethernet connectivity
- **tc/netem** — controlled network impairment
- **iperf3** — TCP/UDP traffic generation and measurement
- **ping** — RTT measurement
- **tcpdump/Wireshark** — optional packet-level inspection
- **Python + pandas** — data processing
- **NumPy** — numerical analysis
- **Matplotlib** — visualization
- **Nix** — reproducible development environment

---

## Research Question

> **How do TCP and UDP behave when network conditions such as latency and packet loss change?**

NetLab evaluates this experimentally rather than relying solely on theoretical descriptions.

The default experiment suite examines:

| Condition | Delay | Packet Loss |
|---|---:|---:|
| Baseline | 0 ms | 0% |
| Moderate delay | 20 ms | 0% |
| High delay | 50 ms | 0% |
| Low loss | 0 ms | 1% |
| High loss | 0 ms | 3% |

Each condition is evaluated using both TCP and UDP, with multiple repetitions.

---

# Features

- Isolated client/server network namespaces
- Virtual Ethernet topology
- Configurable `tc netem` impairments
- TCP benchmarking
- Fixed-rate UDP benchmarking
- RTT measurement
- Optional packet capture
- Configuration-driven experiments
- Automated experiment suites
- Experiment resumption
- Raw JSON preservation
- Normalized datasets
- Statistical analysis
- Automated visualization
- Reproducible experiment metadata
- Nix development environment
- Sample datasets for analysis without privileged networking
- Report-ready output

---

# Why This Project?

TCP and UDP are usually introduced through statements such as:

> TCP is reliable.

> UDP is faster.

Those statements are incomplete.

NetLab attempts to answer the more useful question:

> **What measurable behavior emerges from each protocol when the network becomes worse?**

The experiment separates:

```text
Network condition
       ↓
Protocol behavior
       ↓
Measured metrics
       ↓
Statistical analysis
       ↓
Interpretation
```

This makes the project both a networking experiment and a reproducible data-analysis pipeline.

---

# Experimental Methodology

Each experiment follows the same lifecycle:

```text
Configuration
     │
     ▼
Create virtual network
     │
     ▼
Verify connectivity
     │
     ▼
Apply network impairment
     │
     ▼
Start iperf3 server
     │
     ▼
Generate TCP/UDP traffic
     │
     ├──────────────┐
     ▼              ▼
  iperf3           ping
     │              │
     └──────┬───────┘
            ▼
      Store raw data
            │
            ▼
      Process results
            │
            ▼
   Statistical analysis
            │
            ▼
      Visualizations
            │
            ▼
        Report
```

Each experimental condition is repeated at least three times.

The default suite therefore contains:

```text
5 conditions
× 2 protocols
× 3 repetitions
────────────────
30 traffic experiments
```

---

# Requirements

## Supported Environment

Primary development environment:

- Linux
- Nix/NixOS recommended

The project relies on Linux networking primitives and therefore is **not natively supported on Windows or macOS**.

## Required privileges

Network namespaces and traffic-control configuration generally require elevated privileges.

NetLab minimizes privileged operations and does not require the entire application to run as root.

## Dependencies

The environment requires:

- `iproute2`
- `iperf3`
- `iputils` / `ping`
- `tcpdump` — optional
- Python 3
- pandas
- NumPy
- Matplotlib

Nix users can obtain these through the project's development environment.

---

# Quick Start

## 1. Clone

```bash
git clone https://github.com/<owner>/netlab.git
cd netlab
```

## 2. Enter the development environment

With Nix:

```bash
nix develop
```

Verify:

```bash
iperf3 --version
ip -V
tc -V
python --version
```

## 3. Create the experimental network

```bash
netlab setup
```

Expected topology:

```text
client namespace
10.0.0.1
     │
     │ veth
     │
10.0.0.2
server namespace
```

## 4. Verify connectivity

```bash
netlab ping
```

Example:

```text
$ netlab ping

Network validation
──────────────────
Client namespace : OK
Server namespace : OK
Client address   : 10.0.0.1
Server address   : 10.0.0.2

PING 10.0.0.2
64 bytes from 10.0.0.2: icmp_seq=1 ttl=64 time=0.08 ms
64 bytes from 10.0.0.2: icmp_seq=2 ttl=64 time=0.07 ms
64 bytes from 10.0.0.2: icmp_seq=3 ttl=64 time=0.08 ms

Connectivity: PASS
```

## 5. Run a TCP experiment

```bash
netlab run \
  --protocol tcp \
  --condition baseline
```

## 6. Run a UDP experiment

```bash
netlab run \
  --protocol udp \
  --condition baseline
```

## 7. Run the complete experiment suite

```bash
netlab run-suite
```

## 8. Analyze

```bash
netlab analyze
```

## 9. Generate figures

```bash
netlab plot
```

## 10. Clean up

```bash
netlab clean
```

---

# Demo

The following demonstrates the conceptual workflow.

## Baseline

```bash
netlab apply --condition baseline
netlab run --protocol tcp --condition baseline
```

Example output:

```text
Experiment
──────────
Protocol       : TCP
Condition      : baseline
Delay          : 0 ms
Packet loss    : 0%
Duration       : 10 s

Throughput     : 94.82 Mbps
Retransmits    : 0

Result         : PASS
Raw data       : data/raw/baseline/tcp/run-01.json
```

Now run UDP:

```bash
netlab run --protocol udp --condition baseline
```

Example:

```text
Experiment
──────────
Protocol       : UDP
Condition      : baseline
Delay          : 0 ms
Packet loss    : 0%
Offered rate   : 100 Mbps
Duration       : 10 s

Throughput     : 99.74 Mbps
Jitter         : 0.041 ms
Packet loss    : 0.00%

Result         : PASS
Raw data       : data/raw/baseline/udp/run-01.json
```

> Numerical values above are illustrative. Actual measurements depend on the host and environment.

---

# Applying Network Impairments

## 20 ms delay

```bash
netlab apply --delay 20ms
```

or:

```bash
netlab apply --condition delay_20ms
```

## 50 ms delay

```bash
netlab apply --condition delay_50ms
```

## 1% packet loss

```bash
netlab apply --condition loss_1pct
```

## 3% packet loss

```bash
netlab apply --condition loss_3pct
```

The system records the configured condition in the experiment metadata.

---

# Configuration

Experiments are configuration-driven.

Example:

```yaml
name: delay_20ms

network:
  delay_ms: 20
  loss_percent: 0

protocols:
  - tcp
  - udp

runs: 3
duration_seconds: 10

udp:
  offered_rate_mbps: 100
```

This allows new experiments to be added without changing the experiment runner.

For example:

```yaml
name: custom_loss

network:
  delay_ms: 10
  loss_percent: 2

protocols:
  - tcp
  - udp

runs: 5
duration_seconds: 30

udp:
  offered_rate_mbps: 50
```

---

# Data Pipeline

Raw measurements are never overwritten.

```text
iperf3 JSON
     │
     ▼
┌─────────────┐
│ Raw Dataset │
└──────┬──────┘
       ▼
┌─────────────┐
│   Parser    │
└──────┬──────┘
       ▼
┌─────────────┐
│ Normalized  │
│   Dataset   │
└──────┬──────┘
       ▼
┌─────────────┐
│ Statistics  │
└──────┬──────┘
       ▼
┌─────────────┐
│ Visualizer  │
└──────┬──────┘
       ▼
    Figures
```

---

# Metrics

## TCP

The analysis pipeline collects, where available:

- throughput
- interval throughput
- retransmissions
- duration

## UDP

The analysis pipeline collects:

- offered rate
- throughput
- jitter
- packet loss
- packets sent
- packets received
- duration

## Network

The project independently measures:

- minimum RTT
- average RTT
- maximum RTT
- ICMP packet loss

---

# Output

A typical experiment produces:

```text
data/
├── raw/
│   └── delay_20ms/
│       ├── tcp/
│       │   ├── run-01.json
│       │   ├── run-02.json
│       │   └── run-03.json
│       │
│       └── udp/
│           ├── run-01.json
│           ├── run-02.json
│           └── run-03.json
│
├── processed/
│   └── results.csv
│
└── sample/
```

Figures:

```text
figures/
├── tcp-throughput-delay.png
├── tcp-throughput-loss.png
├── tcp-retransmissions-loss.png
├── udp-throughput-delay.png
├── udp-throughput-loss.png
├── udp-jitter.png
├── udp-loss.png
└── rtt-delay.png
```

---

# Example Analysis

After running the experiment suite:

```bash
netlab analyze
```

the processed dataset can conceptually look like:

| Protocol | Condition | Throughput | RTT | Loss | Jitter |
|---|---|---:|---:|---:|---:|
| TCP | baseline | 94.8 Mbps | 0.2 ms | — | — |
| TCP | 20 ms | 93.1 Mbps | 40.2 ms | — | — |
| TCP | 50 ms | 87.6 Mbps | 100.1 ms | — | — |
| UDP | baseline | 99.7 Mbps | 0.2 ms | 0.0% | 0.04 ms |
| UDP | loss_1pct | 98.8 Mbps | 0.2 ms | 1.0% | 0.12 ms |
| UDP | loss_3pct | 96.7 Mbps | 0.2 ms | 3.0% | 0.31 ms |

> Values are illustrative and must not be interpreted as actual project results.

---

# Visualization

Generate all figures:

```bash
netlab plot
```

Example conceptual output:

```text
TCP Throughput vs Delay

Throughput
   │
100│ ●
 90│       ●
 80│              ●
   │
   └────────────────────
      0      20      50
             Delay (ms)
```

The actual plotting system generates publication/report-ready figures rather than ASCII graphs.

---

# Packet Capture

For protocol-level investigation:

```bash
netlab run \
  --protocol tcp \
  --condition loss_1pct \
  --capture
```

Packet captures can be inspected using Wireshark:

```bash
wireshark captures/<experiment>.pcap
```

Useful observations include:

- TCP sequence numbers
- ACKs
- retransmissions
- connection establishment
- packet timing
- UDP datagrams
- packet loss patterns

Packet capture is a diagnostic tool and is not required for every experiment.

---

# Experiment Metadata

Every run receives a unique identifier.

Example:

```json
{
  "experiment_id": "2026-10-08T120000Z_loss_1pct_tcp_run_01",
  "protocol": "tcp",
  "condition": "loss_1pct",
  "delay_ms": 0,
  "loss_percent": 1,
  "duration_seconds": 10,
  "run_number": 1,
  "client_ip": "10.0.0.1",
  "server_ip": "10.0.0.2"
}
```

Where practical, metadata also records:

- Git commit
- Linux kernel version
- iperf3 version
- Python version
- experiment configuration
- host information

This allows results to be traced back to the exact experiment configuration.

---

# Reproducibility

A central design principle is:

```text
Configuration
      ↓
Experiment
      ↓
Raw Evidence
      ↓
Analysis
      ↓
Visualization
      ↓
Report
```

The repository should contain everything necessary to reproduce the experiment except environment-specific system state.

Experiments should never depend on undocumented manual commands.

---

# Research Questions

NetLab is designed to investigate:

### RQ1

How does increasing network delay affect TCP and UDP throughput?

### RQ2

How does packet loss affect TCP throughput and retransmission behavior?

### RQ3

How does packet loss affect UDP throughput, jitter, and observed packet loss?

### RQ4

How does measured RTT correspond to configured network delay?

### RQ5

What observable behavioral differences exist between TCP and UDP under identical network impairments?

---

# Scientific Approach

NetLab deliberately separates:

### Observation

> What did the experiment measure?

### Explanation

> What networking mechanism could explain the observation?

### Conclusion

> What can legitimately be inferred from the experiment?

The project must not assume that one protocol is universally superior.

The correct conclusion depends on:

- network conditions;
- application requirements;
- reliability requirements;
- latency requirements;
- observed protocol behavior.

---

# Limitations

This project deliberately uses a controlled virtual environment.

Therefore:

- both endpoints run on one physical host;
- virtual networking is not equivalent to a physical network;
- `tc netem` approximates real network impairments;
- host CPU scheduling can affect results;
- virtual interfaces differ from physical interfaces;
- results may vary across kernels and hardware;
- five network conditions do not represent all Internet conditions.

The results should therefore be interpreted as **controlled experimental observations**, not universal Internet benchmarks.

---

# Project Structure

```text
netlab/
├── flake.nix
├── flake.lock
├── README.md
│
├── config/
│   ├── default.yaml
│   └── experiments.yaml
│
├── src/
│   └── netlab/
│       ├── cli.py
│       ├── config.py
│       ├── topology.py
│       ├── impairment.py
│       ├── traffic.py
│       ├── measurement.py
│       ├── capture.py
│       ├── runner.py
│       ├── parser.py
│       ├── statistics.py
│       ├── plotting.py
│       └── reporting.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample/
│
├── figures/
├── reports/
├── captures/
├── tests/
└── docs/
```

---

# CLI Reference

| Command | Purpose |
|---|---|
| `netlab setup` | Create the virtual network |
| `netlab status` | Show topology status |
| `netlab ping` | Verify connectivity and RTT |
| `netlab apply` | Apply network impairment |
| `netlab run` | Run one experiment |
| `netlab run-suite` | Run the configured experiment suite |
| `netlab analyze` | Process experimental data |
| `netlab plot` | Generate figures |
| `netlab report` | Generate report artifacts |
| `netlab clean` | Remove experimental resources |

Run:

```bash
netlab --help
```

for the current command interface.

---

# Development

## Enter development environment

```bash
nix develop
```

## Run tests

```bash
pytest
```

## Run static checks

```bash
# Project-specific checks will be documented here.
```

## Run a development experiment

```bash
netlab setup
netlab run --protocol tcp --condition baseline
netlab clean
```

Do not run experiments against the host's real network interface.

---

# Testing Strategy

The project uses three levels of testing.

### Unit tests

- configuration parsing
- validation
- JSON parsing
- statistical calculations
- dataset transformations

### Integration tests

- namespace creation
- veth connectivity
- `tc` configuration
- iperf3 execution
- data collection

### End-to-End

```text
setup
 ↓
impair
 ↓
run
 ↓
collect
 ↓
analyze
 ↓
plot
```

Sample datasets allow the analysis pipeline to be tested without privileged networking.

---

# Roadmap

## Phase 1 — Network Foundation

- [ ] Nix development environment
- [ ] namespace manager
- [ ] veth topology
- [ ] IP configuration
- [ ] connectivity validation
- [ ] cleanup

## Phase 2 — Traffic Generation

- [ ] TCP iperf3 integration
- [ ] UDP iperf3 integration
- [ ] fixed UDP offered rate
- [ ] JSON collection

## Phase 3 — Network Impairment

- [ ] delay
- [ ] packet loss
- [ ] condition configuration
- [ ] automated application/removal

## Phase 4 — Experiment Runner

- [ ] experiment definitions
- [ ] repetitions
- [ ] metadata
- [ ] resume support
- [ ] failure recovery

## Phase 5 — Analysis

- [ ] JSON parser
- [ ] normalized dataset
- [ ] statistical summaries
- [ ] TCP analysis
- [ ] UDP analysis

## Phase 6 — Visualization

- [ ] throughput plots
- [ ] RTT plots
- [ ] loss plots
- [ ] jitter plots
- [ ] retransmission plots

## Phase 7 — Reporting

- [ ] automated report data
- [ ] methodology documentation
- [ ] results generation
- [ ] reproducibility documentation

---

# Future Work

Potential future extensions include:

- jitter emulation;
- bandwidth limitation;
- packet reordering;
- packet corruption;
- packet duplication;
- QUIC experiments;
- SCTP experiments;
- multi-router topologies;
- RIP/OSPF experiments;
- routing experiments;
- more complex network graphs.

These are outside the initial scope.

---

# Contributing

Contributions should preserve the project's core principle:

> **Configuration → Controlled Experiment → Raw Evidence → Analysis → Interpretation**

When adding a new experiment:

1. Define the experimental condition.
2. Add configuration.
3. Preserve raw output.
4. Add metadata.
5. Update parsers if required.
6. Add analysis.
7. Add tests.
8. Document the experiment.
9. Do not hard-code results or conclusions.

---

# License

This project is licensed under the terms specified in [`LICENSE`](LICENSE).

---

# Acknowledgements

This project builds upon established open-source networking tools and Linux networking primitives, particularly:

- Linux network namespaces
- Linux `tc` / `netem`
- `iperf3`
- Wireshark / tcpdump
- Python
- pandas
- NumPy
- Matplotlib

---

# Author

**Ojaswi Om**

Computer Science & Engineering  
VIT Vellore

---

## Project Philosophy

```text
Don't just learn that TCP reacts to packet loss.

Create the loss.

Measure the reaction.

Capture the packets.

Analyze the numbers.

Then explain why it happened.
```
