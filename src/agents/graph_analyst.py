import os
from typing import Dict, List, Optional, Any
from neo4j import GraphDatabase, Driver

from src.skills.bloodhound_queries import (
    query_shortest_path_to_domain_admins,
    query_shortest_path_between_nodes,
    query_outbound_lateral_edges,
    query_user_session_locations,
    query_owned_nodes,
)


class GraphAnalyst:
    """
    Sub-agent responsible for interfacing with Neo4j/BloodHound graph databases
    to query attack paths, high-value targets, and domain relationships using
    centralized skill helpers.
    """

    def __init__(
        self,
        uri: Optional[str] = None,
        auth: Optional[tuple] = None,
        driver: Optional[Driver] = None
    ):
        if driver:
            self.driver = driver
        else:
            neo4j_uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
            user = os.getenv("NEO4J_USER", "neo4j")
            password = os.getenv("NEO4J_PASSWORD", "password")
            auth_credentials = auth or (user, password)
            self.driver = GraphDatabase.driver(neo4j_uri, auth=auth_credentials)

    def close(self) -> None:
        """Close the underlying Neo4j driver connection."""
        if self.driver:
            self.driver.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def execute_query(
        self, query: str, parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute an arbitrary Cypher query and return results as a list of dictionaries."""
        parameters = parameters or {}
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]

    def find_path_to_domain_admins(self, source_node: str) -> List[Dict[str, Any]]:
        """Queries the shortest path from a starting host/user to Domain Admins."""
        payload = query_shortest_path_to_domain_admins(source_node)
        return self.execute_query(payload["query"], payload["parameters"])

    def find_shortest_path(self, source_node: str, target_node: str) -> List[Dict[str, Any]]:
        """Queries the shortest lateral movement path between two specified nodes."""
        payload = query_shortest_path_between_nodes(source_node, target_node)
        return self.execute_query(payload["query"], payload["parameters"])

    def get_outbound_execution_paths(self, host_name: str) -> List[Dict[str, Any]]:
        """Queries direct outbound lateral movement edges from a target host."""
        payload = query_outbound_lateral_edges(host_name)
        return self.execute_query(payload["query"], payload["parameters"])

    def locate_user_sessions(self, username: str) -> List[Dict[str, Any]]:
        """Queries hosts where a specific target user currently has active sessions."""
        payload = query_user_session_locations(username)
        return self.execute_query(payload["query"], payload["parameters"])

    def get_owned_nodes(self) -> List[Dict[str, Any]]:
        """Returns all nodes currently flagged as owned in BloodHound."""
        payload = query_owned_nodes()
        return self.execute_query(payload["query"], payload["parameters"])