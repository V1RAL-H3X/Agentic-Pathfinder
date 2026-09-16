# main.py
import argparse
import os
import subprocess
from src.orchestrator import PathfinderOrchestrator


def get_wsl_gateway_ip() -> str:
    """ Returns the Windows host IP from inside WSL """
    # Replace "172.X.X.X" with your actual Windows host IP if auto-detection fails
    windows_ip = "172.31.0.1"
    if windows_ip != "172.30.0.1":
        return windows_ip

    try:
        gateway_ip = subprocess.check_output(
            "ip route show | grep default | awk '{print $3}'",
            shell=True,
            text=True
        ).strip()
        if gateway_ip:
            return gateway_ip
    except Exception:
        pass
    return "localhost"


def main():
    parser = argparse.ArgumentParser(description="Agentic-Pathfinder Security Automation Framework")
    parser.add_argument("--source", type=str, help="Source host or workstation")
    parser.add_argument("--target", type=str, help="Target host or domain controller")
    parser.add_argument("--mock", action="store_true", help="Enable offline mock mode execution")
    parser.add_argument("--run-graph-recon", action="store_true", help="Execute BloodHound/Neo4j graph analysis")
    parser.add_argument("--run-infrastructure-scan", action="store_true",
                        help="Execute infrastructure vulnerability scan")
    parser.add_argument("--run-attack-mapping", action="store_true", help="Execute MITRE ATT&CK mapping")

    args = parser.parse_args()

    # Configure mock environment variable if flagged
    if args.mock:
        os.environ["PATHFINDER_MOCK_MODE"] = "true"

    # Route Ollama correctly whether running native Linux or WSL
    if "WSL_DISTRO_NAME" in os.environ or os.path.exists("/etc/wsl.conf"):
        host_ip = get_wsl_gateway_ip()
        ollama_url = f"http://{host_ip}:11434"
    else:
        ollama_url = "http://localhost:11434"

    print(f"[*] Initializing PathfinderOrchestrator connecting to Ollama at {ollama_url}...")

    orchestrator = PathfinderOrchestrator(
        model_name="ollama/llama3.1",
        base_url=ollama_url
    )

    try:
        result = orchestrator.run_assessment(
            source_host=args.source,
            target_host=args.target,
            run_graph_recon=args.run_graph_recon,
            run_infrastructure_scan=args.run_infrastructure_scan,
            run_attack_mapping=args.run_attack_mapping
        )
        print("\n=== Assessment Completed Successfully ===")
        print(result)
    except Exception as e:
        print(f"\n[!] Pipeline Error: {str(e)}")


if __name__ == "__main__":
    main()