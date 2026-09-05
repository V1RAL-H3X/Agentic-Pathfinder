"""
Report Formatter Skill for Agentic-Pathfinder.

Converts lists of evaluated PlanStep objects into structured Markdown tables
and execution summaries for reporting and audit logging.
"""

from typing import List
from src.models.plan_step import PlanStep


def format_plan_to_markdown_table(steps: List[PlanStep]) -> str:
    """
    Renders a list of PlanStep models into a scannable Markdown table.
    """
    if not steps:
        return "*No lateral movement path steps recorded.*"

    table_lines = [
        "| Step | Source Host | Target Host | Technique | OpSec Risk | Reason / Notes |",
        "| :---: | :--- | :--- | :--- | :---: | :--- |"
    ]

    for step in steps:
        table_lines.append(
            f"| {step.step_id} | {step.source_host} | {step.target_host} | "
            f"`{step.technique_name}` | **{step.opsec_risk_score}/10** | {step.reason_for_risk} |"
        )

    return "\n".join(table_lines)


def format_plan_execution_guide(steps: List[PlanStep]) -> str:
    """
    Generates a step-by-step Markdown execution breakdown with raw command blocks.
    """
    if not steps:
        return "### Lateral Movement Execution Guide\n\n*No actionable steps in plan.*"

    markdown_output = ["### Synthesized Execution Playbook\n"]

    for step in steps:
        markdown_output.append(
            f"#### Step {step.step_id}: `{step.technique_name}` → {step.target_host}\n"
            f"* **Origin:** `{step.source_host}`\n"
            f"* **Target:** `{step.target_host}`\n"
            f"* **OpSec Score:** `{step.opsec_risk_score}/10`\n"
            f"* **Assessment:** {step.reason_for_risk}\n\n"
            "```powershell\n"
            f"{step.execution_command_template}\n"
            "```\n"
        )

    return "\n".join(markdown_output)


def export_full_report_markdown(steps: List[PlanStep], title: str = "Agentic-Pathfinder Assessment Report") -> str:
    """
    Combines table summary and detailed execution blocks into a cohesive report string.
    """
    table = format_plan_to_markdown_table(steps)
    guide = format_plan_execution_guide(steps)

    report = (
        f"# {title}\n\n"
        "## Executive Summary\n\n"
        f"{table}\n\n"
        "---\n\n"
        "## Technical Execution Steps\n\n"
        f"{guide}"
    )

    return report