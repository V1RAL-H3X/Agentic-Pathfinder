from typing import Dict, List, Optional, Any
from src.models.plan_step import PlanStep
from src.agents.graph_analyst import GraphAnalyst
from src.agents.opsec_assessor import OpSecAssessor
from src.agents.command_synthesizer import CommandSynthesizer


class PathfinderOrchestrator:
    """
    Main pipeline orchestrator for Agentic-Pathfinder.

    Coordinates the sub-agents (GraphAnalyst, OpSecAssessor, CommandSynthesizer)
    to query Neo4j attack paths, parse raw graph relationships into structured PlanSteps,
    evaluate OpSec risk against target host security controls, and synthesize execution commands.
    """

    # Mapping BloodHound relationship types to tactical lateral movement techniques
    RELATIONSHIP_TECHNIQUE_MAP: Dict[str, str] = {
        "AdminTo": "Pass-the-Hash",
        "CanPSRemote": "WinRM",
        "ExecuteDCOM": "DCOM",
        "CanRDP": "RDP",
        "HasSession": "PsExec"
    }

    def __init__(
            self,
            graph_analyst: Optional[GraphAnalyst] = None,
            opsec_assessor: Optional[OpSecAssessor] = None,
            command_synthesizer: Optional[CommandSynthesizer] = None
    ):
        self.graph_analyst = graph_analyst or GraphAnalyst()
        self.opsec_assessor = opsec_assessor or OpSecAssessor()
        self.command_synthesizer = command_synthesizer or CommandSynthesizer()

    def parse_graph_edges_to_plan(self, graph_edges: List[Dict[str, Any]]) -> List[PlanStep]:
        """
        Converts raw Neo4j graph edge outputs into un-evaluated PlanStep objects.
        """
        steps: List[PlanStep] = []
        for index, edge in enumerate(graph_edges, start=1):
            rel_type = edge.get("relationship_type", "AdminTo")
            technique = self.RELATIONSHIP_TECHNIQUE_MAP.get(rel_type, "WMI")
            source_host = edge.get("source_name", "UNKNOWN_SOURCE")
            target_host = edge.get("target_name", "UNKNOWN_TARGET")

            step = PlanStep(
                step_id=index,
                source_host=source_host,
                target_host=target_host,
                technique_name=technique,
                opsec_risk_score=5,  # Default baseline prior to OpSec assessment
                reason_for_risk="Pending OpSec evaluation",
                execution_command_template=""
            )
            steps.append(step)

        return steps

    def generate_lateral_movement_plan(
            self,
            source_host: str,
            target_host: Optional[str] = None,
            host_controls_map: Optional[Dict[str, List[str]]] = None,
            command_payload: str = "whoami",
            username: str = "Administrator",
            domain: str = "CORP.LOCAL"
    ) -> List[PlanStep]:
        """
        Executes the full end-to-end pathfinding pipeline:
        1. Queries Neo4j for outbound edges or pathing.
        2. Converts graph relationships into structured PlanSteps.
        3. Evaluates OpSec risk scores based on target security controls.
        4. Synthesizes executable command syntaxes for each step.
        """
        host_controls_map = host_controls_map or {}

        # Step 1: Query Neo4j via GraphAnalyst
        if target_host:
            raw_edges = self.graph_analyst.find_shortest_path(source_host, target_host)
        else:
            raw_edges = self.graph_analyst.get_outbound_execution_paths(source_host)

        # Step 2: Parse raw graph edges into PlanStep objects
        steps = self.parse_graph_edges_to_plan(raw_edges)

        # Step 3 & 4: Evaluate OpSec risk and synthesize execution commands
        final_plan: List[PlanStep] = []
        for step in steps:
            target_controls = host_controls_map.get(step.target_host, [])

            # OpSec evaluation
            evaluated_step = self.opsec_assessor.evaluate_step(
                step, target_security_controls=target_controls
            )

            # Command synthesis
            populated_step = self.command_synthesizer.populate_step_command(
                evaluated_step,
                command=command_payload,
                username=username,
                domain=domain
            )

            final_plan.append(populated_step)

        return final_plan