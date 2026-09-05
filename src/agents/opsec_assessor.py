from typing import Dict, List, Optional
from src.models.plan_step import PlanStep


class OpSecAssessor:
    """
    Sub-agent responsible for evaluating operational security (OpSec) risks
    associated with specific lateral movement techniques, commands, and target environments.
    """

    # Baseline risk mapping for common Active Directory lateral movement techniques (1=Stealthy, 10=Loud)
    BASE_RISK_MAP: Dict[str, Dict[str, any]] = {
        "Pass-the-Hash": {
            "score": 4,
            "reason": "Generates Event ID 4624 (Type 3 network logon), but avoids cleartext password exposure."
        },
        "WMI": {
            "score": 6,
            "reason": "Executes via WMI/RPC (Event ID 4688 / WMI-Activity logs); frequently flagged by modern EDRs."
        },
        "WinRM": {
            "score": 3,
            "reason": "Standard administrative protocol (HTTP/S port 5985/5986); blends well into enterprise management traffic."
        },
        "PsExec": {
            "score": 8,
            "reason": "Creates an ephemeral service and writes binaries to Admin$ share; highly signatured and loud."
        },
        "DCOM": {
            "score": 5,
            "reason": "Instantiates remote COM objects; can bypass common service-creation detections but generates RPC traffic."
        },
        "RDP": {
            "score": 7,
            "reason": "GUI-based session (Event ID 21/25/4624 Type 10); leaves significant forensic artifacts and session footprints."
        }
    }

    # High-risk EDR/AV security controls that amplify technique risk
    HIGH_SENSITIVITY_CONTROLS: List[str] = ["CrowdStrike", "Defender for Endpoint", "SentinelOne", "Cortex XDR"]

    def evaluate_step(
            self,
            step: PlanStep,
            target_security_controls: Optional[List[str]] = None
    ) -> PlanStep:
        """
        Evaluates and adjusts the opsec_risk_score and reason_for_risk of a PlanStep
        based on the execution technique and presence of security controls.
        """
        target_security_controls = target_security_controls or []
        technique = step.technique_name

        # Determine base risk
        if technique in self.BASE_RISK_MAP:
            base_score = self.BASE_RISK_MAP[technique]["score"]
            base_reason = self.BASE_RISK_MAP[technique]["reason"]
        else:
            base_score = 5
            base_reason = f"Unmapped technique '{technique}'; assigned baseline medium risk."

        # Adjust score based on active security controls on target host
        detected_controls = [
            ctrl for ctrl in target_security_controls
            if any(hc.lower() in ctrl.lower() for hc in self.HIGH_SENSITIVITY_CONTROLS)
        ]

        if detected_controls:
            adjusted_score = min(base_score + 2, 10)
            reason = f"{base_reason} Risk escalated (+2) due to active EDR/AV controls: {', '.join(detected_controls)}."
        else:
            adjusted_score = base_score
            reason = base_reason

        # Return updated step
        step.opsec_risk_score = adjusted_score
        step.reason_for_risk = reason
        return step

    def evaluate_plan(
            self,
            steps: List[PlanStep],
            host_controls_map: Optional[Dict[str, List[str]]] = None
    ) -> List[PlanStep]:
        """
        Evaluates an entire lateral movement sequence step-by-step.

        `host_controls_map` maps target hostnames to lists of detected security controls.
        """
        host_controls_map = host_controls_map or {}
        evaluated_steps = []

        for step in steps:
            controls = host_controls_map.get(step.target_host, [])
            evaluated_step = self.evaluate_step(step, target_security_controls=controls)
            evaluated_steps.append(evaluated_step)

        return evaluated_steps