# Query-Doc Agent

An autonomous database sentinel and self-healing SQL diagnostics AI agent built to query documents and structured data seamlessly.

## 🚀 Project Architecture

The system follows a strict modular design pattern to separate operational layers:

- **Root**: System orchestration and packaging deployment tracking.
- **src/core**: Cognitive agent logic and feedback-driven self-healing query layers.
- **src/tools**: Specialized data connection executors and vector space retrievers.
- **src/utils**: System diagnostics environmental configurations.

## 🛠️ Tech Stack

- **Language**: Python
- **Orchestration**: LangGraph State-Machine Framework
- **Data Stores**: SQLite, FAISS Vector Database
- **Packaging**: Setuptools