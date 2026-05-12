"# MONDAY - JARVIS File Management Agent

A conversational AI agent inspired by Iron Man's JARVIS that intelligently handles all file management queries. Ask natural language questions about your files and get instant, detailed responses.

## Overview

JARVIS is an intelligent assistant designed to:
- **List and explore** files and directories naturally
- **Find large files** taking up disk space
- **Search for files** by name or pattern
- **Get file metadata** (size, modification date, creation date, etc.)
- **Discover recent files** modified within a time period
- **Understand context** through conversational AI

## Tech Stack

- **Language:** Python 3.8+
- **LLM Provider:** Ollama (Open Source - 100% Free)
- **Supported Models:** Llama 2, Mistral, Neural-Chat, and more
- **File System:** Python's `pathlib`
- **API Communication:** `requests`
- **Environment Management:** `python-dotenv`

## Installation

### 1. Install Ollama (One-time setup)

Download and install Ollama from **[https://ollama.ai](https://ollama.ai)**

After installation, download a model:
```bash
ollama run llama2
```

Or try other models:
```bash
ollama run mistral
ollama run neural-chat
```

Ollama will run on `http://localhost:11434` by default.

### 2. Clone or setup the project

```bash
cd MONDAY
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment (optional)

```bash
copy .env.example .env
```

The `.env` is optional—defaults work for standard Ollama setup. Edit only if you changed Ollama's port or want to use a different model.

## Usage

### Running the Agent

```bash
python main.py
```

This starts an interactive conversation with JARVIS.

### Example Queries

```
You: Show me all files in C:\Users\Downloads
JARVIS: [Lists all files with details]

You: Find large files in my Documents folder
JARVIS: [Shows files over 10MB, sorted by size]

You: What files were modified in the last 24 hours?
JARVIS: [Lists recent files with modification times]

You: Search for *.pdf files
JARVIS: [Finds all PDF files with their locations]

You: Get detailed info about C:\path\to\file.txt
JARVIS: [Shows file metadata and analysis]
```

## Project Structure

```
MONDAY/
├── main.py              # Entry point - interactive conversation loop
├── agent.py             # JARVIS agent logic and LLM integration
├── file_manager.py      # File system utilities and operations
├── config.py            # Configuration and environment setup
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── .gitignore          # Git ignore file
└── README.md           # This file
```

## Configuration

Edit `.env` to customize:

```env
# LLM Configuration
OPENAI_API_KEY=your_key_here
AGENT_MODEL=gpt-4
MAX_TOKENS=2000
TEMPERATURE=0.7

# Debug mode (optional)
DEBUG=False
```

## Features

### Current Capabilities
- ✅ List directory contents
- ✅ Get file/directory information
- ✅ Search files by pattern
- ✅ Find large files
- ✅ Find recently modified files
- ✅ Natural language conversation
- ✅ Conversation history tracking

### Planned Features
- 🔄 File monitoring and alerts
- 🔄 Batch file operations
- 🔄 File organization suggestions
- 🔄 Duplicate file detection
- 🔄 Advanced filtering and sorting
- 🔄 Web interface
- 🔄 Multi-user support

## Commands

During conversation:
- `quit` - Exit the agent
- `reset` - Clear conversation history

## Troubleshooting

### "Cannot connect to Ollama"
1. Make sure Ollama is installed: [https://ollama.ai](https://ollama.ai)
2. Start Ollama and run a model:
   ```bash
   ollama run llama2
   ```
3. Verify it's running at `http://localhost:11434`

### "Model not found"
Download a model first:
```bash
ollama run llama2
```

### "Permission denied" on file access
The agent may not have access to certain directories. Run with appropriate permissions or specify accessible paths.

## Development

### Running in Debug Mode
```bash
set DEBUG=True
python main.py
```

### Adding New File Operations
1. Add method to `FileManager` class in `file_manager.py`
2. Add operation to `execute_file_operation()` in `agent.py`
3. The LLM will automatically understand and use it

## License

MIT License - Feel free to use and modify

## Author

Created by: Anjali19991
Project: MONDAY - Intelligent File Management Agent" 
