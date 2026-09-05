from typing import List, Optional
from pydantic import BaseModel, Field


class PlanStep(BaseModel):
    step_id: int = Field(..., description="Sequential step index in lateral movement path")
    source_host: str = Field(..., description="Origin host for movement")
    target_host: str = Field(..., description="Destination target host")

    technique_name: str = Field(..., description="Technique applied (e.g., Pass-the-Hash, WMI, WinRM)")
    target_service: Optional[str] = Field(default=None, description="Targeted RPC/SMB/HTTP service")
    required_credentials: List[str] = Field(default_factory=list,
                                            description="Hashes, tokens, or plaintext creds required")

    opsec_risk_score: int = Field(..., ge=1, le=10, description="Evaluated risk score (1=Stealthy, 10=Loud)")
    reason_for_risk: str = Field(..., description="Operational reason for risk classification")
    execution_command_template: str = Field(..., description="Syntax template for execution")