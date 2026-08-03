# build_index.py
import os
from app.core.document_processor import DocumentProcessor
from app.core.vector_search import VectorSearch

def build_index():
    print("📚 Building FAISS index...")
    
    # Initialize processor and search
    processor = DocumentProcessor()
    vector_search = VectorSearch()
    
    # Path to your policy documents
    policies_dir = "app/data/policies"
    
    # Get all PDF files
    pdf_files = []
    if os.path.exists(policies_dir):
        for file in os.listdir(policies_dir):
            if file.endswith('.pdf'):
                pdf_files.append(os.path.join(policies_dir, file))
    
    if not pdf_files:
        print("❌ No PDF files found in app/data/policies/")
        print("📁 Please add policy PDFs to app/data/policies/")
        return
    
    print(f"📄 Found {len(pdf_files)} policy files")
    
    # Extract text from each PDF
    all_chunks = []
    all_metadata = []
    
    for pdf_path in pdf_files:
        print(f"📖 Processing: {os.path.basename(pdf_path)}")
        text = processor.extract_text(pdf_path)
        
        if text:
            # Split into chunks
            chunks = text.split('\n\n')
            chunks = [chunk.strip() for chunk in chunks if len(chunk.strip()) > 50]
            
            for i, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                all_metadata.append({
                    'filename': os.path.basename(pdf_path),
                    'chunk_id': i,
                    'text': chunk[:100] + '...'
                })
            
            print(f"   ✅ Extracted {len(chunks)} chunks")
        else:
            print(f"   ⚠️ No text extracted from {os.path.basename(pdf_path)}")
    
    if all_chunks:
        print(f"📊 Building index with {len(all_chunks)} total chunks...")
        vector_search.build_indices(all_chunks, all_metadata)
        vector_search.save_index()
        print("✅ Index built and saved to faiss_index.pkl")
    else:
        print("❌ No chunks extracted. Please check your PDF files.")

if __name__ == "__main__":
    build_index()