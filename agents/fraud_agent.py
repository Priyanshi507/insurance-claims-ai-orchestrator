"""
Fraud Detection Agent — Insurance Claims Orchestrator
UiPath AgentHack 2026 — Track 2: Maestro BPMN

This agent receives structured claim data, analyzes it for fraud
risk using Claude, and returns a structured decision that the
UiPath Maestro BPMN process uses to route the claim:
  - LOW risk  -> auto-approve and settle
  - HIGH risk -> escalate to a human adjuster (Action Center task)

This module is designed to be called either:
  1. Directly as a Python script (for local testing), or
  2. As a UiPath Coded Agent (imported into Studio), or
  3. As a FastAPI endpoint that Maestro calls via an API Workflow
"""

import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic

# Load the API key from .env (never hardcode it)
load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def assess_claim_fraud_risk(claim_data: dict) -> dict:
    """
    Takes a claim's data and returns a structured fraud risk assessment.

    Args:
        claim_data: dict with keys like:
            - claimant_name
            - incident_description
            - claimed_amount
            - policy_number
            - incident_date
            - submission_date

    Returns:
        dict with keys:
            - fraud_score: float between 0.0 and 1.0
            - risk_level: "LOW" | "MEDIUM" | "HIGH"
            - reasoning: str explaining the assessment
            - requires_human_review: bool
    """

    prompt = f"""You are a fraud detection analyst for an insurance company.
Analyze the following claim and assess its fraud risk.

Claim details:
- Claimant: {claim_data.get('claimant_name')}
- Policy number: {claim_data.get('policy_number')}
- Incident date: {claim_data.get('incident_date')}
- Submission date: {claim_data.get('submission_date')}
- Claimed amount: ${claim_data.get('claimed_amount')}
- Incident description: {claim_data.get('incident_description')}

Look for common fraud indicators such as:
- Large gap between incident date and submission date
- Vague or inconsistent incident descriptions
- Unusually high claimed amounts relative to the described incident
- Patterns suggestive of staged incidents

Respond ONLY with valid JSON in this exact format, no other text:
{{
  "fraud_score": <float 0.0 to 1.0>,
  "risk_level": "<LOW or MEDIUM or HIGH>",
  "reasoning": "<2-3 sentence explanation>",
  "requires_human_review": <true or false>
}}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    # Extract and parse the JSON response
    raw_text = response.content[0].text.strip()

    # Defensive cleanup in case the model wraps JSON in markdown fences
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`").replace("json\n", "", 1)

    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError:
        # Fail-safe: if parsing fails, default to human review
        # (never auto-approve on uncertainty — this is critical for safety)
        result = {
            "fraud_score": 1.0,
            "risk_level": "HIGH",
            "reasoning": "Could not parse AI assessment. Defaulting to human review for safety.",
            "requires_human_review": True
        }

    return result


# Local test — run this file directly to verify everything works
if __name__ == "__main__":
    sample_claim = {
        "claimant_name": "John Doe",
        "policy_number": "POL-2026-001234",
        "incident_date": "2026-06-01",
        "submission_date": "2026-06-15",
        "claimed_amount": 4500,
        "incident_description": "Rear-ended at a traffic light, minor bumper damage, repair estimate attached."
    }

    print("Testing fraud detection agent...")
    print("-" * 50)
    result = assess_claim_fraud_risk(sample_claim)
    print(json.dumps(result, indent=2))