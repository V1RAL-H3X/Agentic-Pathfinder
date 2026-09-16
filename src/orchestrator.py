import os
from typing import Dict, List, Optional, Any
from crewai import Crew, Task, LLM

# Import all modular agent factory functions
from src.crew.agents.graph_recon import create_graph_recon_agent
from src.crew.agents.infrastructure_scanning import create_infrastructure_scanning_agent
from src.crew.agents.attack_mapping import create_attack_mapping_agent
from src.crew.agents.mobile_assessment import create_mobile_assessment_agent
from src.crew.agents.llm_safety_testing import create_llm_safety_testing_agent
from src.crew.agents.exploit_execution import create_exploit_execution_agent


class PathfinderOrchestrator:
    """
    Main pipeline orchestrator for Agentic-Pathfinder using CrewAI and Ollama.
    Executes specific security agents strictly on user-defined opt-in parameters.
    """

    def __init__(self, model_name: str = "ollama/llama3.1", base_url: str = "http://localhost:11434"):
        # Force LiteLLM to treat local ollama correctly via environment variables
        os.environ["OPENAI_API_KEY"] = "not-needed"
        os.environ["OPENAI_API_BASE"] = base_url

        # Ensure model is formatted for LiteLLM
        if not model_name.startswith("ollama/"):
            model_name = f"ollama/{model_name}"

        self.local_llm = LLM(
            model=model_name,
            base_url=base_url,
            api_key="not-needed"
        )

    def run_assessment(
            self,
            source_host: Optional[str] = None,
            target_host: Optional[str] = None,
            run_graph_recon: bool = False,
            run_infrastructure_scan: bool = False,
            run_attack_mapping: bool = False,
            mobile_binary_path: Optional[str] = None,
            llm_endpoint: Optional[str] = None,
            exploit_target: Optional[str] = None,
            exploit_module: Optional[str] = None,
            dry_run_exploit: bool = True
    ) -> Any:
        """
        Dynamically builds and runs a CrewAI crew using only the modules
        explicitly requested by the user.
        """
        agents_list = []
        tasks_list = []

        # 1. Active Directory Graph Recon (BloodHound / Neo4j)
        if run_graph_recon and source_host:
            graph_agent = create_graph_recon_agent(self.local_llm)
            agents_list.append(graph_agent)
            tasks_list.append(
                Task(
                    description=f"Interrogate BloodHound graph paths originating from {source_host} targeting {target_host or 'Domain Controllers'}.",
                    expected_output="Structured JSON list of graph edges, relationship types, and movement paths.",
                    agent=graph_agent
                )
            )

        # 2. Infrastructure Vulnerability Scanning (OpenVAS)
        if run_infrastructure_scan and (source_host or target_host):
            target = target_host or source_host
            infra_agent = create_infrastructure_scanning_agent(self.local_llm)
            agents_list.append(infra_agent)
            tasks_list.append(
                Task(
                    description=f"Execute vulnerability assessment scans against target asset {target}.",
                    expected_output="Prioritized list of unpatched CVEs and service misconfigurations.",
                    agent=infra_agent
                )
            )

        # 3. Threat Intelligence & Attack Mapping (MITRE ATT&CK)
        if run_attack_mapping:
            attack_map_agent = create_attack_mapping_agent(self.local_llm)
            agents_list.append(attack_map_agent)
            tasks_list.append(
                Task(
                    description="Analyze previous scan results or target behaviors and map them to MITRE ATT&CK tactical techniques.",
                    expected_output="Tactical threat mapping report with precise TTP identifiers.",
                    agent=attack_map_agent
                )
            )

        # 4. Mobile Application Assessment (MobSF)
        if mobile_binary_path:
            mobile_agent = create_mobile_assessment_agent(self.local_llm)
            agents_list.append(mobile_agent)
            tasks_list.append(
                Task(
                    description=f"Perform static binary analysis on mobile application package at {mobile_binary_path}.",
                    expected_output="Mobile security summary detailing hardcoded secrets, weak crypto, and API weaknesses.",
                    agent=mobile_agent
                )
            )

        # 5. AI Endpoint Safety Testing (Garak)
        if llm_endpoint:
            llm_safety_agent = create_llm_safety_testing_agent(self.local_llm)
            agents_list.append(llm_safety_agent)
            tasks_list.append(
                Task(
                    description=f"Execute Garak vulnerability scan suites against target AI model endpoint at {llm_endpoint}.",
                    expected_output="AI red-teaming report identifying prompt injection, data leakage, or safety bypass vectors.",
                    agent=llm_safety_agent
                )
            )

        # 6. Exploit Execution & Verification (Metasploit)
        if exploit_target and exploit_module:
            exploit_agent = create_exploit_execution_agent(self.local_llm)
            agents_list.append(exploit_agent)

            mode_str = "DRY RUN" if dry_run_exploit else "LIVE EXECUTION"
            tasks_list.append(
                Task(
                    description=f"Verify target path against {exploit_target} using Metasploit module '{exploit_module}' under {mode_str} policy.",
                    expected_output="Execution status log and validation report confirming control accessibility.",
                    agent=exploit_agent
                )
            )

        # Ensure at least one agent and task are selected before kicking off
        if not agents_list:
            raise ValueError(
                "No agents were selected for execution. Please enable at least one module flag or target parameter.")

        # Assemble and kickoff the custom-scoped Crew
        scoped_crew = Crew(
            agents=agents_list,
            tasks=tasks_list,
            verbose=True
        )

        return scoped_crew.kickoff()