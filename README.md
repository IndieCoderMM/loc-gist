# LocGist 

**LocGist** is a offline AI tool designed to help you quickly summarize and extract key information from your documents. It uses the Qwen 3 model to provide fast and efficient document processing without relying on external APIs.

- [Tutorial](https://www.freecodecamp.org/news/build-a-local-ai/)

## Features

- 🛡️Privacy: No data leaves your system.

- 💵 No Cost: Run locally without API fees.

- 🖥️Offline Capability: Process documents without internet access.

- ⚙️ Customization: Use any LLM, embedding, and adapt to your needs

## Getting Started

### Ollama Setup 🦙

**1. Install Ollama**
- Windows: Download the installer from the Ollama website: https://ollama.com/download
- Linux/Mac: Open a terminal and run `curl -fsSL https://ollama.com/install.sh | sh`

**2. Verify Ollama Installation**
- Open a new terminal window and run: `ollama --version`

**3. Choose Your Qwen 3 Model**
- Select a Qwen 3 model (e.g., qwen3:8b, qwen3:4b, qwen3:30b-a3b) based on your intended task and available hardware resources
- Consider the model's size, performance, and reasoning capabilities

**4. Pull and Run Qwen 3**
- Pull the chosen Qwen 3 model with: `ollama pull <model_tag>`
- *Interactive Mode*: `ollama run <model_tag>`
- *Server Mode*:
  - Start the Ollama server with: `ollama serve <model_tag>`
  - Access the model via API at `http://localhost:11434`

### Python Setup 🐍

1. Create a virtual environment to manage dependencies
```bash
python -m venv .venv
```

2. Activate the environment
```bash
source .venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

3. Install necessary libraries using pip
```bash
pip install langchain langchain-community langchain-core langchain-ollama chromadb pypdf ttkbootstrap
```

