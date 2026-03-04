# AI Reliability Project

This project focuses on AI failure autopsy, self-healing mechanisms, and drift monitoring to ensure robust and reliable AI systems.

## Project Structure

- **ai-engineering-hub**: Core engine for AI failure analysis and repair.
- **ai-failure-autopsy**: Tools and dashboards for visualizing and diagnosing AI failures.
- **self-healing**: Logic for autonomous repair of AI models and pipelines.
- **observer**: Monitoring tools for detecting data and model drift.

## Getting Started

### Prerequisites

- Python 3.x
- [Ollama](https://ollama.com/) (for local LLM support)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ai-reliability-project
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1
   ```

3. Install dependencies:
   ```bash
   pip install langchain-ollama streamlit
   ```

## Running the Project

To run the pipeline and the dashboard:
```bash
python ai-engineering-hub/ai_failure_autopsy/run_pipeline.py
python -m streamlit run ai-engineering-hub/ai_failure_autopsy/ui/dashboard.py
```

## Features

- **Real-time Failure Simulation**: Input failure descriptions and get instant AI-driven classification.
- **Drift Monitoring**: Track model performance and data consistency over time.
- **Repair Engine**: Automatically suggest and apply fixes to common AI failure modes.
- **Premium Dashboard**: A sleek, interactive UI built with Streamlit for clear visualization of system health.
