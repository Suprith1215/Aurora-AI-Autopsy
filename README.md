# 🌌 Aurora AI: Failure Autopsy & Self-Healing Framework

<p align="center">
  <img src="ai-engineering-hub/resources/ai-eng-hub.gif" alt="Aurora AI Banner" width="800">
</p>

---

## 🚀 Overview

**Aurora AI** is a state-of-the-art AI Reliability framework designed to detect, diagnose, and repair failures in production AI systems. Built as a specialized module within the **[AI Engineering Hub](https://github.com/patchy631/ai-engineering)** ecosystem, Aurora provides a comprehensive suite of tools for maintaining the health and transparency of Large Language Model (LLM) applications.

Whether it's detecting data drift, classifying hallucination types, or autonomously suggesting code fixes, Aurora ensures your AI remains resilient and trustworthy.

---

## 🌟 Key Features

### 🔍 AI Failure Autopsy
A deep-dive diagnostic engine that analyzes failed interactions to identify root causes. It categorizes failures into specific types like "Hallucination," "Constraint Violation," or "Context Omission."

### 🛡️ Autonomous Self-Healing
An intelligent repair engine that doesn't just find bugs—it fixes them. It generates and applies code patches to mitigate recurring failure modes, significantly reducing manual intervention.

### 📈 Real-Time Drift Monitoring
The **Aurora Sentinel** monitors input and output distributions in real-time, alerting developers when the model's performance begins to deviate from the baseline.

### 🖥️ Premium Dashboard
A sleek, interactive Streamlit-based command center for visualizing system health, simulating failures, and reviewing automated repairs.

---

## 📁 Project Structure

```bash
Aurora-AI-Autopsy/
├── ai-engineering-hub/             # Core logic and research modules
│   ├── ai_failure_autopsy/         # Principal Aurora source code
│   │   ├── autopsy_engine/         # Root cause analysis logic
│   │   ├── self_healing/           # Autonomous repair engine
│   │   ├── observer/               # Drift and performance monitoring
│   │   ├── failure_classifier/     # AI-driven failure categorization
│   │   ├── ui/                     # Streamlit Dashboard source
│   │   └── run_pipeline.py         # Main execution entry point
├── data/                           # Local storage for incident logs and metrics
└── README.md                       # You are here!
```

---

## 🛠️ Getting Started

### Prerequisites

- **Python 3.10+**
- **Ollama**: Required for running local LLMs (Llama 3, DeepSeek, etc.)
- **Git**

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Suprith1215/Aurora-AI-Autopsy.git
   cd Aurora-AI-Autopsy
   ```

2. **Set Up Virtual Environment**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\Activate.ps1
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install langchain-ollama streamlit pandas plotly
   ```

4. **Prepare local LLM (Ollama)**
   ```bash
   ollama pull llama3
   ```

---

## 🚀 Running Aurora

### 1. Initialize the Pipeline
Run the main pipeline to seed initial data and start the monitoring services:
```bash
python ai-engineering-hub/ai_failure_autopsy/run_pipeline.py
```

### 2. Launch the Dashboard
Open the interactive command center:
```bash
python -m streamlit run ai-engineering-hub/ai_failure_autopsy/ui/dashboard.py
```

---

## 🤝 Relationship with AI Engineering Hub

This project is a specialized branch of the **[AI Engineering Hub](https://github.com/patchy631/ai-engineering)**, a massive ecosystem containing 90+ production-ready AI projects. Aurora focuses specifically on the **Reliability and Observability** pillar of AI Engineering, implementing best practices for production-grade LLM deployments.

---

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 💬 Connect

Developed as part of the Advanced AI Engineering initiative. For feedback or contributions, feel free to open an issue!

**"Bringing light to AI failures."** — 🌌 **Aurora AI**
