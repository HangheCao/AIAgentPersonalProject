# agentic_workflow.py

# TODO: 1 - Import the following agents: ActionPlanningAgent, KnowledgeAugmentedPromptAgent, EvaluationAgent, RoutingAgent from the workflow_agents.base_agents module

import os
import sys
from dotenv import load_dotenv

# --- Make phase_1 importable + load phase_1/.env ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))        # phase_2
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..")) # starter
PHASE1_DIR = os.path.join(PROJECT_ROOT, "phase_1")

sys.path.insert(0, PHASE1_DIR)
load_dotenv(os.path.join(PHASE1_DIR, ".env"), override=True)


from workflow_agents.base_agents import (
    ActionPlanningAgent,
    KnowledgeAugmentedPromptAgent,
    EvaluationAgent,
    RoutingAgent
)

# TODO: 2 - Load the OpenAI key into a variable called openai_api_key
openai_api_key = os.getenv("VOC_API_KEY")
if not openai_api_key:
    raise ValueError("Missing VOC_API_KEY. Check phase_1/.env")
# load the product spec
# TODO: 3 - Load the product spec document Product-Spec-Email-Router.txt into a variable called product_spec
product_spec_path = os.path.join(os.path.dirname(__file__), "Product-Spec-Email-Router.txt")
product_spec = open(product_spec_path, "r", encoding="utf-8").read()

# Instantiate all the agents

# Action Planning Agent
knowledge_action_planning = (
    "Return EXACTLY 3 steps and nothing else.\n"
    "Step 1) PM: Generate User Stories\n"
    "Step 2) PgM: Define Product Features\n"
    "Step 3) ENG: Create Development Tasks\n"
    "Do NOT output additional steps.\n"
)


# TODO: 4 - Instantiate an action_planning_agent using the 'knowledge_action_planning'
action_planning_agent = ActionPlanningAgent(openai_api_key = openai_api_key, 
                                            knowledge=knowledge_action_planning
                                            )
# Product Manager - Knowledge Augmented Prompt Agent
persona_product_manager = "You are a Product Manager, you are responsible for defining the user stories for a product."
knowledge_product_manager = (
    "Stories are defined by writing sentences with a persona, an action, and a desired outcome. "
    "The sentences always start with: As a "
    "Write several stories for the product spec below, where the personas are the different users of the product. "
    # TODO: 5 - Complete this knowledge string by appending the product_spec loaded in TODO 3
    f"\n\nProduct Specification:\n{product_spec}"
)
# TODO: 6 - Instantiate a product_manager_knowledge_agent using 'persona_product_manager' and the completed 'knowledge_product_manager'
product_manager_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona=persona_product_manager,
    knowledge=knowledge_product_manager
)

# Product Manager - Evaluation Agent
# TODO: 7 - Define the persona and evaluation criteria for a Product Manager evaluation agent and instantiate it as product_manager_evaluation_agent. This agent will evaluate the product_manager_knowledge_agent.
# The evaluation_criteria should specify the expected structure for user stories (e.g., "As a [type of user], I want [an action or feature] so that [benefit/value].").
persona_product_manager_eval = "You are an evaluation agent that checks the answers of other worker agents"
evaluation_criteria_product_manager = (
    "The answer should be stories that follow the following structure: "
    "As a [type of user], I want [an action or feature] so that [benefit/value]."
)

product_manager_evaluation_agent = EvaluationAgent(
    openai_api_key=openai_api_key,
    persona=persona_product_manager_eval,
    evaluation_criteria=evaluation_criteria_product_manager,
    worker_agent=product_manager_knowledge_agent,
    max_interactions=10
)
# Program Manager - Knowledge Augmented Prompt Agent
persona_program_manager = (
    "You are a Program Manager.\n"
    "Your job is to define product features for the Email Router.\n"
    "You MUST output ONLY product features.\n"
    "You MUST NOT output templates or explanations.\n"
)

knowledge_program_manager = (
    "Output 3-6 product features.\n"
    "Each feature MUST follow this EXACT format (including colons):\n\n"
    "Feature Name: <name>\n"
    "Description: <1-2 sentences>\n"
    "Key Functionality: <comma-separated or short sentence>\n"
    "User Benefit: <1 sentence>\n\n"
    "Repeat the block for each feature.\n"
    "Do NOT use numbering like 'Feature 1'.\n"
    "Do NOT add any other headings (no 'Email Router Features:', no bullets)."
)

# Instantiate a program_manager_knowledge_agent using 'persona_program_manager' and 'knowledge_program_manager'
# (This is a necessary step before TODO 8. Students should add the instantiation code here.)
program_manager_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona=persona_program_manager,
    knowledge=knowledge_program_manager
)
# Program Manager - Evaluation Agent
persona_program_manager_eval = "You are an evaluation agent that checks the answers of other worker agents."

# TODO: 8 - Instantiate a program_manager_evaluation_agent using 'persona_program_manager_eval' and the evaluation criteria below.
#                      "The answer should be product features that follow the following structure: " \
#                      "Feature Name: A clear, concise title that identifies the capability\n" \
#                      "Description: A brief explanation of what the feature does and its purpose\n" \
#                      "Key Functionality: The specific capabilities or actions the feature provides\n" \
#                      "User Benefit: How this feature creates value for the user"
# For the 'agent_to_evaluate' parameter, refer to the provided solution code's pattern.
evaluation_criteria_program_manager = (
    "Return product features for the Email Router.\n"
    "EACH feature MUST be in this EXACT format (no bullets, no numbering):\n"
    "Feature Name: ...\n"
    "Description: ...\n"
    "Key Functionality: ...\n"
    "User Benefit: ...\n"
    "Do NOT use 'Feature:' or '- Description:' or 'Feature 1:'."
)



program_manager_evaluation_agent = EvaluationAgent(
    openai_api_key=openai_api_key,
    persona=persona_program_manager_eval,
    evaluation_criteria=evaluation_criteria_program_manager,
    worker_agent=program_manager_knowledge_agent,
    max_interactions=10
)

# Development Engineer - Knowledge Augmented Prompt Agent
persona_dev_engineer = (
    "You are a Development Engineer.\n"
    "Your responsibility is to produce concrete development tasks for a product.\n"
    "You MUST output ONLY development tasks.\n"
    "You MUST NOT explain how to create tasks.\n"
    "You MUST NOT include instructions, commentary, or templates.\n"
)

knowledge_dev_engineer = (
    "You will be given User Stories.\n"
    "For each task, the 'Related User Story' MUST be copied EXACTLY from the provided user stories.\n"
    "Do NOT invent IDs like US-101.\n\n"
    "Each development task MUST follow this EXACT format:\n\n"
    "Task ID: <unique id like DEV-001>\n"
    "Task Title: <short title>\n"
    "Related User Story: <paste exact user story sentence>\n"
    "Description: <what to build>\n"
    "Acceptance Criteria: <done conditions>\n"
    "Estimated Effort: <hours or days>\n"
    "Dependencies: <DEV-### or None>\n\n"
    "Output 6-12 tasks."
)


# Instantiate a development_engineer_knowledge_agent using 'persona_dev_engineer' and 'knowledge_dev_engineer'
# (This is a necessary step before TODO 9. Students should add the instantiation code here.)
dev_engineer_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona=persona_dev_engineer,
    knowledge=knowledge_dev_engineer
)
# Development Engineer - Evaluation Agent
persona_dev_engineer_eval = (
    "Accept ONLY if:\n"
    "- There are 3-6 features.\n"
    "- Every feature block contains ALL four required lines with exact labels:\n"
    "  'Feature Name:', 'Description:', 'Key Functionality:', 'User Benefit:'\n"
    "- No numbering like 'Feature 1'\n"
    "- No extra headings like 'Email Router Features:'\n"
    "- Content is specific to Email Router."
)
# TODO: 9 - Instantiate a development_engineer_evaluation_agent using 'persona_dev_engineer_eval' and the evaluation criteria below.
#                      "The answer should be tasks following this exact structure: " \
#                      "Task ID: A unique identifier for tracking purposes\n" \
#                      "Task Title: Brief description of the specific development work\n" \
#                      "Related User Story: Reference to the parent user story\n" \
#                      "Description: Detailed explanation of the technical work required\n" \
#                      "Acceptance Criteria: Specific requirements that must be met for completion\n" \
#                      "Estimated Effort: Time or complexity estimation\n" \
#                      "Dependencies: Any tasks that must be completed first"
# For the 'agent_to_evaluate' parameter, refer to the provided solution code's pattern.
evaluation_criteria_dev_engineer = (
    "Accept ONLY if ALL of the following are true:\n"
    "- The response contains 3 or more development tasks.\n"
    "- EACH task includes ALL of these exact labels:\n"
    "  Task ID:\n"
    "  Task Title:\n"
    "  Related User Story:\n"
    "  Description:\n"
    "  Acceptance Criteria:\n"
    "  Estimated Effort:\n"
    "  Dependencies:\n"
    "- The labels must appear exactly as written above.\n"
    "- Tasks must be related to the Email Router product.\n"
    "- Do NOT require bullet points or numbered lists.\n"
    "- Reject only if any label is missing or content is unrelated."
)




dev_engineer_evaluation_agent = EvaluationAgent(
    openai_api_key=openai_api_key,
    persona=persona_dev_engineer_eval,
    evaluation_criteria=evaluation_criteria_dev_engineer,
    worker_agent=dev_engineer_knowledge_agent,
    max_interactions=10
)

# Job function persona support functions
# TODO: 11 - Define the support functions for the routes of the routing agent (e.g., product_manager_support_function, program_manager_support_function, development_engineer_support_function).
# Each support function should:
#   1. Take the input query (e.g., a step from the action plan).
#   2. Get a response from the respective Knowledge Augmented Prompt Agent.
#   3. Have the response evaluated by the corresponding Evaluation Agent.
#   4. Return the final validated response.
# Job function persona support functions
def product_manager_support_function(query: str):
    # 1) Knowledge agent responds
    response_from_knowledge = product_manager_knowledge_agent.respond(query)

    # 2) Evaluation agent evaluates (iterative refinement happens inside evaluate())
    evaluation_result = product_manager_evaluation_agent.evaluate(response_from_knowledge)

    # 3) Return final validated response
    return evaluation_result["final_response"]


def program_manager_support_function(query: str):
    response_from_knowledge = program_manager_knowledge_agent.respond(query)

    combined = (
        "TASK: Produce product features in the required template.\n\n"
        f"INPUT STEP:\n{query}\n\n"
        f"DRAFT FEATURES:\n{response_from_knowledge}\n"
    )

    evaluation_result = program_manager_evaluation_agent.evaluate(combined)
    return evaluation_result["final_response"]


def dev_engineer_support_function(query: str):
    response_from_knowledge = dev_engineer_knowledge_agent.respond(query)
    evaluation_result = dev_engineer_evaluation_agent.evaluate(response_from_knowledge)
    return evaluation_result["final_response"]

# Routing Agent
# TODO: 10 - Instantiate a routing_agent. You will need to define a list of agent dictionaries (routes) for Product Manager, Program Manager, and Development Engineer. Each dictionary should contain 'name', 'description', and 'func' (linking to a support function). Assign this list to the routing_agent's 'agents' attribute.
routing_agent = RoutingAgent(openai_api_key=openai_api_key, agents=[])

routes = [
    {
        "name": "Product Manager",
        "description": (
            "Creates user stories and defines user needs. "
            "Writes stories in the format: "
            "'As a <user>, I want <feature> so that <benefit>'."
        ),
        "func": product_manager_support_function,
    },
    {
        "name": "Program Manager",
        "description": (
            "Defines product features, groups user stories into features, "
            "and describes feature scope, functionality, and user benefit."
        ),
        "func": program_manager_support_function,
    },
    {
        "name": "Development Engineer",
        "description": (
            "Creates detailed development tasks including implementation steps, "
            "acceptance criteria, dependencies, and effort estimates."
        ),
        "func": dev_engineer_support_function,
    },
]

routing_agent.agents = routes

# Run the workflow

print("\n*** Workflow execution started ***\n")
# Workflow Prompt
# ****
workflow_prompt = (
    "IMPORTANT: Return ONLY 3 to 5 total steps.\n"
    "Create a comprehensive project plan for the Email Router product described in the product spec.\n\n"
    "The final plan MUST include ALL three components:\n"
    "A) User Stories (format: 'As a <type of user>, I want <action/feature> so that <benefit/value>.')\n"
    "B) Product Features (format EXACTLY:\n"
    "   Feature Name: ...\n"
    "   Description: ...\n"
    "   Key Functionality: ...\n"
    "   User Benefit: ...)\n"
    "C) Development Tasks (format EXACTLY:\n"
    "   Task ID: ...\n"
    "   Task Title: ...\n"
    "   Related User Story: ...\n"
    "   Description: ...\n"
    "   Acceptance Criteria: ...\n"
    "   Estimated Effort: ...\n"
    "   Dependencies: ...)\n\n"
    "Generate steps that will produce A, B, and C. Do not output only tasks."
)



# ****
print(f"Task to complete in this workflow, workflow prompt = {workflow_prompt}")

print("\nDefining workflow steps from the workflow prompt")
# TODO: 12 - Implement the workflow.
#   1. Use the 'action_planning_agent' to extract steps from the 'workflow_prompt'.
#   2. Initialize an empty list to store 'completed_steps'.
#   3. Loop through the extracted workflow steps:
#      a. For each step, use the 'routing_agent' to route the step to the appropriate support function.
#      b. Append the result to 'completed_steps'.
#      c. Print information about the step being executed and its result.
#   4. After the loop, print the final output of the workflow (the last completed step).
workflow_steps = action_planning_agent.extract_steps_from_prompt(workflow_prompt)

MAX_STEPS = 6
workflow_steps = workflow_steps[:MAX_STEPS]
print(f"\n[Debug] Planner generated {len(workflow_steps)} steps (capped to {MAX_STEPS})")
completed_steps = []

for i, step in enumerate(workflow_steps, start=1):
    if not step or not step.strip():
        continue

    print(f"\n--- Executing step {i} ---")
    print(f"Step: {step}")

    result = routing_agent.route(step)
    completed_steps.append(result)

    print(f"Result:\n{result}")

if completed_steps:
    print("\n*** Workflow execution completed ***\n")
    print("\nFinal Output (all completed steps):\n")
    for idx, item in enumerate(completed_steps, start=1):
        print(f"\n--- Completed Step {idx} Output ---\n{item}")
else:
    print("\nNo steps were generated by the Action Planning Agent.")



