from unittest.mock import MagicMock
from src.orchestrator import PathfinderOrchestrator


def test_orchestrator_pipeline_execution():
    # Mock GraphAnalyst output
    mock_graph_analyst = MagicMock()
    mock_graph_analyst.get_outbound_execution_paths.return_value = [
        {
            "source_name": "WORKSTATION01.CORP.LOCAL",
            "target_name": "DC01.CORP.LOCAL",
            "relationship_type": "CanPSRemote"
        }
    ]

    # Instantiate orchestrator with mock analyst
    orchestrator = PathfinderOrchestrator(graph_analyst=mock_graph_analyst)

    # Define target security controls
    controls_map = {
        "DC01.CORP.LOCAL": ["CrowdStrike Falcon"]
    }

    # Execute end-to-end pipeline
    plan = orchestrator.generate_lateral_movement_plan(
        source_host="WORKSTATION01.CORP.LOCAL",
        host_controls_map=controls_map,
        command_payload="hostname",
        username="DomainAdmin",
        domain="CORP.LOCAL"
    )

    # Assertions
    assert len(plan) == 1
    step = plan[0]

    assert step.step_id == 1
    assert step.technique_name == "WinRM"
    assert step.source_host == "WORKSTATION01.CORP.LOCAL"
    assert step.target_host == "DC01.CORP.LOCAL"

    # Verify OpSec escalation for EDR
    assert step.opsec_risk_score == 5  # WinRM (3 base) + 2 for CrowdStrike
    assert "CrowdStrike Falcon" in step.reason_for_risk

    # Verify Command Synthesis
    assert "Invoke-Command" in step.execution_command_template
    assert "hostname" in step.execution_command_template