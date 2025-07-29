import ollama
import datetime
import os
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
MODEL_A = "llama2"
MODEL_B = "mistral"
TRANSCRIPT_DIR = "conversations"
TRANSCRIPT_FILENAME_PREFIX = "ai_conversation_"
MAX_CONVERSATION_TURNS = 50
DAILY_UPLOAD_TIME_HOUR = 3 # 3 AM UTC

# --- GitHub Configuration (for daily upload) ---
GITHUB_REPO_OWNER = "EricSpencer00"
GITHUB_REPO_NAME = "ai-conversation"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN") # Store your token securely in an environment variable

# Ensure the transcript directory exists
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

def generate_response(model_name, conversation_history):
    """Generates a response from an Ollama model given conversation history."""
    try:
        response = ollama.chat(model=model_name, messages=conversation_history)
        return response['message']['content']
    except Exception as e:
        print(f"Error generating response from {model_name}: {e}")
        return "Sorry, I'm having trouble responding right now."

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
    conversation_history_a = []
    conversation_history_b = []
    current_day = datetime.datetime.now().day
    transcript_filename = f"{TRANSCRIPT_FILENAME_PREFIX}{datetime.date.today().isoformat()}.txt"

    print("Starting AI conversation...")

    # Initial prompt for the first AI
    initial_prompt = "Hello, I am an AI. What are your thoughts on the nature of consciousness?"
    conversation_history_a.append({"role": "user", "content": initial_prompt})
    print(f"[{MODEL_A}]: {initial_prompt}")
    save_transcript(transcript_filename, f"[{MODEL_A}]: {initial_prompt}")

    for turn in range(MAX_CONVERSATION_TURNS):
        # AI B responds to AI A
        response_b = generate_response(MODEL_B, conversation_history_a)
        conversation_history_a.append({"role": "assistant", "content": response_b})
        conversation_history_b.append({"role": "user", "content": response_b})
        print(f"[{MODEL_B}]: {response_b}")
        save_transcript(transcript_filename, f"[{MODEL_B}]: {response_b}")

        time.sleep(1) # Small delay to avoid overwhelming the system

        # AI A responds to AI B
        response_a = generate_response(MODEL_A, conversation_history_b)
        conversation_history_a.append({"role": "user", "content": response_a}) # This continues A's perspective
        conversation_history_b.append({"role": "assistant", "content": response_a})
        print(f"[{MODEL_A}]: {response_a}")
        save_transcript(transcript_filename, f"[{MODEL_A}]: {response_a}")

        time.sleep(1) # Small delay

        # Daily GitHub upload check
        now = datetime.datetime.now()
        if now.day != current_day and now.hour >= DAILY_UPLOAD_TIME_HOUR:
            print("Time for daily GitHub upload.")
            upload_to_github(os.path.join(TRANSCRIPT_DIR, transcript_filename),
                             f"Daily AI conversation transcript for {datetime.date.today().isoformat()}")
            current_day = now.day
            transcript_filename = f"{TRANSCRIPT_FILENAME_PREFIX}{datetime.date.today().isoformat()}.txt"
            # Reset conversation history for a fresh start on a new day
            conversation_history_a = []
            conversation_history_b = []
            initial_prompt = "Good morning! Let's continue our philosophical discussion." # Or a new prompt
            conversation_history_a.append({"role": "user", "content": initial_prompt})
            print(f"[{MODEL_A}]: {initial_prompt}")
            save_transcript(transcript_filename, f"[{MODEL_A}]: {initial_prompt}")
            time.sleep(5) # Give some time after upload

    print("Conversation concluded after maximum turns.")

if __name__ == "__main__":
    main()