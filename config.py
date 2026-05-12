"""Configuration module for JARVIS File Management Agent"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# LLM Configuration (Open Source - Ollama)
LLM_PROVIDER = "ollama"
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
AGENT_MODEL = os.getenv("AGENT_MODEL", "llama2")

# Agent Behavior Configuration
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

# File Operations Configuration
MAX_FILES_TO_DISPLAY = 50
MAX_SEARCH_DEPTH = 10

# System Configuration
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
