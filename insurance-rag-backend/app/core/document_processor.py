"""
Multi-format document processor for PDF, DOCX, TXT, HTML, XLSX, PPTX
with classification and structured data extraction
"""

import os
import re
import PyPDF2
from docx import Document
from bs4 import BeautifulSoup
import openpyxl
from pptx import Presentation
from typing import Dict, List, Any, Tuple
import json

class DocumentProcessor:
    """Process various document formats and extract text with classification"""
    
    # Insurance keywords for classification
    INSURANCE_KEYWORDS = [
        'policy', 'coverage', 'premium', 'deductible', 'claim',
        'insured', 'beneficiary', 'exclusion', 'liability',
        'underwriting', 'renewal', 'copay', 'coinsurance',
        'auto', 'renters', 'health', 'life', 'motorcycle',
        'collision', 'comprehensive', 'liability'
    ]
    
    # Non-insurance keywords for rejection
    NON_INSURANCE_KEYWORDS = [
        'salary', 'compensation', 'bonus', 'employment', 'contract',
        'probation', 'termination', 'notice period', 'NDA',
        'non-compete', 'confidential', 'intellectual property',
        'employee', 'handbook', 'job description', 'offer letter'
    ]
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"Error reading PDF: {e}")
        return text
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """Extract text from DOCX file"""
        text = ""
        try:
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                if paragraph.text:
                    text += paragraph.text + "\n"
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text:
                            text += cell.text + " "
                    text += "\n"
        except Exception as e:
            print(f"Error reading DOCX: {e}")
        return text
    
    @staticmethod
    def extract_text_from_txt(file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading TXT: {e}")
            return ""
    
    @staticmethod
    def extract_text_from_html(file_path: str) -> str:
        """Extract text from HTML file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                soup = BeautifulSoup(file.read(), 'html.parser')
                for script in soup(["script", "style"]):
                    script.decompose()
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)
                return text
        except Exception as e:
            print(f"Error reading HTML: {e}")
            return ""
    
    @staticmethod
    def extract_text_from_xlsx(file_path: str) -> str:
        """Extract text from Excel file"""
        text = ""
        try:
            workbook = openpyxl.load_workbook(file_path, data_only=True)
            for sheet_name in workbook.sheetnames:
                sheet = workbook[sheet_name]
                text += f"\n--- Sheet: {sheet_name} ---\n"
                for row in sheet.iter_rows(values_only=True):
                    row_text = " | ".join([str(cell) for cell in row if cell is not None])
                    if row_text:
                        text += row_text + "\n"
        except Exception as e:
            print(f"Error reading XLSX: {e}")
        return text
    
    @staticmethod
    def extract_text_from_pptx(file_path: str) -> str:
        """Extract text from PowerPoint file"""
        text = ""
        try:
            prs = Presentation(file_path)
            for slide_num, slide in enumerate(prs.slides):
                text += f"\n--- Slide {slide_num + 1} ---\n"
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text:
                        text += shape.text + "\n"
        except Exception as e:
            print(f"Error reading PPTX: {e}")
        return text
    
    @staticmethod
    def extract_text(file_path: str, file_extension: str = None) -> str:
        """Extract text based on file extension"""
        if file_extension is None:
            file_extension = os.path.splitext(file_path)[1].lower()
        
        extractors = {
            '.pdf': DocumentProcessor.extract_text_from_pdf,
            '.docx': DocumentProcessor.extract_text_from_docx,
            '.txt': DocumentProcessor.extract_text_from_txt,
            '.html': DocumentProcessor.extract_text_from_html,
            '.htm': DocumentProcessor.extract_text_from_html,
            '.xlsx': DocumentProcessor.extract_text_from_xlsx,
            '.xls': DocumentProcessor.extract_text_from_xlsx,
            '.pptx': DocumentProcessor.extract_text_from_pptx,
            '.ppt': DocumentProcessor.extract_text_from_pptx,
        }
        
        if file_extension in extractors:
            return extractors[file_extension](file_path)
        else:
            print(f"Unsupported file format: {file_extension}")
            return ""
    
    @staticmethod
    def get_supported_extensions() -> list:
        """Return list of supported file extensions"""
        return ['.pdf', '.docx', '.txt', '.html', '.htm', '.xlsx', '.xls', '.pptx', '.ppt']
    
    @staticmethod
    def classify_document(text: str) -> Dict[str, Any]:
        """
        Classify document as insurance or non-insurance
        
        Returns:
            {
                "type": "insurance" | "non_insurance",
                "confidence": float (0-1),
                "detected_type": "Auto" | "Health" | "Renters" | "Unknown",
                "keywords_found": [],
                "reason": "..."
            }
        """
        text_lower = text.lower()
        
        # Count insurance keywords
        insurance_count = 0
        insurance_keywords_found = []
        for kw in DocumentProcessor.INSURANCE_KEYWORDS:
            if kw in text_lower:
                insurance_count += 1
                insurance_keywords_found.append(kw)
        
        # Count non-insurance keywords
        non_insurance_count = 0
        non_insurance_keywords_found = []
        for kw in DocumentProcessor.NON_INSURANCE_KEYWORDS:
            if kw in text_lower:
                non_insurance_count += 1
                non_insurance_keywords_found.append(kw)
        
        # Calculate confidence
        total = insurance_count + non_insurance_count
        if total == 0:
            return {
                "type": "unknown",
                "confidence": 0.0,
                "detected_type": "Unknown",
                "keywords_found": [],
                "reason": "No insurance or non-insurance keywords detected."
            }
        
        insurance_ratio = insurance_count / total
        
        # Detect specific policy type
        detected_type = "Unknown"
        if "auto" in text_lower or "vehicle" in text_lower or "car" in text_lower:
            detected_type = "Auto"
        elif "health" in text_lower or "medical" in text_lower or "hospital" in text_lower:
            detected_type = "Health"
        elif "renters" in text_lower or "rental" in text_lower or "tenant" in text_lower:
            detected_type = "Renters"
        elif "life" in text_lower or "death" in text_lower or "beneficiary" in text_lower:
            detected_type = "Life"
        
        if insurance_ratio >= 0.6:
            return {
                "type": "insurance",
                "confidence": insurance_ratio,
                "detected_type": detected_type,
                "keywords_found": insurance_keywords_found[:10],
                "reason": f"Insurance keywords found: {', '.join(insurance_keywords_found[:5])}"
            }
        elif insurance_ratio >= 0.3:
            return {
                "type": "uncertain",
                "confidence": insurance_ratio,
                "detected_type": detected_type,
                "keywords_found": insurance_keywords_found[:10],
                "reason": f"Mixed content. Insurance ratio: {insurance_ratio:.2%}"
            }
        else:
            return {
                "type": "non_insurance",
                "confidence": 1 - insurance_ratio,
                "detected_type": "Unknown",
                "keywords_found": non_insurance_keywords_found[:10],
                "reason": f"Non-insurance keywords found: {', '.join(non_insurance_keywords_found[:5])}"
            }
    
    @staticmethod
    def extract_structured_data(text: str, doc_type: str = None) -> Dict[str, Any]:
        """
        Extract structured data from document text
        
        Returns:
            {
                "policy_number": "...",
                "insurer": "...",
                "coverage_period": "...",
                "deductible": "...",
                "coverage_limit": "...",
                "premium": "..."
            }
        """
        data = {}
        
        # Pattern matching for common insurance data
        patterns = {
            "policy_number": r'(?:policy|policy\s*number|policy\s*no)[:\s]*([A-Z0-9\-]+)',
            "insurer": r'(?:insurer|insurance\s*company|provider)[:\s]*([A-Za-z\s]+)',
            "coverage_period": r'(?:coverage\s*period|policy\s*period)[:\s]*([\w\s,]+)',
            "deductible": r'(?:deductible)[:\s]*\$?([\d,]+)',
            "coverage_limit": r'(?:coverage\s*limit|limit)[:\s]*\$?([\d,]+)',
            "premium": r'(?:premium|monthly\s*premium)[:\s]*\$?([\d,]+)',
            "vehicle": r'(?:vehicle|car)[:\s]*([\d\s\w]+)',
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data[key] = match.group(1).strip()
        
        return data