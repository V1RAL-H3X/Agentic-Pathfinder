# src/crew/agents/mobile_assessment.py
import os
import requests
from crewai import Agent
from crewai.tools import tool

# Configuration for local MobSF instance
MOBSF_URL = os.getenv("MOBSF_URL", "http://localhost:8000")
MOBSF_API_KEY = os.getenv("MOBSF_API_KEY", "your_mobsf_api_key_here")


@tool("Scan Mobile Binary via MobSF API")
def scan_mobile_binary(file_path: str) -> str:
    """Uploads and initiates a static security scan on an APK or IPA file using MobSF."""
    if not os.path.exists(file_path):
        return f"Error: File path '{file_path}' does not exist."

    headers = {"Authorization": MOBSF_API_KEY}
    upload_url = f"{MOBSF_URL}/api/v1/upload"
    scan_url = f"{MOBSF_URL}/api/v1/scan"

    try:
        # Step 1: Upload binary
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f)}
            response = requests.post(upload_url, headers=headers, files=files, timeout=30)

        if response.status_code != 200:
            return f"Failed to upload binary: {response.text}"

        data = response.json()
        hash_val = data.get("hash")
        file_name = data.get("file_name")

        # Step 2: Trigger static analysis scan
        scan_payload = {"hash": hash_val, "file_name": file_name}
        scan_response = requests.post(scan_url, headers=headers, data=scan_payload, timeout=60)

        if scan_response.status_code == 200:
            return f"MobSF Scan Completed Successfully. Results Summary:\n{scan_response.text[:2000]}"
        else:
            return f"Scan triggered but failed to complete: {scan_response.text}"

    except requests.exceptions.ConnectionError:
        return f"Error: Could not connect to MobSF server at {MOBSF_URL}. Ensure container is running."
    except Exception as e:
        return f"MobSF Tool Execution Error: {str(e)}"


def create_mobile_assessment_agent(llm):
    return Agent(
        role="Mobile Application Security Assessor",
        goal="Analyze MobSF static and dynamic scan reports to identify insecure data storage, hardcoded credentials, weak cryptography, and unsafe API configurations in mobile application binaries.",
        backstory=(
            "You are a senior mobile security engineer expert in Android and iOS internals. "
            "You dissect mobile application packages to uncover hidden vulnerabilities, "
            "insecure permissions, and exposed attack surfaces that could be leveraged by external threat actors."
        ),
        tools=[scan_mobile_binary],
        llm=llm,
        verbose=True
    )