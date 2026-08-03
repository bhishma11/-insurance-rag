# src/vector_search.py
import os

class VectorSearch:
    def __init__(self):
        # Check if we should use Azure AI Search (cloud) or FAISS (local)
        self.use_azure = os.getenv('AZURE_DEPLOYMENT', 'false').lower() == 'true'
        
        # HyDE settings (can be toggled from app)
        self.use_hyde = True
        self.use_rewrite = True
        
        if self.use_azure:
            # Will implement Azure AI Search later
            from app.core.azure_search import AzureSearchRAG
            self.search = AzureSearchRAG()
            print("✅ Using Azure AI Search (cloud mode)")
        else:
            from app.core.hybrid_search import HybridSearch
            self.search = HybridSearch()
            print("🔍 Using FAISS + BM25 (local mode)")
    
    def build_indices(self, chunks, metadata):
        """Build search indices from chunks"""
        return self.search.build_indices(chunks, metadata)
    
    def hybrid_search(self, query, k=5):
        """Search for relevant chunks (original - no HyDE)"""
        return self.search.hybrid_search(query, k)
    
    def hybrid_search_with_hyde(self, query, k=5, use_hyde=None, use_rewrite=None):
        """
        Hybrid search with HyDE and query rewriting
        
        Args:
            query: User's question
            k: Number of results to return
            use_hyde: Enable hypothetical document embeddings
            use_rewrite: Enable query rewriting
        """
        # Use instance settings if not specified
        if use_hyde is None:
            use_hyde = self.use_hyde
        if use_rewrite is None:
            use_rewrite = self.use_rewrite
        
        # If both are disabled, just use regular search
        if not use_hyde and not use_rewrite:
            return self.hybrid_search(query, k)
        
        # Import here to avoid circular imports
        from app.core.hybrid_retriever import HybridRetriever
        
        retriever = HybridRetriever(self, use_hyde=use_hyde, use_rewrite=use_rewrite)
        return retriever.search(query, k=k)
    
    def set_hyde_settings(self, use_hyde: bool, use_rewrite: bool):
        """Update HyDE settings from UI toggles"""
        self.use_hyde = use_hyde
        self.use_rewrite = use_rewrite
        if use_hyde or use_rewrite:
            print(f"✨ HyDE enabled: {use_hyde} | Query Rewriting: {use_rewrite}")
        else:
            print("🔍 Using standard search (HyDE disabled)")
    
    @property
    def chunks(self):
        """Get all chunks (for compatibility)"""
        if hasattr(self.search, 'chunks'):
            return self.search.chunks
        return []
    
    @property
    def metadata(self):
        """Get metadata (for compatibility)"""
        if hasattr(self.search, 'metadata'):
            return self.search.metadata
        return []
    
    def save_index(self, path="faiss_index.pkl"):
        """Save the index to disk"""
        import pickle
        if hasattr(self.search, 'faiss_index'):
            with open(path, 'wb') as f:
                pickle.dump({
                    'chunks': self.chunks,
                    'metadata': self.metadata,
                    'faiss_index': self.search.faiss_index
                }, f)
            print(f"✅ Index saved to {path}")

    def load_index(self, path="faiss_index.pkl"):
        """Load the index from disk and rebuild BM25"""
        import pickle
        try:
            with open(path, 'rb') as f:
                data = pickle.load(f)
            
            # Check if this is a full index or just chunks
            if 'chunks' in data and 'metadata' in data:
                # Rebuild both FAISS and BM25
                self.search.chunks = data['chunks']
                self.search.metadata = data['metadata']
                
                # Rebuild BM25
                from rank_bm25 import BM25Okapi
                tokenized_chunks = [chunk.split() for chunk in data['chunks']]
                self.search.bm25_index = BM25Okapi(tokenized_chunks)
                
                # Rebuild FAISS
                if 'faiss_index' in data:
                    self.search.faiss_index = data['faiss_index']
                
                print(f"✅ Full index loaded and BM25 rebuilt from {len(data['chunks'])} chunks")
            else:
                # Legacy: only FAISS index
                self.search.faiss_index = data['faiss_index']
                print("✅ FAISS index loaded (BM25 will be built when chunks are available)")
                
        except FileNotFoundError:
            print(f"⚠️ No index found at {path}")
        except Exception as e:
            print(f"⚠️ Error loading index: {e}")
