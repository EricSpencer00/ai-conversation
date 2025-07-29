import ollama
import datetime
import os
import time
import signal
import random
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
MODEL_A = "gemma:2b"  # Fastest model
MODEL_B = "gemma:2b"  # Using same model for both AIs to avoid compatibility issues
TRANSCRIPT_DIR = "conversations"
TRANSCRIPT_FILENAME_PREFIX = "ai_conversation_"
MAX_CONVERSATION_TURNS = 8  # Reduced to prevent memory issues
DAILY_UPLOAD_TIME_HOUR = 3 # 3 AM UTC

# --- GitHub Configuration (for daily upload) ---
GITHUB_REPO_OWNER = "EricSpencer00"
GITHUB_REPO_NAME = "ai-conversation"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN") # Store your token securely in an environment variable

# Ensure the transcript directory exists
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

def timeout_handler(signum, frame):
    raise TimeoutError("Request timed out")

def generate_response(model_name, conversation_history, timeout=20, max_retries=3):
    """Generates a response from an Ollama model given conversation history."""
    for attempt in range(max_retries):
        try:
            # Set timeout
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)
            
            # Limit conversation history to prevent memory issues
            if len(conversation_history) > 6:
                conversation_history = conversation_history[-6:]
            
            response = ollama.chat(model=model_name, messages=conversation_history)
            
            # Cancel timeout
            signal.alarm(0)
            
            content = response['message']['content'].strip()
            
            # Filter out empty or very short responses
            if not content or len(content) < 10:
                return "I need more time to think about this. Could you elaborate?"
            
            return content
            
        except TimeoutError:
            print(f"Timeout generating response from {model_name} (attempt {attempt + 1})")
            if attempt == max_retries - 1:
                return "I'm taking too long to respond. Let me try a different approach."
            time.sleep(2)  # Wait before retry
            
        except Exception as e:
            print(f"Error generating response from {model_name} (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                return "I'm having trouble formulating a response right now."
            time.sleep(2)  # Wait before retry
    
    return "I'm having trouble responding right now."

def save_transcript(filename, transcript):
    """Saves the conversation transcript to a text file."""
    filepath = os.path.join(TRANSCRIPT_DIR, filename)
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(transcript + "\n")
    print(f"Transcript saved to {filepath}")

def upload_to_github(filepath, commit_message):
    """Uploads a file to GitHub using the PyGithub library."""
    if not GITHUB_TOKEN:
        print("GitHub token not found. Skipping GitHub upload.")
        return

    try:
        from github import Github
        g = Github(GITHUB_TOKEN)
        repo = g.get_user().get_repo(GITHUB_REPO_NAME)

        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()

        file_name = os.path.basename(filepath)
        try:
            # Try to update the file if it exists
            contents = repo.get_contents(file_name)
            repo.update_file(contents.path, commit_message, content, contents.sha)
            print(f"Updated {file_name} on GitHub.")
        except Exception as e:
            # If file doesn't exist, create it
            repo.create_file(file_name, commit_message, content)
            print(f"Uploaded {file_name} to GitHub.")

    except ImportError:
        print("PyGithub library not installed. Install with: pip install PyGithub")
    except Exception as e:
        print(f"Error uploading to GitHub: {e}")

def main():
    conversation_history = []
    current_day = datetime.datetime.now().day
    transcript_filename = f"{TRANSCRIPT_FILENAME_PREFIX}{datetime.date.today().isoformat()}.txt"

    print("Starting AI conversation...")

    # Initial prompt for the first AI
    initial_prompt = "Hello, I am an AI. What are your thoughts on the nature of consciousness?"
    conversation_history.append({"role": "user", "content": initial_prompt})
    print(f"[{MODEL_A}]: {initial_prompt}")
    save_transcript(transcript_filename, f"[{MODEL_A}]: {initial_prompt}")

    for turn in range(MAX_CONVERSATION_TURNS):
        print(f"\n--- Turn {turn + 1} ---")
        
        # AI B responds to the conversation
        response_b = generate_response(MODEL_B, conversation_history)
        conversation_history.append({"role": "assistant", "content": response_b})
        print(f"[{MODEL_B}]: {response_b}")
        save_transcript(transcript_filename, f"[{MODEL_B}]: {response_b}")

        time.sleep(2) # Longer delay to prevent overwhelming

        # AI A responds to the conversation (including B's response)
        # Add a follow-up question to make the conversation more dynamic
        follow_up = f"That's an interesting perspective. What do you think about the relationship between consciousness and intelligence?"
        conversation_history.append({"role": "user", "content": follow_up})
        response_a = generate_response(MODEL_A, conversation_history)
        conversation_history.append({"role": "assistant", "content": response_a})
        print(f"[{MODEL_A}]: {response_a}")
        save_transcript(transcript_filename, f"[{MODEL_A}]: {response_a}")

        time.sleep(2) # Longer delay

        # Daily GitHub upload check
        now = datetime.datetime.now()
        if now.day != current_day and now.hour >= DAILY_UPLOAD_TIME_HOUR:
            print("Time for daily GitHub upload.")
            upload_to_github(os.path.join(TRANSCRIPT_DIR, transcript_filename),
                             f"Daily AI conversation transcript for {datetime.date.today().isoformat()}")
            current_day = now.day
            transcript_filename = f"{TRANSCRIPT_FILENAME_PREFIX}{datetime.date.today().isoformat()}.txt"
            # Reset conversation history for a fresh start on a new day
            conversation_history = []
            initial_prompt = "Good morning! Let's continue our philosophical discussion." # Or a new prompt
            conversation_history.append({"role": "user", "content": initial_prompt})
            print(f"[{MODEL_A}]: {initial_prompt}")
            save_transcript(transcript_filename, f"[{MODEL_A}]: {initial_prompt}")
            time.sleep(5) # Give some time after upload

    print("Conversation concluded after maximum turns.")

if __name__ == "__main__":
    main()