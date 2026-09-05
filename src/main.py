import argparse
import json
import sys
from typing import Dict, List
from unittest.mock import MagicMock

from src.orchestrator import PathfinderOrchestrator
from src.agents.graph_analyst import GraphAnalyst
from src.skills.report_formatter import export_full_report_markdown


def parse_args():
    parser = argparse.ArgumentParser(
        description="Agentic-Pathfinder: Graph-Driven Lateral Movement Pipeline"
    )
    parser.add_argument(
        "-s", "--source", required=True, help="Source host FQDN (e.g., WORKSTATION01.CORP.LOCAL)"
    )
    parser.add_argument(
        "-t", "--target", help="Target host FQDN (optional, e.g., DC01.CORP.LOCAL)"
    )
    parser.add_argument(
        "-u", "--user", default="Administrator", help="Target username for command synthesis"
    )
    parser.add_argument(
        "-d", "--domain", default="CORP.LOCAL", help="Target Active Directory domain"
    )
    parser.add_argument(
        "-c", "--command", default="whoami", help="Command payload to execute"
    )
    parser.add_argument(
        "--edr", help="Comma-separated list of detected target security controls (e.g., 'CrowdStrike,Defender')"
    )
    parser.add_argument(
        "--mock", action="store_true", help="Run with mock graph data (no live Neo4j required)"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output lateral movement plan as raw JSON"
    )
    parser.add_argument(
        "--markdown", action="store_true", help="Export lateral movement assessment report as Markdown"
    )
    parser.add_argument(
        "-o", "--output", help="Optional output file path to save JSON or Markdown report"
    )
    return parser.parse_args()


def get_mock_graph_analyst(source: str, target: str) -> GraphAnalyst:
    """Builds a mocked GraphAnalyst instance for offline testing without Neo4j."""
    mock_analyst = MagicMock(spec=GraphAnalyst)
    if target:
        mock_analyst.find_shortest_path.return_value = [
            {
                "source_name": source,
                "target_name": target,
                "relationship_type": "CanPSRemote"
            }
        ]
    else:
        mock_analyst.get_outbound_execution_paths.return_value = [
            {
                "source_name": source,
                "target_name": "SERVER01.CORP.LOCAL",
                "relationship_type": "AdminTo"
            },
            {
                "source_name": source,
                "target_name": "DC01.CORP.LOCAL",
                "relationship_type": "CanPSRemote"
            }
        ]
    return mock_analyst


def print_formatted_plan(plan: List[any]):
    """Pretty-prints the plan steps in terminal."""
    print("\n" + "=" * 70)
    print(" AGENTIC-PATHFINDER: SYNTHESIZED LATERAL MOVEMENT PLAN")
    print("=" * 70)

    for step in plan:
        print(f"\n[Step {step.step_id}] {step.source_host}  ==[{step.technique_name}]==>  {step.target_host}")
        print(f"  ├─ OpSec Risk Score: {step.opsec_risk_score}/10")
        print(f"  ├─ Risk Assessment : {step.reason_for_risk}")
        print(f"  └─ Exec Command    : {step.execution_command_template}")

    print("\n" + "=" * 70 + "\n")


def main():
    args = parse_args()

    # Parse EDR controls if provided
    host_controls_map: Dict[str, List[str]] = {}
    if args.edr:
        controls = [ctrl.strip() for ctrl in args.edr.split(",")]
        target_key = args.target if args.target else "DC01.CORP.LOCAL"
        host_controls_map[target_key] = controls

    # Initialize GraphAnalyst (live or mock)
    if args.mock:
        print("[*] Running in MOCK mode (bypassing Neo4j connection)...", file=sys.stderr)
        analyst = get_mock_graph_analyst(args.source, args.target)
    else:
        try:
            analyst = GraphAnalyst()
        except Exception as e:
            print(f"[-] Failed to connect to Neo4j database: {e}", file=sys.stderr)
            print("[!] Tip: Pass --mock flag to test the pipeline without a live Neo4j instance.", file=sys.stderr)
            sys.exit(1)

    # Instantiate orchestrator and generate plan
    orchestrator = PathfinderOrchestrator(graph_analyst=analyst)

    plan = orchestrator.generate_lateral_movement_plan(
        source_host=args.source,
        target_host=args.target,
        host_controls_map=host_controls_map,
        command_payload=args.command,
        username=args.user,
        domain=args.domain
    )

    if not plan:
        print("[-] No lateral movement paths found for given criteria.", file=sys.stderr)
        sys.exit(0)

    # Format output content
    if args.json:
        output_content = json.dumps([step.model_dump() for step in plan], indent=2)
    elif args.markdown:
        output_content = export_full_report_markdown(plan)
    else:
        output_content = None

    # Write to file or stdout
    if args.output and output_content:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_content)
        print(f"[+] Report exported successfully to {args.output}", file=sys.stderr)
    elif output_content:
        print(output_content)
    else:
        print_formatted_plan(plan)


if __name__ == "__main__":
    main()