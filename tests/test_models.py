from src.models.host_state import HostState
from src.models.plan_step import PlanStep


def test_host_state_instantiation():
    host = HostState(
        hostname="DC01.CORP.LOCAL",
        ip_address="192.168.1.10",
        local_admin_privileges=True,
        security_controls=["Defender"]
    )
    assert host.hostname == "DC01.CORP.LOCAL"
    assert host.local_admin_privileges is True


def test_plan_step_instantiation():
    step = PlanStep(
        step_id=1,
        source_host="WORKSTATION01",
        target_host="DC01",
        technique_name="Pass-the-Hash",
        opsec_risk_score=4,
        reason_for_risk="Generates Event ID 4624 Type 3 logon",
        execution_command_template="mimikatz.exe \"sekurlsa::pth /user:Admin /domain:CORP /ntlm:HASH\""
    )
    assert step.opsec_risk_score == 4