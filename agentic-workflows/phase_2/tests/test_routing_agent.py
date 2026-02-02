import os, sys
from dotenv import load_dotenv
__file__ = "D:/AIAgent/Agentic Workflows/starter/phase_2/tests/test_routing_agent.py"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PHASE2_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
PROJECT_ROOT = os.path.abspath(os.path.join(PHASE2_DIR, ".."))
PHASE1_DIR = os.path.join(PROJECT_ROOT, "phase_1")
sys.path.insert(0, PHASE1_DIR)
load_dotenv(os.path.join(PHASE1_DIR, ".env"), override=True)

openai_api_key = os.getenv("VOC_API_KEY")
if not openai_api_key:
    raise RuntimeError("Missing VOC_API_KEY")

from workflow_agents.base_agents import RoutingAgent


def main():
    print("[RoutingAgent Test]")
    print("This agent selects the best worker agent based on embedding similarity.")
    print("VOC_API_KEY loaded:", bool(openai_api_key))

    # Define candidate agents (name, description, callable)
    def refunds_agent(user_input: str) -> str:
        return "Routed to Refunds Agent: Refunds are available within 30 days with receipt."

    def shipping_agent(user_input: str) -> str:
        return "Routed to Shipping Agent: Standard shipping is 3–5 business days."

    def damaged_item_agent(user_input: str) -> str:
        return "Routed to Damaged Item Agent: Please send a photo and we will replace the item."

    agents = [
        {
            "name": "RefundsAgent",
            "description": "Handles refund requests, returns, and money-back questions.",
            "func": refunds_agent,
        },
        {
            "name": "ShippingAgent",
            "description": "Handles shipping status, delivery estimates, tracking, and delays.",
            "func": shipping_agent,
        },
        {
            "name": "DamagedItemAgent",
            "description": "Handles damaged, broken, defective items and replacement requests.",
            "func": damaged_item_agent,
        },
    ]

    router = RoutingAgent(openai_api_key=openai_api_key, agents=agents)

    user_input = "My package arrived broken and I want a replacement."
    result = router.route(user_input)

    print("\n--- Routing Result ---")
    print(result)


if __name__ == "__main__":
    main()