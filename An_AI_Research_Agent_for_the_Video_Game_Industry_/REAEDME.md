📁 Project Files

This project is organized into two main Jupyter notebooks, each corresponding to a major stage of the UdaPlay system.

Udaplay_01_starter_project.ipynb
Udaplay_02_starter_project.ipynb
📓 Udaplay_01_starter_project.ipynb — RAG Pipeline

This notebook focuses on building the Retrieval-Augmented Generation (RAG) foundation.

Key components:

Load and preprocess video game data from JSON files

Chunk and embed game information

Create and persist a ChromaDB vector database

Implement semantic search over the game dataset

Validate retrieval quality with example queries

🤖 Udaplay_02_starter_project.ipynb — AI Agent Implementation

This notebook implements the UdaPlay AI Research Agent.

Key components:

Tool-based agent architecture:

Internal retrieval from vector database

Retrieval quality evaluation

Web search fallback (Tavily API)

Stateful agent workflow implemented as a state machine

Confidence-based decision making

Structured reporting with citations

Demonstration of the agent answering multiple example queries
