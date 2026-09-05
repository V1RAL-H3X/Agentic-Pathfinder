from src.models.plan_step import PlanStep
from src.agents.opsec_assessor import OpSecAssessor


def test_opsec_evaluator_base_technique():
    assessor = OpSecAssessor()
    step = PlanStep(
        step_id=1,
        source_host="WORKSTATION01",
        target_host="WORKSTATION02",
        technique_name="WinRM",
        opsec_risk_score=1,
        reason_for_risk="Pending evaluation",
        execution_command_template="Invoke-Command -ComputerName WORKSTATION02 -ScriptBlock {whoami}"
    )

    evaluated = assessor.evaluate_step(step)
    assert evaluated.opsec_risk_score == 3
    assert "blends well" in evaluated.reason_for_risk


def test_opsec_evaluator_edr_escalation():
    assessor = OpSecAssessor()
    step = PlanStep(
        step_id=1,
        source_host="WORKSTATION01",
        target_host="DC01",
        technique_name="Pass-the-Hash",
        opsec_risk_score=1,
        reason_for_risk="Pending evaluation",
        execution_command_template="mimikatz.exe \"sekurlsa::pth /user:Admin /domain:CORP /ntlm:HASH\""
    )

    evaluated = assessor.evaluate_step(step, target_security_controls=["CrowdStrike Falcon"])
    assert evaluated.opsec_risk_score == 6  # 4 base + 2 escalation
    assert "CrowdStrike Falcon" in evaluated.reason_for_risk