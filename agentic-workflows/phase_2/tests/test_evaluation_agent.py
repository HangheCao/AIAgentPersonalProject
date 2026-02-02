import os, sys
from dotenv import load_dotenv
__file__ = "D:/AIAgent/Agentic Workflows/starter/phase_2/tests/test_evaluation_agent.py"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PHASE2_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
PROJECT_ROOT = os.path.abspath(os.path.join(PHASE2_DIR, ".."))
PHASE1_DIR = os.path.join(PROJECT_ROOT, "phase_1")
sys.path.insert(0, PHASE1_DIR)
load_dotenv(os.path.join(PHASE1_DIR, ".env"), override=True)

openai_api_key = os.getenv("VOC_API_KEY")
if not openai_api_key:
    raise RuntimeError("Missing VOC_API_KEY")

from workflow_agents.base_agents import DirectPromptAgent, EvaluationAgent


def main():
    print("[EvaluationAgent Test]")
    print("This agent iteratively evaluates a worker agent’s response against criteria and requests fixes.")
    print("VOC_API_KEY loaded:", bool(openai_api_key))

    # Worker agent (must implement .respond())
    worker_agent = DirectPromptAgent(openai_api_key=openai_api_key)

    persona = "a strict quality assurance evaluator"
    evaluation_criteria = (
        "1) Polite tone\n"
        "2) Provides clear next steps\n"
        "3) Does NOT mention internal-only info\n"
        "4) Under 120 words\n"
    )
    max_interactions = 2  # keep small so the test runs fast

    evaluator = EvaluationAgent(
        openai_api_key=openai_api_key,
        persona=persona,
        evaluation_criteria=evaluation_criteria,
        worker_agent=worker_agent,
        max_interactions=max_interactions,
    )

    initial_prompt = "Customer says: 'My package arrived damaged.' Draft a reply."
    result = evaluator.evaluate(initial_prompt)

    print("\n--- Evaluation Output (dict) ---")
    print(result)
    print("\nFinal response:\n", result.get("final_response"))
    print("\nEvaluation:\n", result.get("evaluation"))
    print("\nIterations:", result.get("iterations"))


if __name__ == "__main__":
    main()
