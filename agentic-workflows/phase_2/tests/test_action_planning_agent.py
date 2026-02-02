import os, sys
from dotenv import load_dotenv
__file__ = "D:/AIAgent/Agentic Workflows/starter/phase_2/tests/test_action_planning_agent.py"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PHASE2_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
PROJECT_ROOT = os.path.abspath(os.path.join(PHASE2_DIR, ".."))
PHASE1_DIR = os.path.join(PROJECT_ROOT, "phase_1")
sys.path.insert(0, PHASE1_DIR)
load_dotenv(os.path.join(PHASE1_DIR, ".env"), override=True)

openai_api_key = os.getenv("VOC_API_KEY")
if not openai_api_key:
    raise RuntimeError("Missing VOC_API_KEY")

from workflow_agents.base_agents import ActionPlanningAgent


def main():
    print("[ActionPlanningAgent Test]")
    print("This agent extracts an ordered list of steps using ONLY the provided knowledge.")
    print("VOC_API_KEY loaded:", bool(openai_api_key))

    # Provide knowledge that the agent is allowed to use
    knowledge = (
        "Allowed steps for handling a damaged delivery:\n"
        "1) Apologize and acknowledge the issue.\n"
        "2) Ask the customer to provide a photo of the damage.\n"
        "3) Confirm order number and shipping address.\n"
        "4) Offer a replacement shipment or refund (if within policy).\n"
        "5) Provide next steps and expected timeline.\n"
    )

    agent = ActionPlanningAgent(openai_api_key=openai_api_key, knowledge=knowledge)

    prompt = "A customer says their package arrived damaged. What steps should support take?"
    steps = agent.extract_steps_from_prompt(prompt)

    print("\n--- Extracted Steps (list) ---")
    for i, step in enumerate(steps, start=1):
        print(f"{i}. {step}")


if __name__ == "__main__":
    main()
