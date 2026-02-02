import os
import sys
from dotenv import load_dotenv

__file__ = "D:/AIAgent/Agentic Workflows/starter/phase_2/tests/test_direct_prompt_agent.py"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PHASE2_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
PROJECT_ROOT = os.path.abspath(os.path.join(PHASE2_DIR, ".."))
PHASE1_DIR = os.path.join(PROJECT_ROOT, "phase_1")

sys.path.insert(0, PHASE1_DIR)
dotenv_path = os.path.join(PHASE1_DIR, ".env")
loaded = load_dotenv(dotenv_path, override=True)

openai_api_key = os.getenv("VOC_API_KEY")
if not openai_api_key:
    raise RuntimeError(f"Missing VOC_API_KEY. dotenv_loaded={loaded}. Checked: {dotenv_path}")

from workflow_agents.base_agents import DirectPromptAgent

def main():
    print("[DirectPromptAgent Test]")
    print("This agent answers using general LLM knowledge (no external docs provided).")
    print("VOC_API_KEY loaded:", bool(openai_api_key))

    agent = DirectPromptAgent(openai_api_key=openai_api_key)

    prompt = "In 2-3 sentences, explain what an API key is and why it should be kept secret."
    response = agent.respond(prompt)

    print("\n--- Response ---")
    print(response)

if __name__ == "__main__":
    main()
