import ollama
import datetime
import os
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
MODEL = "gemma:2b"  # Use single model to avoid memory issues
TRANSCRIPT_DIR = "conversations"
TRANSCRIPT_FILENAME_PREFIX = "ai_conversation_"
MAX_TURNS = 100  # Number of back-and-forth exchanges

# Ensure the transcript directory exists
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

def generate_response(prompt):
    """Generates a response from Ollama."""
    try:
        print("Generating response...")
        response = ollama.chat(model=MODEL, messages=[{"role": "user", "content": prompt}])
        content = response['message']['content'].strip()
        return content if content else "I need more time to think about this."
    except Exception as e:
        print(f"Error: {e}")
        return "I'm having trouble responding right now."

def save_transcript(filename, transcript):
    """Saves the conversation transcript to a text file."""
    filepath = os.path.join(TRANSCRIPT_DIR, filename)
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(transcript + "\n")
    print(f"Transcript saved to {filepath}")

def main():
    transcript_filename = f"{TRANSCRIPT_FILENAME_PREFIX}{datetime.date.today().isoformat()}.txt"

    print("Starting AI back-and-forth conversation...")

    # AI 1 starts the conversation
    ai1_question = "Hello! I'm AI 1. What do you think about the nature of consciousness?"
    print(f"[AI 1]: {ai1_question}")
    save_transcript(transcript_filename, f"[AI 1]: {ai1_question}")

    for turn in range(MAX_TURNS):
        print(f"\n--- Turn {turn + 1} ---")
        
        # AI 2 responds and asks a question back
        ai2_response = generate_response(ai1_question)
        print(f"[AI 2]: {ai2_response}")
        save_transcript(transcript_filename, f"[AI 2]: {ai2_response}")
        
        time.sleep(2)
        
        # AI 1 responds and asks a question back
        ai1_response = generate_response(ai2_response)
        print(f"[AI 1]: {ai1_response}")
        save_transcript(transcript_filename, f"[AI 1]: {ai1_response}")
        
        time.sleep(2)

    print("Conversation concluded.")

if __name__ == "__main__":
    main() 