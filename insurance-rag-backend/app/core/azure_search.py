import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchableField, SearchFieldDataType
)

class AzureSearchRAG:
    def __init__(self):
        self.endpoint = os.getenv('AZURE_SEARCH_ENDPOINT')
        self.key = os.getenv('AZURE_SEARCH_KEY')
        self.index_name = "insurance-policies"
        
        # Check if credentials exist
        if not self.endpoint or not self.key:
            print("? " + "❌ Azure AI Search credentials not configured. Falling back to FAISS.")
            from app.core.hybrid_search import HybridSearch
            self.search = HybridSearch()
            self.use_faiss_fallback = True
            return
        
        self.use_faiss_fallback = False
        self.credential = AzureKeyCredential(self.key)
        self.search_client = SearchClient(self.endpoint, self.index_name, self.credential)
        self.index_client = SearchIndexClient(self.endpoint, self.credential)
        
        # Create index if it doesn't exist
        self._create_index_if_not_exists()
        
        print("✅ Azure AI Search active!")
    
    def _create_index_if_not_exists(self):
        """Create search index"""
        try:
            existing = self.index_client.get_index(self.index_name)
            print(f"📚 Using existing index: {self.index_name}")
            return
        except Exception:
            print(f"🔧 Creating new index: {self.index_name}")
        
        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="content", type=SearchFieldDataType.String),
            SimpleField(name="filename", type=SearchFieldDataType.String),
        ]
        
        index = SearchIndex(name=self.index_name, fields=fields)
        self.index_client.create_index(index)
        print("✅ Search index created!")
    
    def build_indices(self, chunks, metadata):
        """Upload chunks to Azure AI Search"""
        if self.use_faiss_fallback:
            return self.search.build_indices(chunks, metadata)
        
        with print("? Processing..."):
            documents = []
            for i, (chunk, meta) in enumerate(zip(chunks, metadata)):
                # Remove dots from the ID (Azure AI Search doesn't allow dots)
                safe_filename = meta['filename'].replace('.', '_')
                doc = {
                    "id": f"{safe_filename}_{i}",
                    "content": chunk,
                    "filename": meta['filename'],
                }
                documents.append(doc)
            
            # Upload in batches
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i+batch_size]
                self.search_client.upload_documents(batch)
            
            print(f"✅ Uploaded {len(documents)} policy chunks")
            return True
    
    def hybrid_search(self, query, k=5):
        """Simple search (no vector, just keyword)"""
        if self.use_faiss_fallback:
            return self.search.hybrid_search(query, k)
        
        results = self.search_client.search(
            search_text=query,
            select=["filename", "content"],
            top=k
        )
        
        retrieved_chunks = []
        confidences = []
        for result in results:
            retrieved_chunks.append({
                'filename': result['filename'],
                'text': result['content']
            })
            confidences.append(result['@search.score'])
        
        return retrieved_chunks, confidences
    
    @property
    def chunks(self):
        return []
