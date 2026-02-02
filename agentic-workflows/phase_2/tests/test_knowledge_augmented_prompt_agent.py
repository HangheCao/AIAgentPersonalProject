import os, sys
from dotenv import load_dotenv
__file__ = "D:/AIAgent/Agentic Workflows/starter/phase_2/tests/test_knowledge_augmented_prompt_agent.py"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PHASE2_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
PROJECT_ROOT = os.path.abspath(os.path.join(PHASE2_DIR, ".."))
PHASE1_DIR = os.path.join(PROJECT_ROOT, "phase_1")
sys.path.insert(0, PHASE1_DIR)
load_dotenv(os.path.join(PHASE1_DIR, ".env"), override=True)

openai_api_key = os.getenv("VOC_API_KEY")
if not openai_api_key:
    raise RuntimeError("Missing VOC_API_KEY")

from workflow_agents.base_agents import KnowledgeAugmentedPromptAgent


def main():
    print("[KnowledgeAugmentedPromptAgent Test]")
    print("This agent uses provided company/product knowledge and must NOT use its own general knowledge.")
    print("VOC_API_KEY loaded:", bool(openai_api_key))

    persona = "a support agent for an email routing product"
    knowledge = (
        "Product facts:\n"
        "- Refunds allowed within 30 days.\n"
        "- Damaged items: request a photo and offer replacement.\n"
        "- Shipping: 3–5 business days.\n"
    )

    agent = KnowledgeAugmentedPromptAgent(
        openai_api_key=openai_api_key,
        persona=persona,
        knowledge=knowledge
    )

    prompt = "Customer: My order arrived damaged yesterday. What can you do?"
    result = agent.respond(prompt)

    print("\n--- Response ---")
    print(result)


if __name__ == "__main__":
    main()