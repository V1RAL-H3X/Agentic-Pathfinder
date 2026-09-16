# src/crew/agents/llm_safety_testing.py
import subprocess
from crewai import Agent
from crewai.tools import tool


@tool("Run Garak AI Vulnerability Scan")
def run_garak_scan(target_endpoint: str, model_type: str = "rest", plugin_module: str = "promptinject") -> str:
    """Executes Garak scanning suites against a target LLM endpoint to detect safety vulnerabilities, prompt injections, and jailbreaks."""
    try:
        # Construct command for garak CLI wrapper
        cmd = [
            "python3", "-m", "garak",
            "--model_type", model_type,
            "--model_name", target_endpoint,
            "--probes", plugin_module
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            check=False
        )

        output_summary = result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout
        return f"Garak Scan Completed.\nOutput Summary:\n{output_summary}"

    except subprocess.TimeoutExpired:
        return "Error: Garak scan execution timed out after 300 seconds."
    except Exception as e:
        return f"Garak tool execution failed: {str(e)}"


def create_llm_safety_testing_agent(llm):
    return Agent(
        role="AI Vulnerability Assessment Engineer",
        goal="Execute Garak scanning workflows against target LLM endpoints to detect prompt injections, jailbreaks, and data exfiltration vectors.",
        backstory=(
            "You are an AI red-teamer specializing in LLM safety architecture, probing "
            "machine learning endpoints for robustness failures, prompt injection vulnerabilities, and policy bypasses."
        ),
        tools=[run_garak_scan],
        llm=llm,
        verbose=True
    )