from typing import List, Optional
from pydantic import BaseModel, Field


class HostState(BaseModel):
    hostname: str = Field(..., description="Target hostname or FQDN")
    ip_address: str = Field(..., description="IPv4 or IPv6 address")
    os_type: str = Field(default="Windows", description="Operating system type")
    domain: Optional[str] = Field(default=None, description="Active Directory domain")

    active_sessions: List[str] = Field(default_factory=list, description="Active user sessions")
    logged_in_users: List[str] = Field(default_factory=list, description="Currently logged-in accounts")
    local_admin_privileges: bool = Field(default=False, description="Whether administrative access is confirmed")

    open_ports: List[int] = Field(default_factory=list, description="Open network ports")
    running_services: List[str] = Field(default_factory=list, description="Identified services running on host")
    security_controls: List[str] = Field(default_factory=list, description="EDR/AV solutions detected")