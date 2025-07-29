import ollama

def test_ollama():
    print("Testing Ollama connection...")
    
    # Test with a simple message
    try:
        response = ollama.chat(model='llama2', messages=[{'role': 'user', 'content': 'Hello'}])
        print(f"✅ Llama2 response: {response['message']['content']}")
    except Exception as e:
        print(f"❌ Llama2 error: {e}")
    
    # Test with mistral
    try:
        response = ollama.chat(model='mistral', messages=[{'role': 'user', 'content': 'Hello'}])
        print(f"✅ Mistral response: {response['message']['content']}")
    except Exception as e:
        print(f"❌ Mistral error: {e}")
    
    # Test with conversation history
    try:
        messages = [
            {'role': 'user', 'content': 'Hello, I am an AI. What are your thoughts on the nature of consciousness?'},
        ]
        response = ollama.chat(model='llama2', messages=messages)
        print(f"✅ Llama2 with conversation: {response['message']['content']}")
        
        # Add the response to conversation
        messages.append({'role': 'assistant', 'content': response['message']['content']})
        messages.append({'role': 'user', 'content': 'That is interesting. Can you elaborate?'})
        
        response2 = ollama.chat(model='mistral', messages=messages)
        print(f"✅ Mistral with conversation: {response2['message']['content']}")
        
    except Exception as e:
        print(f"❌ Conversation error: {e}")

if __name__ == "__main__":
    test_ollama() 