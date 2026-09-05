# Agentic-Pathfinder

**Agentic-Pathfinder** is a local-first Python security automation framework designed for graph-driven post-exploitation analysis and lateral movement planning in Active Directory environments.

By combining **Neo4j** (BloodHound graph topographies) with a decoupled multi-agent architecture, the pipeline queries optimal attack paths, evaluates operational security (OpSec) risks against host-level EDR/AV controls, and generates populated, actionable command-line execution payloads.

---

## Key Features

* **Graph-Driven Pathfinding:** Interrogates Neo4j/BloodHound graph data using a modular Cypher query skill set to calculate shortest paths to Domain Admins, high-value assets, and active session locations.
* **Multi-Agent Orchestration:**
  * **GraphAnalyst:** Interrogates graph relationships and extracts lateral attack paths.
  * **OpSecAssessor:** Evaluates technical detection risks (1–10 scale) and applies dynamic risk escalations for active security controls (CrowdStrike, Defender for Endpoint, SentinelOne, Cortex XDR).
  * **CommandSynthesizer:** Populates execution templates (WinRM, WMI, Pass-the-Hash, PsExec) with targeted credentials and execution parameters.
* **Flexible Reporting:** Exports structured Markdown assessment tables, technical execution playbooks, or raw JSON structures for downstream tooling.
* **Offline / Mock Testing Mode:** Supports full pipeline execution without requiring an active Neo4j database connection using built-in mock modes.
* **Robust Quality Assurance:** Test-driven architecture backed by unit and integration tests via `pytest`.

---

## Project Architecture
```
Agentic-Pathfinder/
├── src/
│   ├── agents/
│   │   ├── command_synthesizer.py  # Populates execution syntaxes
│   │   ├── graph_analyst.py        # Neo4j & Cypher query interface
│   │   └── opsec_assessor.py       # Evaluates OpSec risk & EDR escalation
│   ├── models/
│   │   ├── host_state.py           # Pydantic v2 schema for host states
│   │   └── plan_step.py            # Pydantic v2 schema for plan steps
│   ├── skills/
│   │   ├── bloodhound_queries.py   # Centralized Cypher query builders
│   │   └── report_formatter.py    # Formats plans into Markdown reports
│   ├── main.py                     # CLI entry point
│   └── orchestrator.py             # Multi-agent execution pipeline
├── tests/                          # Unit and integration test suite
├── requirements.txt
└── README.md
```
---

## Prerequisites

* **Python:** 3.10+
* **Neo4j Database:** (Optional for live analysis) BloodHound dataset loaded into Neo4j via Bolt (`bolt://localhost:7687`).

---

## Installation

1. Clone the repository:
   ```bash
   git clone [https://github.com/YourUsername/Agentic-Pathfinder.git](https://github.com/YourUsername/Agentic-Pathfinder.git)
   cd Agentic-Pathfinder
   

---

## Virtual Environment and Dependencies
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
```
# Usage Examples

1. Run Pipeline in Mock Mode (Offline Testing)
    ```bash
       python -m src.main -s WORKSTATION01.CORP.LOCAL -t DC01.CORP.LOCAL --edr "CrowdStrike Falcon" --mock 
   ```
2. Generate Markdown Assessment Report
    ```bash
   python -m src.main -s WORKSTATION01.CORP.LOCAL -t DC01.CORP.LOCAL --edr "Defender for Endpoint" --mock --markdown -o report.md
    ```
3. Export Plan as Raw JSON
    ```bash
   python -m src.main -s WORKSTATION01.CORP.LOCAL -t DC01.CORP.LOCAL --command "ipconfig /all" --mock --json
    ```
---

# Running Unit Tests
```
Execute the full test suite using: pytest

pytest -v

``` 