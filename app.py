"""Flask web server for JARVIS UI"""
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from agent import FileManagementAgent
import config
import threading
import json
from logger_util import log_step, log_success, log_error

app = Flask(__name__)
CORS(app)

# Global agent instance
agent = None
agent_lock = threading.Lock()

def get_agent():
    """Get or initialize the agent"""
    global agent
    if agent is None:
        try:
            agent = FileManagementAgent()
        except Exception as e:
            raise Exception(f"Failed to initialize agent: {str(e)}")
    return agent

@app.route("/")
def index():
    """Serve the main UI"""
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    """Handle chat messages"""
    try:
        data = request.json
        user_message = data.get("message", "").strip()
        
        if not user_message:
            log_error("Empty message received")
            return jsonify({"error": "Empty message"}), 400
        
        log_step("Chat request received", f"Message: '{user_message[:50]}'...")
        
        # Get agent response
        with agent_lock:
            agent_instance = get_agent()
            response = agent_instance.process_query(user_message)
        
        log_success("Chat response generated")
        
        return jsonify({
            "user": user_message,
            "response": response,
            "success": True
        })
    
    except Exception as e:
        error_msg = f"Chat error: {str(e)}"
        log_error(error_msg)
        return jsonify({
            "error": error_msg,
            "success": False
        }), 500

@app.route("/api/reset", methods=["POST"])
def reset():
    """Reset conversation history"""
    try:
        with agent_lock:
            agent_instance = get_agent()
            agent_instance.reset_conversation()
        
        return jsonify({"success": True, "message": "Conversation reset"})
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route("/api/health", methods=["GET"])
def health():
    """Check if agent is ready"""
    try:
        with agent_lock:
            agent_instance = get_agent()
        
        return jsonify({
            "status": "healthy",
            "model": config.AGENT_MODEL,
            "api_url": config.OLLAMA_API_URL
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 503

if __name__ == "__main__":
    print("=" * 60)
    print("JARVIS - File Management Agent (Web UI)")
    print("=" * 60)
    log_step("Initializing", f"Model: {config.AGENT_MODEL}")
    log_step("Ollama", f"URL: {config.OLLAMA_API_URL}")
    print("=" * 60)
    log_step("Starting", "Server at http://localhost:5000")
    print("=" * 60)
    
    app.run(debug=False, host="0.0.0.0", port=5000)
