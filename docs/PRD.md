# PRD — Controlled TCP/UDP Network Performance Experimental Framework

## 1. Overview

Build a reproducible Linux-based networking laboratory for experimentally evaluating **TCP and UDP under controlled network impairments**.

The system will create an isolated virtual client-server network, generate TCP/UDP traffic, introduce configurable delay and packet loss, collect measurements, analyze results, generate visualizations, and produce the material required for a technical academic report.

The academic report is an **output of the experimental framework**, not the definition of the project.

---

## 2. Core Research Question

> How do TCP and UDP behave when network conditions such as latency and packet loss change?

The project must measure behavior rather than simply assert theoretical differences between TCP and UDP.

---

## 3. Objectives

The system must:

- Create an isolated virtual network on a Linux host.
- Generate TCP and UDP traffic.
- Configure controlled network impairments.
- Measure throughput, RTT, jitter, packet loss, and retransmissions where available.
- Repeat experiments automatically.
- Preserve raw experimental data.
- Process and statistically analyze results.
- Generate meaningful graphs.
- Optionally capture packets for protocol-level investigation.
- Generate reproducible report material.
- Record sufficient metadata to reproduce experiments.

---

## 4. Non-Goals

The project will not:

- Implement TCP/UDP from scratch.
- Simulate the entire Internet.
- Benchmark physical networking hardware.
- Claim universal superiority of TCP or UDP.
- Require external Internet connectivity during experiments.
- Use ML to predict network behavior.
- Select results to support predetermined conclusions.

---

# 5. Architecture

```text
                    Linux Host
┌─────────────────────────────────────────────┐
│                                             │
│ ┌─────────────────┐     ┌─────────────────┐ │
│ │ Client Namespace│     │ Server Namespace│ │
│ │                 │     │                 │ │
│ │ 10.0.0.1        │─────│ 10.0.0.2        │ │
│ │ iperf3 client   │veth │ iperf3 server   │ │
│ └─────────────────┘     └─────────────────┘ │
│              │                              │
│          tc/netem                           │
│       delay / loss                          │
│                                             │
│    iperf3 + ping + tcpdump                  │
│              ↓                              │
│      Python / pandas                        │
│              ↓                              │
│      analysis + graphs                      │
└─────────────────────────────────────────────┘
```

Use native Linux networking primitives:

- network namespaces;
- veth pairs;
- `ip`;
- `tc`;
- `netem`.

Docker should not be the primary networking mechanism.

---

# 6. Environment

Primary development platform:

- NixOS/Linux.

Provide a reproducible Nix development environment containing:

- iproute2 (`ip`, `tc`);
- iperf3;
- ping;
- tcpdump;
- Python;
- pandas;
- NumPy;
- Matplotlib;
- required analysis dependencies.

Preferred entry point:

```bash
nix develop
```

The project should remain usable on Ubuntu/Debian where practical.

---

# 7. Network Topology

Create two isolated namespaces:

```text
client
server
```

Connected by a virtual Ethernet pair:

```text
client:veth-client
        │
        │ virtual Ethernet
        │
server:veth-server
```

Default addresses:

```text
Client: 10.0.0.1
Server: 10.0.0.2
```

The setup system must:

- create namespaces;
- create veth pair;
- assign addresses;
- configure routes;
- bring interfaces up;
- verify connectivity.

Cleanup must remove all created resources safely.

---

# 8. Network Impairment Engine

Provide a configuration-driven abstraction over `tc netem`.

Required impairments:

- delay;
- packet loss.

Default supported conditions:

| Condition | Delay | Loss |
|---|---:|---:|
| baseline | 0 ms | 0% |
| delay_20ms | 20 ms | 0% |
| delay_50ms | 50 ms | 0% |
| loss_1pct | 0 ms | 1% |
| loss_3pct | 0 ms | 3% |

The system must explicitly record:

- configured delay;
- configured loss;
- impairment direction.

Configured one-way delay must not be confused with measured RTT.

Architecture should allow future support for:

- jitter;
- bandwidth limitation;
- duplication;
- corruption;
- reordering.

---

# 9. Experiment Configuration

Experiments must be configuration-driven rather than hard-coded.

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

Configuration format may be YAML, TOML, or JSON; YAML is preferred.

---

# 10. Experimental Matrix

Each condition must test:

- TCP;
- UDP.

Each protocol/condition combination must run at least **3 times**.

Default suite:

```text
5 conditions
× 2 protocols
× 3 repetitions
= 30 experiments
```

The runner should support additional repetitions.

---

# 11. TCP Experiments

Use `iperf3`.

For each run:

1. Configure network.
2. Start server.
3. Apply impairment.
4. Start TCP client.
5. Run for configured duration.
6. Save raw JSON.
7. Record metadata.
8. Repeat.

Collect where available:

- throughput;
- interval throughput;
- retransmissions;
- duration;
- protocol information.

The complete raw iperf3 JSON must be preserved.

---

# 12. UDP Experiments

Use `iperf3` with a **fixed, configurable offered rate**.

Collect:

- offered rate;
- achieved throughput;
- packet loss;
- jitter;
- packet counts;
- interval measurements;
- duration.

The offered rate must be recorded as part of experiment metadata.

The complete raw iperf3 JSON must be preserved.

---

# 13. RTT Measurement

Measure RTT independently using `ping`.

Record:

- minimum;
- maximum;
- average;
- packet loss;
- number of probes.

RTT must remain separate from configured one-way delay.

---

# 14. Packet Capture

Support optional diagnostic packet capture using:

- tcpdump;
- Wireshark.

Normal experiments should not require packet capture.

Diagnostic mode should allow investigation of:

### TCP

- connection establishment;
- sequence numbers;
- acknowledgements;
- retransmissions;
- timing.

### UDP

- datagram transmission;
- packet timing;
- packet loss.

Packet capture complements iperf3 measurements rather than replacing them.

---

# 15. Experiment Runner

Provide a central runner that automates:

```text
load configuration
      ↓
validate
      ↓
setup network
      ↓
verify connectivity
      ↓
apply impairment
      ↓
start server
      ↓
run traffic
      ↓
collect measurements
      ↓
collect RTT
      ↓
optional packet capture
      ↓
store results
      ↓
cleanup
```

The runner must:

- fail safely;
- clean up after errors;
- identify completed runs;
- support resuming interrupted experiment suites.

---

# 16. Metadata

Every run must have a unique experiment ID and store:

- timestamp;
- protocol;
- condition;
- delay;
- loss;
- duration;
- run number;
- client/server addresses;
- software versions;
- configuration;
- Git commit where practical.

Example:

```json
{
  "experiment_id": "...",
  "protocol": "tcp",
  "condition": "loss_1pct",
  "delay_ms": 0,
  "loss_percent": 1,
  "run_number": 1,
  "duration_seconds": 10
}
```

---

# 17. Data Architecture

Never overwrite raw results.

```text
data/
├── raw/
├── processed/
└── sample/
```

Raw data should contain original iperf3 output and metadata.

Processed data should contain normalized experiment records.

Recommended fields include:

```text
experiment_id
protocol
condition
delay_ms
loss_percent
run_number
udp_offered_rate
throughput_mbps
rtt_ms
jitter_ms
packet_loss_percent
packets_sent
packets_received
retransmissions
duration_seconds
```

---

# 18. Analysis Pipeline

Implement:

```text
raw JSON
   ↓
parser
   ↓
normalized dataset
   ↓
validation
   ↓
statistics
   ↓
visualization
```

Calculate at minimum:

- mean;
- minimum;
- maximum;
- standard deviation.

Where useful, also calculate:

- median;
- confidence intervals.

Individual runs must remain accessible.

---

# 19. Visualizations

Generate a focused set of meaningful graphs.

Required where applicable:

### TCP

- throughput vs delay;
- throughput vs packet loss;
- retransmissions vs packet loss.

### UDP

- throughput vs delay;
- throughput vs packet loss;
- jitter vs condition;
- packet loss vs condition.

### Network

- RTT vs configured delay.

Every graph must contain:

- labels;
- units;
- meaningful title;
- legend where necessary;
- experimental conditions.

---

# 20. Research Questions

The project should evaluate:

### RQ1
How does increasing network delay affect TCP and UDP throughput?

### RQ2
How does packet loss affect TCP throughput and retransmission behavior?

### RQ3
How does packet loss affect UDP throughput, jitter, and observed loss?

### RQ4
How does measured RTT correspond to configured network delay?

### RQ5
What observable behavioral differences exist between TCP and UDP under identical network impairments?

---

# 21. Analysis Principles

The system must distinguish:

```text
Observation
    ↓
Measurement
    ↓
Interpretation
```

Do not assume the result before running the experiment.

Do not claim:

> TCP is better than UDP.

Instead, analyze the measured trade-offs under each condition.

---

# 22. Reproducibility

Another Linux user should be able to reproduce the experiments from the repository.

Required:

- dependency specification;
- environment configuration;
- experiment definitions;
- automation;
- raw-data format;
- analysis scripts;
- sample data;
- documentation.

Preferred workflow:

```bash
nix develop
netlab setup
netlab run-suite
netlab analyze
netlab plot
netlab report
netlab clean
```

Exact CLI syntax may change during implementation.

---

# 23. CLI

Provide a unified CLI rather than requiring users to remember many unrelated commands.

Expected capabilities:

```text
setup
status
ping
apply impairment
run experiment
run suite
analyze
plot
report
clean
```

Python is preferred for the orchestration layer.

Shell commands should be invoked safely through Python.

---

# 24. Safety

The experiment must remain isolated from the host's normal network.

It must:

- avoid modifying the host's real Internet interface;
- clearly identify privileged operations;
- minimize root execution;
- validate commands;
- provide reliable cleanup.

The experiment should continue working without Internet access after dependencies are installed.

---

# 25. Testing

### Unit tests

Test:

- configuration;
- validation;
- JSON parsing;
- statistics;
- data transformation.

### Integration tests

Test:

- namespace creation;
- veth connectivity;
- iperf3;
- `tc`;
- measurement collection.

### End-to-end test

A small experiment must execute:

```text
setup → impair → run → collect → analyze → plot
```

automatically.

---

# 26. Sample Data

Provide sample data so analysis and visualization can be tested without privileged networking.

This should allow:

```bash
netlab analyze --input sample
```

without running a live experiment.

---

# 27. Report Generation

The framework should generate or provide structured data for a technical report containing:

1. Abstract
2. Introduction
3. Objectives
4. Background
5. Architecture
6. Methodology
7. Experimental Conditions
8. Tools
9. Results
10. Statistical Analysis
11. TCP Analysis
12. UDP Analysis
13. TCP/UDP Comparison
14. Discussion
15. Limitations
16. Threats to Validity
17. Conclusion
18. Future Work
19. References
20. Appendix

The report must distinguish measured results from interpretation.

---

# 28. Limitations

The report must explicitly state that:

- both endpoints run on one physical host;
- the virtual link is not equivalent to the public Internet;
- `netem` approximates network impairments;
- host CPU scheduling/load can influence measurements;
- virtual networking differs from physical networking;
- results may vary between systems;
- the selected conditions do not represent every real-world network.

---

# 29. Repository Structure

```text
tcp-udp-network-lab/
├── flake.nix
├── flake.lock
├── README.md
├── config/
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
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample/
├── figures/
├── reports/
├── tests/
└── docs/
```

Exact structure may evolve, but responsibilities must remain separated.

---

# 30. MVP

The minimum working version must provide:

```text
Linux namespaces
        ↓
veth connection
        ↓
TCP + UDP iperf3
        ↓
tc/netem delay + loss
        ↓
JSON results
        ↓
Python analysis
        ↓
basic graphs
```

It must successfully execute the five default conditions for both protocols with repeated runs.

---

# 31. Future Extensions

The architecture should allow future addition of:

- jitter;
- bandwidth limitation;
- packet corruption/reordering;
- QUIC;
- SCTP;
- multi-router topologies;
- routing experiments;
- RIP/OSPF experiments;
- more complex network graphs.

These are outside the initial implementation.

---

# 32. Definition of Done

The project is complete when:

- [ ] Reproducible Linux environment exists.
- [ ] Namespaces and veth topology are automated.
- [ ] Connectivity is automatically verified.
- [ ] TCP experiments work.
- [ ] UDP experiments work at a fixed configurable rate.
- [ ] Delay and packet loss are configurable.
- [ ] Five default conditions execute automatically.
- [ ] Each protocol/condition has ≥3 runs.
- [ ] Raw data is preserved.
- [ ] Metadata is preserved.
- [ ] Experiments can resume after interruption.
- [ ] RTT is measured.
- [ ] Analysis produces statistical summaries.
- [ ] Required graphs are generated.
- [ ] Optional packet capture works.
- [ ] Results are reproducible from configuration.
- [ ] Report material can be generated.
- [ ] Limitations are documented.
- [ ] Repository documentation is complete.

---

# 33. Core Design Principle

The entire project follows:

```text
Configuration
      ↓
Controlled Experiment
      ↓
Raw Evidence
      ↓
Measurement
      ↓
Statistical Analysis
      ↓
Visualization
      ↓
Interpretation
      ↓
Report
```

The project is therefore **not an iperf3 automation script**.

It is a reproducible experimental framework for observing and explaining TCP/UDP behavior under controlled network conditions.
