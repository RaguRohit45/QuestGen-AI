import json
import os
import re
from openai import OpenAI

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

class RAGSystem:
    """Retrieval Augmented Generation system for processing documents"""
    
    def __init__(self, client, model):
        """
        Initialize RAG system
        
        Args:
            client: OpenAI client instance
            model: Model name to use
        """
        self.documents = {
            'previous_papers': [],
            'copo': [],
            'syllabus': []
        }
        
        self.vector_store = []
        
        self.client = client
        self.model = model
        print(f"RAG System initialized with OpenRouter model: {model}")
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                self.embedder = None
        else:
            self.embedder = None
    
    def add_documents(self, documents, doc_type='general'):
        """
        Add documents to the RAG system
        
        Args:
            documents: List of document dicts with 'filename', 'content', 'filepath'
            doc_type: Type of document ('previous_papers', 'copo', 'syllabus')
        """
        if doc_type not in self.documents:
            doc_type = 'general'
        
        for doc in documents:
            self.documents[doc_type].append(doc)
            
            if self.embedder and doc.get('content'):
                chunks = self._split_into_chunks(doc['content'])
                
                for chunk in chunks:
                    embedding = self.embedder.encode(chunk).tolist()
                    self.vector_store.append({
                        'text': chunk,
                        'embedding': embedding,
                        'doc_type': doc_type,
                        'filename': doc.get('filename', 'unknown'),
                        'metadata': doc
                    })
    
    def _split_into_chunks(self, text, chunk_size=500, overlap=50):
        """
        Split text into chunks for embedding
        
        Args:
            text: Text to split
            chunk_size: Size of each chunk
            overlap: Overlap between chunks
            
        Returns:
            list: List of text chunks
        """
        if not text:
            return []
        
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        return chunks
    
    def get_copo_mapping(self):
        """Extract CO-PO mapping from uploaded documents"""
        copo_mapping = {}
        for doc in self.documents.get('copo', []):
            content = doc.get('content', '')
            matches = re.finditer(r'(CO\d+):\s*\[([^\]]+)\]', content)
            for match in matches:
                co = match.group(1)
                pos = [p.strip() for p in match.group(2).split(',')]
                copo_mapping[co] = pos
        return copo_mapping
    
    def get_previous_questions(self):
        """Extract all questions from previous papers"""
        questions = []
        for doc in self.documents.get('previous_papers', []):
            content = doc.get('content', '')
            question_matches = re.finditer(r'(?i)(?:Q\s*\d+\.?|Question\s*\d*:?)([^Q]+?)(?=(?:Q\s*\d+\.?|Question\s*\d*:?|$))', content, re.DOTALL)
            for match in question_matches:
                question_text = match.group(1).strip()
                if question_text and len(question_text) > 10: 
                    questions.append(question_text)
        return questions
    
    def retrieve_context(self, query, top_k=5):
        """
        Retrieve relevant context for a query with CO-PO mapping
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            dict: Dictionary containing context, CO-PO mapping, and previous questions
        """
        copo_mapping = self.get_copo_mapping()
        
        previous_questions = self.get_previous_questions()
        
        if not self.vector_store:
            all_texts = [doc['content'] for doc_type in self.documents.values() for doc in doc_type]
            context = "\n\n".join(all_texts[:top_k]) if all_texts else "No documents available"
        else:
            query_embedding = self.embedder.encode(query).tolist()
            
            similarities = []
            for i, item in enumerate(self.vector_store):
                sim = self._cosine_similarity(query_embedding, item['embedding'])
                similarities.append((i, sim, item))
            
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            results = []
            for i, (idx, sim, item) in enumerate(similarities[:top_k]):
                results.append(f"Document {i+1} (Similarity: {sim:.2f}):\n{item['text']}")
            
            context = "\n\n".join(results)
        
        return {
            'context': context,
            'copo_mapping': copo_mapping,
            'previous_questions': previous_questions
        }
    
    def _cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors"""
        import numpy as np
        
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0
        
        return dot_product / (norm1 * norm2)
    
    def get_all_documents(self):
        """
        Get all stored documents
        
        Returns:
            dict: All documents organized by type
        """
        return self.documents
    
    def generate_with_context(self, prompt, context=None):
        """
        Generate response using OpenRouter with context
        
        Args:
            prompt: User prompt
            context: Additional context (if None, will retrieve)
            
        Returns:
            str: Generated response
        """
        if context is None:
            context = self.retrieve_context(prompt)
        
        full_prompt = f"""
        Context from documents:
        {context}
        
        User query:
        {prompt}
        
        Please provide a comprehensive answer based on the context provided.
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": full_prompt
                }
            ]
        )
        return response.choices[0].message.content

