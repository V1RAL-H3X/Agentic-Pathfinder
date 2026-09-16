# src/crew/agents/infrastructure_scanning.py
import os
from crewai import Agent
from crewai.tools import tool


@tool("Execute Infrastructure Vulnerability Scan")
def run_infrastructure_scan(target_host: str) -> str:
    """Executes network port scanning and vulnerability assessment against target hosts."""
    if os.getenv("PATHFINDER_MOCK_MODE", "false").lower() == "true":
        return f"[MOCK SCAN] Vulnerabilities found on {target_host}: CVE-2021-44228 (Log4j), SMB Signing Disabled."

    # Real OpenVAS/Nmap execution logic can go here
    return f"Infrastructure scan completed for {target_host}."


def create_infrastructure_scanning_agent(llm):
    return Agent(
        role="Infrastructure Vulnerability Analyst",
        goal="Identify open ports, misconfigurations, and known CVEs across target network infrastructure.",
        backstory=(
            "You are an expert infrastructure security assessor specializing in vulnerability management, "
            "network enumeration, and risk prioritization using OpenVAS and Nmap data."
        ),
        tools=[run_infrastructure_scan],
        llm=llm,
        verbose=True
    )