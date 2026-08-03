# src/hybrid_retriever.py
"""
Hybrid Retriever with Query Rewriting and HyDE support
"""

from typing import List, Dict, Any, Tuple
from .query_rewriter import QueryRewriter

class HybridRetriever:
    def __init__(self, vector_search_instance, use_hyde: bool = True, use_rewrite: bool = True):
        """
        Args:
            vector_search_instance: Your VectorSearch instance
            use_hyde: Enable HyDE (hypothetical document embeddings)
            use_rewrite: Enable query rewriting
        """
        self.vector_search = vector_search_instance
        self.use_hyde = use_hyde
        self.use_rewrite = use_rewrite
        self.query_rewriter = QueryRewriter()
    
    def search(self, query: str, k: int = 5) -> Tuple[List[Dict], List[float]]:
        """
        Search with query rewriting and HyDE
        
        Returns:
            Tuple of (results, scores)
        """
        # Process query to get multiple search variations
        search_queries = self.query_rewriter.process_query(
            query, 
            use_hyde=self.use_hyde, 
            use_rewrite=self.use_rewrite
        )
        
        print(f"🔍 Original query: {query[:50]}...")
        print(f"📝 Generated {len(search_queries)} search variations")
        
        # Search with each variation and collect results
        all_results = {}
        all_scores = {}
        
        for q in search_queries:
            results, scores = self.vector_search.hybrid_search(q, k=k)
            
            # Merge results (keep highest score for each unique chunk)
            for i, result in enumerate(results):
                chunk_id = result.get('text', '')[:100]  # Simple dedup by text preview
                if chunk_id not in all_scores or scores[i] > all_scores.get(chunk_id, 0):
                    all_scores[chunk_id] = scores[i]
                    all_results[chunk_id] = result
        
        # Convert back to list and sort by score
        merged_results = []
        merged_scores = []
        for chunk_id in sorted(all_scores.keys(), key=lambda x: all_scores[x], reverse=True):
            merged_results.append(all_results[chunk_id])
            merged_scores.append(all_scores[chunk_id])
        
        # Return top k
        return merged_results[:k], merged_scores[:k]
    
    def search_with_original_only(self, query: str, k: int = 5) -> Tuple[List[Dict], List[float]]:
        """Baseline search without HyDE/rewriting for comparison"""
        return self.vector_search.hybrid_search(query, k=k)
