from huggingface_hub import InferenceClient
import requests
import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import Config

HF_TOKEN = Config.get_hf_token()

def test_token():
    """Test if the HF token is valid"""
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    response = requests.get("https://huggingface.co/api/whoami", headers=headers)
    if response.status_code == 200:
        print("✅ Token is valid!")
        print(f"User: {response.json().get('name', 'Unknown')}")
        return True
    else:
        print(f"❌ Token validation failed: {response.status_code}")
        return False

def try_simple_models():
    """Try simple, commonly available models"""
    models_to_try = [
        "distilbert-base-uncased-finetuned-sst-2-english",  # Sentiment analysis
        "facebook/bart-large-mnli",  # Text classification
        "microsoft/DialoGPT-medium",  # Conversational
    ]
    
    for model in models_to_try:
        try:
            print(f"\n🔄 Trying model: {model}")
            client = InferenceClient(model=model, token=HF_TOKEN)
            
            if "sentiment" in model or "sst" in model:
                # Sentiment analysis
                result = client.text_classification("I love using Hugging Face!")
                print(f"✅ {model} works! Result: {result}")
                return True
                
            elif "mnli" in model:
                # Text classification
                result = client.text_classification("This is a test.", "This is about testing.")
                print(f"✅ {model} works! Result: {result}")
                return True
                
            else:
                # Try text generation
                result = client.text_generation("Hello, how are you?", max_new_tokens=20)
                print(f"✅ {model} works! Result: {result}")
                return True
                
        except Exception as e:
            print(f"❌ {model} failed: {str(e)[:100]}...")
    
    return False

if __name__ == "__main__":
    print("🚀 Testing Hugging Face setup...\n")
    
    # Test 1: Check token
    if not test_token():
        print("Please check your HF_TOKEN")
        exit(1)
    
    # Test 2: Try simple models
    if try_simple_models():
        print("\n🎉 At least one model is working!")
    else:
        print("\n😞 No models are working. This might be due to:")
        print("1. Network connectivity issues")
        print("2. Hugging Face API being down")
        print("3. Token permissions")
        print("4. Rate limiting")
        
    print("\n💡 Alternative: Try using transformers library locally instead:")
