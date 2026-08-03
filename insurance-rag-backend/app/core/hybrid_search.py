# src/hybrid_search.py
import numpy as np
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import faiss

class HybridSearch:
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.faiss_index = None
        self.bm25_index = None
        self.chunks = []
        self.metadata = []
    
    def build_indices(self, chunks, metadata):
        """Build both FAISS (semantic) and BM25 (keyword) indices"""
        self.chunks = chunks
        self.metadata = metadata
        
        # FAISS - for semantic similarity
        print(f"📊 Building FAISS index with {len(chunks)} chunks...")
        embeddings = self.embedding_model.encode(chunks)
        dimension = embeddings.shape[1]
        self.faiss_index = faiss.IndexFlatL2(dimension)
        self.faiss_index.add(np.array(embeddings).astype('float32'))
        
        # BM25 - for exact keyword matching
        print(f"📊 Building BM25 index...")
        tokenized_chunks = [chunk.split() for chunk in chunks]
        self.bm25_index = BM25Okapi(tokenized_chunks)
        
        print(f"✅ Hybrid search ready: FAISS + BM25")
        return True
    
    def hybrid_search(self, query, k=5):
        """Combine BM25 + FAISS using Reciprocal Rank Fusion (RRF)"""
        if not self.faiss_index or not self.bm25_index:
            return [], []
        
        # BM25 scores (keyword matching)
        tokenized_query = query.split()
        bm25_scores = self.bm25_index.get_scores(tokenized_query)
        bm25_top_k = np.argsort(bm25_scores)[-k:][::-1]
        
        # FAISS scores (semantic meaning)
        query_embedding = self.embedding_model.encode([query])
        distances, faiss_top_k = self.faiss_index.search(
            np.array(query_embedding).astype('float32'), k
        )
        
        # Reciprocal Rank Fusion - combines both result sets
        combined_scores = {}
        
        for rank, idx in enumerate(bm25_top_k):
            combined_scores[idx] = combined_scores.get(idx, 0) + 1.0 / (rank + 1)
        
        for rank, idx in enumerate(faiss_top_k[0]):
            combined_scores[idx] = combined_scores.get(idx, 0) + 1.0 / (rank + 1)
        
        # Sort by combined score
        sorted_indices = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:k]
        
        results = []
        confidences = []
        for idx, score in sorted_indices:
            if idx < len(self.metadata):
                results.append(self.metadata[idx])
                confidences.append(min(score, 1.0))
        
        return results, confidences
