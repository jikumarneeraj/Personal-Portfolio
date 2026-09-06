import logging
import requests
from typing import Dict, Any

logger = logging.getLogger("neeraj_portfolio_assistant.tools")

# Verified Links from Neeraj's official portfolio
VERIFIED_LINKS: Dict[str, Dict[str, str]] = {
    "resume": {
        "title": "Neeraj Kumar's Resume",
        "url": "https://drive.google.com/file/d/17CbTEI_mVizfbBjQ4nMXTnU73dylpGUg/view",
        "action_text": "View / Download Resume"
    },
    "github": {
        "title": "Neeraj Kumar's GitHub Profile",
        "url": "https://github.com/jikumarneeraj",
        "action_text": "Visit GitHub Profile"
    },
    "linkedin": {
        "title": "Neeraj Kumar's LinkedIn Profile",
        "url": "https://www.linkedin.com/in/neeraj-kumar-data-scientist",
        "action_text": "Connect on LinkedIn"
    },
    "kaggle": {
        "title": "Neeraj Kumar's Kaggle Profile",
        "url": "https://www.kaggle.com/jikumarneeraj",
        "action_text": "Visit Kaggle Profile"
    },
    "email": {
        "title": "Neeraj Kumar's Direct Email",
        "url": "mailto:suneerajkumar@gmail.com",
        "action_text": "Send Email"
    },
    "gate_certificate": {
        "title": "GATE 2026 CSE Certificate",
        "url": "https://drive.google.com/file/d/1towJFGkqurTibie2kjY5d314Rw_ELIWb/view?usp=sharing",
        "action_text": "View GATE Certificate"
    },
    "lenovo_internship": {
        "title": "Lenovo LeAP Internship Verification",
        "url": "https://drive.google.com/file/d/1aRv7B4REcb2rlPQrmEfeS6hGU22orz3i/view?usp=sharing",
        "action_text": "View Lenovo Certificate"
    }
}

# Contact us integration endpoints (reusing existing mechanisms from script.js)
GOOGLE_APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbysOd5d3iq8afAH3GzBzTy9QL_jF4z7H-bwr2X7mz1qXzqbhKsw7NiEgNIFXCCw6o7_Vg/exec"
GOOGLE_FORM_ACTION_URL = "https://docs.google.com/forms/d/e/1FAIpQLSe8JjxOjzQocMJx-vehcyqiNd_v0Aou4s19aWN9kgkctbt0Mw/formResponse"

GOOGLE_FORM_ENTRIES = {
    "name": "entry.2005620554",
    "email": "entry.1045781291",
    "subject": "entry.1158223365",
    "message": "entry.839337160"
}

def submit_contact(name: str, email: str, subject: str, message: str) -> bool:
    """
    Submits contact message using the existing portfolio infrastructure.
    Uses Google Apps Script endpoint (primary) and Google Form response (secondary).
    Returns True if submission succeeds, False otherwise.
    """
    cleaned_name = name.strip()
    cleaned_email = email.strip()
    cleaned_subject = subject.strip()
    cleaned_message = message.strip()

    if not cleaned_name or not cleaned_email or not cleaned_subject or not cleaned_message:
        logger.warning("Contact submission rejected: missing required fields.")
        return False

    success = False

    # 1. Primary: Google Apps Script Web App
    try:
        response = requests.post(
            GOOGLE_APPS_SCRIPT_URL,
            data={
                "name": cleaned_name,
                "email": cleaned_email,
                "subject": cleaned_subject,
                "message": cleaned_message
            },
            timeout=8
        )
        if response.status_code in [200, 302]:
            logger.info("Successfully delivered contact message via Google Apps Script.")
            success = True
    except Exception as e:
        logger.warning(f"Google Apps Script delivery error: {e}")

    # 2. Secondary: Google Form endpoint backup
    try:
        form_payload = {
            GOOGLE_FORM_ENTRIES["name"]: cleaned_name,
            GOOGLE_FORM_ENTRIES["email"]: cleaned_email,
            GOOGLE_FORM_ENTRIES["subject"]: cleaned_subject,
            GOOGLE_FORM_ENTRIES["message"]: cleaned_message
        }
        form_res = requests.post(
            GOOGLE_FORM_ACTION_URL,
            data=form_payload,
            timeout=8
        )
        # Google forms returns 200 on formResponse
        if form_res.status_code in [200, 302]:
            logger.info("Successfully delivered contact message via Google Form.")
            success = True
    except Exception as e:
        logger.warning(f"Google Form delivery error: {e}")

    return success
