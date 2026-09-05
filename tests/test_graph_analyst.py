from unittest.mock import MagicMock
from src.agents.graph_analyst import GraphAnalyst


def test_graph_analyst_skill_integration():
    mock_driver = MagicMock()
    mock_result = [
        {
            "target_labels": ["Computer"],
            "target_name": "DC01.CORP.LOCAL",
            "relationship_type": "AdminTo",
            "is_acl": False
        }
    ]

    mock_driver.session.return_value.__enter__.return_value.run.return_value = [
        MagicMock(data=lambda: item) for item in mock_result
    ]

    analyst = GraphAnalyst(driver=mock_driver)
    paths = analyst.get_outbound_execution_paths("WORKSTATION01.CORP.LOCAL")

    assert len(paths) == 1
    assert paths[0]["target_name"] == "DC01.CORP.LOCAL"
    assert paths[0]["relationship_type"] == "AdminTo"


def test_find_path_to_domain_admins_mock():
    mock_driver = MagicMock()
    mock_driver.session.return_value.__enter__.return_value.run.return_value = []

    analyst = GraphAnalyst(driver=mock_driver)
    res = analyst.find_path_to_domain_admins("USER01@CORP.LOCAL")

    assert res == []
    # Confirm query execution was dispatched
    assert mock_driver.session.return_value.__enter__.return_value.run.called