# src/crew/agents/graph_recon.py
import os
from crewai import Agent
from crewai.tools import tool


@tool("Query BloodHound Neo4j Database")
def query_bloodhound_graph(source_host: str, target_host: str = None) -> str:
    """Queries Neo4j for attack paths and lateral movement edges originating from a source host."""
    # Check if mock mode is requested via environment variable or local state
    if os.getenv("PATHFINDER_MOCK_MODE", "false").lower() == "true":
        if target_host:
            return f"[MOCK GRAPH] Found shortest path: {source_host} --[CanPSRemote]--> {target_host}"
        else:
            return f"[MOCK GRAPH] Outbound paths from {source_host}: Server01 (AdminTo), {target_host or 'DC01'} (CanPSRemote)"

    # Live Neo4j connection logic using neo4j driver
    try:
        from neo4j import GraphDatabase
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")

        with GraphDatabase.driver(uri, auth=(user, password)) as driver:
            with driver.session() as session:
                query = """
                MATCH p = shortestPath((s:Computer {name: $source})-[:MemberOf|AdminTo|CanPSRemote*1..5]->(t:Computer))
                RETURN [node in nodes(p) | node.name] AS path_nodes, [rel in relationships(p) | type(rel)] AS rel_types
                LIMIT 5
                """
                result = session.run(query, source=source_host.upper())
                records = [record.data() for record in result]
                return str(records) if records else "No paths found."
    except Exception as e:
        return f"Neo4j query failed: {str(e)}"


def create_graph_recon_agent(llm):
    return Agent(
        role="Active Directory Graph Analyst",
        goal="Interrogate BloodHound Neo4j datasets to uncover structural lateral movement paths and attack vectors.",
        backstory=(
            "You are an expert in Active Directory topology and graph theory. "
            "You analyze permission hierarchies, trust relationships, and delegation rights to map paths to Domain Controllers."
        ),
        tools=[query_bloodhound_graph],
        llm=llm,
        verbose=True
    )