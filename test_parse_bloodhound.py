import json
import networkx as nx


# 1. Simulate creating a mock BloodHound JSON file for this example
def create_mock_json_file():
    mock_data = {
        "data": [
            {
                "kind": "User",
                "Properties": {"name": "JOHN.DOE@CORP.LOCAL"},
                "Members": []
            },
            {
                "kind": "Group",
                "Properties": {"name": "IT_SUPPORT@CORP.LOCAL"},
                # Represents objects that belong to this group
                "Members": [
                    {"MemberName": "JOHN.DOE@CORP.LOCAL", "MemberType": "User"}
                ]
            }
        ]
    }
    with open("mock_bloodhound.json", "w") as f:
        json.dump(mock_data, f, indent=4)


# 2. The core function to load JSON data into NetworkX
def load_bloodhound_to_networkx(file_path: str) -> nx.DiGraph:
    G = nx.DiGraph()

    with open(file_path, 'r', encoding='utf-8') as f:
        content = json.load(f)

    # Loop through the items in the BloodHound data export
    items = content.get("data", [])
    for item in items:
        kind = item.get("kind", "Unknown")
        props = item.get("Properties", {})
        node_name = props.get("name")

        if node_name:
            # Add the node with its metadata/type
            G.add_node(node_name, type=kind)

            # Parse any outbound relationships or memberships
            for member in item.get("Members", []):
                member_name = member.get("MemberName")
                if member_name:
                    # In BloodHound style, a member links to the container group (MemberOf)
                    G.add_edge(member_name, node_name, relationship="MemberOf")

    return G


if __name__ == "__main__":
    # Generate our mock file first
    create_mock_json_file()

    # Parse it into NetworkX
    ad_graph = load_bloodhound_to_networkx("mock_bloodhound.json")

    print(f"Successfully loaded graph from JSON!")
    print(f"Nodes in graph: {list(ad_graph.nodes(data=True))}")
    print(f"Edges in graph: {list(ad_graph.edges(data=True))}")