from src.models.plan_step import PlanStep
from src.skills.report_formatter import (
    format_plan_to_markdown_table,
    format_plan_execution_guide,
    export_full_report_markdown,
)


def test_format_plan_to_markdown_table():
    step = PlanStep(
        step_id=1,
        source_host="WORKSTATION01.CORP.LOCAL",
        target_host="DC01.CORP.LOCAL",
        technique_name="WinRM",
        opsec_risk_score=5,
        reason_for_risk="CrowdStrike active",
        execution_command_template="Invoke-Command -ComputerName DC01"
    )

    table = format_plan_to_markdown_table([step])
    assert "| Step | Source Host |" in table
    assert "| 1 | WORKSTATION01.CORP.LOCAL | DC01.CORP.LOCAL | `WinRM` | **5/10** |" in table


def test_export_full_report_markdown():
    step = PlanStep(
        step_id=1,
        source_host="WORKSTATION01",
        target_host="DC01",
        technique_name="Pass-the-Hash",
        opsec_risk_score=4,
        reason_for_risk="Type 3 logon",
        execution_command_template="mimikatz.exe sekurlsa::pth"
    )

    report = export_full_report_markdown([step])
    assert "# Agentic-Pathfinder Assessment Report" in report
    assert "## Executive Summary" in report
    assert "mimikatz.exe sekurlsa::pth" in report