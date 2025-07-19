from transformers import pipeline
import torch

def test_local_models():
    """Test local models that don't require API tokens"""
    
    print("🚀 Testing local transformers models...\n")
    
    try:
        # Test 1: Sentiment Analysis (small model)
        print("1. Testing Sentiment Analysis...")
        sentiment_pipeline = pipeline("sentiment-analysis", 
                                     model="distilbert-base-uncased-finetuned-sst-2-english")
        result = sentiment_pipeline("I love using Hugging Face transformers!")
        print(f"✅ Sentiment: {result}")
        
        # Test 2: Text Generation (small model)
        print("\n2. Testing Text Generation...")
        generator = pipeline("text-generation", 
                           model="distilgpt2",
                           max_new_tokens=50)
        prompt = "Retrieval-Augmented Generation (RAG) is"
        result = generator(prompt)
        print(f"✅ Generated text: {result[0]['generated_text']}")
        
        # Test 3: Question Answering
        print("\n3. Testing Question Answering...")
        qa_pipeline = pipeline("question-answering", 
                              model="distilbert-base-cased-distilled-squad")
        
        context = """
        Retrieval-Augmented Generation (RAG) is a natural language processing technique 
        that combines information retrieval with text generation. It works by first 
        retrieving relevant documents from a knowledge base, then using those documents 
        to generate more accurate and informed responses.
        """
        
        question = "What is RAG?"
        result = qa_pipeline(question=question, context=context)
        print(f"✅ QA Result: {result['answer']}")
        
        print("\n🎉 All local models are working!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Try installing: pip install torch transformers")
        return False

if __name__ == "__main__":
    test_local_models()
