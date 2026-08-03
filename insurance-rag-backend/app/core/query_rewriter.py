"""
Query Rewriting + HyDE for improved RAG retrieval
"""

import os
from openai import OpenAI
from typing import List, Tuple

class QueryRewriter:
    def __init__(self, api_key: str = None, base_url: str = "https://api.deepseek.com"):
        """Initialize with DeepSeek API"""
        if api_key is None:
            api_key = os.getenv('DEEPSEEK_API_KEY')
        self.client = OpenAI(api_key=api_key, base_url=base_url)
    
    def rewrite_query(self, original_query: str) -> str:
        """
        Convert casual question into a better search query
        """
        prompt = f"""You are a search query optimizer for an insurance RAG system.

Convert this user question into a BETTER search query that will find relevant policy documents.

Rules:
- Remove conversational words (can, I, my, the, a, an)
- Keep only key insurance terms
- Add relevant policy types (renters, auto, health)
- Make it keyword-focused for BM25 search
- Keep it under 20 words

User Question: "{original_query}"

Return ONLY the rewritten query as a single line, nothing else.
Better query:"""
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=100
            )
            rewritten = response.choices[0].message.content.strip()
            return rewritten
        except Exception as e:
            print(f"Query rewrite failed: {e}")
            return original_query
    
    def generate_hypothetical_document(self, query: str) -> str:
        """
        Generate a hypothetical ideal answer (HyDE) - IMPROVED for better retrieval
        """
        prompt = f"""You are an expert insurance claims adjuster. Generate a detailed, factual policy document excerpt that would be the PERFECT answer to this user's insurance question.

User Question: "{query}"

Write a professional, detailed policy excerpt (4-6 sentences) that:
- Directly answers the question with specific policy language
- Uses realistic insurance terminology
- Includes specific numbers (deductibles, limits, percentages)
- Mentions relevant policy type (renters/auto/health)
- Is structured like an actual policy document
- Focuses on coverage details, exclusions, and claim procedures

Return ONLY the hypothetical document text, nothing else.
Hypothetical policy excerpt:"""
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=350
            )
            hypothetical = response.choices[0].message.content.strip()
            return hypothetical
        except Exception as e:
            print(f"HyDE generation failed: {e}")
            return query
    
    def expand_query(self, query: str, num_queries: int = 3) -> List[str]:
        """
        Generate multiple query variations for better coverage
        """
        prompt = f"""Generate {num_queries} different search queries for this user question.

User Question: "{query}"

Each query should:
- Be keyword-focused
- Target different aspects of the question
- Be under 15 words

Return ONLY {num_queries} lines, one query per line.
Queries:"""
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=200
            )
            queries = response.choices[0].message.content.strip().split('\n')
            queries = [q.strip() for q in queries if q.strip()]
            return queries[:num_queries]
        except Exception as e:
            print(f"Query expansion failed: {e}")
            return [query]
    
    def process_query(self, query: str, use_hyde: bool = True, use_rewrite: bool = True) -> List[str]:
        """
        Full query processing pipeline
        
        Args:
            query: Original user question
            use_hyde: Whether to generate hypothetical document
            use_rewrite: Whether to rewrite query
            
        Returns:
            List of search queries to use
        """
        search_queries = []
        
        # 1. Original query
        search_queries.append(query)
        
        # 2. Rewritten query (if enabled)
        if use_rewrite:
            rewritten = self.rewrite_query(query)
            if rewritten != query:
                search_queries.append(rewritten)
        
        # 3. HyDE document (if enabled)
        if use_hyde:
            hypothetical = self.generate_hypothetical_document(query)
            if hypothetical != query:
                search_queries.append(hypothetical)
        
        return search_queries