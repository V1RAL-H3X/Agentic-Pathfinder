"""
BloodHound Cypher Query Helpers for Agentic-Pathfinder.

Provides standard Cypher query templates and helper functions to extract
attack paths, high-value target paths, session overlays, and lateral movement
opportunities from BloodHound/Neo4j graph databases.
"""

from typing import Dict, Any


# Standard relationships evaluated during lateral movement analysis
LATERAL_MOVEMENT_EDGES = (
    "AdminTo|HasSession|CanPSRemote|CanRDP|ExecuteDCOM|"
    "AllowedToDelegate|AllowedToAct|GenericAll|GenericWrite|WriteDacl"
)


def query_shortest_path_to_domain_admins(source_node: str) -> Dict[str, Any]:
    """
    Builds Cypher query to calculate the shortest path from a starting node
    to the Domain Admins group or Tier-0 assets.
    """
    cypher = f"""
    MATCH (src {{name: $source_node}}), (target:Group)
    WHERE target.name =~ "(?i).*DOMAIN ADMINS.*"
    MATCH p = shortestPath((src)-[:{LATERAL_MOVEMENT_EDGES}*1..15]->(target))
    RETURN p
    """
    return {"query": cypher, "parameters": {"source_node": source_node}}


def query_shortest_path_between_nodes(source_node: str, target_node: str) -> Dict[str, Any]:
    """
    Builds Cypher query to calculate the shortest attack path between two explicit nodes.
    """
    cypher = f"""
    MATCH (src {{name: $source_node}}), (target {{name: $target_node}})
    MATCH p = shortestPath((src)-[:{LATERAL_MOVEMENT_EDGES}*1..15]->(target))
    RETURN p
    """
    return {
        "query": cypher,
        "parameters": {"source_node": source_node, "target_node": target_node}
    }


def query_outbound_lateral_edges(host_name: str) -> Dict[str, Any]:
    """
    Builds Cypher query to list all direct outbound administrative, session,
    and code execution paths extending from a specified host.
    """
    cypher = f"""
    MATCH (h:Computer {{name: $host_name}})-[r:{LATERAL_MOVEMENT_EDGES}]->(target)
    RETURN 
        labels(target) AS target_labels,
        target.name AS target_name,
        type(r) AS relationship_type,
        r.is_acl AS is_acl
    """
    return {"query": cypher, "parameters": {"host_name": host_name}}


def query_user_session_locations(username: str) -> Dict[str, Any]:
    """
    Builds Cypher query to locate active user sessions across computers in the domain.
    """
    cypher = """
    MATCH (u:User {name: $username})<-[r:HasSession]-(c:Computer)
    RETURN c.name AS computer_name, c.operatingsystem AS os_type
    """
    return {"query": cypher, "parameters": {"username": username}}


def query_owned_nodes() -> Dict[str, Any]:
    """
    Builds Cypher query to return all nodes currently marked as 'owned' in the graph.
    """
    cypher = """
    MATCH (n)
    WHERE n.owned = true
    RETURN n.name AS name, labels(n) AS labels
    """
    return {"query": cypher, "parameters": {}}