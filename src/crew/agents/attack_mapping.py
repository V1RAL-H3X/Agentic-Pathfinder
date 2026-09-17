import os
from crewai import Agent, Task
from crewai.tools import tool

class MitreMapperTool:
    @tool("Map Vulnerabilities to MITRE ATT&CK Techniques")
    def map_to_mitre(findings_summary: str, mock: bool = True) -> str:
        """
        Analyzes security findings or vulnerabilities and maps them to corresponding
        MITRE ATT&CK tactics, techniques, and IDs. Set mock=True for offline testing.
        """
        if mock or os.getenv("PATHFINDER_MOCK_MODE", "true").lower() == "true":
            return (
                "[MOCK MITRE MAPPING REPORT]\n"
                "1. Finding: PrintNightmare (CVE-2021-34527)\n"
                "   - Tactic: Privilege Escalation / Execution\n"
                "   - Technique: Exploitation for Client Execution (T1203) / Remote Services (T1021)\n"
                "2. Finding: SMBv1 Enabled\n"
                "   - Tactic: Lateral Movement\n"
                "   - Technique: Lateral Tool Transfer (T1570) / SMB/Windows Admin Shares (T1021.002)\n"
                "3. Finding: Insecure SSL/TLS Configuration\n"
                "   - Tactic: Discovery / Credential Access\n"
                "   - Technique: Network Service Discovery (T1046)"
            )

        try:
            # TODO: Live MITRE ATT&CK API or local STIX/TAXII database query placeholder
            pass
        except Exception as e:
            return f"[ERROR] Failed to execute MITRE ATT&CK mapping: {str(e)}"

def create_attack_mapping_agent(llm) -> Agent:
    mapper_tool = MitreMapperTool.map_to_mitre

    return Agent(
        role="Threat Intelligence & Attack Mapper",
        goal="Bridge raw vulnerability reports and graph telemetry into structured MITRE ATT&CK tactical matrices.",
        backstory=(
            "An elite threat intelligence analyst specializing in adversary emulation, "
            "framework mapping, and translating technical exposures into recognized TTPs."
        ),
        tools=[mapper_tool],
        llm=llm,
        verbose=True,
        memory=True
    )