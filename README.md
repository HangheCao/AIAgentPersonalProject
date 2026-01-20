# AgentsVille Trip Planner  
### LLM Agents + ReAct + Evaluations

This project implements an end-to-end **LLM-based travel planning system** for a fictional city called **AgentsVille**.  
It demonstrates practical agent design patterns, including structured outputs, tool use, evaluation loops, and ReAct-style reasoning.

---

## ✨ Key Features

- **Role-based prompting**
  - Specialized itinerary planning agent
  - Revision agent for iterative improvement
- **Structured outputs**
  - Pydantic schemas for strict validation
- **Tool use**
  - Calculator for reliable arithmetic
  - Activity lookup to prevent hallucinations
  - Automated evaluation tools
- **ReAct loop**
  - `THOUGHT → ACTION → OBSERVATION` for controlled iteration
- **Feedback loops**
  - Evaluate → revise → re-evaluate → finalize
- **Final narration**
  - Human-readable story version of the trip itinerary

---

## ✅ What the System Produces

A validated, day-by-day itinerary that:

- Matches the requested **dates and destination**
- **Respects the budget**
- Uses **only available activities** (no hallucinations)
- Avoids **outdoor-only activities during bad weather**
- Includes **at least one activity per day**

---

## 📁 Repository Contents

- `project_starter.ipynb`  
  Main notebook implementing the entire pipeline

- `project_lib.py`  
  Helper library (mock APIs, agent utilities, evaluation helpers)

---

## 1️⃣ Define Vacation Details + Validate with Pydantic

Trip details are first encoded in a JSON-like Python dictionary:

- Travelers (name, age, interests)
- Destination
- Arrival / departure dates
- Budget

Pydantic models (`Traveler`, `VacationInfo`) are then used to validate the input:

```python
vacation_info = VacationInfo.model_validate(VACATION_INFO_DICT)




