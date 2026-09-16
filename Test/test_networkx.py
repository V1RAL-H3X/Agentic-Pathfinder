import networkx as nx


def build_mock_ad_graph():
    G = nx.DiGraph()
    G.add_node("john.doe@corp.local", type="User")
    G.add_node("IT_Support@corp.local", type="Group")
    G.add_node("DC01.corp.local", type="Computer")

    G.add_edge("john.doe@corp.local", "IT_Support@corp.local", relationship="MemberOf")
    G.add_edge("IT_Support@corp.local", "DC01.corp.local", relationship="AdminTo")
    return G


# This function is structured like a tool an agent can call
def find_path_tool(source_host: str, target_host: str) -> str:
    """Finds an attack path between two Active Directory objects."""
    G = build_mock_ad_graph()

    if source_host not in G or target_host not in G:
        return f"Error: Source or target node not found in graph."

    try:
        path = nx.shortest_path(G, source=source_host, target=target_host)
        path_description = " -> ".join(path)
        return f"Success! Path found: {path_description}"
    except nx.NetworkXNoPath:
        return f"No path found between {source_host} and {target_host}."


if __name__ == "__main__":
    # Test calling the tool function directly
    result = find_path_tool("john.doe@corp.local", "DC01.corp.local")
    print(result)