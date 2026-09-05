from unittest.mock import patch, MagicMock
import pytest
from src.main import parse_args, main


def test_parse_args_defaults():
    test_args = ["main.py", "-s", "WORKSTATION01.CORP.LOCAL"]
    with patch("sys.argv", test_args):
        args = parse_args()
        assert args.source == "WORKSTATION01.CORP.LOCAL"
        assert args.target is None
        assert args.user == "Administrator"
        assert args.domain == "CORP.LOCAL"
        assert args.command == "whoami"
        assert args.mock is False
        assert args.json is False
        assert args.markdown is False


def test_parse_args_full_flags():
    test_args = [
        "main.py",
        "-s", "WORKSTATION01.CORP.LOCAL",
        "-t", "DC01.CORP.LOCAL",
        "-u", "DomainAdmin",
        "-d", "TEST.LOCAL",
        "-c", "ipconfig /all",
        "--edr", "CrowdStrike,Defender",
        "--mock",
        "--markdown",
        "-o", "output.md"
    ]
    with patch("sys.argv", test_args):
        args = parse_args()
        assert args.source == "WORKSTATION01.CORP.LOCAL"
        assert args.target == "DC01.CORP.LOCAL"
        assert args.user == "DomainAdmin"
        assert args.domain == "TEST.LOCAL"
        assert args.command == "ipconfig /all"
        assert args.edr == "CrowdStrike,Defender"
        assert args.mock is True
        assert args.markdown is True
        assert args.output == "output.md"


def test_main_mock_execution_markdown_output(capsys):
    test_args = [
        "main.py",
        "-s", "WORKSTATION01.CORP.LOCAL",
        "-t", "DC01.CORP.LOCAL",
        "--edr", "CrowdStrike Falcon",
        "--mock",
        "--markdown"
    ]
    with patch("sys.argv", test_args):
        main()

    captured = capsys.readouterr()
    assert "# Agentic-Pathfinder Assessment Report" in captured.out
    assert "WORKSTATION01.CORP.LOCAL" in captured.out
    assert "DC01.CORP.LOCAL" in captured.out


def test_main_mock_execution_json_output(capsys):
    test_args = [
        "main.py",
        "-s", "WORKSTATION01.CORP.LOCAL",
        "-t", "DC01.CORP.LOCAL",
        "--mock",
        "--json"
    ]
    with patch("sys.argv", test_args):
        main()

    captured = capsys.readouterr()
    assert '"source_host": "WORKSTATION01.CORP.LOCAL"' in captured.out
    assert '"target_host": "DC01.CORP.LOCAL"' in captured.out