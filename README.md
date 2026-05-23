"# MONDAY - Monday File Management Agent

A conversational AI agent inspired by Iron Man's Monday that intelligently handles all file management queries. Ask natural language questions about your files and get instant, detailed responses.

## Overview

Monday is an intelligent assistant designed to:
- **List and explore** files and directories naturally
- **Find large files** taking up disk space
- **Search for files** by name or pattern
- **Get file metadata** (size, modification date, creation date, etc.)
- **Discover recent files** modified within a time period
- **Understand context** through conversational AI

## Tech Stack

- **Language:** Python 3.8+
- **LLM Provider:** Ollama (Open Source - 100% Free)
- **Default Model:** TinyLlama (1.1B - Lightweight, ~1.1GB)
- **Supported Models:** Gemma 2B, Orca Mini, Llama 2, Mistral, and more
- **File System:** Python's `pathlib`
- **API Communication:** `requests`
- **Environment Management:** `python-dotenv`

## Installation

### 1. Install Ollama (One-time setup)

Download and install Ollama from **[https://ollama.ai](https://ollama.ai)**

After installation, download TinyLlama (lightweight, ~1.1GB):
```bash
ollama run tinyllama
```

Or try other lightweight models:
```bash
ollama run gemma:2b      # Ultra-lightweight, ~2GB
ollama run orca-mini     # Small, high-quality
ollama run neural-chat   # Good for conversations
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

This starts an interactive conversation with Monday. Make sure Ollama is running with TinyLlama:
```bash
ollama run tinyllama
```

### Example Queries

```
You: Show me all files in C:\Users\Downloads
Monday: [Lists all files with details]

You: Find large files in my Documents folder
Monday: [Shows files over 10MB, sorted by size]

You: What files were modified in the last 24 hours?
Monday: [Lists recent files with modification times]

You: Search for *.pdf files
Monday: [Finds all PDF files with their locations]

You: Get detailed info about C:\path\to\file.txt
Monday: [Shows file metadata and analysis]
```

## Project Structure

```
MONDAY/
├── main.py              # Entry point - interactive conversation loop
├── agent.py             # Monday agent logic and LLM integration
├── file_manager.py      # File system utilities and operations
├── config.py            # Configuration and environment setup
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── .gitignore          # Git ignore file
└── README.md           # This file
```

## Configuration

Edit `.env` to customize (optional):

```env
# LLM Configuration
OLLAMA_API_URL=http://localhost:11434
AGENT_MODEL=tinyllama
MAX_TOKENS=2000
TEMPERATURE=0.7

# Debug mode (optional)
DEBUG=False
```

**Available lightweight models:**
- `tinyllama` - 1.1B (default, recommended) ~1.1GB
- `gemma:2b` - 2B (ultra-lightweight) ~2GB
- `orca-mini` - 3B (good quality) ~3GB
- `neural-chat` - 7B (better conversations)

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
2. Start Ollama and run TinyLlama:
   ```bash
   ollama run tinyllama
   ```
3. Verify it's running at `http://localhost:11434`

### "Model requires more system memory"
Download a smaller model:
```bash
ollama run tinyllama      # 1.1GB (recommended for limited RAM)
ollama run gemma:2b       # 2GB (ultra-lightweight)
```

### "Model not found"
Download the model first:
```bash
ollama run tinyllama
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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author & Certificate

**Created by:** Anjali19991  
**Project:** MONDAY - Intelligent File Management Agent  
**Version:** 1.0.0  
**License:** MIT  
**GitHub:** [@Anjali19991](https://github.com/Anjali19991/MONDAY)  

### Copyright Notice
Copyright © 2026 Anjali19991. All rights reserved." 
