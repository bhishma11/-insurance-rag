"""
Document Service for handling document uploads, classification, and processing
"""

import os
import tempfile
from typing import Dict, Any, List
from fastapi import UploadFile
from app.core.document_processor import DocumentProcessor

class DocumentService:
    def __init__(self):
        self.processor = DocumentProcessor()
        self.supported_extensions = self.processor.get_supported_extensions()
    
    async def process_document(self, file: UploadFile) -> Dict[str, Any]:
        """
        Process an uploaded document:
        1. Save temporarily
        2. Extract text
        3. Classify document
        4. Extract structured data
        5. Clean up
        """
        # Get file extension
        filename = file.filename or "unknown"
        file_extension = os.path.splitext(filename)[1].lower()
        
        # Check if format is supported
        if file_extension not in self.supported_extensions:
            return {
                "status": "error",
                "message": f"Unsupported file format: {file_extension}. Supported: {', '.join(self.supported_extensions)}"
            }
        
        # Save temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            # Extract text
            text = self.processor.extract_text(tmp_path, file_extension)
            
            if not text or len(text.strip()) < 10:
                return {
                    "status": "error",
                    "message": "Could not extract text from document. File may be empty or scanned image."
                }
            
            # Classify document
            classification = self.processor.classify_document(text)
            
            # Extract structured data if it's insurance
            structured_data = {}
            if classification["type"] in ["insurance", "uncertain"]:
                structured_data = self.processor.extract_structured_data(text, classification.get("detected_type"))
            
            return {
                "status": "success",
                "filename": filename,
                "file_extension": file_extension,
                "classification": classification,
                "structured_data": structured_data,
                "text_length": len(text),
                "preview": text[:500] + "..." if len(text) > 500 else text
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error processing document: {str(e)}"
            }
        finally:
            # Clean up temp file
            try:
                os.unlink(tmp_path)
            except:
                pass
    
    def classify_document_text(self, text: str) -> Dict[str, Any]:
        """Classify document text directly"""
        return self.processor.classify_document(text)
    
    def extract_structured_data(self, text: str, doc_type: str = None) -> Dict[str, Any]:
        """Extract structured data from text"""
        return self.processor.extract_structured_data(text, doc_type)