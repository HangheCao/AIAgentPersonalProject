# AI Agent Personal Project

This repository contains a collection of projects exploring **agentic AI systems** built with large language models (LLMs).  
The projects focus on role-based prompting, multi-agent collaboration, evaluation loops, and structured reasoning workflows.

Each subproject demonstrates a different aspect of agent design and orchestration.

---

## 📁 Projects

### 🔹 AI-Powered Agentic Workflows for Project Management
**Path:** `agentic-workflows/`

A multi-agent system that simulates collaboration between specialized roles such as:
- Product Manager
- Program Manager
- Development Engineer

Key features:
- Agent routing based on task intent
- Role-specific prompting
- Automated evaluation and feedback loops
- Structured outputs including user stories, features, and development tasks

This project demonstrates how complex planning tasks can be decomposed and solved reliably using agentic patterns.

---

### 🔹 AgentsVille Trip Planner: A Multi-Agent Travel Assistant System
**Path:** `agentsville-trip-planner/`

An AI-powered travel planning system for a fictional city called *AgentsVille*.

Key concepts:
- Role-based prompting
- Chain-of-thought reasoning
- ReAct-style Thought → Action → Observation loops
- Tool usage for cost calculation, activity lookup, and itinerary evaluation
- Iterative self-improvement based on feedback

The system generates and refines a day-by-day travel itinerary while respecting user preferences, constraints, and environmental factors such as weather.

---

### 🔹 UdaPlay: AI Research Agent for Video Game Intelligence

**Path:** `An_AI_Research_Agent_for_the_Video_Game_Intelligence/`

An AI-powered research assistant designed to answer natural language questions about video games, publishers, platforms, and release information.

Key concepts:
- Retrieval-Augmented Generation (RAG) using a local vector database  
- Semantic search over structured video game datasets  
- Confidence-based evaluation of retrieved information  
- Web search fallback for missing or low-confidence answers  
- Tool-based agent architecture (retrieve → evaluate → search)  
- Stateful agent workflow implemented as a decision/state machine  

The system first attempts to answer user queries using internal game knowledge stored in a vector database. When the retrieved information is incomplete or unreliable, the agent automatically falls back to web search, integrates external results, and produces a clean, structured, and well-cited response.

---

## 🛠 Technologies & Concepts

- Python
- Large Language Models (LLMs)
- Agent routing and orchestration
- Evaluation-driven refinement
- Structured prompt engineering

---

## 📌 Purpose

This repository serves as:
- A learning project for advanced LLM agent design
- A demonstration of practical agentic workflows
- A portfolio piece showcasing applied AI reasoning techniques
