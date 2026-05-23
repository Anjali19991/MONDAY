"""Main entry point for Monday File Management Agent"""
import sys
from agent import FileManagementAgent
import config


def print_welcome():
    """Print welcome message"""
    print("=" * 60)
    print("Monday - File Management Agent")
    print("=" * 60)
    print("I am your intelligent file management assistant.")
    print("Ask me about files, directories, and more!")
    print("\nExamples:")
    print("  - Show me all files in C:\\Users\\Downloads")
    print("  - Find large files in my Documents folder")
    print("  - What files were modified in the last 24 hours?")
    print("  - Search for *.pdf files in my Desktop")
    print("\nType 'quit' to exit, 'reset' to clear conversation history")
    print("=" * 60)


def main():
    """Main conversation loop"""
    try:
        # Initialize agent
        agent = FileManagementAgent()
        print_welcome()
        
        # Conversation loop
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == "quit":
                    print("Goodbye!")
                    break
                
                if user_input.lower() == "reset":
                    agent.reset_conversation()
                    print("Conversation history cleared.")
                    continue
                
                # Process query
                print("\nMonday: Processing...", end="", flush=True)
                response = agent.process_query(user_input)
                print("\r" + " " * 30 + "\r", end="")  # Clear the "Processing..." message
                print(f"Monday: {response}")
                
            except KeyboardInterrupt:
                print("\n\nInterrupted by user. Type 'quit' to exit.")
            except Exception as e:
                print(f"Error: {e}")
                if config.DEBUG:
                    import traceback
                    traceback.print_exc()
    
    except Exception as e:
        print(f"Fatal error: {e}")
        if config.DEBUG:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
