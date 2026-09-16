# src/crew/agents/attack_mapping.py
from crewai import Agent
from crewai.tools import tool


@tool("Query MITRE ATT&CK Reference Mapping")
def lookup_attack_technique(technique_id: str) -> str:
    """Looks up description, mitigation, and detection strategies for a specific MITRE ATT&CK ID (e.g., T1078, T1021)."""
    # A lightweight offline lookup dictionary or API wrapper
    attack_database = {
        "T1021": {"name": "Remote Services", "tactic": "Lateral Movement",
                  "description": "Adversaries may use valid accounts to log into remote services like RDP, SSH, or WinRM."},
        "T1078": {"name": "Valid Accounts", "tactic": "Defense Evasion / Persistence",
                  "description": "Adversaries may steal and use credentials of existing accounts to gain access."},
        "T1484": {"name": "Domain Policy Modification", "tactic": "Privilege Escalation",
                  "description": "Adversaries may modify domain-wide policies to gain control over systems."}
    }

    tech = attack_database.get(technique_id.upper())
    if tech:
        return f"Technique: {tech['name']} ({technique_id})\nTactic: {tech['tactic']}\nDetails: {tech['description']}"
    return f"Technique ID '{technique_id}' not found in local tactical cache."


def create_attack_mapping_agent(llm):
    return Agent(
        role="MITRE ATT&CK Framework Strategist",
        goal="Analyze raw scan outputs, graph paths, and vulnerabilities to map adversary behaviors to precise MITRE ATT&CK tactics, techniques, and procedures (TTPs).",
        backstory=(
            "You are a threat intelligence analyst expert in the MITRE ATT&CK framework. "
            "You take technical indicators of compromise and structural access vectors, categorizing "
            "them accurately to measure defensive detection telemetry coverage and adversary modeling."
        ),
        tools=[lookup_attack_technique],
        llm=llm,
        verbose=True
    )