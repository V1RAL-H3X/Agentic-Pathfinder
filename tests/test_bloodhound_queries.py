from src.skills.bloodhound_queries import (
    query_shortest_path_to_domain_admins,
    query_outbound_lateral_edges,
    query_user_session_locations,
)


def test_query_shortest_path_to_domain_admins():
    result = query_shortest_path_to_domain_admins("WORKSTATION01.CORP.LOCAL")
    assert "source_node" in result["parameters"]
    assert result["parameters"]["source_node"] == "WORKSTATION01.CORP.LOCAL"
    assert "shortestPath" in result["query"]
    assert "DOMAIN ADMINS" in result["query"]


def test_query_outbound_lateral_edges():
    result = query_outbound_lateral_edges("DC01.CORP.LOCAL")
    assert result["parameters"]["host_name"] == "DC01.CORP.LOCAL"
    assert "AdminTo" in result["query"]


def test_query_user_session_locations():
    result = query_user_session_locations("DA_ADMIN@CORP.LOCAL")
    assert result["parameters"]["username"] == "DA_ADMIN@CORP.LOCAL"
    assert "HasSession" in result["query"]