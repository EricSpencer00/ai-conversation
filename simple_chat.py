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
MAX_CONVERSATION_TURNS = 5  # Very conservative
DAILY_UPLOAD_TIME_HOUR = 3 # 3 AM UTC

# --- GitHub Configuration (for daily upload) ---
GITHUB_REPO_OWNER = "EricSpencer00"
GITHUB_REPO_NAME = "ai-conversation"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

# Ensure the transcript directory exists
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

def generate_response(prompt, max_retries=2):
    """Generates a response from Ollama with retry logic."""
    for attempt in range(max_retries):
        try:
            print(f"Generating response (attempt {attempt + 1})...")
            response = ollama.chat(model=MODEL, messages=[{"role": "user", "content": prompt}])
            content = response['message']['content'].strip()
            
            if content and len(content) > 10:
                return content
            else:
                return "I need more time to think about this."
                
        except Exception as e:
            print(f"Error (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(3)  # Wait before retry
            else:
                return "I'm having trouble responding right now."
    
    return "I'm having trouble responding right now."

def save_transcript(filename, transcript):
    """Saves the conversation transcript to a text file."""
    filepath = os.path.join(TRANSCRIPT_DIR, filename)
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(transcript + "\n")
    print(f"Transcript saved to {filepath}")

def main():
    current_day = datetime.datetime.now().day
    transcript_filename = f"{TRANSCRIPT_FILENAME_PREFIX}{datetime.date.today().isoformat()}.txt"

    print("Starting simple AI conversation...")

    # Initial prompt
    initial_prompt = "Hello, I am an AI. What are your thoughts on the nature of consciousness?"
    print(f"[AI]: {initial_prompt}")
    save_transcript(transcript_filename, f"[AI]: {initial_prompt}")

    # Generate initial response
    response = generate_response(initial_prompt)
    print(f"[AI]: {response}")
    save_transcript(transcript_filename, f"[AI]: {response}")

    # Continue conversation with follow-up questions
    follow_up_questions = [
        "What do you think about the relationship between consciousness and intelligence?",
        "How does consciousness differ from other forms of awareness?",
        "What are the philosophical implications of artificial consciousness?",
        "How might we measure or test for consciousness?",
        "What role does consciousness play in decision-making?"
    ]

    for i, question in enumerate(follow_up_questions[:MAX_CONVERSATION_TURNS]):
        print(f"\n--- Turn {i + 1} ---")
        
        response = generate_response(question)
        print(f"[AI]: {response}")
        save_transcript(transcript_filename, f"[AI]: {response}")
        
        time.sleep(3)  # Longer delay between responses

    print("Conversation concluded.")

if __name__ == "__main__":
    main() 