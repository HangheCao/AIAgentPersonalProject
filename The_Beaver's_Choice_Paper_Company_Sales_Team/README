# 🧾 The Beaver’s Choice: Multi-Agent Sales & Inventory System

An AI-powered multi-agent system that simulates the operations of a paper supply company.  
The system manages inventory, generates customer quotes, processes sales orders, enforces financial constraints, and produces automated financial reports.

---

## 📁 Project Structure
The_Beaver's_Choice_Paper_Company_Sales_Team/
│
├── assets/ # Workflow diagram
├── project_starter.py # Main multi-agent implementation
├── reflection_report_updated.pdf
└── test_results.csv # Simulation results


---

## 🏗 System Architecture

This project implements a modular **multi-agent architecture** consisting of:

### 🔹 Orchestrator Agent
- Parses incoming customer requests
- Routes tasks to specialized agents
- Combines outputs into a final response

### 🔹 Inventory Agent
- Checks stock availability
- Identifies low-stock items
- Provides inventory snapshots

### 🔹 Quoting Agent
- Calculates prices with markup logic
- Verifies stock availability
- Generates structured quote explanations

### 🔹 Ordering Agent
- Places customer sales transactions
- Executes stock reorders
- Ensures sufficient cash before purchases

### 🔹 Financial Tools
- Tracks company cash balance
- Calculates inventory valuation
- Generates full financial reports

---

## 🔄 End-to-End Workflow

1. Customer request received  
2. Orchestrator extracts items and quantities  
3. Inventory availability checked  
4. Financial feasibility verified  
5. Quote generated  
6. Sale executed (if possible)  
7. Optional stock reorder triggered  
8. Cash and inventory updated  
9. Results recorded in `test_results.csv`

---

## 🛠 Technologies & Concepts

- Python
- Large Language Models (GPT-4o-mini)
- Tool-calling agent architecture
- SQLite database integration
- SQLAlchemy ORM
- Multi-agent orchestration patterns
- ReAct-style reasoning loops
- Structured prompt engineering
- Financial constraint enforcement
- Deterministic simulation with seeded data

---

## 📊 Evaluation

The system was tested using the provided `quote_requests_sample.csv` dataset.

Results demonstrate:

- Successful order fulfillment and cash balance updates
- Correct rejection of invalid or infeasible requests
- Accurate inventory enforcement
- Consistent financial tracking

See `test_results.csv` for full output logs.

---

## ▶️ How to Run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
