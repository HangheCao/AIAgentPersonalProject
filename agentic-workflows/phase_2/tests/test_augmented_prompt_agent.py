import os, sys
from dotenv import load_dotenv
__file__ = "D:/AIAgent/Agentic Workflows/starter/phase_2/tests/test_augmented_prompt_agent.py"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PHASE2_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
PROJECT_ROOT = os.path.abspath(os.path.join(PHASE2_DIR, ".."))
PHASE1_DIR = os.path.join(PROJECT_ROOT, "phase_1")
sys.path.insert(0, PHASE1_DIR)
load_dotenv(os.path.join(PHASE1_DIR, ".env"), override=True)

openai_api_key = os.getenv("VOC_API_KEY")
if not openai_api_key:
    raise RuntimeError("Missing VOC_API_KEY")

from workflow_agents.base_agents import AugmentedPromptAgent

def main():
    print("[AugmentedPromptAgent Test]")
    print("This agent uses a system persona to shape responses (augmented prompt).")
    print("VOC_API_KEY loaded:", bool(openai_api_key))

    persona = (
        "You are an email assistant.\n"
        "Follow these rules:\n"
        "1) Be polite.\n"
        "2) Ask one clarifying question if needed.\n"
        "3) End with a short call-to-action.\n"
    )

    agent = AugmentedPromptAgent(openai_api_key=openai_api_key, persona=persona)

    prompt = "Customer says: 'My package arrived damaged.' Draft a reply."
    result = agent.respond(prompt)

    print("\n--- Response ---")
    print(result)


if __name__ == "__main__":
    main()
