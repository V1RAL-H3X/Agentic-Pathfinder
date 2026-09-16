import json
import networkx as nx


def load_graph_from_json(file_path: str) -> nx.DiGraph:
    """Parses a BloodHound JSON export into a NetworkX Directed Graph."""
    G = nx.DiGraph()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = json.load(f)

        items = content.get("data", [])
        for item in items:
            kind = item.get("kind", "Unknown")
            props = item.get("Properties", {})
            node_name = props.get("name")

            if node_name:
                G.add_node(node_name, type=kind)

                # Add edges for memberships or permissions
                for member in item.get("Members", []):
                    member_name = member.get("MemberName")
                    if member_name:
                        G.add_edge(member_name, node_name, relationship="MemberOf")
    except Exception as e:
        print(f"Error loading graph data: {e}")

    return G


# --- THIS IS YOUR AGENT TOOL FUNCTION ---
def find_attack_path_tool(source_host: str, target_host: str, json_path: str = "mock_bloodhound.json") -> str:
    """
    Finds an Active Directory attack path between a source object and a target object
    using local graph analysis.
    """
    # Load the graph (in a real app, you can load this once globally so you don't reload it every call)
    G = load_graph_from_json(json_path)

    if source_host not in G:
        return f"Error: Source node '{source_host}' does not exist in the graph."
    if target_host not in G:
        return f"Error: Target node '{target_host}' does not exist in the graph."

    try:
        # Run NetworkX pathfinding
        path = nx.shortest_path(G, source=source_host, target=target_host)

        # Format the output clearly for an LLM to read
        formatted_path = []
        for i, node in enumerate(path):
            node_type = G.nodes[node].get('type', 'Unknown')
            formatted_path.append(f"{node} ({node_type})")

            if i < len(path) - 1:
                next_node = path[i + 1]
                edge_data = G.get_edge_data(node, next_node)
                rel = edge_data.get('relationship', 'ConnectedTo')
                formatted_path.append(f" --[{rel}]--> ")

        return "Success! Attack Path Found:\n" + "".join(formatted_path)

    except nx.NetworkXNoPath:
        return f"No valid attack path found between {source_host} and {target_host}."


if __name__ == "__main__":
    # Test our tool function directly
    result = find_attack_path_tool(
        source_host="JOHN.DOE@CORP.LOCAL",
        target_host="IT_SUPPORT@CORP.LOCAL"
    )
    print(result)