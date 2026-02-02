# Agentic Workflows Project

This project demonstrates how to design and implement **agentic AI workflows** using large language models (LLMs).  
The system simulates collaboration between multiple specialized agents—such as a Product Manager, Program Manager, and Development Engineer—to generate a complete, structured project plan from a single high-level product specification.

Rather than relying on a single prompt-response interaction, this project showcases **multi-step reasoning, role-based prompting, routing, and self-evaluation loops** to produce higher-quality and more reliable outputs.

## Key Concepts Demonstrated

- **Role-Based Prompting**  
  Each agent operates under a clearly defined role (e.g., Product Manager, Program Manager, Development Engineer) with strict responsibilities and output constraints.

- **Agent Routing**  
  A routing agent dynamically selects the most appropriate agent for each workflow step based on the task description.

- **Evaluation and Feedback Loops**  
  Dedicated evaluation agents validate outputs against strict formatting and content criteria.  
  If an output fails evaluation, feedback is automatically generated and the agent is prompted to refine its response.

- **Structured Outputs**  
  The final workflow output always includes:
  - User Stories (user-centered requirements)
  - Product Features (grouped capabilities derived from user needs)
  - Development Tasks (implementation-level work items with acceptance criteria)

- **Deterministic Workflow Control**  
  The workflow enforces step limits, agent responsibilities, and output formats to reduce hallucination and ensure consistency.

## Project Structure

- `phase_1/`  
  Core agent implementations, including base agents, routing logic, and evaluation mechanisms.

- `phase_2/`  
  Workflow orchestration logic that coordinates agents to produce a complete project plan.

- `agentic_workflow.py`  
  The main executable that runs the agentic workflow end-to-end.

## Why This Project Matters

Traditional prompt-based systems often struggle with:
- Long-term reasoning
- Role confusion
- Inconsistent output formats

This project demonstrates how **agentic design patterns** can solve these problems by:
- Breaking complex tasks into well-defined steps
- Assigning responsibility to specialized agents
- Using evaluators to enforce correctness and structure

The result is a scalable pattern for building reliable, multi-agent AI systems for planning, analysis, and decision support.

