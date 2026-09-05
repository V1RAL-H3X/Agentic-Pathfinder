from src.models.plan_step import PlanStep
from src.agents.command_synthesizer import CommandSynthesizer


def test_generate_winrm_command():
    synthesizer = CommandSynthesizer()
    cmd = synthesizer.generate_command(
        technique_name="WinRM",
        target_host="DC01.CORP.LOCAL",
        command="hostname"
    )
    assert "Invoke-Command" in cmd
    assert "DC01.CORP.LOCAL" in cmd
    assert "hostname" in cmd


def test_populate_step_command():
    synthesizer = CommandSynthesizer()
    step = PlanStep(
        step_id=1,
        source_host="WORKSTATION01",
        target_host="SERVER01",
        technique_name="Pass-the-Hash",
        opsec_risk_score=4,
        reason_for_risk="Type 3 logon",
        execution_command_template=""
    )

    updated_step = synthesizer.populate_step_command(
        step,
        command="ipconfig /all",
        username="DomainAdmin",
        domain="CORP.LOCAL"
    )

    assert "sekurlsa::pth" in updated_step.execution_command_template
    assert "DomainAdmin" in updated_step.execution_command_template
    assert "ipconfig /all" in updated_step.execution_command_template