# Insurance Claims AI Orchestrator

**UiPath AgentHack 2026 — Track 2: UiPath Maestro BPMN**

An end-to-end agentic insurance claims processing system built on the UiPath Platform. AI agents handle fraud risk assessment and document extraction, while UiPath Maestro orchestrates the full claim lifecycle — from intake to settlement — keeping a human adjuster in the loop for every claim that needs one.

## The Business Problem

Insurance fraud costs the industry tens of billions of dollars annually, while legitimate claims are often slowed down by manual review queues that treat every claim the same way, regardless of risk. Adjusters spend their time on routine, low-risk claims that could be processed automatically, while genuinely suspicious claims don't always get the deeper scrutiny they need.

This project automates the triage decision itself: AI agents assess every incoming claim for fraud risk in seconds, low-risk claims are auto-approved and settled immediately, and only claims that actually need human judgment are routed to an adjuster — with full visibility into why.

## How It Works

1. **Claim Received** — a new insurance claim enters the process
2. **Extract Claim Details** — a document extraction AI agent parses raw, unstructured claim text (from forms, emails, or claimant descriptions) into structured fields: claimant name, policy number, incident date, submission date, claimed amount, and incident description
3. **Lookup Policy & Coverage / Retrieve Policy Limits** — the process checks the claim against policy data
4. **Run Fraud Risk Assessment (Agent)** — a fraud detection AI agent (powered by Claude Sonnet 4.6) analyzes the claim for common fraud indicators: timeline gaps between incident and submission, vague or inconsistent descriptions, disproportionate claimed amounts, and patterns suggestive of staged incidents. It returns a structured fraud score, risk level, reasoning, and a clear flag for whether human review is required
5. **Risk Gateway** — low-risk claims move straight to settlement; medium/high-risk claims are escalated
6. **Escalate to Adjuster (Human Task)** — a human adjuster reviews flagged claims with full visibility into the AI's reasoning, and makes the final call
7. **Process Settlement Payment / Update Claims System** — approved claims are settled and the system of record is updated
8. **Timeout Safety Path** — if a claimant doesn't respond to a request for more information within 3 days, the process resolves gracefully rather than stalling indefinitely

Humans are never removed from the loop for claims that need judgment — the system's only job is to make sure their time is spent on the claims that actually need it.

## UiPath Components Used

- **UiPath Maestro (BPMN 2.0)** — orchestrates the entire claim lifecycle: sequencing, gateways, human tasks, timers, and exception/timeout handling
- **UiPath Agent Builder** — two autonomous agents built natively on the platform:
  - **Fraud Risk Assessment Agent** (Claude Sonnet 4.6 via UiPath's model integration) — analyzes claims for fraud indicators and returns a structured risk assessment
  - **Claim Document Extraction Agent** (Claude Sonnet 4.6) — converts raw, unstructured claim text into structured data
- **UiPath Orchestrator** — hosts the deployed agent processes and manages execution
- **UiPath Automation Cloud** — the platform all components run on

## Agent Type

This solution uses **Low-Code Agents** built natively in UiPath Agent Builder (Autonomous Agent type), running on Claude Sonnet 4.6 through UiPath's built-in model integration. A standalone Python reference implementation of the fraud detection logic (using the Anthropic API directly) is also included in `/agents/fraud_agent.py` to demonstrate the underlying logic and for local testing/development purposes.

## Setup Instructions

### Prerequisites
- UiPath Automation Cloud account with access to Maestro and Agent Builder
- Python 3.11+ (for local agent testing only)
- An Anthropic API key (only needed if testing `fraud_agent.py` locally outside UiPath)

### Running the UiPath solution
1. Clone or import the `Insurance_Claims_Processing.bpmn` file into UiPath Studio Web under a new Maestro project
2. In Agent Builder, recreate the two agents using the system prompts provided in `/agents/fraud_agent_prompt.md` and `/agents/extraction_agent_prompt.md`, selecting `anthropic.claude-sonnet-4-6` as the model
3. Publish both agents from their respective solutions
4. In the Maestro BPMN canvas, wire the "Run Fraud Risk Assessment (Agent)" and "Extract Claim Details" tasks to their respective published agents via the agentic process action
5. Run the process via Debug to test end-to-end

### Running the local Python reference agent (optional)
```bash
cd agents
python -m venv venv
venv\Scripts\activate   # or source venv/bin/activate on Mac/Linux
pip install langchain langchain-anthropic anthropic --break-system-packages
# Add your ANTHROPIC_API_KEY to a .env file in this folder
python fraud_agent.py
```

## Built With Claude Code

This project was built with assistance from **Claude Code** for:
- Generating the Python reference implementation of the fraud detection agent (`fraud_agent.py`)
- Drafting and refining the BPMN XML structure for the Maestro claims process, including gateway conditions and variable wiring
- Writing structured system prompts for both Agent Builder agents to enforce clean JSON output

Screenshots of the Claude Code development sessions are included in `/docs/claude_code_sessions/`.

## Architecture Notes

This is a hackathon prototype built under a 7-week timeline. The fraud detection agent has been fully tested end-to-end within UiPath Agent Builder, returning live structured assessments from Claude Sonnet 4.6 (see `/docs/fraud_agent_test_output.png`). The document extraction agent is configured identically and is included for architectural completeness; live debug testing of this specific agent was blocked by an intermittent platform runtime issue ("Robot not installed") in our trial sandbox environment, which we've documented in our product feedback submission to the UiPath team.

## License

MIT License — see LICENSE file for details.
