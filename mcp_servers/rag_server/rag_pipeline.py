from typing import List, Tuple, Optional
import logging
from langchain.schema import Document
from huggingface_hub import InferenceClient

logger = logging.getLogger(__name__)

class RAGPipeline:
    """RAG pipeline for question answering using Hugging Face models"""
    
    def __init__(self, YOUR_HF_TOKEN_HERE: str, model: str = "microsoft/DialoGPT-medium"):
        self.YOUR_HF_TOKEN_HERE = YOUR_HF_TOKEN_HERE
        self.model = model
        self.client = InferenceClient(model=model, token=YOUR_HF_TOKEN_HERE)
        # Create multiple clients for different types of questions
        self.general_client = InferenceClient(model="gpt2", token=YOUR_HF_TOKEN_HERE)
        self.text_client = InferenceClient(model="google/flan-t5-base", token=YOUR_HF_TOKEN_HERE)
        
        # Question type detection keywords
        self.document_keywords = {
            'machine learning', 'ml', 'ai', 'artificial intelligence', 'neural network',
            'algorithm', 'model', 'training', 'data', 'learning', 'rag', 'retrieval',
            'document', 'text', 'embedding', 'vector', 'classification', 'regression'
        }
        
        self.generic_keywords = {
            'what is', 'tell me', 'explain', 'how', 'why', 'when', 'where', 'who',
            'define', 'describe', 'list', 'example', 'help', 'can you'
        }
        
    def generate_answer(self, question: str, relevant_docs: List[Tuple[Document, float]], 
                       max_tokens: int = 512) -> str:
        """Generate answer using RAG approach or general knowledge with enhanced detection"""
        try:
            # Enhanced question analysis
            question_type = self._analyze_question_type(question, relevant_docs)
            
            if question_type == "document_based":
                # Document-based answer
                context_parts = []
                for doc, score in relevant_docs:
                    if score > 0.3:  # Only use highly relevant documents
                        context_parts.append(f"Document: {doc.page_content[:500]}")
                
                context = "\n\n".join(context_parts)
                prompt = self._create_rag_prompt(question, context)
                logger.info(f"Using document-based approach for: {question[:50]}...")
                
            elif question_type == "hybrid":
                # Hybrid approach - use documents + general knowledge
                context_parts = []
                for doc, score in relevant_docs:
                    if score > 0.2:  # Lower threshold for hybrid
                        context_parts.append(f"Reference: {doc.page_content[:300]}")
                
                context = "\n\n".join(context_parts)
                prompt = self._create_hybrid_prompt(question, context)
                logger.info(f"Using hybrid approach for: {question[:50]}...")
                
            else:
                # Pure general knowledge
                prompt = self._create_general_prompt(question)
                logger.info(f"Using general knowledge for: {question[:50]}...")
            
            # Enhanced generation with multiple strategies
            answer = self._try_enhanced_generation(prompt, question_type, max_tokens, question)
            
            return self._post_process_answer(answer, question)
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return f"I'm sorry, I encountered an error while generating the answer: {str(e)}"
    
    def _create_rag_prompt(self, question: str, context: str) -> str:
        """Create a well-formatted prompt for document-based questions"""
        return f"""Based on the following context, please answer the question accurately and concisely.

Context:
{context}

Question: {question}

Answer:"""

    def _create_general_prompt(self, question: str) -> str:
        """Create a prompt for general knowledge questions"""
        return f"""Please answer the following question based on your general knowledge. Provide a clear and helpful response.

Question: {question}

Answer:"""
    
    def _create_hybrid_prompt(self, question: str, context: str) -> str:
        """Create a prompt that combines document context with general knowledge"""
        return f"""Answer the following question using both the provided context and your general knowledge. 
If the context is relevant, use it as supporting information. If not sufficient, expand with general knowledge.

Context:
{context}

Question: {question}

Answer:"""
    
    def _analyze_question_type(self, question: str, relevant_docs: List[Tuple[Document, float]]) -> str:
        """Analyze question to determine the best answering approach"""
        question_lower = question.lower()
        
        # Check document relevance
        has_high_relevance = relevant_docs and any(score > 0.4 for _, score in relevant_docs)
        has_medium_relevance = relevant_docs and any(score > 0.2 for _, score in relevant_docs)
        
        # Check for document-specific keywords
        has_doc_keywords = any(keyword in question_lower for keyword in self.document_keywords)
        
        # Check for generic question patterns
        has_generic_patterns = any(pattern in question_lower for pattern in self.generic_keywords)
        
        # Decision logic
        if has_high_relevance and has_doc_keywords:
            return "document_based"
        elif has_medium_relevance or (has_doc_keywords and has_generic_patterns):
            return "hybrid"
        else:
            return "general"
    
    def _try_enhanced_generation(self, prompt: str, question_type: str, max_tokens: int, question: str = "") -> str:
        """Enhanced generation with multiple strategies based on question type"""
        
        # Strategy 1: Try the most appropriate model first
        try:
            if question_type == "general":
                # Use text-generation model for general questions
                response = self.text_client.text_generation(
                    prompt, 
                    max_new_tokens=min(max_tokens, 256),
                    temperature=0.7,
                    do_sample=True,
                    return_full_text=False
                )
            else:
                # Use main model for document-based questions
                response = self.client.text_generation(
                    prompt, 
                    max_new_tokens=max_tokens,
                    temperature=0.6,
                    do_sample=True,
                    return_full_text=False
                )
            
            if response and len(response.strip()) > 10:
                return response.strip()
        except Exception as e:
            logger.warning(f"Primary generation failed: {e}")
        
        # Strategy 2: Fallback to original methods
        return self._try_generation_methods(prompt, max_tokens, question)
    
    def _post_process_answer(self, answer: str, question: str) -> str:
        """Post-process the generated answer for better quality"""
        if not answer or len(answer.strip()) < 5:
            return "I apologize, but I couldn't generate a suitable answer to your question."
        
        # Clean up the answer
        answer = answer.strip()
        
        # Remove incomplete sentences at the end
        sentences = answer.split('.')
        if len(sentences) > 1 and len(sentences[-1].strip()) < 10:
            answer = '.'.join(sentences[:-1]) + '.'
        
        # Ensure the answer is not too repetitive
        words = answer.split()
        if len(set(words)) < len(words) * 0.3:  # Too many repeated words
            # Fallback to a simpler answer
            return f"Regarding your question about '{question}', I can provide some information but my response generation is limited. Please try rephrasing your question for better results."
        
        return answer
    
    def _try_generation_methods(self, prompt: str, max_tokens: int, question: str = "") -> str:
        """Try different generation methods with fallbacks"""
        
        # Method 1: Try text generation
        try:
            response = self.client.text_generation(
                prompt, 
                max_new_tokens=max_tokens,
                temperature=0.7,
                do_sample=True,
                return_full_text=False
            )
            if response and len(response.strip()) > 10:
                return response.strip()
        except Exception as e:
            logger.warning(f"Text generation failed: {e}")
        
        # Method 2: Try with chat completion format
        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.client.chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7
            )
            if response and response.choices:
                return response.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"Chat completion failed: {e}")
        
        # Method 3: Try with different model
        try:
            fallback_client = InferenceClient(model="gpt2", token=self.YOUR_HF_TOKEN_HERE)
            response = fallback_client.text_generation(
                prompt, 
                max_new_tokens=min(max_tokens, 200),
                temperature=0.8
            )
            if response:
                return response.strip()
        except Exception as e:
            logger.warning(f"Fallback generation failed: {e}")
        
        # Method 4: Smart extraction and fallback
        return self._provide_smart_fallback(question if 'Question:' in prompt else prompt, [])
    
    def _extract_answer_from_context(self, prompt: str) -> str:
        """Extract a simple answer from the context when generation fails"""
        try:
            # Extract the context and question
            parts = prompt.split("Question:")
            if len(parts) >= 2:
                context_part = parts[0]
                question = parts[1].split("Answer:")[0].strip()
                
                # Simple keyword-based extraction
                context_sentences = context_part.split(".")
                relevant_sentences = []
                
                question_words = set(question.lower().split())
                
                for sentence in context_sentences:
                    sentence_words = set(sentence.lower().split())
                    if len(question_words.intersection(sentence_words)) >= 2:
                        relevant_sentences.append(sentence.strip())
                
                if relevant_sentences:
                    return ". ".join(relevant_sentences[:2]) + "."
                else:
                    return "Based on the provided context, I can see relevant information but cannot generate a specific answer due to model limitations."
            
        except Exception as e:
            logger.error(f"Error in extraction fallback: {e}")
        
        return "I'm sorry, I couldn't generate an answer based on the provided context."
    
    def _provide_smart_fallback(self, question: str, relevant_docs: List[Tuple[Document, float]]) -> str:
        """Provide a smart fallback answer when generation fails"""
        question_lower = question.lower()
        
        # Try to provide context-based answers for common question types
        if any(word in question_lower for word in ['what is', 'define', 'explain']):
            if relevant_docs:
                # Extract key information from documents
                key_sentences = []
                for doc, score in relevant_docs[:2]:  # Top 2 docs
                    sentences = doc.page_content.split('.')
                    for sentence in sentences[:3]:  # First 3 sentences
                        if len(sentence.strip()) > 20:
                            key_sentences.append(sentence.strip())
                
                if key_sentences:
                    return f"Based on the available information: {'. '.join(key_sentences[:2])}."
        
        elif any(word in question_lower for word in ['how', 'process', 'steps']):
            if relevant_docs:
                # Look for process-related content
                for doc, score in relevant_docs:
                    content = doc.page_content.lower()
                    if any(keyword in content for keyword in ['step', 'process', 'method', 'algorithm']):
                        # Extract process information
                        sentences = doc.page_content.split('.')
                        process_sentences = [s for s in sentences if any(k in s.lower() for k in ['step', 'first', 'then', 'next', 'finally'])]
                        if process_sentences:
                            return f"Here's the process: {'. '.join(process_sentences[:3])}."
        
        elif any(word in question_lower for word in ['list', 'types', 'kinds', 'examples']):
            if relevant_docs:
                # Look for lists or examples
                for doc, score in relevant_docs:
                    content = doc.page_content
                    lines = content.split('\n')
                    list_items = [line.strip() for line in lines if line.strip().startswith(('-', '•', '1.', '2.', '3.'))]
                    if list_items:
                        return f"Here are some key points: {', '.join(list_items[:5])}."
        
        # Generic fallback responses based on question type
        if 'machine learning' in question_lower or 'ml' in question_lower:
            return "Machine learning is a field of AI that enables computers to learn from data without explicit programming. It includes supervised, unsupervised, and reinforcement learning approaches."
        
        elif 'ai' in question_lower or 'artificial intelligence' in question_lower:
            return "Artificial Intelligence (AI) refers to computer systems that can perform tasks typically requiring human intelligence, such as reasoning, learning, and perception."
        
        elif any(word in question_lower for word in ['help', 'assistance', 'support']):
            return "I'm here to help! You can ask me questions about machine learning, AI, or any topics in the uploaded documents. Try asking specific questions about concepts you'd like to understand better."
        
        else:
            return f"I understand you're asking about '{question}'. While I don't have specific information readily available, I'd be happy to help if you could provide more context or try rephrasing your question."
    
    def test_model_connection(self) -> bool:
        """Test if the model connection is working"""
        try:
            test_prompt = "Hello, this is a test."
            response = self.client.text_generation(test_prompt, max_new_tokens=10)
            return True
        except Exception as e:
            logger.error(f"Model connection test failed: {e}")
            return False
