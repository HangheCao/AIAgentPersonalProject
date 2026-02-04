🧭 AgentsVille Trip Planner: A Multi-Agent Travel Assistant System

AgentsVille Trip Planner is an AI-powered travel planning system designed to demonstrate advanced large language model (LLM) reasoning and agentic workflows. The project simulates a real-world travel assistant that generates, evaluates, and iteratively refines personalized travel itineraries for a fictional city called AgentsVille.

The system showcases modern agent design patterns, including structured prompting, tool use, self-evaluation, and feedback-driven revision loops. Rather than producing a single static response, the agent reasons step by step, checks its own work, and improves the plan until it satisfies all constraints.

🚀 Key Concepts Demonstrated

This project implements and integrates several advanced LLM techniques:

Role-Based Prompting
The agent operates as a specialized travel planner, guided by a carefully designed system prompt.

Chain-of-Thought Reasoning
The itinerary is planned step by step, ensuring logical consistency across days, activities, costs, and constraints.

ReAct Prompting (Reasoning + Acting)
The agent follows a Thought → Action → Observation cycle, invoking tools to retrieve information, perform calculations, and validate decisions.

Feedback Loops & Self-Evaluation
The agent evaluates its own itinerary using predefined criteria and revises it iteratively to correct errors and improve quality.

🛠 Project Workflow Overview

Vacation Definition
Trip details such as duration, interests, and constraints are defined and validated using a Pydantic model (VacationInfo).

Weather & Activity Review
Simulated API calls provide bulk weather data and activity schedules, forming the knowledge base for planning.

Itinerary Generation (ItineraryAgent)
A dedicated agent generates a detailed, day-by-day itinerary in a single LLM call using a structured prompt that includes role, instructions, examples, and output format.

Itinerary Evaluation
The itinerary is checked against multiple criteria, including:

Date and location alignment

Budget accuracy

Availability of activities

Weather suitability
Some evaluations leverage an LLM to compare activity descriptions against weather conditions.

Tool-Augmented Reasoning
The agent uses the following tools:

calculator_tool for cost calculations

get_activities_by_date_tool for activity lookup

run_evals_tool for automated evaluation

final_answer_tool to return the completed itinerary

Iterative Revision (ItineraryRevisionAgent)
A second agent refines the itinerary using the ReAct loop, incorporating both evaluation results and user feedback. The final plan guarantees:

All constraints are met

Weather-appropriate activities

At least two activities per day

🎯 Goal

The final outcome is a robust, self-correcting AI travel agent capable of producing high-quality, personalized itineraries while demonstrating practical agentic reasoning patterns used in modern LLM applications.



